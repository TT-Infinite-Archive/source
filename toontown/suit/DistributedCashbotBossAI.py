from panda3d.core import CollisionInvSphere, CollisionNode, CollisionSphere, ConfigVariable, ConfigVariableBool, NodePath, Point3, Vec3
import math
import random
from direct.directnotify import DirectNotifyGlobal
from toontown.toonbase import ToontownBattleGlobals
from toontown.toonbase import ToontownGlobals
from toontown.battle.DistributedBattleVaultAI import DistributedBattleVaultAI
from toontown.coghq import DistributedCashbotBossCraneAI
from toontown.coghq import DistributedCashbotBossSafeAI
from toontown.suit.SuitDNA import getRandomSuitByDept
from toontown.suit import DistributedCashbotBossGoonAI
from toontown.suit import DistributedVirtualGoonAI
from toontown.coghq import DistributedCashbotBossTreasureAI
from toontown.battle import BattleExperienceAI
from toontown.chat import ResistanceChat
from direct.fsm import FSM
from time import time
from . import DistributedBossCogAI
from otp.ai.MagicWordGlobal import *


class DistributedCashbotBossAI(DistributedBossCogAI.DistributedBossCogAI, FSM.FSM):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedCashbotBossAI')
    maxGoons = 8
    stunBuildupKnockout = [30, 120]

    def __init__(self, air):
        if simbase.air.holidayManager.isHolidayRunning(ToontownGlobals.APRIL_FOOLS_COSTUMES):
            DistributedBossCogAI.DistributedBossCogAI.__init__(self, air, 'l')
        else:
            DistributedBossCogAI.DistributedBossCogAI.__init__(self, air, 'm')
        FSM.FSM.__init__(self, 'DistributedCashbotBossAI')
        self.cranes = None
        self.safes = None
        self.goons = None
        self.treasures = {}
        self.grabbingTreasures = {}
        self.recycledTreasures = []
        self.healAmount = 0
        self.rewardIds = [ResistanceChat.getRandomId(), ResistanceChat.getRandomId(), ResistanceChat.getRandomId()]
        self.rewardedToons = []
        self.scene = NodePath('scene')
        self.reparentTo(self.scene)
        cn = CollisionNode('walls')
        cs = CollisionSphere(0, 0, 0, 13)
        cn.addSolid(cs)
        cs = CollisionInvSphere(0, 0, 0, 42)
        cn.addSolid(cs)
        self.attachNewNode(cn)
        self.heldObject = None
        self.waitingForHelmet = 0
        self.avatarHelmets = {}
        self.bossMaxDamage = ToontownGlobals.CashbotBossMaxDamage
        self.battleDifficulty = 0
        self.battleThreeDuration = [0, 500, 1500, 3000]
        self.attackSpeed = 1
        self.stunBuildup = 0
        self.goonBuildup = 0
        self.isSwarming = False
        self.numSwarmGoons = 0
        self.destroyedGoons = []
        self.battleTwoBattles = {}
        self.battleTwoToons = []
        self.threatDict = {}

    def generate(self):
        DistributedBossCogAI.DistributedBossCogAI.generate(self)
        if __dev__:
            self.scene.reparentTo(self.getRender())

    def getHoodId(self):
        return ToontownGlobals.CashbotHQ

    def formatReward(self):
        return str(self.rewardIds)

    def progressValue(self, fromValue, toValue):
        t0 = float(self.bossDamage) / float(self.bossMaxDamage)
        elapsed = globalClock.getFrameTime() - self.battleThreeStart
        t1 = elapsed / float(self.battleThreeDuration[self.battleDifficulty])
        t = max(t0, t1)
        result = fromValue + (toValue - fromValue) * min(t, 1)
        return result

    def makeBattleOneBattles(self):
        self.postBattleState = 'PrepareBattleTwo'
        self.initializeBattles(1, ToontownGlobals.CashbotBossBattleOnePosHpr)

    def makeBattleTwoBattles(self):
        self.postBattleState = 'PrepareBattleThree'
        self.initializeBattles(2, [0 for i in range(6)])

    def divideToons(self, battleTwo=False):
        if not battleTwo:
            DistributedBossCogAI.DistributedBossCogAI.divideToons(self)
            return

        toons = self.involvedToons[:]
        random.shuffle(toons)
        numToons = min(len(toons), 8)
        self.battleTwoToons = []

        if len(toons) > 1:
            for i in range(int(round(len(toons) / 2.0))):
                if len(toons) > 1:
                    self.battleTwoToons.append([toons.pop(0), toons.pop(0)])
                else:
                    self.battleTwoToons.append([toons.pop(0)])
        else:
            self.battleTwoToons.append([toons.pop(0)])

        self.looseToons += toons[numToons:]

        self.sendToonIds(battleTwo=battleTwo)

    def sendToonIds(self, battleTwo=False):
        if battleTwo:
            self.sendUpdate('setBattleTwoGroups', [self.battleTwoToons])

        self.sendUpdate('setToonIds', [self.involvedToons, self.toonsA, self.toonsB])

    def sendBattleIds(self):
        if self.battleTwoBattles:
            battleIds = []

            for battleTuple in list(self.battleTwoBattles.values()):
                battleIds.append(battleTuple[0].doId)

            if battleIds:
                self.sendUpdate('setBattleTwoIds', [battleIds])
                return

        self.sendUpdate('setBattleIds', [self.battleNumber, self.battleAId, self.battleBId])

    def initializeBattles(self, battleNumber, bossCogPosHpr):
        if battleNumber != 2:
            DistributedBossCogAI.DistributedBossCogAI.initializeBattles(self, battleNumber, bossCogPosHpr)
            return

        if not self.involvedToons:
            self.notify.warning('initializeBattles: no toons!')
            return

        self.battleNumber = battleNumber
        self.battleTwoBattles = {}
        for i in range(len(self.battleTwoToons)):
            suitHandles = self.generateSuits(battleNumber)
            suits = suitHandles['activeSuits']
            activeSuits = suits[:]

            if not self.reserveSuits:
                self.reserveSuits = suitHandles['reserveSuits']
            else:
                self.reserveSuits += suitHandles['reserveSuits']

            self.battleTwoBattles[i] = [
                self.makeBattleTwoBattle(bossCogPosHpr, ToontownGlobals.CashbotBossCranePosHprs[i],
                                         self.handleBattleTwoRoundDone, self.handleBattleTwoDone, battleNumber, 0, activeSuits, i),
                suits, activeSuits]

        self.sendBattleIds()

    def enterBattleTwo(self):
        for i in range(len(self.battleTwoBattles)):
            battleTuple = self.battleTwoBattles[i]
            battleTuple[0].startBattle(self.battleTwoToons[i], battleTuple[1])

    def exitBattleTwo(self):
        self.resetBattles()

    def makeBattleTwoBattle(self, bossCogPosHpr, battlePosHpr, roundCallback, finishCallback, battleNumber, battleSide, activeSuits, index):
        battle = DistributedBattleVaultAI(self.air, self, roundCallback, finishCallback, battleSide, index)
        self.setBattlePos(battle, bossCogPosHpr, battlePosHpr)
        battle.suitsKilled = self.suitsKilled
        battle.battleCalc.toonSkillPtsGained = self.toonSkillPtsGained
        battle.toonExp = self.toonExp
        battle.toonOrigQuests = self.toonOrigQuests
        battle.toonItems = self.toonItems
        battle.toonOrigMerits = self.toonOrigMerits
        battle.toonMerits = self.toonMerits
        battle.toonParts = self.toonParts
        battle.helpfulToons = self.helpfulToons
        mult = ToontownBattleGlobals.getBossBattleCreditMultiplier(battleNumber)
        battle.battleCalc.setSkillCreditMultiplier(mult)

        for suit in activeSuits:
            battle.addSuit(suit)

        battle.generateWithRequired(self.zoneId)
        return battle

    def handleBattleTwoRoundDone(self, toonIds, totalHp, deadSuits, index):
        if index in self.battleTwoBattles:
            self.handleRoundDone(self.battleTwoBattles[index][0], self.battleTwoBattles[index][1],
                                 self.battleTwoBattles[index][2], toonIds, totalHp, deadSuits)

    def handleBattleTwoDone(self, zoneId, toonIds, index):
        if index in self.battleTwoBattles:
            self.battleTwoBattles[index][0].requestDelete()
            del self.battleTwoBattles[index]
            self.sendBattleIds()

        if not self.battleTwoBattles and self.hasToons() and self.hasToonsAlive():
            self.b_setState(self.postBattleState)
        return

    def generateSuits(self, battleNumber):
        if battleNumber != 2:
            cogs = self.invokeSuitPlanner(11, 0)
            skelecogs = self.invokeSuitPlanner(12, 1)
        else:
            if self.battleDifficulty == 1:
                sp = 27
            elif self.battleDifficulty == 2:
                sp = 28
            else:
                sp = 29

            cogs = self.invokeSuitPlanner(sp, 0)
            skelecogs = self.invokeSuitPlanner(sp, 1)

        activeSuits = cogs['activeSuits'] + skelecogs['activeSuits']
        reserveSuits = cogs['reserveSuits'] + skelecogs['reserveSuits']
        random.shuffle(activeSuits)
        while len(activeSuits) > 4:
            suit = activeSuits.pop()
            reserveSuits.append((suit, 100))

        reserveSuits.sort(key=lambda joinChance: joinChance[1])
        return {'activeSuits': activeSuits,
         'reserveSuits': reserveSuits}

    def enterElevator(self):
        self.d_setRewardIds(self.rewardIds)
        DistributedBossCogAI.DistributedBossCogAI.enterElevator(self)
        self.calcAndSetBattleDifficulty()

    def removeToon(self, avId):
        if self.cranes is not None:
            for crane in self.cranes:
                crane.removeToon(avId)

        if self.safes is not None:
            for safe in self.safes:
                safe.removeToon(avId)

        if self.goons is not None:
            for goon in self.goons:
                goon.removeToon(avId)

        DistributedBossCogAI.DistributedBossCogAI.removeToon(self, avId)
        return

    def __makeBattleThreeObjects(self):
        if self.cranes is None:
            self.cranes = []
            for index in range(len(ToontownGlobals.CashbotBossCranePosHprs)):
                crane = DistributedCashbotBossCraneAI.DistributedCashbotBossCraneAI(self.air, self, index)
                crane.generateWithRequired(self.zoneId)
                self.cranes.append(crane)

        if self.safes is None:
            self.safes = []
            for index in range(len(ToontownGlobals.CashbotBossSafePosHprs)):
                safe = DistributedCashbotBossSafeAI.DistributedCashbotBossSafeAI(self.air, self, index)
                safe.generateWithRequired(self.zoneId)
                self.safes.append(safe)

        if self.goons is None:
            self.goons = []
        return

    def __resetBattleThreeObjects(self):
        if self.cranes is not None:
            for crane in self.cranes:
                crane.request('Free')

        if self.safes is not None:
            for safe in self.safes:
                safe.request('Initial')

        return

    def __deleteBattleThreeObjects(self):
        if self.cranes is not None:
            for crane in self.cranes:
                crane.request('Off')
                crane.requestDelete()

            self.cranes = None
        if self.safes is not None:
            for safe in self.safes:
                safe.request('Off')
                safe.requestDelete()

            self.safes = None
        if self.goons is not None:
            for goon in self.goons:
                goon.request('Off')
                goon.requestDelete()

            self.goons = None
        return

    def doNextAttack(self, task):
        doAttack = random.randrange(1, 101)
        attackSpeed = self.progressValue(1, 1.60)
        self.b_setAttackSpeed(attackSpeed)

        if doAttack <= self.progressValue(7, 15):
            self.__doAreaAttack()
            self.lastAreaAttackTime = globalClock.getFrameTime()
            self.waitForNextAttack(self.progressValue(10, 6))
        else:
            rng = random.randint(0, 6)
            if rng < 2:
                self.__doFrontAttack()
            else:
                self.__doDirectedAttack()
            self.waitForNextAttack(self.progressValue(10, 6))

        if self.heldObject is None and not self.waitingForHelmet:
            self.waitForNextHelmet()
        return

    def __doDirectedAttack(self):
        if self.toonsToAttack:
            toonId = max(iter(self.threatDict.keys()), key=lambda k: self.getThreat(k)) if self.threatDict else self.toonsToAttack.pop(0)
            toonThreat = self.getThreat(toonId)
            toonThreat *= 0.15
            self.subtractThreat(toonId, toonThreat)
            while toonId not in self.involvedToons:
                if not self.toonsToAttack:
                    self.b_setAttackCode(ToontownGlobals.BossCogNoAttack)
                    return
                toonId = self.toonsToAttack.pop(0)

            self.toonsToAttack.append(toonId)
            self.b_setAttackCode(ToontownGlobals.BossCogSlowDirectedAttack, toonId)

    def __doAreaAttack(self):
        self.b_setAttackCode(ToontownGlobals.BossCogAreaAttack)

        def stunGoons(task=None):
            if self.attackCode != ToontownGlobals.BossCogAreaAttack:
                if task:
                    return task.done
                return
            if self.goons:
                for goon in self.goons:
                    if goon.state == 'Stunned':
                        goon.request('Recovery')
            if task:
                return task.done

        taskMgr.doMethodLater(4.5, stunGoons, 'stunGoons-%d' % self.doId)

    def __doFrontAttack(self):
        self.b_setAttackCode(ToontownGlobals.BossCogFrontAttack)

    def reprieveToon(self, avId):
        if avId in self.toonsToAttack:
            i = self.toonsToAttack.index(avId)
            del self.toonsToAttack[i]
            self.toonsToAttack.append(avId)

    def makeTreasure(self, goon):
        if self.state != 'BattleThree':
            return
        pos = goon.getPos(self)
        v = Vec3(pos[0], pos[1], 0.0)
        if not v.normalize():
            v = Vec3(1, 0, 0)
        v *= 27
        angle = random.uniform(0.0, 2.0 * math.pi)
        radius = 5
        dx = radius * math.cos(angle)
        dy = radius * math.sin(angle)
        fpos = self.scene.getRelativePoint(self, Point3(v[0] + dx, v[1] + dy, 0))
        if goon.strength <= 10:
            style = random.choice(
                [ToontownGlobals.TheBrrrgh, ToontownGlobals.DonaldsDreamland])
            healAmount = random.randint(7, 10)
        elif goon.strength <= 15:
            style = random.choice(
                [ToontownGlobals.DonaldsDock, ToontownGlobals.DaisyGardens, ToontownGlobals.MinniesMelodyland])
            healAmount = random.randint(4, 7)
        else:
            style = random.choice(
                [ToontownGlobals.ToontownCentral, ToontownGlobals.OutdoorZone, ToontownGlobals.MyEstate])
            healAmount = random.randint(1, 4)
        if self.recycledTreasures:
            treasure = self.recycledTreasures.pop(0)
            treasure.d_setGrab(0)
            treasure.b_setGoonId(goon.doId)
            treasure.b_setStyle(style)
            treasure.b_setPosition(pos[0], pos[1], 0)
            treasure.b_setFinalPosition(fpos[0], fpos[1], 0)
        else:
            treasure = DistributedCashbotBossTreasureAI.DistributedCashbotBossTreasureAI(
                self.air, self, goon, style, fpos[0], fpos[1], 0)
            treasure.generateWithRequired(self.zoneId)
        treasure.healAmount = healAmount
        self.treasures[treasure.doId] = treasure

    def grabAttempt(self, avId, treasureId):
        av = self.air.doId2do.get(avId)
        if not av:
            return
        treasure = self.treasures.get(treasureId)
        if treasure:
            if treasure.validAvatar(av):
                del self.treasures[treasureId]
                treasure.d_setGrab(avId)
                self.grabbingTreasures[treasureId] = treasure
                taskMgr.doMethodLater(5, self.__recycleTreasure, treasure.uniqueName('recycleTreasure'), extraArgs=[treasure])
            else:
                treasure.d_setReject()

    def __recycleTreasure(self, treasure):
        if treasure.doId in self.grabbingTreasures:
            del self.grabbingTreasures[treasure.doId]
            self.recycledTreasures.append(treasure)

    def deleteAllTreasures(self):
        for treasure in list(self.treasures.values()):
            treasure.requestDelete()

        self.treasures = {}
        for treasure in list(self.grabbingTreasures.values()):
            taskMgr.remove(treasure.uniqueName('recycleTreasure'))
            treasure.requestDelete()

        self.grabbingTreasures = {}
        for treasure in self.recycledTreasures:
            treasure.requestDelete()

        self.recycledTreasures = []

    def getBattleThreeTime(self):
        elapsed = globalClock.getFrameTime() - self.battleThreeStart
        t1 = elapsed / float(self.battleThreeDuration[self.battleDifficulty])
        return t1

    def getMaxGoons(self):
        t = self.getBattleThreeTime()
        if t <= 1.0:
            return self.maxGoons
        else:
            return self.maxGoons + min(int(t * 10) - 10, 6)

    def getMinGoons(self):
        return int(min(self.getMaxGoons() / 2, 5))

    def makeGoon(self, side=None, virtual=False, swarm=False, task=None):
        if side is None:
            side = random.choice(['EmergeA', 'EmergeB'])
        goon = self.__chooseOldGoon()
        if goon is None or virtual:
            if len(self.goons) >= self.getMaxGoons():
                return
            if virtual:
                goon = DistributedVirtualGoonAI.DistributedVirtualGoonAI(self.air, self)
                goon.setSuitName(getRandomSuitByDept(self.dept))
            else:
                goon = DistributedCashbotBossGoonAI.DistributedCashbotBossGoonAI(self.air, self)
            goon.generateWithRequired(self.zoneId)
            self.goons.append(goon)
            if goon.doId in self.destroyedGoons:
                self.destroyedGoons.remove(goon.doId)
        goon.STUN_TIME = self.progressRandomValue(16, 8)
        goon.b_setupGoon(
            velocity=self.progressRandomValue(4, 9, 0.3),
            hFov=80,
            attackRadius=self.progressRandomValue(4, 15, 0.35),
            strength=int(self.progressRandomValue(4, 45, 0.35)),
            scale=self.progressRandomValue(1, 2.5, 0.3))
        goon.request(side)
        goon.hasDroppedTreasure = False
        if task:
            return task.done
        return

    def __chooseOldGoon(self):
        for goon in self.goons:
            if goon.state == 'Off':
                if not isinstance(goon, DistributedVirtualGoonAI.DistributedVirtualGoonAI):
                    return goon
                else:
                    self.goons.remove(goon)
                    goon.requestDelete()
                    return

    def waitForNextGoon(self, delayTime):
        currState = self.getCurrentOrNextState()
        if currState == 'BattleThree':
            taskName = self.uniqueName('NextGoon')
            taskMgr.remove(taskName)
            taskMgr.doMethodLater(delayTime, self.doNextGoon, taskName)

    def stopGoons(self):
        taskMgr.remove(self.uniqueName('NextGoon'))
        taskMgr.remove(self.uniqueName('goonBuildup'))

        for i in range(7):
            taskName = self.uniqueName('spawnGoon-%d' % i)
            taskMgr.remove(taskName)

        self.cleanupSwarm()

    def doNextGoon(self, task):
        if self.attackCode not in (ToontownGlobals.BossCogDizzy, ToontownGlobals.BossCogAreaAttack):
            virtual = random.random() < self.progressValue(0.10, 0.50)
            self.makeGoon(virtual=virtual)

        delayTime = self.progressValue(8, 4)
        self.waitForNextGoon(delayTime)

    def waitForNextHelmet(self):
        currState = self.getCurrentOrNextState()
        if currState == 'BattleThree':
            taskName = self.uniqueName('NextHelmet')
            taskMgr.remove(taskName)
            delayTime = self.progressValue(45, 20)
            taskMgr.doMethodLater(delayTime, self.__donHelmet, taskName)
            self.waitingForHelmet = 1

    def __donHelmet(self, task):
        self.waitingForHelmet = 0
        if self.heldObject is None:
            safe = self.safes[0]
            safe.request('Grabbed', self.doId, self.doId)
            self.heldObject = safe
        return

    def stopHelmets(self):
        self.waitingForHelmet = 0
        taskName = self.uniqueName('NextHelmet')
        taskMgr.remove(taskName)

    def acceptHelmetFrom(self, avId):
        now = globalClock.getFrameTime()
        then = self.avatarHelmets.get(avId, None)
        if then is None or now - then > 300:
            self.avatarHelmets[avId] = now
            return 1
        return 0

    def magicWordHit(self, damage, avId):
        if self.heldObject:
            self.heldObject.demand('Dropped', avId, self.doId)
            self.heldObject.avoidHelmet = 1
            self.heldObject = None
            self.waitForNextHelmet()
        else:
            self.recordHit(damage)
        return

    def magicWordReset(self):
        if self.state == 'BattleThree':
            self.__resetBattleThreeObjects()

    def magicWordResetGoons(self):
        if self.state == 'BattleThree':
            if self.goons is not None:
                for goon in self.goons:
                    goon.request('Off')
                    goon.requestDelete()

                self.goons = None
            self.__makeBattleThreeObjects()
        return

    def recordHit(self, damage):
        avId = self.air.getAvatarIdFromSender()
        if not self.validate(avId, avId in self.involvedToons, 'recordHit from unknown avatar'):
            return
        if self.state != 'BattleThree':
            return

        self.b_setBossDamage(self.bossDamage + damage)
        self.sendUpdate('leaderboardUpdateAvatar', [avId, damage])
        self.sendUpdate('healthBarUpdate', [])
        self.addThreat(avId, damage)

        if self.bossDamage >= self.bossMaxDamage:
            self.sendUpdate('timerStop', [time()])
            self.b_setState('Victory')
        elif self.attackCode != ToontownGlobals.BossCogDizzy:
            if self.validateStun(damage):
                self.b_setAttackCode(ToontownGlobals.BossCogDizzy)
                self.stopHelmets()
            else:
                self.b_setAttackCode(ToontownGlobals.BossCogNoAttack)
                self.stopHelmets()
                self.waitForNextHelmet()

    def validateStun(self, damage):
        if self.attackCode in (ToontownGlobals.BossCogDizzy, ToontownGlobals.BossCogDizzyNow):
            return False
        self.stunBuildup += damage
        if self.stunBuildup >= int(self.progressValue(*self.stunBuildupKnockout)):
            self.clearStunBuildUp()
            return True

        taskMgr.doMethodLater(10, self.clearStunBuildUp, self.uniqueName('clear-stun-buildup'))
        return False

    def clearStunBuildUp(self, task=None):
        self.stunBuildup = 0

    def b_setBossDamage(self, bossDamage):
        self.d_setBossDamage(bossDamage)
        self.setBossDamage(bossDamage)

    def setBossDamage(self, bossDamage):
        self.reportToonHealth()
        self.bossDamage = bossDamage

    def d_setBossDamage(self, bossDamage):
        self.sendUpdate('setBossDamage', [bossDamage])

    def d_setRewardIds(self, rewardIds):
        self.sendUpdate('setRewardIds', [rewardIds])

    def applyReward(self):
        avId = self.air.getAvatarIdFromSender()
        if avId in self.involvedToons and avId not in self.rewardedToons:
            self.rewardedToons.append(avId)
            toon = self.air.doId2do.get(avId)
            if toon:
                toon.doResistanceEffect(self.rewardIds[0])
                if self.battleDifficulty >= 2:
                    toon.doResistanceEffect(self.rewardIds[1])
                if self.battleDifficulty == 3:
                    toon.doResistanceEffect(self.rewardIds[2])

            if ConfigVariableBool('cfo-staff-event', False).getValue():

                withStaff = False
                for avId in self.involvedToons:
                    av = self.air.doId2do.get(avId)
                    if av:
                        if av.adminAccess > 100:
                            withStaff = True

                if withStaff:
                    participants = simbase.backups.load('cfo-staff-event', ('participants',), default={'doIds': []})
                    if avId not in participants['doIds']:
                        participants['doIds'].append(toon.doId)
                    simbase.backups.save('cfo-staff-event', ('participants',), participants)

    def enterOff(self):
        DistributedBossCogAI.DistributedBossCogAI.enterOff(self)
        self.rewardedToons = []

    def exitOff(self):
        DistributedBossCogAI.DistributedBossCogAI.exitOff(self)

    def enterIntroduction(self):
        DistributedBossCogAI.DistributedBossCogAI.enterIntroduction(self)
        self.__makeBattleThreeObjects()
        self.__resetBattleThreeObjects()

    def exitIntroduction(self):
        DistributedBossCogAI.DistributedBossCogAI.exitIntroduction(self)
        self.__deleteBattleThreeObjects()

    def enterPrepareBattleTwo(self):
        self.calcAndSetBattleDifficulty()
        if self.battleDifficulty == 2:
            self.bossMaxDamage = 1000
            self.maxGoons = 10
        elif self.battleDifficulty == 3:
            self.bossMaxDamage = 2000
            self.maxGoons = 15

        self.__makeBattleThreeObjects()
        self.__resetBattleThreeObjects()

        if not self.battleTwoBattles:
            self.divideToons(battleTwo=True)
            self.makeBattleTwoBattles()

        self.barrier = self.beginBarrier('PrepareBattleTwo', self.involvedToons, 75, self.__donePrepareBattleTwo)

    def __donePrepareBattleTwo(self, avIds):
        self.b_setState('BattleTwo')

    def exitPrepareBattleTwo(self):
        if self.newState != 'BattleTwo':
            self.__deleteBattleThreeObjects()
        self.ignoreBarrier(self.barrier)

    def cleanupBattleTwoBattles(self):
        for i in range(len(self.battleTwoToons)):
            if i in self.battleTwoBattles:
                self.battleTwoBattles[i][0].b_setState('Off')
                self.battleTwoBattles[i][0].requestDelete()
                self.battleTwoBattles[i][0] = None
                del self.battleTwoBattles[i]

        self.battleTwoToons = []

        self.sendBattleIds()

    def enterPrepareBattleThree(self):
        self.barrier = self.beginBarrier('PrepareBattleThree', self.involvedToons, 55, self.__donePrepareBattleThree)

    def __donePrepareBattleThree(self, avIds):
        self.b_setState('BattleThree')

    def exitPrepareBattleThree(self):
        self.ignoreBarrier(self.barrier)

    def enterBattleThree(self):
        self.resetBattles()
        for avId in self.involvedToons:
            av = self.air.doId2do.get(avId)
            if av:
                av.b_setBattleId(0)

        self.stunBuildupKnockout[0] += len(self.involvedToons) * 2
        self.stunBuildupKnockout[1] += len(self.involvedToons) * 2
        self.setPosHpr(*ToontownGlobals.CashbotBossBattleThreePosHpr)
        self.reportToonHealth()
        self.toonsToAttack = self.involvedToons[:]
        random.shuffle(self.toonsToAttack)
        self.b_setBossDamage(0)
        self.__makeBattleThreeObjects()
        self.__resetBattleThreeObjects()
        self.cleanupBattleTwoBattles()
        self.battleThreeStart = globalClock.getFrameTime()
        self.sendUpdate('timerStart', [time()])
        self.waitForNextAttack(15)
        self.waitForNextHelmet()
        self.makeGoon(side='EmergeA')
        self.makeGoon(side='EmergeB')
        taskName = self.uniqueName('NextGoon')
        taskMgr.remove(taskName)
        taskMgr.doMethodLater(2, self.__doInitialGoons, taskName)

    def __doInitialGoons(self, task):
        def doGoon(i, task):
            i += 1
            self.makeGoon(side='EmergeA')
            self.makeGoon(side='EmergeB')
            if i < 4:
                taskMgr.doMethodLater(1.5, doGoon, self.uniqueName('initialGoons'), extraArgs=[i], appendTask=True)
            else:
                return task.done

        taskMgr.doMethodLater(1.5, doGoon, self.uniqueName('initialGoons'), extraArgs=[0], appendTask=True)

        self.waitForNextGoon(6)

    def exitBattleThree(self):
        helmetName = self.uniqueName('helmet')
        taskMgr.remove(helmetName)
        if self.newState != 'Victory':
            self.__deleteBattleThreeObjects()
        self.deleteAllTreasures()
        self.stopAttacks()
        self.stopGoons()
        self.stopHelmets()
        self.heldObject = None
        return

    def enterVictory(self):
        self.resetBattles()
        self.suitsKilled.append({'type': None,
         'level': None,
         'track': self.dna.dept,
         'isSkelecog': 0,
         'isForeman': 0,
         'isVP': 0,
         'isCFO': 1,
         'isSupervisor': 0,
         'isVirtual': 0,
         'activeToons': self.involvedToons[:]})
        self.barrier = self.beginBarrier('Victory', self.involvedToons, 30, self.__doneVictory)
        return

    def __doneVictory(self, avIds):
        self.d_setBattleExperience()
        self.b_setState('Reward')
        BattleExperienceAI.assignRewards(self.involvedToons, self.toonSkillPtsGained, self.suitsKilled, ToontownGlobals.dept2cogHQ(self.dept), self.helpfulToons)
        for toonId in self.involvedToons:
            toon = self.air.doId2do.get(toonId)
            if toon is not None:
                amount = self.battleDifficulty
                for i in range(0, amount):
                    if i >= len(self.rewardIds):
                        # We haven't predefined a reward here, so get a random one
                        toon.addResistanceMessage(ResistanceChat.getRandomId())
                    else:
                        # Add a predefined reward to the toon
                        toon.addResistanceMessage(self.rewardIds[i])
                toon.b_promote(self.deptIndex)

    def exitVictory(self):
        self.__deleteBattleThreeObjects()

    def enterEpilogue(self):
        DistributedBossCogAI.DistributedBossCogAI.enterEpilogue(self)

    def resetBattles(self):
        sendReset = 0
        for suit in self.suitsA + self.suitsB:
            suit.requestDelete()

        if self.battleA:
            self.battleA.requestDelete()
            self.battleA = None
            self.battleAId = 0
            sendReset = 1
        if self.battleB:
            self.battleB.requestDelete()
            self.battleB = None
            self.battleBId = 0
            sendReset = 1

        for battleTuple in list(self.battleTwoBattles.values()):
            battleTuple[0].requestDelete()

        self.battleTwoBattles = {}

        for suit, joinChance in self.reserveSuits:
            suit.requestDelete()

        self.suitsA = []
        self.activeSuitsA = []
        self.suitsB = []
        self.activeSuitsB = []
        self.reserveSuits = []
        self.battleNumber = 0
        if sendReset:
            self.sendBattleIds()
        return

    def goonDestroyed(self, goon):
        if goon.doId in self.destroyedGoons:
            return
        self.destroyedGoons.append(goon.doId)
        self.goonBuildup += 1
        rng = random.random()
        goonBuildupPoint = self.progressValue(6, 12) + len(self.involvedToons)
        if self.goonBuildup > goonBuildupPoint and not self.isSwarming:
            self.startSwarm()
        elif rng < self.goonBuildup * .10:
            self.makeGoon(side='EmergeA', virtual=isinstance(goon, DistributedVirtualGoonAI.DistributedCashbotBossGoonAI))
            self.makeGoon(side='EmergeB', virtual=isinstance(goon, DistributedVirtualGoonAI.DistributedCashbotBossGoonAI))

        activeGoonsCount = len(self.getActiveGoons())
        if activeGoonsCount < self.getMinGoons():
            diff = self.getMinGoons() - activeGoonsCount
            if not diff <= 0:
                for i in range(diff):
                    taskName = self.uniqueName('spawnGoon-%d' % i)
                    taskMgr.remove(taskName)
                    isVirtual = random.random() <= 0.3
                    taskMgr.doMethodLater(i + 1, self.makeGoon, taskName,
                                          extraArgs=[None, isVirtual, False], appendTask=True)

        taskMgr.remove(self.uniqueName('goonBuildup'))
        taskMgr.doMethodLater(7.5, self.clearGoonBuildup, self.uniqueName('goonBuildup'))

    def clearGoonBuildup(self, task=None):
        self.goonBuildup = 0
        if task:
            return task.done
        else:
            taskMgr.remove(self.uniqueName('goonBuildup'))

    def startSwarm(self):
        self.isSwarming = True
        self.numSwarmGoons = int(self.progressValue(5, 10))
        side = random.choice(['EmergeA', 'EmergeB'])
        taskMgr.doMethodLater(2, self.makeSwarmGoon, self.uniqueName('goonSwarm'),
                              extraArgs=[side, 0], appendTask=True)

    def makeSwarmGoon(self, side, i, task):
        i += 1
        self.makeGoon(side=side, virtual=False, swarm=True)
        if i == self.numSwarmGoons - 1:
            taskMgr.doMethodLater(2, self.makeSwarmGoon, self.uniqueName('goonSwarm'),
                                  extraArgs=[side, i], appendTask=True, uponDeath=self.cleanupSwarm)
            return
        elif i < self.numSwarmGoons:
            taskMgr.doMethodLater(2, self.makeSwarmGoon, self.uniqueName('goonSwarm'),
                                  extraArgs=[side, i], appendTask=True)
        return task.done

    def cleanupSwarm(self, task=None):
        self.isSwarming = False
        self.clearGoonBuildup()
        taskMgr.remove(self.uniqueName('goonSwarm'))

    def getThreat(self, toonId):
        if toonId in self.threatDict:
            return self.threatDict[toonId]
        return 0

    def addThreat(self, toonId, threat):
        if toonId in self.threatDict:
            self.threatDict[toonId] += threat
            return
        self.threatDict[toonId] = threat

    def subtractThreat(self, toonId, threat):
        if toonId in self.threatDict:
            self.threatDict[toonId] -= threat
            if self.threatDict[toonId] < 0:
                self.threatDict[toonId] = 0
        else:
            self.threatDict[toonId] = 0

    def getActiveGoons(self):
        activeGoons = []
        goons = self.goons
        for goon in goons:
            if goon.doId not in self.destroyedGoons:
                activeGoons.append(goon)

        return activeGoons

