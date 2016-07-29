from toontown.hood.HoodAI import HoodAI
from toontown.toonbase import ToontownGlobals


class RGHoodAI(HoodAI):
    def __init__(self, air):
        HoodAI.__init__(self, air,
                        ToontownGlobals.ResistanceGrounds,
                        ToontownGlobals.ResistanceGrounds)

        self.startup()

    def startup(self):
        HoodAI.startup(self)