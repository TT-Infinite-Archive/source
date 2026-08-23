import time
from panda3d.core import ConfigVariableBool, ConfigVariableList, ConfigVariableString, MultiplexStream, Notify, StreamWriter

from otp.distributed.DistributedDirectoryAI import DistributedDirectoryAI
from toontown.distributed.ToontownInternalRepository import \
    ToontownInternalRepository
from otp.distributed import OtpDoGlobals

if ConfigVariableBool('want-rpc-server', False).getValue():
    from toontown.rpc.ToontownRPCServer import ToontownRPCServer
    from toontown.rpc.ToontownRPCHandler import ToontownRPCHandler

if ConfigVariableBool('want-game-gateway', False).getValue():
    from toontown.web.GameGateway import GameGateway

from toontown.parties.ToontownTimeManager import ToontownTimeManager

class ToontownUberRepository(ToontownInternalRepository):
    def __init__(self, baseChannel, serverId):
        ToontownInternalRepository.__init__(
            self, baseChannel, serverId, dcSuffix='UD')

        self.rpcServer = None
        self.gateway = None
        self.globalObjects = {}
        self.remoteGlobalObjects = {}

        self.notify.setInfo(True)

        # Logging
        from direct.directnotify import Notifier
        self.nout = MultiplexStream()
        Notify.ptr().setOstreamPtr(self.nout, 0)
        Notifier.Notifier.streamWriter = StreamWriter(self.nout, False)
        self.nout.addStandardOutput()

    def handleConnected(self):
        ToontownInternalRepository.handleConnected(self)
        self.registerForChannel(OtpDoGlobals.MESSENGER_CHANNEL_UD)

        if ConfigVariableBool('generate-root-object', False).getValue():
            rootObj = DistributedDirectoryAI(self)
            rootObj.generateWithRequiredAndId(self.getGameDoId(), 0, 0)

        if ConfigVariableBool('want-rpc-server', False).getValue():
            endpoint = ConfigVariableString(
                'rpc-server-endpoint', 'http://localhost:8080/').getValue()
            self.rpcServer = ToontownRPCServer(
                endpoint, ToontownRPCHandler(self))
            self.rpcServer.start(useTaskChain=True)

        self.toontownTimeManager = ToontownTimeManager(time.time(), time.time(), globalClock.getRealTime())

        globalObjectDefs = ConfigVariableList('generate-global-object')
        for globalObjectDef in globalObjectDefs:
            doId, dcname = globalObjectDef.split(' ', 1)
            doId = int(doId)
            self.notify.info('Creating %s(%d)...' % (dcname, doId))
            self.globalObjects[dcname] = self.generateGlobalObject(doId, dcname)

        for dcname, doId in list(OtpDoGlobals.dcname2doId.items()):
            if dcname not in self.globalObjects:
                self.remoteGlobalObjects[dcname] = \
                    RemoteGlobalObject(self, dcname, doId)

        # Last, so its first heartbeat has the globals it reports on.
        if ConfigVariableBool('want-game-gateway', False).getValue():
            self.gateway = GameGateway(self)

        self.notify.info('Done.')

    def getGlobalObject(self, dcname):
        if dcname in self.globalObjects:
            return self.globalObjects.get(dcname)
        elif dcname in self.remoteGlobalObjects:
            return self.remoteGlobalObjects[dcname]


class RemoteGlobalObject:
    def __init__(self, air, dcname, doId):
        self.air = air
        self.dcname = dcname
        self.doId = doId

    def __getattr__(self, item):
        if not item.startswith('_'):
            return RemoteGlobalObjectMethod(self.air, self.dcname, self.doId, item)


class RemoteGlobalObjectMethod:
    def __init__(self, air, dcname, doId, name):
        self.air = air
        self.dcname = dcname
        self.doId = doId
        self.name = name

    def __call__(self, *args):
        dclass = self.air.dclassesByName[self.dcname + 'UD']
        dg = dclass.aiFormatUpdate(
            self.name, self.doId, self.doId, self.air.ourChannel, list(args))
        self.air.send(dg)
