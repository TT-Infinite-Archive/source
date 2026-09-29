from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectGlobalAI import DistributedObjectGlobalAI

from toontown.catalog import CatalogItem


class DistributedDeliveryManagerAI(DistributedObjectGlobalAI):
    notify = DirectNotifyGlobal.directNotify.newCategory("DistributedDeliveryManagerAI")

    def sendDeliverGifts(self, doId, timestamp):
        self.sendUpdate('deliverGifts', [doId, timestamp])

    def sendRequestPurchaseGift(self, item, toId, fromId, context, phone):
        self.sendUpdate('receiveRequestPurchaseGift',
                        [item.getBlob(store=CatalogItem.Customization), toId, fromId, phone.doId, context])
