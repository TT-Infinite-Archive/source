from direct.distributed.DistributedObjectGlobalAI import DistributedObjectGlobalAI
from toontown.toonbase.ToontownGlobals import HoodHierarchy
import os
import shutil


class ZoneManagerAI(DistributedObjectGlobalAI):
    notify = directNotify.newCategory('ZoneManagerAI')
    notify.setDebug(1)

    def __init__(self, air):
        DistributedObjectGlobalAI.__init__(self, air)

        self.zoneData = {}

        if __debug__:
            self.mountPoint = '../resources'
        else:
            self.mountPoint = 'resources'

    def announceGenerate(self):
        DistributedObjectGlobalAI.announceGenerate(self)
        self.loadZoneData()

    def loadZoneData(self):
        tmpFolder = self.mountPoint + '/tmp'
        if os.path.exists(tmpFolder):
            shutil.rmtree(tmpFolder)

        for hoodId in HoodHierarchy.keys():
            self.loadZone(hoodId)
            for branchId in HoodHierarchy[hoodId]:
                self.loadZone(branchId)

    def loadZone(self, zoneId):
        filename = self.getZoneFilename(zoneId)
        location = self.mountPoint + '/' + filename
        if not os.path.exists(location):
            self.notify.debug('%s does not exist! Skipping...' % location)
            return
        self.extract(location)
        self.zoneData[zoneId] = 'tmp/' + 'zone_%d/' % zoneId + 'zone_%d.pdna' % zoneId

    def extract(self, filename):
        from panda3d.core import Multifile, Filename
        self.notify.debug('Extracting %s...' % filename)
        mf = Multifile()
        fn = Filename(filename)
        fn.makeAbsolute()
        mf.openRead(fn)
        for i, f in enumerate(mf.getSubfileNames()):
            self.notify.debug('%s: %s %s' % (filename, i, f))
            if f.split('.')[-1] in ('dna', 'pdna'):
                self.notify.debug('Extracting %s...' % f)
                s = Filename(self.mountPoint + '/tmp/' + f)
                mf.extractSubfile(i, s)
        mf.close()

    def sendRequestReload(self):
        self.sendUpdate('requestReload', [])

    def getZoneFilename(self, zoneId):
        return 'zone_%d.mf' % zoneId
