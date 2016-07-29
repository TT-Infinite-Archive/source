from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectAI import DistributedObjectAI

from toontown.catalog import CatalogGlobals
from toontown.catalog.CatalogInvalidItem import CatalogInvalidItem
from toontown.catalog.CatalogClothingItem import CatalogClothingItem

import time

class TTCodeRedemptionMgrAI(DistributedObjectAI):
    notify = DirectNotifyGlobal.directNotify.newCategory("TTCodeRedemptionMgrAI")

    # TODO: Possibly place these in a better location
    Success = 0
    InvalidCode = 1
    ExpiredCode = 2
    Ineligible = 3
    AwardError = 4
    TooManyFails = 5
    ServiceUnavailable = 6

    def __init__(self, air):
        DistributedObjectAI.__init__(self, air)
        self.air = air

    def announceGenerate(self):
        DistributedObjectAI.announceGenerate(self)

    def delete(self):
        DistributedObjectAI.delete(self)
        
    def giveAwardToToonResult(self, todo0, todo1):
        pass

    def redeemCode(self, context, code):
        avId = self.air.getAvatarIdFromSender()
        if not avId:
            self.air.writeServerEvent('suspicious', avId=avId, issue='Tried to redeem a code from an invalid avId')
            return

        av = self.air.doId2do.get(avId)
        if not av:
            self.air.writeServerEvent('suspicious', avId=avId, issue='Invalid avatar tried to redeem a code')
            return

        valid = True
        eligible = True
        expired = False
        delivered = False

        # TODO: Come up with a way to determine if the Toon is eligible for the prize

        # Get our redeemed Codes
        codes = av.getRedeemedCodes()
        if not codes:
            codes = []

        if code in codes:
            # Already redeemed this code
            valid = False

        if code.lower() == 'sellbot-storm':
            eligible = False

        # Is the code valid?
        if not valid:
            self.air.writeServerEvent('code-redeemed', avId=avId, issue='Invalid code: %s' % code)
            self.sendUpdateToAvatarId(avId, 'redeemCodeResult', [context, self.InvalidCode, 0])
            return

        # Did our code expire?
        if expired:
            self.air.writeServerEvent('code-redeemed', avId=avId, issue='Expired code: %s' % code)
            self.sendUpdateToAvatarId(avId, 'redeemCodeResult', [context, self.ExpiredCode, 0])
            return

        # Are we able to redeem this code?
        if not eligible:
            self.air.writeServerEvent('code-redeemed', avId=avId, issue='Ineligible for code: %s' % code)
            self.sendUpdateToAvatarId(avId, 'redeemCodeResult', [context, self.Ineligible, 0])
            return

        # Deliver the reward to the user
        items = self.getItemsForCode(code)

        for item in items:
            if isinstance(item, CatalogInvalidItem):
                self.air.writeServerEvent('suspicious', avId=avId, issue='Invalid CatalogItem\'s for code: %s' % code)
                self.sendUpdateToAvatarId(avId, 'redeemCodeResult', [context, self.InvalidCode, 0]) # TODO: Come up with a special code for this
                break

            if len(av.mailboxContents) + len(av.onGiftOrder) >= CatalogGlobals.MaxMailboxContents:
                # Mailbox is full
                delivered = False
                break

            item.deliveryDate = int(time.time() / 60) + 1
            av.onOrder.append(item)
            av.b_setDeliverySchedule(av.onOrder)
            delivered = True

        if not delivered:
            # 0 is Success
            # 1, 2, 15, & 16 is an UnknownError
            # 3 & 4 is MailboxFull
            # 5 & 10 is AlreadyInMailbox
            # 6, 7, & 11 is AlreadyInQueue
            # 8 is AlreadyInCloset
            # 9 is AlreadyBeingWorn
            # 12, 13, & 14 is AlreadyReceived
            self.air.writeServerEvent('code-redeemed', avId=avId, issue='Could not deliver items for code: %s' % code)
            self.sendUpdateToAvatarId(avId, 'redeemCodeResult', [context, self.AwardError, 3])
            return

        # This code checked out, and all items were delivered. Add the code to the avatar's current redeemed codes
        codes.append(code)
        av.setRedeemedCodes(codes)

        # Send the item and tell the user its A-Okay
        self.air.writeServerEvent('code-redeemed', avId=avId, issue='Successfully redeemed code: %s' % code)
        self.sendUpdateToAvatarId(avId, 'redeemCodeResult', [context, self.Success, 0])

    def redeemCodeAiToUd(self, todo0, todo1, todo2, todo3, todo4):
        pass

    def redeemCodeResultUdToAi(self, todo0, todo1, todo2, todo3, todo4):
        pass

    def redeemCodeResult(self, todo0, todo1, todo2):
        pass

    def getItemsForCode(self, code):
        return [CatalogInvalidItem()]
        
    def awardCode(self, avId, code):
        av = self.air.doId2do.get(avId)
        
        if not av:
            self.air.writeServerEvent('suspicious', avId=avId, issue='Invalid avatar tried to redeem a code')
            return
            
        codes = av.getRedeemedCodes()
        if not codes:
            codes = [code]
            av.setRedeemedCodes(codes)
        else:
            if not code in codes:
                codes.append(code)
                av.setRedeemedCodes(codes)
            else:
                return           
            
        items = self.getItemsForCode(code)

        for item in items:
            if isinstance(item, CatalogInvalidItem):
                self.air.writeServerEvent('suspicious', avId=avId, issue='Invalid CatalogItem\'s for code: %s' % code)
                break

            if len(av.mailboxContents) + len(av.onGiftOrder) >= CatalogGlobals.MaxMailboxContents:
                # Mailbox is full
                delivered = False
                break

            item.deliveryDate = int(time.time() / 60) + 1
            av.onOrder.append(item)
            av.b_setDeliverySchedule(av.onOrder)
            delivered = True

        if not delivered:
            self.air.writeServerEvent('code-redeemed', avId=avId, issue='Could not deliver items for code: %s' % code)
            return        
