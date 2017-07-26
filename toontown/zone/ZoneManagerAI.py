from direct.distributed.DistributedObjectGlobalAI import DistributedObjectGlobalAI
from toontown.toonbase.ToontownGlobals import HoodHierarchy
import os


class ZoneManagerAI(DistributedObjectGlobalAI):
    def __init__(self, air):
        DistributedObjectGlobalAI.__init__(self, air)

        self.zoneData = {}

        self.mountPoint = '../resources'

    def announceGenerate(self):
        DistributedObjectGlobalAI.announceGenerate(self)
        self.loadZoneData()

    def loadZoneData(self):
        for zoneId in HoodHierarchy.keys():
            filename = self.getZoneFilename(zoneId)
            location = os.path.join(self.mountPoint, filename)
            if not os.path.exists(location):
                self.notify.debug('%s does not exist!' % location)
                continue
            self.mountFile(filename)
            self.zoneData[zoneId] = 'zone_%d/zone_%d.pdna' % (zoneId, zoneId)

    def mountFile(self, filename):
        from panda3d.core import Multifile, Filename, VirtualFileSystem
        mf = Multifile()
        mf.openRead(Filename(filename))

        vfs = VirtualFileSystem.getGlobalPtr()

        if __debug__:
            mountPoint = '../resources'
        else:
            mountPoint = '/'

        vfs.mount(mf, mountPoint, 0)

    def sendRequestReload(self):
        self.sendUpdate('requestReload', [])

    def getZoneFilename(self, zoneId):
        return 'zone_%d.mf' % zoneId