@magicWord(category=CATEGORY_ADMINISTRATOR)
def startCraneRound():
    """
    Skips to the crane round of the CFO.
    """
    invoker = spellbook.getInvoker()
    boss = None
    for do in list(simbase.air.doId2do.values()):
        if isinstance(do, DistributedCashbotBossAI):
            if invoker.doId in do.involvedToons:
                boss = do
                break
    if not boss:
        return "You aren't in a C.F.O.!"
    if boss.state in ('PrepareBattleTwo', 'PrepareBattleThree', 'BattleThree'):
        return "You can't skip this round."
    boss.exitIntroduction()
    boss.b_setState('PrepareBattleTwo')
    boss.b_setState('BattleTwo')
    boss.b_setState('PrepareBattleThree')
    boss.b_setState('BattleThree')
    return 'Starting the crane round...'

@magicWord(category=CATEGORY_ADMINISTRATOR)
def restartCraneRound():
    """
    Restarts the crane round in the CFO.
    """
    invoker = spellbook.getInvoker()
    boss = None
    for do in list(simbase.air.doId2do.values()):
        if isinstance(do, DistributedCashbotBossAI):
            if invoker.doId in do.involvedToons:
                boss = do
                break
    if not boss:
        return "You aren't in a C.F.O.!"
    boss.exitIntroduction()
    boss.b_setState('PrepareBattleTwo')
    boss.b_setState('BattleThree')
    return 'Restarting the crane round...'

