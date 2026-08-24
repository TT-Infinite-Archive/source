from panda3d.core import ConfigVariableInt, ConfigVariableString

from direct.directnotify import DirectNotifyGlobal
from direct.showbase.DirectObject import DirectObject

from otp.distributed import OtpDoGlobals
from toontown.distributed.ShardStatusReceiver import ShardStatusReceiver
from toontown.web.AccountServiceClient import AccountServiceClient

NOT_PENDING = 'The Toon is no longer awaiting a name.'

# lastFailure otherwise holds an HTTP status, or None for a network error, so
# neither of those can double as a way of saying the website is fine.
NEVER_FAILED = 'never'
HEALTHY = 'healthy'

class GameGateway(DirectObject):
    """
    The UberDOG's half of the website gateway. There are two types of communication, but 
    only one connection (always outgoing from us):

    Commands: The website queues actions for us to perform. We long-poll for these commands, 
    process them, and send back the results. UberDOG isn't exposed to incoming connections for 
    security reasons.

    Heartbeat: We regularly send district status updates, so the website/launcher can check the 
    latest population info.
    """

    notify = DirectNotifyGlobal.directNotify.newCategory('GameGateway')

    COMMANDS_PATH = 'api/game/commands'
    SHARDS_PATH = 'api/game/shards'
    POLL_TIMEOUT = 40
    RETRY_DELAY = 15
    # How long a batch has to finish before the stragglers are given up on
    BATCH_TIMEOUT = 60
    # How long a district has to acknowledge an invasion command
    INVASION_TIMEOUT = 10
    # Used when the website does not say how many Cogs should invade
    DEFAULT_INVASION_COGS = 1000

    def __init__(self, air):
        DirectObject.__init__(self)

        self.air = air
        self.service = AccountServiceClient(
            ConfigVariableString('account-service-url',
                                 'http://localhost:4321').getValue(),
            ConfigVariableString('account-service-secret', '').getValue())

        self.shardStatus = ShardStatusReceiver(air)

        self.ops = {
            'approveName': self.approveName,
            'denyName': self.denyName,
            'startInvasion': self.startInvasion,
            'stopInvasion': self.stopInvasion,
        }

        self.invasionRequest = 0

        self.pending = set()
        self.results = []
        self.batchId = 0
        self.polling = False

        self.lastFailure = NEVER_FAILED

        self.poll()

        interval = ConfigVariableInt('shard-heartbeat-interval', 15).getValue()
        taskMgr.doMethodLater(
            interval, self.heartbeatTask, 'GameGateway-heartbeat')

    # --- COMMANDS ---

    def poll(self):
        if self.polling:
            return

        self.polling = True
        self.service.get(
            self.COMMANDS_PATH, self.handleCommands, self.handlePollFailure,
            timeout=self.POLL_TIMEOUT)

    def retryLater(self):
        taskMgr.doMethodLater(
            self.RETRY_DELAY, self.retryTask, 'GameGateway-retry')

    def retryTask(self, task):
        self.poll()
        return task.done

    def handlePollFailure(self, status):
        self.polling = False

        # Said once per change of fortune rather than once per retry.
        if status != self.lastFailure:
            self.lastFailure = status

            if status == 503:
                self.notify.warning(
                    'The website has no game server secret configured; no '
                    'command will be delivered until it does.')
            elif status == 401:
                self.notify.warning(
                    'The website refused our secret-- check '
                    'account-service-secret against GAME_SERVER_SECRET.')
            else:
                # Ordinarily just the website not being up, which in
                # development is most of the time
                self.notify.debug('Command poll failed with status %s.' % status)

        self.retryLater()

    def handleCommands(self, response):
        self.polling = False

        if self.lastFailure != HEALTHY:
            if self.lastFailure != NEVER_FAILED:
                self.notify.info('The website is answering again.')
            self.lastFailure = HEALTHY

        commands = response.get('commands') or []
        if not commands:
            self.poll()
            return

        self.notify.info('Applying %d command(s).' % len(commands))
        self.batchId += 1
        self.pending = set(command.get('id') for command in commands)
        self.results = []

        taskMgr.doMethodLater(
            self.BATCH_TIMEOUT, self.batchTimeoutTask,
            'GameGateway-batch-%d' % self.batchId,
            extraArgs=[self.batchId], appendTask=True)

        for command in commands:
            self.apply(command)

    def apply(self, command):
        commandId = command.get('id')
        op = self.ops.get(command.get('op'))

        def done(ok, result=None):
            self.finish(commandId, ok, result)

        if op is None:
            done(False, {'error': 'No such op: %s' % command.get('op')})
            return

        try:
            op(command.get('args') or {}, done)
        except Exception as error:
            self.notify.warning('Command %s raised: %s' % (commandId, error))
            import traceback
            self.notify.warning(traceback.format_exc())
            done(False, {'error': str(error)})

    def finish(self, commandId, ok, result):
        if commandId not in self.pending:
            return

        self.pending.discard(commandId)
        self.results.append({'id': commandId, 'ok': ok, 'result': result})

        if self.pending:
            return

        results, self.results = self.results, []
        self.service.post(
            self.COMMANDS_PATH, {'results': results},
            lambda response: self.poll(),
            self.handleResultFailure)

    def batchTimeoutTask(self, batchId, task):
        if batchId != self.batchId or not self.pending:
            # Finished or superseded
            return task.done

        self.notify.warning(
            '%d command(s) did not finish in %ss; giving up on them so the '
            'queue keeps moving.' % (len(self.pending), self.BATCH_TIMEOUT))

        for commandId in list(self.pending):
            self.finish(commandId, False, {'error': 'Timed out in the game server.'})

        return task.done

    def handleResultFailure(self, status):
        self.notify.warning(
            'Could not report command results (status %s). They will be '
            'handed to us again once the claim goes stale.' % status)
        self.retryLater()

    # --- HEARTBEAT ---

    def heartbeatTask(self, task):
        shards = {}

        # A district reports its name and availability from ToontownDistrictAI
        # and its population from ToontownDistrictStatsAI, so one is only
        # worth sending once both have been heard from
        for channel, status in self.shardStatus.getShards().items():
            if not all(key in status for key in
                       ('name', 'available', 'population', 'created',
                        'timezone')):
                continue

            shards[str(channel)] = {
                'name': status['name'],
                'available': bool(status['available']),
                'population': int(status['population']),
                'created': int(status['created']),
                'timezone': int(status['timezone']),
                'invasion': status.get('invasion'),
                # 0 until the district has scheduled one of its own
                'nextInvasion': int(status.get('nextInvasion') or 0)
            }

        self.service.post(
            self.SHARDS_PATH, {'shards': shards},
            lambda response: None,
            lambda status: self.notify.debug(
                'Shard heartbeat failed with status %s.' % status))

        return task.again

    # --- OPS ---

    def approveName(self, args, done):
        """
        Give the Toon the custom name the player submitted.
        """
        avId = int(args['toonId'])
        name = args['name']

        def online(fields):
            if fields:
                done(False, {'error': NOT_PENDING})
                return

            self.air.dbInterface.updateObject(
                self.air.dbId, avId,
                self.air.dclassesByName['DistributedToonUD'],
                {'setName': (name,)})
            self.setLiveField(avId, 'setName', [name])

            self.whisper(
                avId,
                'Congratulations! The Toon Council has approved your name.'
                ' You are now known as %s!' % name)

            done(True, {'online': True})

        def offline(fields):
            if fields:
                done(False, {'error': NOT_PENDING})
                return
            done(True, {'online': False})

        def activated(doId, isActivated):
            if isActivated:
                # Already told, so nothing is left to acknowledge
                self.claimName(avId, name, ('',), ('',), online)
            else:
                self.claimName(avId, name, ('APPROVED',), (name,), offline)

        self.air.getActivated(avId, activated)

    def denyName(self, args, done):
        """
        Turn the name down.
        """
        avId = int(args['toonId'])
        reason = args['reason']

        def rejected(fields):
            if fields:
                done(False, {'error': NOT_PENDING})
                return

            self.whisper(avId, reason)
            done(True, {})

        self.air.dbInterface.updateObject(
            self.air.dbId, avId,
            self.air.dclassesByName['DistributedToonUD'],
            {'WishNameState': ('REJECTED',)},
            {'WishNameState': ('PENDING',)},
            rejected)

    def startInvasion(self, args, done):
        """
        Send the Cogs into one district.
        """
        shardId = int(args['shardId'])
        cogType = args['cogType']
        totalNumCogs = args.get('numCogs')
        totalNumCogs = (self.DEFAULT_INVASION_COGS if totalNumCogs is None
                        else int(totalNumCogs))
        duration = int(args.get('duration') or 0)
        skeleton = bool(args.get('skeleton'))

        if totalNumCogs < 1:
            done(False, {'error': 'An invasion needs at least one Cog.'})
            return

        if duration < 0:
            done(False, {'error': 'An invasion cannot last a negative time.'})
            return

        self.command(
            'startInvasion', shardId,
            [shardId, cogType, totalNumCogs, skeleton, duration], done)

    def stopInvasion(self, args, done):
        """
        Call the invasion off early.
        """
        shardId = int(args['shardId'])

        self.command('stopInvasion', shardId, [shardId], done)

    # --- HELPERS ---

    def command(self, event, shardId, eventArgs, done):
        """
        Ask one district to do something and wait for it to say how it went.
        """
        if shardId not in self.shardStatus.getShards():
            done(False, {'error': 'No district is running on channel %s.' % shardId})
            return

        self.invasionRequest += 1
        requestId = self.invasionRequest
        responseEvent = 'invasionResponse-%d' % requestId
        taskName = 'GameGateway-%s' % responseEvent

        def settle(ok, error):
            self.ignore(responseEvent)
            taskMgr.remove(taskName)
            done(ok, {} if ok else {'error': error})

        def timedOut(task):
            settle(False, 'The district did not answer in %ss.'
                          % self.INVASION_TIMEOUT)
            return task.done

        self.acceptOnce(responseEvent, settle)
        taskMgr.doMethodLater(self.INVASION_TIMEOUT, timedOut, taskName)

        self.air.sendNetEvent(event, [requestId] + eventArgs)

    def claimName(self, avId, wishName, newState, newWish, callback):
        """
        A compare-and-set against the Toon still waiting on this exact name.
        """
        self.air.dbInterface.updateObject(
            self.air.dbId, avId,
            self.air.dclassesByName['DistributedToonUD'],
            {'WishNameState': newState, 'WishName': newWish},
            {'WishNameState': ('PENDING',), 'WishName': (wishName,)},
            callback)

    def setLiveField(self, avId, fieldName, args):
        """
        A player who is logged in sees the change without going anywhere.
        """
        dclass = self.air.dclassesByName['DistributedToonUD']
        self.air.send(dclass.aiFormatUpdate(
            fieldName, avId, avId, self.air.ourChannel, args))

    def whisper(self, avId, message):
        """
        A system whisper to whoever is playing this Toon, on the same channel
        the moderator tools use.
        """
        dclass = self.air.dclassesByName['ClientServicesManagerUD']
        self.air.send(dclass.aiFormatUpdate(
            'systemMessage',
            OtpDoGlobals.OTP_DO_ID_CLIENT_SERVICES_MANAGER,
            avId + (1001 << 32), self.air.ourChannel, [message]))
