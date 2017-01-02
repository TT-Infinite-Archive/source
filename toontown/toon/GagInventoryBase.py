from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.showbase.DirectObject import DirectObject

from toontown.data.Gag import GagItemSlot


class GagInventoryBase(DirectObject):
    notify = directNotify.newCategory('GagInventoryBase')
    SlotIndex = 0
    EquippedIndex = 1

    def __init__(self, toon):
        DirectObject.__init__(self)
        self.toon = toon
        self.inventory = {}

    def unload(self):
        self.inventory.clear()

    def empty(self):
        self.inventory.clear()

    def toList(self):
        ls = []
        for item in self.inventory.values():
            ls.append(item.toList())
        return ls

    def fromList(self, ls):
        self.notify.debug('Filling... %s' % ls)
        self.empty()
        for item in ls:
            uid = item[0]
            slot = GagItemSlot(None, 0, 0)
            slot.fromList(item)
            self.inventory[uid] = slot

    @property
    def items(self):
        return sorted(self.inventory.values(), key=lambda slot: slot.gag.uid)

    @property
    def equippedItems(self):
        return [item for item in self.items if item.equipped]

    def isEquipped(self, gagId):
        return gagId in [item.gag.uid for item in self.equippedItems]

    def getGagSlotAtSlot(self, slot):
        gagSlot = self.equippedItems[slot]
        if gagSlot is None:
            return None
        return gagSlot

    def getGagAtSlot(self, slot):
        gagSlot = self.equippedItems[slot]
        if gagSlot is None:
            return None
        return gagSlot.gag

    def equipGag(self, gagId):
        self.notify.debug('Equipping Gag %s' % gagId)
        gagSlot = self.inventory.get(gagId)
        if gagSlot is None:
            return
        elif gagSlot.equipped:
            return
        else:
            gagSlot.equipped = True
            self.inventory[gagId] = gagSlot
            self.notify.debug('Equipped Gag %s, inventory is now %s' % (gagId, self.toList()))

    def unequipGag(self, gagId):
        self.notify.debug('Unequipping Gag %s' % gagId)
        gagSlot = self.inventory.get(gagId)
        if gagSlot is None:
            return
        elif gagSlot.equipped:
            gagSlot.equipped = False
            self.inventory[gagId] = gagSlot
        else:
            return

    def addItem(self, itemId):
        self.notify.debug('Adding item %s' % itemId)
        if itemId in self.inventory:
            self.inventory[itemId].addOne()
        else:
            self.inventory[itemId] = GagItemSlot(itemId, 1, 0)

    def addItems(self, itemId, amount):
        self.notify.debug('Adding %s of item %s' % (amount, itemId))
        if itemId in self.inventory:
            slot = self.inventory[itemId]
            slot.setAmount(slot.amount + amount)
            self.inventory[itemId] = slot
        else:
            self.inventory[itemId] = GagItemSlot(itemId, amount, 0)

    def getAmount(self, itemId):
        amount = 0
        if itemId in self.inventory:
            amount = self.inventory[itemId].amount
        return amount

    def useItem(self, itemId):
        self.notify.debug('Using item %s' % itemId)
        if itemId not in self.inventory:
            return
        if self.inventory[itemId].amount == 1:
            del self.inventory[itemId]
        else:
            self.inventory[itemId].amount -= 1

    def removeItem(self, itemId):
        del self.inventory[itemId]

    def setAmount(self, itemId, amount):
        self.notify.debug('Setting item %s amount to %s' % (itemId, amount))
        if itemId not in self.inventory:
            self.addItems(itemId, amount)
        else:
            self.inventory[itemId].amount = amount
