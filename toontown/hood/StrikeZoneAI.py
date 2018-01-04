from toontown.hood.CogHQAI import CogHQAI
from toontown.toonbase import ToontownGlobals
from toontown.suit.DistributedSuitPlannerAI import DistributedSuitPlannerAI
from toontown.strike.CorporateStrikeManagerAI import CorporateStrikeManagerAI
from toontown.strike import StrikeAreaGlobals


class StrikeZoneAI(CogHQAI):
    def __init__(self, air):
        CogHQAI.__init__(
            self, air, ToontownGlobals.StrikeZone, None,
        None, None, None)

        self.suitPlanners = []
        self.startup()

    def startup(self):
        CogHQAI.startup(self)
        self.createSuitPlanner()

        # self.strikeManager = CorporateStrikeManagerAI(self.air)
        # self.strikeManager.registerStrike(StrikeAreaGlobals.STRIKE_BOSS)
        # self.strikeManager.generate(self.zoneId)

    def createSuitPlanner(self):
        suitPlanner = DistributedSuitPlannerAI(self.air, self.zoneId)
        suitPlanner.generateWithRequired(self.zoneId)
        suitPlanner.d_setZoneId(self.zoneId)
        suitPlanner.initTasks()
        self.suitPlanners.append(suitPlanner)
        self.air.suitPlanners[self.zoneId] = suitPlanner
        print 'Suit planner created'

    def createLobbyManager(self):
        pass

    def createLobbyElevator(self):
        pass

    def makeCogHQDoor(self, destinationZone, intDoorIndex, extDoorIndex, lock=0):
        pass

    def createBoardingParty(self):
        pass
