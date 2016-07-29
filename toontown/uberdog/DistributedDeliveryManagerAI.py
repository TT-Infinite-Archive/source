from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectGlobalAI import DistributedObjectGlobalAI


class DistributedDeliveryManagerAI(DistributedObjectGlobalAI):
    notify = DirectNotifyGlobal.directNotify.newCategory("DistributedDeliveryManagerAI")

    def sendDeliverGifts(self, doId, timestamp):
        self.sendUpdate('deliverGifts', [doId, timestamp])
