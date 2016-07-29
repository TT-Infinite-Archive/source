from panda3d.core import ConfigVariableList

from otp.distributed.DistributedDirectoryAI import DistributedDirectoryAI
from toontown.distributed.ToontownInternalRepository import \
    ToontownInternalRepository
from otp.distributed import OtpDoGlobals

if config.GetBool('want-rpc-server', False):
    from toontown.rpc.ToontownRPCServer import ToontownRPCServer
    from toontown.rpc.ToontownRPCHandler import ToontownRPCHandler


class ToontownUberRepository(ToontownInternalRepository):
    def __init__(self, baseChannel, serverId):
        ToontownInternalRepository.__init__(
            self, baseChannel, serverId, dcSuffix='UD')

        self.rpcServer = None
        self.globalObjects = {}
        self.remoteGlobalObjects = {}

        self.notify.setInfo(True)

    def handleConnected(self):
        ToontownInternalRepository.handleConnected(self)

        if config.GetBool('generate-root-object', False):
            rootObj = DistributedDirectoryAI(self)
            rootObj.generateWithRequiredAndId(self.getGameDoId(), 0, 0)

        if config.GetBool('want-rpc-server', False):
            endpoint = config.GetString(
                'rpc-server-endpoint', 'http://localhost:8080/')
            self.rpcServer = ToontownRPCServer(
                endpoint, ToontownRPCHandler(self))
            self.rpcServer.start(useTaskChain=True)

        globalObjectDefs = ConfigVariableList('generate-global-object')
        for globalObjectDef in globalObjectDefs:
            doId, dcname = globalObjectDef.split(' ', 1)
            doId = int(doId)
            self.notify.info('Creating %s(%d)...' % (dcname, doId))
            self.globalObjects[dcname] = self.generateGlobalObject(doId, dcname)

        for dcname, doId in OtpDoGlobals.dcname2doId.items():
            if dcname not in self.globalObjects:
                self.remoteGlobalObjects[dcname] = \
                    RemoteGlobalObject(self, dcname, doId)

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
