from otp.ai.AIBaseGlobal import *
from otp.avatar import DistributedAvatarAI
import SuitPlannerBase
import SuitBase
import SuitDNA
from direct.directnotify import DirectNotifyGlobal
from toontown.ai import NewsManagerGlobals
from toontown.battle import SuitBattleGlobals
from toontown.suit import SuitBuffGlobals
import random

class DistributedSuitBaseAI(DistributedAvatarAI.DistributedAvatarAI, SuitBase.SuitBase):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedSuitBaseAI')

    def __init__(self, air, suitPlanner):
        DistributedAvatarAI.DistributedAvatarAI.__init__(self, air)
        SuitBase.SuitBase.__init__(self)
        self.sp = suitPlanner
        self.maxHP = 10
        self.currHP = 10
        self.zoneId = 0
        self.dna = SuitDNA.SuitDNA()
        self.virtual = 0
        self.waiter = 0
        self.skeleRevives = 0
        self.maxSkeleRevives = 0
        self.reviveFlag = 0
        self.buildingHeight = None
        self.buffIndex = 0
        self.scale = 1.0
        self.deadAllies = []

    def generate(self):
        DistributedAvatarAI.DistributedAvatarAI.generate(self)

    def delete(self):
        self.sp = None
        del self.dna

        DistributedAvatarAI.DistributedAvatarAI.delete(self)
        SuitBase.SuitBase.delete(self)

    def requestRemoval(self):
        if self.sp is not None:
            self.sp.removeSuit(self)
        else:
            self.requestDelete()

    def setLevel(self, lvl=None):
        attributes = self.getAttributes()
        if lvl is not None:
            self.level = lvl - attributes['level'] - 1
        else:
            self.level = SuitBattleGlobals.pickFromFreqList(attributes['freq'])
        self.notify.debug('Assigning level %s to suit' % lvl)
        if hasattr(self, 'doId'):
            self.d_setLevelDist(self.level)
        hp = attributes['hp'][self.level]
        self.maxHP = hp
        self.currHP = hp

    def getLevelDist(self):
        return self.getLevel()

    def d_setLevelDist(self, level):
        self.sendUpdate('setLevelDist', [level])

    def setupSuitDNA(self, level, type, track):
        dna = SuitDNA.SuitDNA()
        dna.newSuitRandom(type, track)
        self.dna = dna
        self.track = track
        self.setLevel(level)

    def getDNAString(self):
        if self.dna:
            return self.dna.makeNetString()
        else:
            self.notify.debug('No dna has been created for suit %d!' % self.getDoId())
            return ''

    def b_setBrushOff(self, index):
        self.setBrushOff(index)
        self.d_setBrushOff(index)

    def d_setBrushOff(self, index):
        self.sendUpdate('setBrushOff', [index])

    def setBrushOff(self, index):
        pass

    def d_denyBattle(self, toonId):
        self.sendUpdateToAvatarId(toonId, 'denyBattle', [])

    def b_setSkeleRevives(self, num):
        if num == None:
            num = 0
        self.setSkeleRevives(num)
        self.d_setSkeleRevives(self.getSkeleRevives())
        return

    def d_setSkeleRevives(self, num):
        self.sendUpdate('setSkeleRevives', [num])

    def getSkeleRevives(self):
        return self.skeleRevives

    def setSkeleRevives(self, num):
        if num is None:
            num = 0
        self.skeleRevives = num
        if num > self.maxSkeleRevives:
            self.maxSkeleRevives = num

    def getMaxSkeleRevives(self):
        return self.maxSkeleRevives

    def useSkeleRevive(self):
        self.skeleRevives -= 1
        self.currHP = self.maxHP
        self.reviveFlag = 1

    def reviveCheckAndClear(self):
        returnValue = 0
        if self.reviveFlag == 1:
            returnValue = 1
            self.reviveFlag = 0
        return returnValue

    def getHP(self):
        return self.currHP

    def setHP(self, hp):
        if hp > self.maxHP:
            self.currHP = self.maxHP
        else:
            self.currHP = hp

    def b_setHP(self, hp):
        self.setHP(hp)
        self.d_setHP(hp)

    def d_setHP(self, hp):
        self.sendUpdate('setHP', [hp])

    def b_setMaxHP(self, maxHP):
        self.setMaxHP(maxHP)
        self.d_setMaxHP(maxHP)

    def setMaxHP(self, maxHP):
        self.maxHP = maxHP

    def d_setMaxHP(self, maxHP):
        self.sendUpdate('setMaxHP', [maxHP])

    def releaseControl(self):
        return None

    def getDeathEvent(self):
        return 'cogDead-%s' % self.doId

    def resume(self):
        self.notify.debug('resume, hp=%s' % self.currHP)
        if self.currHP <= 0:
            messenger.send(self.getDeathEvent())
            self.requestRemoval()
        return None

    def prepareToJoinBattle(self):
        pass

    def b_setSkelecog(self, flag):
        self.setSkelecog(flag)
        self.d_setSkelecog(flag)

    def setSkelecog(self, flag):
        SuitBase.SuitBase.setSkelecog(self, flag)

    def d_setSkelecog(self, flag):
        self.sendUpdate('setSkelecog', [flag])

    def inSellbotFactory(self):
        return False

    def isForeman(self):
        return False

    def isSupervisor(self):
        return False

    def setVirtual(self, virtual):
        pass

    def getVirtual(self):
        return None

    def isVirtual(self):
        return False

    def setWaiter(self, flag):
        SuitBase.SuitBase.setWaiter(self, flag)

    def d_setWaiter(self, flag):
        self.sendUpdate('setWaiter', [flag])

    def b_setWaiter(self, flag):
        self.setWaiter(flag)
        self.d_setWaiter(flag)

    def getWaiter(self):
        return self.waiter

    def setGovernaught(self, flag):
        SuitBase.SuitBase.setGovernaught(self, flag)

    def d_setGovernaught(self, flag):
        self.sendUpdate('setGovernaught', [flag])

    def b_setGovernaught(self, flag):
        self.setGovernaught(flag)
        self.d_setGovernaught(flag)

    def getGovernaught(self):
        return self.governaught

    def requestTreasure(self, pos, grabberId=0):
        pass

    def allyDied(self, allyId):
        if allyId not in self.deadAllies and allyId != self.doId:
            self.deadAllies.append(allyId)
            if self.buffIndex == SuitBuffGlobals.SuitBuffAvenger:
                # Buff activates when an ally dies
                bonusHP = int(round(self.maxHP * 0.25))
                self.b_setMaxHP(self.maxHP + bonusHP)
                self.b_setHP(self.currHP + bonusHP)

    def isImmuneToTrack(self, trackIndex):
        if trackIndex == SuitBattleGlobals.LURE:
            if self.buffIndex == SuitBuffGlobals.SuitBuffStable:
                return True
        return False

    def initializeBuffs(self):
        if self.isForeman() and self.inSellbotFactory():
            self.b_setBuff(random.choice(SuitBuffGlobals.ForemanBuffs))
        elif self.air.holidayManager.isHolidayRunning(NewsManagerGlobals.VALENTINES_DAY) and random.randint(0, 9) == 0:
            self.b_setBuff(SuitBuffGlobals.SuitBuffLoveStruck)

    def b_setBuff(self, buffIndex):
        self.notify.debug('Setting buff %d on suit' % buffIndex)
        self.setBuff(buffIndex)
        self.d_setBuff(buffIndex)

    def setBuff(self, buffIndex):
        self.buffIndex = buffIndex
        self.applyBuffs()

    def d_setBuff(self, buffIndex):
        self.sendUpdate('setBuff', [buffIndex])

    def getBuff(self):
        return self.buffIndex

    def applyBuffs(self):
        # Buffs that happen immediately after applied
        if self.buffIndex == SuitBuffGlobals.SuitBuffHealthy:
            attributes = self.getAttributes()
            level = self.getLevel()
            originalHp = attributes['hp'][level]
            newHp = originalHp * 2
            self.b_setMaxHP(newHp)
            self.b_setHP(newHp)
