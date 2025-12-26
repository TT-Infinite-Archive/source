from direct.directnotify import DirectNotifyGlobal
from .RegenTreasurePlannerAI import RegenTreasurePlannerAI

from toontown.toonbase import ToontownGlobals


class SZTreasurePlannerAI(RegenTreasurePlannerAI):
    notify = DirectNotifyGlobal.directNotify.newCategory(
        "SZTreasurePlannerAI")

    def __init__(self, zoneId, treasureType, healAmount, spawnPoints, taskName,
                 spawnInterval, maxTreasures, callback=None):

        RegenTreasurePlannerAI.__init__(self, zoneId, treasureType, spawnPoints, taskName,
                                        spawnInterval, maxTreasures, callback)
        self.healAmount = healAmount

    # override the validate function to indicate that only toons who
    # need healing can pick up treasures.
    def validAvatar(self, av):
        # Only toons with positive hp get rewarded for treasures.
        if (av.hp > 0) and (av.hp < av.maxHp):
            simbase.air.statManager.handleTreasureObtained(av, self)
            # Modify the heal amount based on which holiday is running.
            if simbase.air.holidayManager.isHolidayRunning(ToontownGlobals.VALENTINES_DAY):
                av.toonUp(self.healAmount * 2)
            else:
                av.toonUp(self.healAmount)
            return True
        return False
