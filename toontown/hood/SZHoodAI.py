from toontown.hood.HoodAI import HoodAI
from toontown.toonbase import ToontownGlobals


class SZHoodAI(HoodAI):
    def __init__(self, air):
        HoodAI.__init__(self, air,
                        ToontownGlobals.StrikeZone,
                        ToontownGlobals.StrikeZone)

        self.startup()

    def startup(self):
        HoodAI.startup(self)