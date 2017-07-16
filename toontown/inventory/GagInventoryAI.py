from direct.showbase.DirectObject import DirectObject
from toontown.data.GagDefs import Gags


class GagInventoryAI(DirectObject):
    notify = directNotify.newCategory('GagInventoryAI')

    def __init__(self):
        DirectObject.__init__(self)
        self.inventory = []

    def empty(self):
        del self.inventory[:]

    def setInventory(self, inventory):
        # Store only gags that our server knows about
        self.inventory = sorted([item for item in inventory if item in Gags])

    def addGag(self, gagId):
        if gagId in self.inventory:
            return False
        self.inventory.append(gagId)
        self.inventory = sorted(self.inventory)
        return True

    def removeGag(self, gagId):
        if gagId not in self.inventory:
            return False
        self.inventory.remove(gagId)
        self.inventory = sorted(self.inventory)
        return True

    def gagUnlocked(self, gagId):
        return gagId in self.inventory

    def toList(self):
        return self.inventory
