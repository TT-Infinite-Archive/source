from direct.directnotify.DirectNotifyGlobal import directNotify
from toontown.coghq import FactoryQuestGlobals
from toontown.coghq.DistributedFactoryQuestBarrelAI import DistributedFactoryQuestBarrelAI
from toontown.coghq.DistributedFactoryQuestNPCAI import DistributedFactoryQuestNPCAI
import random

class FactoryQuestManagerAI:
    notify = directNotify.newCategory('FactoryQuestManagerAI')

    def __init__(self, air, factory):
        self.air = air
        self.factory = factory
        self.questId = -1
        self.quest = None
        self.progress = 0
        self.completed = False
        self.entities = []
        self.rewardPos = [0.0, 0.0, 0.0]

    def start(self, task=None):
        # Picks a quest, tells the factory to create a quest poster for the quest, spawns entities necessary for the quest
        # TODO: add a got quest sound?
        if self.questId != -1:
            self.notify.warning('Tried to start an already started quest manager')
            return

        self.questId = FactoryQuestGlobals.getRandomQuestId()
        self.quest = FactoryQuestGlobals.FactoryQuests[self.questId]
        self.factory.createQuestPoster()
        self.setupQuest()

    def setupQuest(self):
        if self.questId == FactoryQuestGlobals.FQLootId:
            # Get a random position to place the barrel
            posHpr = random.choice(FactoryQuestGlobals.FQBarrelPositions)

            # Save the position to do the rewards
            self.rewardPos = [posHpr[0], posHpr[1], posHpr[2]]

            # Spawn the entity and save it in the entity list
            entity = DistributedFactoryQuestBarrelAI(self.factory, *posHpr)
            entity.generateWithRequired(self.factory.zoneId)
            self.entities.append(entity)
        elif self.questId == FactoryQuestGlobals.FQRescueId:
            # Get a random position to place the barrel
            posHpr = random.choice(FactoryQuestGlobals.FQRescueNPCPositions)

            # Get a random npc to spawn
            npcId = random.choice(FactoryQuestGlobals.FQRescuePossibleNPCs)

            # Save the position to do the rewards
            self.rewardPos = [posHpr[0], posHpr[1], posHpr[2]]

            # Spawn the entity and save it in the entity list
            entity = DistributedFactoryQuestNPCAI(self.factory, npcId, *posHpr)
            entity.generateWithRequired(self.factory.zoneId)
            self.entities.append(entity)
        elif self.questId == FactoryQuestGlobals.FQSabotageId:
            # This one doesnt need entities, so lets just set the reward pos
            self.rewardPos = FactoryQuestGlobals.FQSabotageRewardPosition

    def incrementQuestProgress(self, questId):
        # Tries to increment progress for questId given
        if self.quest is None:
            print('quest is none')
            return
        if self.questId != questId:
            print('quest id does not match')
            return

        self.progress += 1
        if self.progress >= self.quest.goal:
            self.progress = self.quest.goal

        self.factory.d_setQuestProgress(self.progress)
        self.__attemptCompleteQuest()

    def __attemptCompleteQuest(self):
        # Completes the quest if it is over
        if self.progress >= self.quest.goal:
            # Quest is done
            if not self.completed:
                self.completed = True
                self.factory.setQuestCompleted()

    def removeEntity(self, entity):
        if entity in self.entities:
            self.entities.remove(entity)

    def destroy(self):
        for entity in self.entities:
            entity.requestDelete()

        self.entities = []
        self.quest = None
        self.factory = None
        self.air = None

