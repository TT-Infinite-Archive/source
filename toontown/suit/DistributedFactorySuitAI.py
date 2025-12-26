from panda3d.core import Point3, Vec3
from otp.ai.AIBaseGlobal import *
from direct.directnotify import DirectNotifyGlobal
from toontown.suit import DistributedSuitBaseAI
from toontown.suit import SuitDialog
from toontown.toonbase.ToontownGlobals import cogDept2index, SellbotFactoryInt
from toontown.toonbase import TTLocalizer
from toontown.suit import SuitBuffGlobals
import random


class DistributedFactorySuitAI(DistributedSuitBaseAI.DistributedSuitBaseAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedFactorySuitAI')

    def __init__(self, air, suitPlanner):
        DistributedSuitBaseAI.DistributedSuitBaseAI.__init__(self, air, suitPlanner)
        self.blocker = None
        self.battleCellIndex = None
        self.chasing = 0
        self.factoryGone = 0
        self.treasureId = 0

    def factoryIsGoingDown(self):
        self.factoryGone = 1

    def delete(self):
        if not self.factoryGone:
            self.setBattleCellIndex(None)
        del self.blocker
        self.ignoreAll()
        self.deadAllies = []
        DistributedSuitBaseAI.DistributedSuitBaseAI.delete(self)

    def setLevelDoId(self, levelDoId):
        self.levelDoId = levelDoId

    def getLevelDoId(self):
        return self.levelDoId

    def setCogId(self, cogId):
        self.cogId = cogId

    def getCogId(self):
        return self.cogId

    def setReserve(self, reserve):
        self.reserve = reserve

    def getReserve(self):
        return self.reserve

    def requestBattle(self, x, y, z, h, p, r):
        toonId = self.air.getAvatarIdFromSender()
        self.notify.debug('Suit %d at zone %d request battle with toon %d' % (self.getDoId(), self.zoneId, toonId))
        self.confrontPos = Point3(x, y, z)
        self.confrontHpr = Vec3(h, p, r)
        if self.sp.requestBattle(self, toonId):
            self.notify.debug('Suit %d requesting battle in zone %d with toon %d' % (self.getDoId(), self.zoneId, toonId))
        else:
            self.notify.debug('requestBattle from suit %d, toon %d- denied by battle manager' % (toonId, self.getDoId()))
            self.b_setBrushOff(SuitDialog.getBrushOffIndex(self.getStyleName()))
            self.d_denyBattle(toonId)

    def getConfrontPosHpr(self):
        return (self.confrontPos, self.confrontHpr)

    def setBattleCellIndex(self, battleCellIndex):
        self.sp.suitBattleCellChange(self, oldCell=self.battleCellIndex, newCell=battleCellIndex)
        self.battleCellIndex = battleCellIndex
        self.attachBattleBlocker()
        self.accept(self.sp.getBattleBlockerEvent(self.battleCellIndex), self.attachBattleBlocker)

    def getBattleCellIndex(self):
        return self.battleCellIndex

    def attachBattleBlocker(self):
        blocker = self.sp.battleMgr.battleBlockers.get(self.battleCellIndex)
        self.blocker = blocker

    def setAlert(self, avId):
        if avId == self.air.getAvatarIdFromSender():
            av = self.air.doId2do.get(avId)
            if av:
                self.chasing = avId
                if self.sp.battleMgr.cellHasBattle(self.battleCellIndex):
                    pass
                else:
                    self.sendUpdate('setConfrontToon', [avId])

    def setStrayed(self):
        if self.chasing > 0:
            self.chasing = 0
            self.sendUpdate('setReturn', [])

    def resume(self):
        self.notify.debug('Suit %s resume' % self.doId)
        if self.currHP <= 0:
            messenger.send(self.getDeathEvent())
            self.notify.debug('Suit %s dead after resume' % self.doId)
            self.requestRemoval()
        else:
            self.sendUpdate('setReturn', [])

    def isForeman(self):
        return self.boss

    def setBossFlag(self, boss):
        self.boss = boss

    def setVirtual(self, isVirtual=1):
        self.virtual = isVirtual

    def getVirtual(self):
        return self.virtual

    def requestTreasure(self, pos, grabberId=0):
        if self.treasureId:
            self.notify.warning('Suit %s tried to make a treasure, but he already generated a treasure.' % self.doId)
            return
        if self.inSellbotFactory():
            factory = self.air.doId2do.get(self.levelDoId)
            dept = cogDept2index[self.dna.dept]
            val = self.getActualLevel()
            self.notify.debug('Suit creating treasure for itself. Dept: %s Value: %s' % (dept, val))
            treasureId = factory.treasureManager.createTreasure(self.zoneId, dept, val, pos, radius=3.0)
            if grabberId:
                treasure = self.air.doId2do.get(treasureId)
                treasure.setGrabberId(grabberId)
            self.b_setTreasureId(treasureId)

    def b_setTreasureId(self, treasureId):
        self.setTreasureId(treasureId)
        self.d_setTreasureId(treasureId)

    def d_setTreasureId(self, treasureId):
        self.sendUpdate('setTreasureId', [treasureId])

    def setTreasureId(self, treasureId):
        self.treasureId = treasureId

    def inSellbotFactory(self):
        factory = self.air.doId2do.get(self.levelDoId)
        if factory is None:
            return False
        if factory.getFactoryId() == SellbotFactoryInt:
            return True
        return False
