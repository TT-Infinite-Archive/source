from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.showbase.DirectObject import DirectObject

from toontown.toonbase import EventGlobals
from toontown.data.Gag import Gags


class GagInventory(DirectObject):
    notify = directNotify.newCategory('GagInventory')

    def __init__(self):
        DirectObject.__init__(self)
        self._inventory = []

    def empty(self):
        del self._inventory[:]
        messenger.send(EventGlobals.InventoryChanged)

    def setInventory(self, inventory):
        self.notify.debug('Setting new inventory: %s' % inventory)
        # Convert the inventory of gag ids to gag objects
        self._inventory = [Gags[gagId] for gagId in sorted(inventory)]
        messenger.send(EventGlobals.InventoryChanged)

    def gagUnlocked(self, gag):
        return gag in self._inventory
