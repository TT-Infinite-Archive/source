from direct.distributed.DistributedObjectAI import DistributedObjectAI
from direct.distributed.ClockDelta import globalClockDelta

from pandac.PandaModules import CollisionNode, CollisionSphere

from toontown.strike import CorporateStrikeGlobals
from toontown.strike.OSTZCalculatorAI import OSTZCalculatorAI

import random


class DistributedStrikeEnemyAI(DistributedObjectAI):
    POS_BROADCAST_INTERVAL = 0.2

    def __init__(self, air, strike, type):
        DistributedObjectAI.__init__(self, air)

        self.strike = strike

        self.type = type
        self.initialPos = None

        self.node = None
        self.aiChar = None
        self.aiBehaviors = None

        self.target = None

    def getType(self):
        return self.type

    def setInitialPos(self, x, y, z, h):
        self.initialPos = (x, y, z, h)

    def getInitialPos(self):
        return self.initialPos

    def getMotion(self):
        return 100 - random.randint(0, 20), 0.4, 10   # Round 1 speed starts at 100 weight

    def setNodePosition(self, x, y, h):
        self.node.setX(x)
        self.node.setY(y)
        self.node.setH(h)

    def registerAiChar(self, node, aiChar, aiBehaviors):
        self.node = node
        self.aiChar = aiChar
        self.aiBehaviors = aiBehaviors

        cs = CollisionSphere(0, 0, 0, CorporateStrikeGlobals.SUIT_RADII[self.type])
        cnp = self.node.attachNewNode(CollisionNode('cnode'))
        cnp.node().addSolid(cs)

    def targetParticipant(self, participant):
        self.aiBehaviors.pathFindTo(participant.node)
        participant.flock.addAiChar(self.aiChar)
        self.aiBehaviors.flock(0.5)
        self.target = participant

    def startPosBroadcast(self):
        taskMgr.remove(self.uniqueName('pos-broadcast'))
        taskMgr.doMethodLater(self.POS_BROADCAST_INTERVAL, self.broadcastPos, self.uniqueName('pos-broadcast'))

    def broadcastPos(self, task):
        pos = self.node.getPos()
        h = self.node.getH()

        def callback(z):
            self.sendUpdate('setPosition', [pos[0], pos[1], z, h+180, globalClockDelta.getRealNetworkTime(bits=16)])

        OSTZCalculatorAI.INSTANCE.calculateZ(pos[0], pos[1], callback=callback)
        task.setDelay(self.POS_BROADCAST_INTERVAL)
        return task.again
