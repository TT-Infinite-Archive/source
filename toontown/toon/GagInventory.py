from toontown.toon.GagInventoryBase import GagInventoryBase
from direct.directnotify.DirectNotifyGlobal import directNotify
from toontown.toonbase import EventGlobals


class GagInventory(GagInventoryBase):
    notify = directNotify.newCategory('GagInventory')

    def __init__(self, toon):
        GagInventoryBase.__init__(self, toon)

    def fromList(self, ls):
        GagInventoryBase.fromList(self, ls)
        messenger.send(EventGlobals.GagsChanged)

    def addItem(self, itemId):
        GagInventoryBase.addItem(self, itemId)
        messenger.send(EventGlobals.GagsChanged)

    def addItems(self, itemId, amount):
        GagInventoryBase.addItems(self, itemId, amount)
        messenger.send(EventGlobals.GagsChanged)

    def useItem(self, itemId):
        GagInventoryBase.useItem(self, itemId)
        messenger.send(EventGlobals.GagsChanged)

    def setAmount(self, itemId, amount):
        GagInventoryBase.setAmount(self, itemId, amount)
        messenger.send(EventGlobals.GagsChanged)

    def equipGag(self, gagId):
        GagInventoryBase.equipGag(self, gagId)
        messenger.send(EventGlobals.GagsChanged)

    def unequipGag(self, gagId):
        GagInventoryBase.unequipGag(self, gagId)
        messenger.send(EventGlobals.GagsChanged)
