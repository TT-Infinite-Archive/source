from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectGlobalUD import DistributedObjectGlobalUD
from direct.fsm.FSM import FSM
from toontown.toonbase import ToontownGlobals
from toontown.catalog import CatalogItem
from toontown.catalog.CatalogItemList import CatalogItemList
from bson import binary
import time


FIELD_NAME = 0
FIELD_MONEY = 1
FIELD_GIFT_SCHEDULE = 2
FIELD_DELIVERY_SCHEDULE = 3
FIELD_MAILBOX_CONTENTS = 4
FIELD_CATALOG = 5
FIELD_DNA = 6

class DistributedDeliveryManagerUD(DistributedObjectGlobalUD):
    notify = DirectNotifyGlobal.directNotify.newCategory("DistributedDeliveryManagerUD")

    def announceGenerate(self):
        DistributedObjectGlobalUD.announceGenerate(self)
        self.fsms = []

    def receiveRequestPurchaseGift(self, blob, toId, fromId, phoneId, context):
        sender = simbase.air.getAvatarIdFromSender()
        data = [blob, phoneId, context, fromId]
        RetrieveAvatarInfoFSM(self, toId, fromId, data, self.handleAvatarInfoResp).start()

    def handleAvatarInfoResp(self, success, avInfo, toId, fromId, data):
        if not success:
            return

        gifteeInfo = avInfo[toId]
        blob, phoneId, context, sender = data
        item = CatalogItem.getItem(blob)
        item.deliveryDate = int(time.time() / 60) + item.getDeliveryTime()
        item.giftTag = fromId

        gifteeSchedule = CatalogItemList(gifteeInfo[FIELD_GIFT_SCHEDULE],
                                         store=CatalogItem.Customization | CatalogItem.DeliveryDate)

        retCode = ToontownGlobals.P_ItemAvailable
        if self.isMailboxFull(gifteeInfo):
            retCode = ToontownGlobals.P_MailboxFull
        elif self.isMailboxFull(gifteeInfo):
            retCode = ToontownGlobals.P_OnOrderListFull
        elif self.reachedPurchaseLimit(item, gifteeInfo):
            retCode = ToontownGlobals.P_ReachedPurchaseLimit

        self.__sendPurchaseResponse(fromId, phoneId, sender, context, retCode)

        if retCode == ToontownGlobals.P_ItemAvailable:
            gifteeSchedule.append(item)
            self.updateDeliverySchedule(toId, gifteeSchedule)
            self.sendToAvatar('setGiftSchedule', [gifteeSchedule.getBlob()], toId)

    def updateDeliverySchedule(self, gifteeId, giftSchedule):
        self.air.dbInterface.updateObject(
            self.air.dbId,
            gifteeId,
            self.air.dclassesByName['DistributedToonUD'],
            {'setGiftSchedule': (giftSchedule.getBlob(),)}
        )

    def sendToAvatar(self, field, values, recipient):
        dg = self.air.dclassesByName['DistributedToonUD'].getFieldByName(field).aiFormatUpdate(
            recipient, recipient, simbase.air.ourChannel, values)
        self.air.send(dg)

    def getCatalog(self, avInfo):
        monthlyCatalog, weeklyCatalog, backCatalog = avInfo[FIELD_CATALOG]

        monthlyCatalog = CatalogItemList(monthlyCatalog)
        weeklyCatalog = CatalogItemList(weeklyCatalog)
        backCatalog = CatalogItemList(backCatalog)

        return monthlyCatalog, weeklyCatalog, backCatalog

    def reachedPurchaseLimit(self, item, avInfo):
        limit = item.getPurchaseLimit()
        if limit == 0:
            return False

        mailboxContents = CatalogItemList(avInfo[FIELD_MAILBOX_CONTENTS])
        onOrder = CatalogItemList(avInfo[FIELD_DELIVERY_SCHEDULE])
        onGiftOrder = CatalogItemList(avInfo[FIELD_GIFT_SCHEDULE])
        if mailboxContents.count(item) >= limit:
            return True
        if onOrder.count(item) >= limit:
            return True
        if onGiftOrder.count(item) >= limit:
            return True
        return False

    def isMailboxFull(self, avInfo):
        onOrder = CatalogItemList(avInfo[FIELD_DELIVERY_SCHEDULE])
        mailboxContents = CatalogItemList(avInfo[FIELD_MAILBOX_CONTENTS])
        if len(mailboxContents) + len(onOrder) >= ToontownGlobals.MaxMailboxContents:
            return True
        return False

    def isGiftOrderFull(self, avInfo):
        onGiftOrder = CatalogItemList(avInfo[FIELD_GIFT_SCHEDULE])
        mailboxContents = CatalogItemList(avInfo[FIELD_MAILBOX_CONTENTS])
        if len(mailboxContents) + len(onGiftOrder) >= ToontownGlobals.MaxMailboxContents:
            return True
        return False

    def __sendPurchaseResponse(self, avId, phoneId, shardId, context, retcode):
        recipient = self.GetPuppetConnectionChannel(avId)
        field = self.air.dclassesByName['DistributedPhoneAI'].getFieldByName('requestGiftPurchaseResponse')
        dg = field.aiFormatUpdate(phoneId, recipient, shardId, [context, retcode])
        simbase.air.send(dg)

    def requestAck(self):
        self.sendUpdateToAvatarId(self.air.getAvatarIdFromSender(), 'returnAck', [])

class RetrieveAvatarInfoFSM(FSM):
    def __init__(self, mgr, toId, fromId, data, callback):
        FSM.__init__(self, 'AvatarInfoFSM')
        self.mgr = mgr
        self.callback = callback
        self.toId = toId
        self.fromId = fromId
        self.data = data
        self.avInfo = {}
        self.avQueried = []

    def start(self):
        self.mgr.fsms.append(self)
        self.demand('QueryAvatar', self.toId)

    def enterQueryAvatar(self, avId):
        self.mgr.air.dbInterface.queryObject(self.mgr.air.dbId, avId, self.handleRetrieveAvatar)

    def handleRetrieveAvatar(self, dclass, fields):
        if 'setCatalog' not in fields:
            self.demand('Error')
            return

        self.avInfo[avId] = (
            fields['setName'][0],
            fields['setMoney'][0],
            fields['setGiftSchedule'][0],
            fields['setDeliverySchedule'][0],
            fields['setMailboxContents'][0],
            fields['setCatalog'][0],
            fields['setDNAString'][0]
        )

        if self.fromId is not None and self.fromId not in self.avInfo.keys():
            self.demand('QueryAvatar', self.fromId)
        else:
            self.demand('Finished')

    def enterFinished(self):
        self.callback(True, self.avInfo, self.toId, self.fromId, self.data)
        self.demand('Off')

    def enterError(self):
        self.callback(False, None, None, None, None)
        self.demand('Off')

    def enterOff(self):
        self.mgr.fsms.remove(self)
