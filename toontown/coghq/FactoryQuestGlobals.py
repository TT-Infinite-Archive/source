from toontown.toonbase.TTLocalizer import FactoryQuestDescriptions, FactoryQuestNames, FactoryQuestProgressString
import random

class FactoryQuest:
    def __init__(self, name, questId, description, goal, progressString, treasureCount, treasureValue):
        self.name = name
        self.questId = questId
        self.description = description
        self.goal = goal
        self.progressString = progressString
        self.treasureCount = treasureCount
        self.treasureValue = treasureValue

    def getReward(self):
        return self.treasureCount * self.treasureValue



FQSabotageId = 0
FQRescueId = 1
FQLootId = 2

FQSabotage = FactoryQuest(FactoryQuestNames[FQSabotageId],
                          FQSabotageId,
                          FactoryQuestDescriptions[FQSabotageId],
                          7,
                          FactoryQuestProgressString[FQSabotageId],
                          10, 10)
FQRescue = FactoryQuest(FactoryQuestNames[FQRescueId],
                        FQRescueId,
                        FactoryQuestDescriptions[FQRescueId],
                        1,
                        FactoryQuestProgressString[FQRescueId],
                        10, 10)
FQLoot = FactoryQuest(FactoryQuestNames[FQLootId],
                      FQLootId,
                      FactoryQuestDescriptions[FQLootId],
                      1,
                      FactoryQuestProgressString[FQLootId],
                      10, 10)

FactoryQuests = {
    FQSabotageId: FQSabotage,
    FQRescueId: FQRescue,
    FQLootId: FQLoot
}

FQBarrelPositions = [
    [-33.488,  162.215,  3.751, 112, 0.0, 0.0],  # Front Entrance second room
    [19.570,  343.650,  58.646, 181, 0.0, 0.0],  # Warehouse view area no one goes to
    [-456.337,  351.912,  18.751, 232, 0.0, 0.0],  # Room after side entrance with stompers
    [-656.328,  628.239,  8.752, 6, 0.0, 0.0],  # Lava room
    [78.623,  649.364,  48.751, 38, 0.0, 0.0],  # East silo elevator where no one goes to
    [218.451,  234.234,  8.708, 227, 0.0, 0.0]  # Gear room
]
FQRescueNPCPositions = [
    [-656.152,  627.320,  8.751, 179.248, 0.0, 0.0],  # Lava room
    [322.935,  324.571,  18.751, -269.743, 0.0, 0.0]  # Paint room
]
FQSabotageRewardPosition = [6, 472, 29]

FQRescuePossibleNPCs = [5207, 5313, 5317]

def getRandomQuestId():
    return random.choice(FactoryQuests.keys())
