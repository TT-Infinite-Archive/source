from . import CatalogItem
from toontown.collectibles.CollectibleInventoryGlobals import CICategoryNametag
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import TTLocalizer
from direct.gui.DirectGui import *


class CatalogNametagItem(CatalogItem.CatalogItem):
    sequenceNumber = 0

    def makeNewItem(self, nametagStyle):
        self.nametagStyle = nametagStyle
        CatalogItem.CatalogItem.makeNewItem(self)

    def getPurchaseLimit(self):
        return 1

    def reachedPurchaseLimit(self, avatar):
        if avatar is None or avatar.collectibleInventory is None:
            return 1
        if self in avatar.onOrder or self in avatar.mailboxContents or self in avatar.onGiftOrder or self in avatar.awardMailboxContents or self in avatar.onAwardOrder:
            return 1

        return avatar.collectibleInventory.isObtained(CICategoryNametag, self.nametagStyle)

    def getAcceptItemErrorText(self, retcode):
        if retcode == ToontownGlobals.P_ItemAvailable:
            return TTLocalizer.CatalogAcceptNametag
        return CatalogItem.CatalogItem.getAcceptItemErrorText(self, retcode)

    def saveHistory(self):
        return 1

    def getTypeName(self):
        return TTLocalizer.NametagTypeName

    def getName(self):
        name = TTLocalizer.NametagFontNames[self.nametagStyle]
        if TTLocalizer.NametagReverse:
            name = TTLocalizer.NametagLabel + name
        else:
            name = name + TTLocalizer.NametagLabel
        return name

    def recordPurchase(self, avatar, optional):
        if avatar is None:
            return
        if simbase.air.wantCollectibles:
            simbase.air.ciManager.handleItemObtained(avatar.doId, CICategoryNametag, self.nametagStyle)
        return ToontownGlobals.P_ItemAvailable

    def getPicture(self, avatar):
        frame = self.makeFrame()
        inFont = ToontownGlobals.getNametagFont(self.nametagStyle)
        DirectLabel(parent=frame, relief=None, pos=(0, 0, 0.24), scale=0.5, text=base.localAvatar.getName(), text_fg=(1.0, 1.0, 1.0, 1), text_shadow=(0, 0, 0, 1), text_font=inFont, text_wordwrap=9)
        self.hasPicture = True
        return (frame, None)

    def output(self, store=-1):
        return 'CatalogNametagItem(%s%s)' % (self.nametagStyle, self.formatOptionalData(store))

    def compareTo(self, other):
        return self.nametagStyle - other.nametagStyle

    def getHashContents(self):
        return self.nametagStyle

    def getBasePrice(self):
        return 500

    def decodeDatagram(self, di, versionNumber, store):
        CatalogItem.CatalogItem.decodeDatagram(self, di, versionNumber, store)
        self.nametagStyle = di.getUint16()
        if self.nametagStyle == 100:
            # This is a patch for removing nametagStyle 100
            self.nametagStyle = 0

    def encodeDatagram(self, dg, store):
        CatalogItem.CatalogItem.encodeDatagram(self, dg, store)
        dg.addUint16(self.nametagStyle)

    def isGift(self):
        return 0

    def getBackSticky(self):
        itemType = 1
        numSticky = 4
        return (itemType, numSticky)
