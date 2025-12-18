from panda3d.core import ConfigVariableBool
from toontown.classicchars import DistributedDonaldAI
from toontown.hood import HoodAI
from toontown.safezone import DistributedTrolleyAI
from toontown.toonbase import ToontownGlobals
from toontown.ai import DistributedResistanceEmoteMgrAI


class DLHoodAI(HoodAI.HoodAI):
    def __init__(self, air):
        HoodAI.HoodAI.__init__(self, air,
                               ToontownGlobals.DonaldsDreamland,
                               ToontownGlobals.DonaldsDreamland)

        self.trolley = None
        self.classicChar = None

        self.startup()

    def startup(self):
        HoodAI.HoodAI.startup(self)

        if ConfigVariableBool('want-minigames', True).getValue():
            self.createTrolley()
        if ConfigVariableBool('want-classic-chars', True).getValue():
            if ConfigVariableBool('want-donald-dreamland', True).getValue():
                self.createClassicChar()
        
        self.resistanceEmoteManager = DistributedResistanceEmoteMgrAI.DistributedResistanceEmoteMgrAI(self.air)
        self.resistanceEmoteManager.generateWithRequired(9720)

    def createTrolley(self):
        self.trolley = DistributedTrolleyAI.DistributedTrolleyAI(self.air)
        self.trolley.generateWithRequired(self.zoneId)
        self.trolley.start()

    def createClassicChar(self):
        self.classicChar = DistributedDonaldAI.DistributedDonaldAI(self.air)
        self.classicChar.generateWithRequired(self.zoneId)
        self.classicChar.start()

    def shutdown(self):
        if self.resistanceEmoteManager:
            self.resistanceEmoteManager.requestDelete()
            self.resistanceEmoteManager = None

        HoodAI.HoodAI.shutdown(self)
