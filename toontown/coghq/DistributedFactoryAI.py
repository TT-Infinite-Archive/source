from direct.directnotify import DirectNotifyGlobal
from otp.level import DistributedLevelAI
from otp.level import LevelSpec
from toontown.coghq.FactoryTreasureManagerAI import FactoryTreasureManagerAI
from toontown.coghq.FactoryQuestManagerAI import FactoryQuestManagerAI
from toontown.coghq import DistributedBattleFactoryAI
from toontown.coghq import FactoryQuestGlobals
from toontown.suit import DistributedFactorySuitAI
from toontown.toonbase import ToontownBattleGlobals

import LevelSuitPlannerAI
import FactoryBase
import FactoryEntityCreatorAI
import FactorySpecs
import FactoryGlobals
import SuitTreasureGlobals

import math
import random


class DistributedFactoryAI(DistributedLevelAI.DistributedLevelAI, FactoryBase.FactoryBase):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedFactoryAI')

    def __init__(self, air, factoryId, zoneId, entranceId, avIds):
        DistributedLevelAI.DistributedLevelAI.__init__(self, air, zoneId, entranceId, avIds)
        FactoryBase.FactoryBase.__init__(self)
        self.setFactoryId(factoryId)

    def createEntityCreator(self):
        return FactoryEntityCreatorAI.FactoryEntityCreatorAI(level=self)

    def getBattleCreditMultiplier(self):
        return ToontownBattleGlobals.getFactoryCreditMultiplier(self.factoryId)

    def generate(self):
        self.notify.info('generate')
        self.notify.info('start factory %s %s creation, frame=%s' % (self.factoryId, self.doId, globalClock.getFrameCount()))
        if __dev__:
            simbase.factory = self
        self.notify.info('loading spec')
        specModule = FactorySpecs.getFactorySpecModule(self.factoryId)
        factorySpec = LevelSpec.LevelSpec(specModule)
        if __dev__:
            self.notify.info('creating entity type registry')
            typeReg = self.getEntityTypeReg()
            factorySpec.setEntityTypeReg(typeReg)
        self.notify.info('creating entities')
        DistributedLevelAI.DistributedLevelAI.generate(self, factorySpec)
        self.notify.info('creating cogs')
        cogSpecModule = FactorySpecs.getCogSpecModule(self.factoryId)
        self.planner = LevelSuitPlannerAI.LevelSuitPlannerAI(self.air, self, DistributedFactorySuitAI.DistributedFactorySuitAI, DistributedBattleFactoryAI.DistributedBattleFactoryAI, cogSpecModule.CogData, cogSpecModule.ReserveCogData, cogSpecModule.BattleCells)
        self.treasureManager = FactoryTreasureManagerAI(self.air, self)
        self.questManager = FactoryQuestManagerAI(self.air, self)
        # Wait some time then start the quest manager
        taskMgr.doMethodLater(10.0, self.questManager.start, self.uniqueName('startQuestManager'))
        suitHandles = self.planner.genSuits()
        messenger.send('plannerCreated-' + str(self.doId))
        self.suits = suitHandles['activeSuits']
        self.reserveSuits = suitHandles['reserveSuits']
        self.d_setSuits()
        scenario = 0
        description = '%s|%s|%s|%s' % (self.factoryId,
         self.entranceId,
         scenario,
         self.avIdList)
        self.currentMeritCount = 0
        for avId in self.avIdList:
            self.air.writeServerEvent('factoryEntered', avId, description)

        self.notify.info('finish factory %s %s creation' % (self.factoryId, self.doId))

    def delete(self):
        self.notify.info('delete: %s' % self.doId)
        taskMgr.remove(self.uniqueName('startQuestManager'))
        if __dev__:
            if hasattr(simbase, 'factory') and simbase.factory is self:
                del simbase.factory
        suits = self.suits
        for reserve in self.reserveSuits:
            suits.append(reserve[0])

        self.planner.destroy()
        self.treasureManager.destroy()
        self.questManager.destroy()

        del self.planner
        del self.treasureManager
        del self.questManager

        for suit in suits:
            if not suit.isDeleted():
                suit.factoryIsGoingDown()
                suit.requestDelete()

        DistributedLevelAI.DistributedLevelAI.delete(self)

    def getTaskZoneId(self):
        return self.factoryId

    def getFactoryId(self):
        return self.factoryId

    def d_setForemanConfronted(self, avId):
        if avId in self.avIdList:
            self.sendUpdate('setForemanConfronted', [avId])
        else:
            self.notify.warning('%s: d_setForemanConfronted: av %s not in av list %s' % (self.doId, avId, self.avIdList))

    def setVictors(self, victorIds):
        activeVictors = []
        activeVictorIds = []
        for victorId in victorIds:
            toon = self.air.doId2do.get(victorId)
            if toon is not None:
                activeVictors.append(toon)
                activeVictorIds.append(victorId)
        scenario = 0
        description = '%s|%s|%s|%s' % (self.factoryId, self.entranceId, scenario, activeVictorIds)

        if self.air.wantGuilds and self.air.wantGuildQuests:
            self.air.guildManager.handleFactoryDefeated(self.factoryId, activeVictorIds)

        for toon in activeVictors:
            self.air.writeServerEvent('factoryDefeated', toon.doId, description)
            simbase.air.questManager.toonDefeatedFactory(toon, self.factoryId, activeVictors)

    def b_setDefeated(self):
        self.d_setDefeated()
        self.setDefeated()

    def d_setDefeated(self):
        self.sendUpdate('setDefeated')

    def setDefeated(self):
        pass

    def getCogLevel(self):
        return self.cogLevel

    def d_setSuits(self):
        self.sendUpdate('setSuits', [self.getSuits(), self.getReserveSuits()])

    def getSuits(self):
        suitIds = []
        for suit in self.suits:
            suitIds.append(suit.doId)

        return suitIds

    def getReserveSuits(self):
        suitIds = []
        for suit in self.reserveSuits:
            suitIds.append(suit[0].doId)

        return suitIds

    def incrementMeritCount(self, value):
        self.currentMeritCount += value
        if self.currentMeritCount >= FactoryGlobals.MaxMerits:
            self.currentMeritCount = FactoryGlobals.MaxMerits
        self.d_setMeritCount(self.currentMeritCount)
        
    def d_setMeritCount(self, amount):
        self.sendUpdate('setMeritCount', [amount])

    def createQuestPoster(self):
        self.d_setQuestPoster(self.questManager.quest.questId)

    def d_setQuestPoster(self, questId):
        self.sendUpdate('setQuestPoster', [questId])

    def d_setQuestProgress(self, progress):
        self.sendUpdate('setQuestProgress', [progress])

    def setQuestCompleted(self):
        # Does necessary rewards for quest completion
        quest = self.questManager.quest
        if quest is None:
            return

        dept = SuitTreasureGlobals.TreasureS
        pos = self.questManager.rewardPos
        value = quest.treasureValue
        count = quest.treasureCount

        if self.questManager.questId == FactoryQuestGlobals.FQSabotageId:
            self.treasureManager.createTreasures(self.zoneId, dept, value, pos, count, 5, 0.1)

        if self.questManager.questId == FactoryQuestGlobals.FQLootId:
            self.treasureManager.createTreasures(self.zoneId, dept, value, pos, count, 3, 0.1)

        if self.questManager.questId == FactoryQuestGlobals.FQRescueId:
            self.treasureManager.createTreasures(self.zoneId, dept, value, pos, count, 3, 0.1)

