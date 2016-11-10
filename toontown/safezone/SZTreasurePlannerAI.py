from RegenTreasurePlannerAI import RegenTreasurePlannerAI
from direct.directnotify import DirectNotifyGlobal
from toontown.safezone.TreasureGlobals import TreasurePD


class SZTreasurePlannerAI(RegenTreasurePlannerAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('SZTreasurePlannerAI')

    def __init__(self, zoneId, treasureType, value, spawnPoints, spawnRate, maxTreasures, isPercentage=False):
        self.zoneId = zoneId
        self.spawnPoints = spawnPoints
        self.value = value
        self.isPercentage = isPercentage
        RegenTreasurePlannerAI.__init__(self, zoneId, treasureType, 'SZTreasurePlanner-%d' % zoneId, spawnRate, maxTreasures)

    def initSpawnPoints(self):
        pass

    def getHealAmount(self, av):
        value = self.value
        if av is not None and self.isPercentage:
            value = float(av.getMaxHp()) * (float(value)/100.0)
        return int(value)

    def validAvatar(self, treasure, av):
        # Avatars can only heal if they are missing some health, but aren't sad.
        if treasure.treasureType in (TreasurePD):
            simbase.air.statManager.handleTreasureObtained(av, treasure)
            return True
        elif 0 < av.getHp() < av.getMaxHp():
            amount = self.getHealAmount(av)
            av.toonUp(amount)
            return True
        else:
            return False
