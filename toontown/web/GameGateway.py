from panda3d.core import ConfigVariableString

from direct.directnotify import DirectNotifyGlobal
from direct.showbase.DirectObject import DirectObject

from otp.distributed import OtpDoGlobals
from toontown.web.GatewaySocket import GatewaySocket, gatewayToken, socketUrl

NOT_PENDING = 'The Toon is no longer awaiting a name.'


class GameGateway(DirectObject):
    """
    The UberDOG's half of the website gateway.

    Each district manages its own socket and status, 
    so commands go directly from the website to the specific district.
    """

    notify = DirectNotifyGlobal.directNotify.newCategory('GameGateway')

    def __init__(self, air):
        DirectObject.__init__(self)

        self.air = air

        self.ops = {
            'approveName': self.approveName,
            'denyName': self.denyName,
        }

        self.socket = None

        token = gatewayToken()
        if not token:
            self.notify.warning(
                'want-game-gateway is set but TTI_GATEWAY_TOKEN is not;'
                ' name review will not reach the game.')
            return

        url = ConfigVariableString('gateway-url', '').getValue()
        endpoint = ConfigVariableString('account-service-url', '').getValue()

        if not url and not endpoint:
            self.notify.warning('account-service-url is unset.')
            return

        self.socket = GatewaySocket(
            url or socketUrl(endpoint), token, onCommand=self.apply)

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

    # --- HELPERS ---

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