@magicWord(category=CATEGORY_ADMINISTRATOR)
def skipCFO():
    """
    Skips the current round in the CFO.
    """
    invoker = spellbook.getInvoker()
    boss = None
    for do in list(simbase.air.doId2do.values()):
        if isinstance(do, DistributedCashbotBossAI):
            if invoker.doId in do.involvedToons:
                boss = do
                break
    if not boss:
        return "You aren't in a C.F.O.!"
    if boss.state in ('PrepareBattleTwo', 'PrepareBattleThree', 'BattleThree'):
        return "You can't skip this round."
    boss.exitIntroduction()
    if boss.state == 'BattleTwo':
        boss.b_setState('PrepareBattleThree')
    else:
        boss.b_setState('PrepareBattleTwo')
    return 'Skipping the round...'

@magicWord(category=CATEGORY_ADMINISTRATOR)
def killCFO():
    """
    Kills the CFO.
    """
    invoker = spellbook.getInvoker()
    boss = None
    for do in list(simbase.air.doId2do.values()):
        if isinstance(do, DistributedCashbotBossAI):
            if invoker.doId in do.involvedToons:
                boss = do
                break
    if not boss:
        return "You aren't in a C.F.O.!"
    if boss.state in ('Victory', 'Reward', 'Epilogue'):
        return "The C.F.O. has already been defeated!"
    boss.b_setState('Victory')
    return 'Killed C.F.O.'

@magicWord(category=CATEGORY_ADMINISTRATOR, types=[int])
def hitCFO(dmg):
    """
    Hits the CFO.
    """
    invoker = spellbook.getInvoker()
    boss = None
    for do in list(simbase.air.doId2do.values()):
        if isinstance(do, DistributedCashbotBossAI):
            if invoker.doId in do.involvedToons:
                boss = do
                break
    if not boss:
        return "You aren't in a CFO!"
    if dmg < 0 or dmg > boss.bossMaxDamage:
        return "Invalid damage!"
    boss.b_setBossDamage(min(boss.bossDamage + dmg, boss.bossMaxDamage))
    return 'Hit CFO with %s damage.' % dmg
