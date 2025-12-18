from panda3d.core import ConfigVariableBool
from toontown.classicchars import DistributedDaisyAI
from toontown.hood import HoodAI
from toontown.safezone import ButterflyGlobals
from toontown.safezone import DistributedDGFlowerAI
from toontown.safezone import DistributedTrolleyAI
from toontown.toonbase import ToontownGlobals
from toontown.ai import DistributedGreenToonEffectMgrAI


class DGHoodAI(HoodAI.HoodAI):
    def __init__(self, air):
        HoodAI.HoodAI.__init__(self, air,
                               ToontownGlobals.DaisyGardens,
                               ToontownGlobals.DaisyGardens)

        self.trolley = None
        self.flower = None
        self.classicChar = None
        self.butterflies = []

        self.startup()

    def startup(self):
        HoodAI.HoodAI.startup(self)

        if ConfigVariableBool('want-minigames', True).getValue():
            self.createTrolley()
        self.createFlower()
        if ConfigVariableBool('want-classic-chars', True).getValue():
            if ConfigVariableBool('want-daisy', True).getValue():
                self.createClassicChar()

    def createTrolley(self):
        self.trolley = DistributedTrolleyAI.DistributedTrolleyAI(self.air)
        self.trolley.generateWithRequired(self.zoneId)
        self.trolley.start()

    def createFlower(self):
        self.flower = DistributedDGFlowerAI.DistributedDGFlowerAI(self.air)
        self.flower.generateWithRequired(self.zoneId)
        self.flower.start()

    def createClassicChar(self):
        self.classicChar = DistributedDaisyAI.DistributedDaisyAI(self.air)
        self.classicChar.generateWithRequired(self.zoneId)
        self.classicChar.start()

    def startupGreenToonManager(self):
        if hasattr(self, 'GreenToonEffectManager'):
            return
        self.GreenToonEffectManager = DistributedGreenToonEffectMgrAI.DistributedGreenToonEffectMgrAI(self.air)
        self.GreenToonEffectManager.generateWithRequired(5819)

    def stopGreenToonManager(self):
        if hasattr(self, 'GreenToonEffectManager'):
            self.GreenToonEffectManager.requestDelete()
            del self.GreenToonEffectManager

    def shutdown(self):
        if hasattr(self, 'flower') and self.flower:
            self.flower.requestDelete()
            self.flower = None

        self.stopGreenToonManager()

        HoodAI.HoodAI.shutdown(self)
