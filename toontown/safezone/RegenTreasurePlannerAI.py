import random
from direct.directnotify import DirectNotifyGlobal
from .TreasurePlannerAI import TreasurePlannerAI


class RegenTreasurePlannerAI(TreasurePlannerAI):
    notify = DirectNotifyGlobal.directNotify.newCategory(
        "RegenTreasurePlannerAI")

    def __init__(self, zoneId, treasureType, spawnPoints, taskName,
                 spawnInterval, maxTreasures, callback=None):

        TreasurePlannerAI.__init__(self, zoneId, treasureType, spawnPoints, callback)

        # will spawn a task that creates a treasure every
        # spawnInterval seconds unless the max has been reached.
        self.taskName = f"{taskName}-{zoneId}"
        self.spawnInterval = spawnInterval
        self.maxTreasures = maxTreasures

    def start(self):
        self.preSpawnTreasures()
        self.startSpawning()

    def stop(self):
        self.stopSpawning()

    def stopSpawning(self):
        self.removeTask(self.taskName)

    def startSpawning(self):
        self.stopSpawning()
        self.doMethodLater(self.spawnInterval, self.upkeepTreasurePopulation, self.taskName)

    def upkeepTreasurePopulation(self, task):
        if self.numTreasures() < self.maxTreasures:
            self.placeRandomTreasure()
        self.doMethodLater(self.spawnInterval, self.upkeepTreasurePopulation, self.taskName)
        return task.done

    def placeRandomTreasure(self):
        self.notify.debug('Placing a Treasure...')
        # Pick a random index from the empty indexes that are available.
        # Probably blows up if there aren't any available.
        spawnPointIndex = self.nthEmptyIndex(
            random.randrange(self.countEmptySpawnPoints()))

        self.placeTreasure(spawnPointIndex)

    def preSpawnTreasures(self):
        for i in range(self.maxTreasures):
            self.placeRandomTreasure()
