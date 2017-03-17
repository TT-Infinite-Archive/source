from toontown.hood.HoodAI import HoodAI
from toontown.toonbase import ToontownGlobals


class CZHoodAI(HoodAI):
    def __init__(self, air):
        HoodAI.__init__(self, air,
                        ToontownGlobals.ConstructionZone,
                        ToontownGlobals.ConstructionZone)

        self.startup()

    def startup(self):
        HoodAI.startup(self)