from direct.distributed.DistributedObjectUD import DistributedObjectUD
from direct.directutil import LargeBlobSenderConsts


class ZoneBlobSenderUD(DistributedObjectUD):
    def __init__(self, air, targetAvId, useDisk=0):
        DistributedObjectUD.__init__(self, air)
        self.targetAvId = targetAvId

        self.mode = 0
        if useDisk:
            self.mode |= LargeBlobSenderConsts.USE_DISK

    def start(self, data):
        # send the data
        self.data = bytes(data)
        self.chunkSize = LargeBlobSenderConsts.ChunkSize
        self.delay = 0.0005
        self.sendChunk()

    def sendChunk(self, task=None):
        if len(self.data):
            self.sendUpdateToAccountId(self.targetAvId, 'setChunk', [self.data[:self.chunkSize]])
            self.data = self.data[self.chunkSize:]
            taskMgr.doMethodLater(self.delay, self.sendChunk, self.uniqueName('chunk-task'))
        else:
            # send final empty string
            self.sendUpdateToAccountId(self.targetAvId, 'setChunk', [''])
            if task:
                return task.done

    def delete(self):
        taskMgr.remove(self.uniqueName('chunk-task'))
        DistributedObjectUD.delete(self)

    def getMode(self):
        return self.mode

    def getTargetAvId(self):
        return self.targetAvId

    def setAck(self):
        assert self.air.getAccountIdFromSender() == self.targetAvId
        self.requestDelete()
