from direct.directnotify.DirectNotifyGlobal import directNotify
from toontown.collectibles.CollectibleInventoryGlobals import *
from toontown.toonbase import EventGlobals


class CollectibleInventory:
    notify = directNotify.newCategory('CollectibleInventory')
    ObtainedIndex = 0
    EquippedIndex = 1

    def __init__(self, av):
        # { Category: { ItemId: (isObtained, isEquipped) } }
        self.inventory = {}
        self.av = av

        for category in CICategoryToItemIds:
            self.inventory[category] = {}
            for id in CICategoryToItemIds[category]:
                self.inventory[category][id] = [False, False]

        self.notify.debug('Instantiated %s' % self.inventory)

    def fillFromNetList(self, netList):
        categories = []
        for item in netList:
            if item[0] not in categories:
                categories.append(item[0])
            if item[0] not in self.inventory:
                self.inventory[item[0]] = {}
            self.inventory[item[0]][item[1]] = [item[2], item[3]]
        self.notify.debug('Filled Inventory: %s From NetList: %s' % (self.inventory, netList))
        for category in categories:
            messenger.send(EventGlobals.CollectibleInventoryUpdated, [category])

    def makeNetList(self, category=None):
        netList = []
        if category is not None:
            for id in self.inventory[category]:
                obtained = self.inventory[category][id][self.ObtainedIndex]
                equipped = self.inventory[category][id][self.EquippedIndex]
                netList.append((category, id, obtained, equipped))
        else:
            for cat in self.inventory:
                for id in self.inventory[cat]:
                    obtained = self.inventory[cat][id][self.ObtainedIndex]
                    equipped = self.inventory[cat][id][self.EquippedIndex]
                    netList.append((cat, id, obtained, equipped))
        return netList

    def setObtained(self, category, id, obtained):
        if self.isObtained(category, id) == obtained:
            return
        self.inventory[category][id][self.ObtainedIndex] = obtained
        messenger.send(EventGlobals.CollectibleInventoryUpdated, [category])

    def isObtained(self, category, id):
        try:
            return self.inventory[category][id][self.ObtainedIndex]
        except KeyError:
            return False

    def setEquipped(self, category, id, equipped):
        if self.isEquipped(category, id) == equipped:
            return
        self.inventory[category][id][self.EquippedIndex] = equipped
        messenger.send(EventGlobals.CollectibleInventoryUpdated, [category])

    def getEquipped(self, category):
        for itemId in self.inventory[category]:
            if self.isEquipped(category, itemId):
                return itemId
        return None

    def isEquipped(self, category, id):
        try:
            return self.inventory[category][id][self.EquippedIndex]
        except KeyError:
            return False
