class Item:
    def __init__(self, name, category, id, desc='Nondescript', flavorText='Nondescript', filepath=None, scale=1.0, pos=(0.0, 0.0, 0.0), color=(1.0, 1.0, 1.0, 1.0)):
        self.name = name
        self.category = category
        self.id = id
        self.desc = desc
        self.flavorText = flavorText
        self.filepath = filepath
        self.scale = scale
        self.pos = pos
        self.color = color

    def isEquippable(self):
        return False


class ModelItem(Item):
    def __init__(self, name, category, id, desc='Nondescript', flavorText='Nondescript', filepath=None, scale=1.0, pos=(0.0, 0.0, 0.0), color=(1.0, 1.0, 1.0, 1.0)):
        Item.__init__(self, name, category, id, desc, flavorText, filepath, scale, pos, color)


class ImageItem(Item):
    def __init__(self, name, category, id, desc='Nondescript', flavorText='Nondescript', filepath=None, scale=1.0, pos=(0.0, 0.0, 0.0), color=(1.0, 1.0, 1.0, 1.0)):
        Item.__init__(self, name, category, id, desc, flavorText, filepath, scale, pos, color)


class FishingRodItem(Item):
    def __init__(self, name, category, id, desc='Nondescript', flavorText='Nondescript', filepath=None, scale=1.0, pos=(0.0, 0.0, 0.0), color=(1.0, 1.0, 1.0, 1.0)):
        Item.__init__(self, name, category, id, desc, flavorText, filepath, scale, pos, color)

    def isEquippable(self):
        return True


class NametagItem(Item):
    def __init__(self, name, category, id, desc='Nondescript', flavorText='Nondescript', filepath=None, scale=1.0, pos=(0.0, 0.0, 0.0), color=(1.0, 1.0, 1.0, 1.0)):
        Item.__init__(self, name, category, id, desc, flavorText, filepath, scale, pos, color)

    def isEquippable(self):
        return True


class ParticleEffectItem(Item):
    def __init__(self, name, category, id, particleName, desc='Nondescript', flavorText='Nondescript', filepath=None, scale=1.0, pos=(0.0, 0.0, 0.0), color=(1.0, 1.0, 1.0, 1.0)):
        Item.__init__(self, name, category, id, desc, flavorText, filepath, scale, pos, color)
        self.particleName = particleName

    def isEquippable(self):
        return True

class CheesyEffectItem(ImageItem):
    def isEquippable(self):
        return True

class CollectibleModelItem(ModelItem):
    def __init__(self, name, reward, category, objective, goal, desc='Nondescript', flavorText='Nondescript', filepath=None, scale=1.0, pos=(0.0, 0.0, 0.0), color=(1.0, 1.0, 1.0, 1.0)):
        Item.__init__(self, name, category, objective, desc, flavorText, filepath, scale, pos, color)
        self.reward = reward
        self.goal = goal


class CollectibleImageItem(ImageItem):
    def __init__(self, name, reward, category, objective, goal, desc='Nondescript', flavorText='Nondescript', filepath=None, scale=1.0, pos=(0.0, 0.0, 0.0), color=(1.0, 1.0, 1.0, 1.0)):
        Item.__init__(self, name, category, objective, desc, flavorText, filepath, scale, pos, color)
        self.reward = reward
        self.goal = goal


class CollectibleCategory:
    def __init__(self, id, name, items=None):
        self.id = id
        self.name = name

        if items is None:
            items = {}
        self.items = items

    def getItems(self, objective=None):
        return [i for i in self.getOrderedItems() if i.id == objective]

    def getOrderedItems(self, minId=0, maxId=None):
        if maxId is None:
            maxId = len(list(self.items.values()))
        # Sort our items by id
        sortedItems = sorted(list(self.items.values()), key=lambda item: item.id)
        # Return the range of items we want
        return sortedItems[minId:maxId]
