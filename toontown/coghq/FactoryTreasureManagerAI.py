from toontown.coghq.DistributedMeritTreasureAI import DistributedMeritTreasureAI

from direct.directnotify.DirectNotifyGlobal import directNotify
import random
import math


class FactoryTreasureManagerAI:
    notify = directNotify.newCategory('FactoryTreasureManagerAI')

    def __init__(self, air, factory):
        self.air = air
        self.factory = factory
        self.treasures = []

    def destroy(self):
        taskMgr.remove('createSingleTreasureTask')
        for treasureId in self.treasures:
            treasure = self.air.doId2do.get(treasureId)
            if treasure is not None:
                treasure.requestDelete()
        self.air = None
        self.factory = None
        self.treasures = []

    def grabAttempt(self, avId, treasureId):
        if avId not in self.factory.avIdList:
            self.notify.warning("Avatar %s tried to grab a treasure in a factory they weren't present in." % avId)
            return

        av = self.air.doId2do.get(avId)
        if av is None:
            self.notify.warning('Unknown avatar %s tried request treasure %s' % (avId, treasureId))
            return

        if treasureId not in self.treasures:
            self.notify.warning('Avatar %s tried to grab non-existent treasure %s' % (avId, treasureId))
            return

        treasure = self.air.doId2do.get(treasureId)
        treasure.d_setGrab(avId)
        self.cleanupTreasure(treasureId)
        self.factory.incrementMeritCount(treasure.getMeritValue())

    def createTreasure(self, zoneId, dept, value, pos, radius, dropImmediate=False):
        # This sets the final pos and offsets it from the floor by 2.0
        finalPos = [round(random.uniform(pos[0] - radius, pos[0] + radius), 2),
                    round(random.uniform(pos[1] - radius, pos[1] + radius), 2),
                    pos[2] + 2.0]

        treasure = DistributedMeritTreasureAI(self.air, self, dept, value, pos, finalPos, dropImmediate)
        treasure.generateWithRequired(zoneId)
        self.treasures.append(treasure.doId)
        return treasure.doId

    def createTreasures(self, zoneId, dept, value, pos, count, radius, delay):
        if count <= 0:
            return

        self.createTreasure(zoneId, dept, value, pos, radius, dropImmediate=True)
        count -= 1
        taskMgr.doMethodLater(delay, self.createTreasures, 'createSingleTreasureTask', extraArgs=[zoneId, dept, value, pos, count, radius, delay])

    def cleanupTreasure(self, treasureId):
        if treasureId not in self.treasures:
            self.notify.warning('Treasure already cleaned up %s' % treasureId)
            return

        treasure = self.air.doId2do.get(treasureId)
        if treasure is None:
            self.notify.warning('Tried to cleanup a non-existent treasure %s' % treasureId)
            return

        self.treasures.remove(treasureId)
        taskMgr.doMethodLater(5.0, self.__destroyTreasure, treasure.uniqueName('-destroy'), extraArgs=[treasure])

    def __destroyTreasure(self, treasure, task=None):
        treasure.requestDelete()