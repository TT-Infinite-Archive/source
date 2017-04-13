from toontown.hood.HoodAI import HoodAI
from toontown.toonbase import ToontownGlobals
from toontown.suit.DistributedSuitPlannerAI import DistributedSuitPlannerAI


class SZHoodAI(HoodAI):
    def __init__(self, air):
        HoodAI.__init__(self, air,
                        ToontownGlobals.StrikeZone,
                        ToontownGlobals.StrikeZone)

        self.startup()

    def startup(self):
        HoodAI.startup(self)
        self.createSuitPlanner()

    def createSuitPlanner(self):
        suitPlanner = DistributedSuitPlannerAI(self.air, self.zoneId)
        suitPlanner.generateWithRequired(self.zoneId)
        suitPlanner.d_setZoneId(self.zoneId)
        suitPlanner.initTasks()
        self.suitPlanners.append(suitPlanner)
        self.air.suitPlanners[self.zoneId] = suitPlanner
        print 'Suit planner created'