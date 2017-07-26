from direct.directutil.DistributedLargeBlobSender import DistributedLargeBlobSender
from direct.distributed.DistributedObject import DistributedObject


class ZoneBlobSender(DistributedLargeBlobSender):
    def announceGenerate(self):
        DistributedLargeBlobSender.notify.debug('announceGenerate')
        DistributedObject.announceGenerate(self)

        if not self.useDisk:
            self.blob = ''

    def setChunk(self, chunk):
        DistributedLargeBlobSender.setChunk(self, chunk)
        if base.cr.zoneManager and base.cr.zoneManager.currentRequestedZone:
            name = 'Zone %d' % base.cr.zoneManager.currentRequestedZone
            filesize = base.cr.zoneManager.currentFileSize
            if filesize == 0:
                return
            else:
                percent = len(self.blob) / float(filesize)
                percent = min(int(percent * 100), 100)
                messenger.send('downloadWatcherUpdate', [name, percent])
