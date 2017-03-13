from direct.stdpy.threading2 import Thread

from panda3d.core import NodePath
from panda3d.ai import AIWorld, AICharacter, Flock

import time


class StrikeWorldAI(Thread):
    def __init__(self, strike):
        Thread.__init__(self, target=self.__process, name='strike-world-ai-%s' % id(self))

        self.strike = strike

        self.world = NodePath('strike-world-node-%s' % id(self))
        self.aiWorld = AIWorld(self.world)

        self.flocks = []
        self.enemies = []

    def addEnemy(self, enemy):
        en = NodePath('enemy-%s' % id(self))
        en.reparentTo(self.world)

        aiChar = AICharacter('strike-enemy-%s' % id(enemy), en, *enemy.getMotion())
        self.aiWorld.addAiChar(aiChar)
        behaviors = aiChar.getAiBehaviors()
        behaviors.initPathFind(self.strike.NAVMESH)
        enemy.registerAiChar(en, aiChar, behaviors)

        self.enemies.append(enemy)

    def removeEnemy(self, enemy):
        pass

    def registerParticipant(self, participant):
        pn = NodePath('participant-%s' % id(self))
        pn.reparentTo(self.world)

        flock = Flock(id(participant), 180, 14, 1, 0, 0)
        self.aiWorld.addFlock(flock)
        self.aiWorld.flockOn(id(participant))

        # Create a new flock for the participant:
        participant.registerFlock(pn, flock)

    def __process(self):
        while True:
            try:
                self.aiWorld.update()
            except:
                pass
            time.sleep(1.0/30)  # We only want to run this 30 times a second max
