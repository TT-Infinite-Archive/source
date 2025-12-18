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


class GiftUD:
    def __init__(self):
        self.gifterId = 0
        self.gifterName = ''
        self.gifteeId = 0
        self.blob = ''
        self.deliveryTime = 0

    def getMongoDocument(self):
        return {
            "gifterId": self.gifterId,
            "gifterName": self.gifterName,
            "gifteeId": self.gifteeId,
            "blob": binary.Binary(self.blob),
            "deliveryTime": self.deliveryTime,
        }

    def makeFromMongoDocument(self, doc):
        self.gifterId = doc['gifterId']
        self.gifterName = doc['gifterName']
        self.gifteeId = doc['gifteeId']
        self.blob = doc['blob']
        self.deliveryTime = doc['deliveryTime']
        self.fromMongo = True


class DistributedDeliveryManagerUD(DistributedObjectGlobalUD):
    notify = DirectNotifyGlobal.directNotify.newCategory("DistributedDeliveryManagerUD")

    def announceGenerate(self):
        DistributedObjectGlobalUD.announceGenerate(self)
        self.fsms = []
        self.gifts = []
        self.deliverydb = self.air.mongodb.gamedata.gifting

    def hello(self, todo0):
        pass

    def rejectHello(self, todo0):
        pass

    def helloResponse(self, todo0):
        pass

    def getName(self, todo0):
        pass

    def addName(self, todo0, todo1):
        pass

    def addGift(self, fromId, item, optional, toId, timeOrdered):
        pass

    def deliverGifts(self, doId, timestamp):
        if time.time() >= timestamp:
            gifts = [gift for gift in self.gifts if gift.toId == doId]
            if not gifts:
                return
            gifts.sort(key=lambda g: g.deliveryTime)
            DeliverGiftFSM(self, gifts[0]).start()

    def receiveRequestPayForGift(self, todo0, todo1, todo2):
        pass

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
        data = binary.Binary(giftSchedule.getBlob())
        self.air.mongodb.astron.objects.find_one_and_update(
            {'_id': gifteeId}, {'$set': {'fields.setGiftSchedule': {'_0': data}}})

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

    def makeGift(self, fromId, toId, blob, deliveryTime):
        gift = GiftUD()
        gift.gifterId = fromId
        gift.blob = blob
        gift.deliveryTime = deliveryTime
        gift.gifteeId = toId
        return gift

    def storeGift(self, gift):
        document = gift.getMongoDocument()
        return self.deliverydb.insert_one(document).inserted_id

    def heartbeat(self):
        pass

    def giveBeanBonus(self, todo0, todo1):
        pass

    def requestAck(self):
        self.sendUpdateToAvatarId(self.air.getAvatarIdFromSender(), 'returnAck', [])

    def givePartyRefund(self, todo0, todo1, todo2, todo3, todo4):
        pass


class DeliverGiftFSM(FSM):
    TaskTime = 5

    def __init__(self, mgr, gift):
        FSM.__init__(self, 'DeliverGiftFSM')
        self.mgr = mgr
        self.gift = gift
        self.retrieveFSM = None
        self.sent = False
        self.avInfo = None

    def start(self):
        self.mgr.fsms.append(self)
        taskMgr.add(self.__checkTask, 'DeliverGift-%s' % id(self))

    def restart(self):
        taskMgr.doMethodLater(self.TaskTime, self.__checkTask, 'DeliverGift-%s' % id(self))

    def enterGetAvatarInfo(self):
        self.retrieveFSM = RetrieveAvatarInfoFSM(self.mgr, self.gift.gifteeId, self.gift.gifterId,
                                                 [None], self.handleAvatarInfo)
        self.retrieveFSM.start()

    def handleAvatarInfo(self, success, avInfo, fromId, toId, data):
        if not success:
            self.demand('Cleanup')
            return

        self.avInfo = avInfo
        self.demand('CheckMailbox')

    def enterCheckMailbox(self):
        gifteeInfo = self.avInfo[self.gift.gifteeId]
        mailboxContents = CatalogItemList(gifteeInfo[FIELD_MAILBOX_CONTENTS],
                                          store=CatalogItem.Customization | CatalogItem.DeliveryDate)
        if len(mailboxContents) >= ToontownGlobals.MaxMailboxContents:
            self.restart()
            return
        self.demand('Deliver', mailboxContents)

    def __checkTask(self, task=None):
        self.demand('GetAvatarInfo')
        if task:
            return task.done

    def enterDeliver(self, mailboxContents):
        item = CatalogItem.getItem(self.gift.blob)
        if not item.deliveryDate:
            item.deliveryDate = int(time.time() / 60)
        mailboxContents.append(item)
        self.mgr.sendToAvatar('setMailboxContents',
                              [mailboxContents.getBlob(store=CatalogItem.Customization | CatalogItem.DeliveryDate)],
                              self.gift.gifteeId)
        self.demand('Cleanup')

    def enterCleanup(self):
        if hasattr(self.gift, 'id'):
            self.mgr.deliverydb.delete_one({'_id': self.gift.id})
        if self.gift in self.mgr.gifts:
            self.mgr.remove(self.gift)
        self.demand('Off')

    def enterOff(self):
        self.mgr.fsms.remove(self)


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
        document = self.mgr.air.mongodb.astron.objects.find_one({'_id': avId})
        if not document:
            self.demand('Error')
            return
        self.handleRetrieveAvatar(avId, document['fields'])

    def handleRetrieveAvatar(self, avId, fields):
        self.avInfo[avId] = (
            fields['setName'],
            fields['setMoney'],
            fields['setGiftSchedule'],
            fields['setDeliverySchedule'],
            fields['setMailboxContents'],
            fields['setCatalog'],
            fields['setDNAString']
        )

        if self.fromId is not None and self.fromId not in list(self.avInfo.keys()):
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
