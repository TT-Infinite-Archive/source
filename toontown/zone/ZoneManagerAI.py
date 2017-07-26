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
            self.mountPoint = '.'

    def announceGenerate(self):
        DistributedObjectGlobalAI.announceGenerate(self)
        self.loadZoneData()

    def loadZoneData(self):
        tmpFolder = self.mountPoint + '/tmp'
        if os.path.exists(tmpFolder):
            shutil.rmtree(tmpFolder)

        for zoneId in HoodHierarchy.keys():
            filename = self.getZoneFilename(zoneId)
            location = self.mountPoint + '/' + filename
            if not os.path.exists(location):
                self.notify.debug('%s does not exist!' % location)
                continue
            self.extract(location)
            self.zoneData[zoneId] = 'tmp/' + 'zone_%d/' % zoneId + 'zone_%d.pdna' % zoneId

    def extract(self, filename):
        from panda3d.core import Multifile, Filename
        mf = Multifile()
        fn = Filename(filename)
        fn.makeAbsolute()
        mf.openReadWrite(fn)
        for i, f in enumerate(mf.getSubfileNames()):
            if f.split('.')[-1] in ('dna', 'pdna'):
                self.notify.debug('Extracting %s...' % f)
                s = Filename(self.mountPoint + '/tmp/' + f)
                mf.extractSubfile(i, s)

    def sendRequestReload(self):
        self.sendUpdate('requestReload', [])

    def getZoneFilename(self, zoneId):
        return 'zone_%d.mf' % zoneId
