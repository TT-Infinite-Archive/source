from toontown.hood import HoodAI
from toontown.toonbase import ToontownGlobals


class TPHoodAI(HoodAI.HoodAI):
    def __init__(self, air):
        HoodAI.HoodAI.__init__(self, air,
                               ToontownGlobals.ToonPalooza,
                               ToontownGlobals.ToonPalooza)

        self.startup()

    def startup(self):
        HoodAI.HoodAI.startup(self)
