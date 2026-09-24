from direct.directnotify import DirectNotifyGlobal
from . import DistributedMintAI
from toontown.toonbase import ToontownGlobals
from direct.showbase import DirectObject
import random

class MintManagerAI(DirectObject.DirectObject):
    notify = DirectNotifyGlobal.directNotify.newCategory('MintManagerAI')
    mintId = None

    def __init__(self, air):
        DirectObject.DirectObject.__init__(self)
        self.air = air

    def getDoId(self):
        return 0

    def createMint(self, mintId, players):
        floor = random.randrange(ToontownGlobals.MintNumFloors[mintId])
        mintZone = self.air.allocateZone()
        mint = DistributedMintAI.DistributedMintAI(self.air, mintId, mintZone, floor, players)
        mint.generateWithRequired(mintZone)
        return mintZone
