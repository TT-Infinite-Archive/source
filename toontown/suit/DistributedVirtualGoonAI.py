from toontown.suit.DistributedCashbotBossGoonAI import DistributedCashbotBossGoonAI
import random

ATTACK_RADIUS = 30
ATTACK_COOLDOWN = 10


class DistributedVirtualGoonAI(DistributedCashbotBossGoonAI):
    def __init__(self, air, boss):
        DistributedCashbotBossGoonAI.__init__(self, air, boss)
        self.isAttacking = False
        self.attackInfo = []
        self.suitName = ''

    def setAttackInfo(self, propId, damage):
        self.attackInfo = [propId, damage]

    def getAttackInfo(self):
        return self.attackInfo

    def d_setAttackInfo(self, propId, damage):
        self.sendUpdate('setAttackInfo', [propId, damage])

    def b_setAttackInfo(self, propId, damage):
        self.setAttackInfo(propId, damage)
        self.d_setAttackInfo(propId, damage)

    def setSuitName(self, name):
        self.suitName = name

    def getSuitName(self):
        return self.suitName

    def d_setSuitName(self, name):
        self.sendUpdate('setSuitName', [name])

    def b_setSuitName(self, name):
        self.setSuitName(name)
        self.d_setSuitName(name)

    def attackToon(self, task=None):
        self.isAttacking = True
        attacks = [0, 1, 2, 3, 5]
        if self.suitName in ('ls', 'bc'):
            attacks.extend([4, 8])
        elif self.suitName in ('pp', 'nc', 'rb'):
            attacks.extend([6, 7, 9])

        self.b_setAttackInfo(
            random.choice(attacks), int(self.boss.progressValue(12, 24))
        )
        self.sendUpdate('attackToon', [])
        taskMgr.doMethodLater(ATTACK_COOLDOWN, self.doneAttacking, 'doneAttacking-%d' % self.doId)

    def doneAttacking(self, task=None):
        self.isAttacking = False
        self.chooseAndAttack()

    def hitToon(self, damage):
        avId = self.air.getAvatarIdFromSender()
        toon = self.air.doId2do.get(avId)
        if not toon:
            return

        self.boss.damageToon(toon, damage)

        self.boss.d_showZapToon(avId,
                                toon.getX(), toon.getY(), toon.getZ(),
                                toon.getH(), toon.getP(), toon.getR(),
                                99, globalClock.getFrameTime())

    def enterWalk(self):
        DistributedCashbotBossGoonAI.enterWalk(self)
        self.chooseAndAttack()

    def chooseAndAttack(self, task=None):
        if self.isAttacking:
            return

        if self.state in ('Recovery', 'Stunned', 'Grabbed', 'Dropped'):
            return

        target = self.chooseTarget()

        if not target:
            taskMgr.doMethodLater(5, self.chooseAndAttack, 'chooseAndAttack-%d' % self.doId)
            return

        self.sendUpdate('setToon', [target])
        self.attackToon()

    def cleanupTasks(self):
        taskMgr.remove('chooseAndAttack-%d' % self.doId)
        taskMgr.remove('attackToon-%d' % self.doId)
        taskMgr.remove('doneAttacking-%d' % self.doId)

    def exitWalk(self):
        DistributedCashbotBossGoonAI.exitWalk(self)
        self.cleanupTasks()

    def chooseTarget(self):
        toonIds = self.boss.involvedToons
        random.shuffle(toonIds)
        for toonId in toonIds:
            toon = self.air.doId2do.get(toonId)
            if not toon:
                continue
            distance = (self.getPos() - toon.getPos()).length()
            if distance > ATTACK_RADIUS:
                continue
            return toonId

        return None

    def disable(self):
        DistributedCashbotBossGoonAI.disable(self)
        self.cleanupTasks()
