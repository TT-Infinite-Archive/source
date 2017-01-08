from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.showbase.DirectObject import DirectObject

from toontown.toonbase import EventGlobals


class GagInventory(DirectObject):
    notify = directNotify.newCategory('GagInventory')

    def __init__(self):
        DirectObject.__init__(self)
        self.inventory = []

    def empty(self):
        del self.inventory[:]
        messenger.send(EventGlobals.InventoryChanged)

    def setInventory(self, inventory):
        self.notify.debug('Setting new inventory: %s' % inventory)
        self.inventory = sorted(inventory)
        messenger.send(EventGlobals.InventoryChanged)
