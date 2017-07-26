from direct.distributed.DistributedObjectGlobalUD import DistributedObjectGlobalUD
from toontown.zone.ZoneBlobSenderUD import ZoneBlobSenderUD
from toontown.toonbase.ToontownGlobals import HoodHierarchy
import os
import hashlib


class ZoneManagerUD(DistributedObjectGlobalUD):
    notify = directNotify.newCategory('ZoneManagerUD')
    notify.setDebug(1)
    COMPLETED = 1
    NOT_DOWNLOADED = 0
    OUTDATED = -1
    MAX_SIZE = int(2.5e+7)  # 25 MB

    def __init__(self,  air):
        DistributedObjectGlobalUD.__init__(self, air)

        self.zoneData = {}

        self.mountPoint = os.path.join('..', 'resources')

    def loadZones(self):
        for zoneId in HoodHierarchy.keys():
            filename = self.getZoneFilename(zoneId)
            location = os.path.join(self.mountPoint, filename)
            if not os.path.exists(location) or not os.path.isfile(location):
                self.notify.debug('%s does not exist!' % location)
                continue
            from panda3d.core import Filename, StreamReader
            # I have to use Panda3D aids to open the file apparently.
            f2 = Filename(location)
            f2.setBinary()
            input = StreamReader(vfs.openReadFile(f2, 1), 1)
            size = os.stat(location).st_size
            data = input.extractBytes(size)
            hash = hashlib.md5(data).hexdigest()
            self.notify.info('Loaded modification: %s, hash=%s, %s bytes' % (location, hash, size))
            self.zoneData[zoneId] = (data, hash, size)
        self.sendUpdate('setModifiedZones', [self.zoneData.keys()])
        self.notify.debug("Modified zones loaded: %s" % self.zoneData.keys())

    def generate(self):
        DistributedObjectGlobalUD.generate(self)
        self.loadZones()

    def requestModifiedZones(self):
        senderId = self.air.getAccountIdFromSender()
        self.sendUpdateToAccountId(senderId, 'setModifiedZones', [self.zoneData.keys()])

    def requestZoneData(self, zone, hash):
        senderId = self.air.getAccountIdFromSender()
        self.notify.debug('requestZoneData: %s %s' % (zone, hash))
        if zone not in self.zoneData.keys():
            self.sendUpdateToAccountId(senderId, 'setBlobId', [0, self.COMPLETED, 0])
            return
        if hash == self.zoneData[zone][1]:
            self.sendUpdateToAccountId(senderId, 'setBlobId', [0, self.COMPLETED, 0])
            return
        elif hash != self.zoneData[zone][1] and hash != '':
            mode = self.OUTDATED
        else:
            mode = self.NOT_DOWNLOADED
        largeBlob = ZoneBlobSenderUD(self.air, senderId)
        largeBlob.generateWithRequiredAndId(doId=self.air.allocateChannel(), parentId=self.air.getGameDoId(), zoneId=2)
        largeBlob.start(self.zoneData[zone][0])

        size = self.zoneData[zone][2]
        self.sendUpdateToAccountId(senderId, 'setBlobId', [largeBlob.doId, mode, size])

    def getZoneFilename(self, zoneId):
        return 'zone_%d.mf' % zoneId

    def requestReload(self):
        self.notify.debug('Reloaded requested.')
        self.loadZones()

