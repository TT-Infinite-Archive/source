from toontown.toonbase import TTLocalizer


class CollectibleReward:
    def __init__(self, id, name):
        self.id = id
        self.name = name

    def awardTo(self, av):
        pass

    def getDescription(self):
        pass


class CollectibleItemReward(CollectibleReward):
    def __init__(self, id, name, category, itemId):
        CollectibleReward.__init__(self, id, name)
        self.category = category
        self.itemId = itemId

    def awardTo(self, av):
        if av.air.wantCollectibles:
            av.air.ciManager.handleItemObtained(av.doId, self.category, self.itemId)

    def getDescription(self):
        return self.name


class HealthCollectibleItemReward(CollectibleItemReward):
    def __init__(self, id, name, category, itemId, amount):
        CollectibleItemReward.__init__(self, id, name, category, itemId)
        self.amount = amount

    def awardTo(self, av):
        if av.air.wantCollectibles:
            CollectibleItemReward.awardTo(self, av)
            av.b_setMaxHp(av.getMaxHp() + self.amount)
            av.toonUp(av.getMaxHp())

    def getDescription(self):
        return '+%d %s' % (self.amount, TTLocalizer.Laff)
