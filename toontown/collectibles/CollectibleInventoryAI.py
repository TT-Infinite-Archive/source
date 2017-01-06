from direct.directnotify.DirectNotifyGlobal import directNotify
from toontown.collectibles.CollectibleInventoryGlobals import *


class CollectibleInventoryAI:
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

        self.catToSaveFunc = {
            CICategoryFishingRod: self.av.d_setFishingRodInventory,
            CICategoryNametag: self.av.d_setNametagStyleInventory,
            CICategoryParticleEffect: self.av.d_setParticleEffectInventory,
            CICategoryLaff: self.av.d_setLaffInventory,
            CICategoryCheesyEffect: self.av.d_setCheesyEffectInventory
        }

    def fillFromNetList(self, netList):
        for item in netList:
            if item[0] not in self.inventory:
                self.inventory[item[0]] = {}
            self.inventory[item[0]][item[1]] = [item[2], item[3]]
        self.notify.debug('Filled Inventory: %s From NetList: %s' % (self.inventory, netList))

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

    def isObtained(self, category, id):
        try:
            return self.inventory[category][id][self.ObtainedIndex]
        except KeyError:
            return False

    def setEquipped(self, category, id, equipped):
        if self.isEquipped(category, id) == equipped:
            return
        self.inventory[category][id][self.EquippedIndex] = equipped

    def isEquipped(self, category, id):
        try:
            return self.inventory[category][id][self.EquippedIndex]
        except KeyError:
            return False

    def getEquipped(self, category):
        for itemId in self.inventory[category]:
            if self.isEquipped(category, itemId):
                return itemId

    def unEquipCategory(self, category):
        for itemId in self.inventory[category]:
            if self.isEquipped(category, itemId):
                self.setEquipped(category, itemId, 0)

    def saveCategory(self, category):
        func = self.catToSaveFunc[category]
        func(self.makeNetList(category))
