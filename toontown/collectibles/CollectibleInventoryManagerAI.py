from direct.directnotify.DirectNotifyGlobal import directNotify
from toontown.collectibles import CollectibleInventoryGlobals, CollectibleGlobals


class CollectibleInventoryManagerAI:
    notify = directNotify.newCategory('CollectibleInventoryManagerAI')

    def __init__(self, air):
        self.air = air

    def handleItemObtained(self, avId, categoryId, itemId):
        self.notify.debug('Handling %d obtaining item %d from category %d' % (avId, itemId, categoryId))
        av = self.air.doId2do.get(avId)
        if av is None:
            return

        inventory = av.collectibleInventory
        if inventory is None:
            self.notify.warning('Av %d has no collectible inventory' % avId)
            return
        if itemId not in CollectibleInventoryGlobals.CICategoryToItemIds[categoryId]:
            self.notify.warning('Av %d attempted to obtain non-existent item %d in category %d' % (avId, itemId, categoryId))
            return

        # Set the item as obtained
        inventory.setObtained(categoryId, itemId, 1)
        # Save the inventory category
        inventory.saveCategory(categoryId)

    def handleItemLost(self, avId, categoryId, itemId):
        self.notify.debug('Handling %d losing item %d from category %d' % (avId, itemId, categoryId))
        av = self.air.doId2do.get(avId)
        if av is None:
            return

        inventory = av.collectibleInventory
        if inventory is None:
            self.notify.warning('Av %d has no collectible inventory' % avId)
            return
        if itemId not in CollectibleInventoryGlobals.CICategoryToItemIds[categoryId]:
            self.notify.warning('Av %d attempted to lose non-existent item %d in category %d' % (avId, itemId, categoryId))
            return

        # Set the item as un-obtained
        inventory.setObtained(categoryId, itemId, 0)
        # Un-equip the item if it was equipped
        inventory.setEquipped(categoryId, itemId, 0)
        # Save the inventory category
        inventory.saveCategory(categoryId)

    def handleEquipItem(self, avId, categoryId, itemId):
        self.notify.debug('Handling %d equipping item %d from category %d' % (avId, itemId, categoryId))
        av = self.air.doId2do.get(avId)
        if av is None:
            return

        inventory = av.collectibleInventory
        if not inventory.isObtained(categoryId, itemId)\
                and itemId == CollectibleInventoryGlobals.DefaultItems.get(categoryId, (-1,))[0]:
            # This is a default item but they don't have it... lets just obtain it for them
            inventory.setObtained(categoryId, itemId, 1)
        if inventory is None:
            self.notify.warning('Av %d has no collectible inventory' % avId)
            return
        if itemId not in CollectibleInventoryGlobals.CICategoryToItemIds[categoryId]:
            self.notify.warning('Av %d attempted to equip non-existent item %d in category %d' % (avId, itemId, categoryId))
            return
        if not inventory.isObtained(categoryId, itemId):
            self.notify.warning('Av %d attempted to equip an item %d in category %d they do not own' % (avId, itemId, categoryId))
            return
        if not CollectibleGlobals.getItem(categoryId, itemId).isEquippable():
            self.notify.warning('Av %d attempted to equip an unequippable item %d in category %d' % (avId, itemId, categoryId))
            return
        if inventory.isEquipped(categoryId, itemId):
            return

        # UnEquip any other item that is equipped in this category
        inventory.unEquipCategory(categoryId)
        # Set the item as equipped
        inventory.setEquipped(categoryId, itemId, 1)
        # Save the inventory category
        inventory.saveCategory(categoryId)
