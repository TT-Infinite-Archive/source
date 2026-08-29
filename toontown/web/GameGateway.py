from bson.int64 import Int64

from direct.directnotify import DirectNotifyGlobal
from direct.showbase.DirectObject import DirectObject

from otp.distributed import OtpDoGlobals
from toontown.web.GatewaySocket import openSocket

NOT_PENDING = 'The Toon is no longer awaiting a name.'

# An account imported from the old database waits under this prefix:
LEGACY_PREFIX = 'legacy:'

# What a superseded account is parked under once its Toons have moved off it:
RETIRED_PREFIX = 'migrated:'

AV_SET_SIZE = 6


class GameGateway(DirectObject):
    """
    The UberDOG's half of the website gateway.

    Each district manages its own socket and status, 
    so commands go directly from the website to the specific district.
    """

    notify = DirectNotifyGlobal.directNotify.newCategory('GameGateway')

    def __init__(self, air, socket=None):
        DirectObject.__init__(self)

        self.air = air

        self.ops = {
            'approveName': self.approveName,
            'denyName': self.denyName,
            'claimLegacyAccount': self.claimLegacyAccount,
        }

        self.socket = socket if socket is not None else openSocket(onCommand=self.apply)
        if socket is not None:
            self.socket.onCommand = self.apply

        if self.socket is None:
            self.notify.warning('No gateway; name review will not reach the game.')

    # --- COMMANDS ---

    def apply(self, command):
        commandId = command.get('id')
        op = self.ops.get(command.get('op'))

        def done(ok, result=None):
            if self.socket:
                self.socket.sendResult(commandId, ok, result)

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

    def claimLegacyAccount(self, args, done):
        """
        Hand an account imported from the old database to a website user.
        """
        userId = str(args['userId'])
        username = str(args['username'])
        legacyName = str(args['legacyUsername'])
        confirm = bool(args.get('confirm'))

        objects = self.air.dbAstronCursor.objects

        legacy = objects.find_one(
            {'fields.ACCOUNT_ID': LEGACY_PREFIX + legacyName})
        if not legacy or legacy.get('dclass') != 'Account':
            done(False, {'error': 'That account has already been migrated.'})
            return

        current = objects.find_one({'fields.ACCOUNT_ID': userId})
        if current is not None and current.get('dclass') != 'Account':
            current = None

        if current is not None and current['_id'] == legacy['_id']:
            done(False, {'error': 'That account is already yours.'})
            return

        legacyToons = self.toonNames(self.liveToons(legacy))
        currentToons = self.toonNames(self.liveToons(current))
        fits = len(legacyToons) + len(currentToons) <= AV_SET_SIZE

        if not confirm:
            done(True, {
                'legacyToons': legacyToons,
                'currentToons': currentToons,
                'fits': fits,
            })
            return

        if not fits:
            done(False, {'error':
                         'Together that is %d Toons, and an account holds %d.'
                         % (len(legacyToons) + len(currentToons), AV_SET_SIZE)})
            return

        self.mergeAccounts(legacy, current, userId, username)

        self.notify.info('Account %s claimed legacy account %s (%d).'
                         % (userId, legacyName, legacy['_id']))

        done(True, {
            'legacyToons': legacyToons,
            'currentToons': currentToons,
            'fits': True,
            'claimed': True,
        })

    # --- HELPERS ---

    def liveToons(self, account):
        """
        The occupied Toon slots, as (index, doId).
        """
        if not account:
            return []
        avSet = account['fields'].get('ACCOUNT_AV_SET') or []
        return [(index, int(avId))
                for index, avId in enumerate(avSet) if int(avId)]

    def toonNames(self, slots):
        names = []
        for _, avId in slots:
            toon = self.air.dbAstronCursor.objects.find_one({'_id': avId})
            if not toon:
                continue
            names.append(toon['fields'].get('setName', {}).get('_0')
                         or '(unnamed)')
        return names

    def mergeAccounts(self, legacy, current, userId, username):
        """
        Move any Toons off the player's current account and onto the legacy
        one, then hand them the legacy account.

        The current account is retired before the legacy one is claimed. If
        this dies in between, the player has no account and logs in to a fresh
        one, which is recoverable; the other order would leave two accounts
        answering to the same user id, which is not good
        """
        objects = self.air.dbAstronCursor.objects

        # Nobody may be holding either account open while it is rewritten.
        for account in (legacy, current):
            if account:
                self.air.csm.killAccount(
                    account['_id'], 'Your account is being migrated.'
                    ' Please log in again.')

        avSet = [Int64(avId) for avId in
                 (legacy['fields'].get('ACCOUNT_AV_SET') or [])]
        avSet += [Int64(0)] * (AV_SET_SIZE - len(avSet))

        estateId = int(legacy['fields'].get('ESTATE_ID') or 0)
        deleted = list(legacy['fields'].get('ACCOUNT_AV_SET_DEL') or [])
        moved = []

        if current is not None:
            for _, avId in self.liveToons(current):
                slot = avSet.index(Int64(0))
                avSet[slot] = Int64(avId)
                moved.append((slot, avId))

            # The Toons moving across need an estate if the legacy one had none.
            if not estateId:
                estateId = int(current['fields'].get('ESTATE_ID') or 0)

            deleted += list(current['fields'].get('ACCOUNT_AV_SET_DEL') or [])

            objects.update_one(
                {'_id': current['_id'], 'fields.ACCOUNT_ID': userId},
                {'$set': {'fields.ACCOUNT_ID': RETIRED_PREFIX + userId,
                          'fields.ACCOUNT_AV_SET': [Int64(0)] * AV_SET_SIZE}})

        objects.update_one(
            {'_id': legacy['_id']},
            {'$set': {'fields.ACCOUNT_ID': userId,
                      'fields.USERNAME': username,
                      'fields.ACCOUNT_AV_SET': avSet,
                      'fields.ACCOUNT_AV_SET_DEL': deleted,
                      'fields.ESTATE_ID': Int64(estateId)}})

        # Each Toon must point to the correct (legacy) account, 
        # including deleted ones, so they don't end up linked to the 
        # retired account after migration or a restore.
        following = [avId for _, avId in moved]
        following += [int(entry['Avatar']) for entry in deleted
                      if int(entry.get('Avatar') or 0)]

        for avId in following:
            objects.update_one(
                {'_id': avId},
                {'$set': {'fields.setDISLid': {'_0': Int64(legacy['_id'])}}})

        if estateId:
            # Estate slot N belongs to Toon slot N; the AI wipes a slot's
            # garden whenever the two disagree.
            #
            # "_0" because setSlotNToonId takes an unnamed parameter. Astron
            # refuses to load an object whose stored shape disagrees with the
            # dclass file, and a refusal here reads as an estate nobody can
            # teleport to, causing a district crash.
            slots = {'fields.setSlot%dToonId' % index: {'_0': avId}
                     for index, avId in enumerate(avSet)}
            objects.update_one({'_id': estateId}, {'$set': slots})

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
