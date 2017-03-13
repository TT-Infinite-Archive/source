from toontown.strike import CorporateStrikeGlobals
from toontown.strike.DistributedStrikeEnemyAI import DistributedStrikeEnemyAI
from toontown.strike.OSTZCalculatorAI import OSTZCalculatorAI
from toontown.suit import SuitTimings

import random
import math


def flip():
    return random.random() > 0.5


def getRandomPoint(pos, radius):
    x = pos[0] + math.ceil(radius*random.random()) * (-1 if flip() else 1)
    y = pos[1] + math.ceil(radius*random.random()) * (-1 if flip() else 1)
    return x, y


class RoundManagerAI:
    SPAWN_RANGES = None
    SPAWN_SPHERES = None
    SPAWN_DELAY = None
    MAX_ENEMIES = None
    TIER_CHART = None

    def __init__(self, strike):
        self.strike = strike
        self.round = 0
        self.intercept = None

        self.spawning = []
        self.enemies = []
        self.destroyed = 0

    def initialize(self):
        self.intercept = random.randint(*self.SPAWN_RANGES[len(self.strike.participants)-1])

    def spawnEnemy(self):
        enemy = DistributedStrikeEnemyAI(self.strike.air, self, self.getSuitType())
        self.strike.world.addEnemy(enemy)

        participant = random.choice(self.strike.participants)

        spawn = self.SPAWN_SPHERES[random.choice(participant.activeSpheres)]
        x, y = getRandomPoint((spawn[0], spawn[1]), spawn[3])

        # Check if there is an enemy within 5 units of us, if so, recalculate:
        while True:
            for pos in self.spawning:
                distance = math.sqrt((pos[0]-x)**2 + (pos[1]-y)**2)
                if distance <= 5:
                    x, y = getRandomPoint((spawn[0], spawn[1]), spawn[3])
                    break
            else:
                break

        self.spawning.append((x, y))

        def targetParticipant(task):
            self.spawning.remove((x, y))
            self.enemies.append(enemy)

            enemy.targetParticipant(participant)
            enemy.startPosBroadcast()
            return task.done

        def callback(z):
            h = random.randint(0, 359)
            enemy.setInitialPos(x, y, z, h)
            enemy.setNodePosition(x, y, h)
            enemy.generateWithRequired(self.strike.zoneId)

            taskMgr.doMethodLater(SuitTimings.fromSky, targetParticipant, '%s-target-participant' % id(enemy))

        OSTZCalculatorAI.INSTANCE.calculateZ(x, y, callback)

    def getSuitType(self):
        rounds = sorted(self.TIER_CHART.keys())

        for round in rounds:
            if round >= self.round:
                tier = random.choice(self.TIER_CHART[round])
                return random.choice(CorporateStrikeGlobals.SUIT_TIERS[tier])

    def getEnemyCount(self):
        return int(math.floor(0.2*(self.round**2)+self.intercept) +
                   (math.floor(0.2*((self.round/32)**2)+self.intercept)*(self.round/32)))

    def spawnEnemies(self):
        for _ in xrange(random.randint(1, 2)):
            self.spawnEnemy()

        taskMgr.add(self.__spawnTask, self.uniqueName('cs-spawn-task'))

    def __spawnTask(self, task):
        if len(self.enemies) == self.MAX_ENEMIES or (len(self.enemies) + self.destroyed == self.getEnemyCount()):
            task.setDelay(random.randint(*self.SPAWN_DELAY))
            return task.again

        maxAmount = self.MAX_ENEMIES
        if self.getEnemyCount() - ((len(self.enemies)) + self.destroyed) <= self.MAX_ENEMIES:
            maxAmount = self.getEnemyCount() - (len(self.enemies) + self.destroyed)

        amount = random.randint(0, min(maxAmount, 2))

        for _ in xrange(amount):
            self.spawnEnemy()

        task.setDelay(random.randint(*self.SPAWN_DELAY))
        return task.again

    def nextRound(self):
        self.round += 1
        self.spawnEnemies()
        self.strike.startRound(self.round)

    def uniqueName(self, name):
        return '%s-%s' % (name, id(self))
