from toontown.safezone import DistributedTreasure
from toontown.toonbase import ToontownGlobals
from direct.interval.IntervalGlobal import *
from pandac.PandaModules import Point3


class DistributedCashbotBossTreasure(DistributedTreasure.DistributedTreasure):

    def __init__(self, cr):
        DistributedTreasure.DistributedTreasure.__init__(self, cr)

    def setGoonId(self, goonId):
        self.goonId = goonId

    def setFinalPosition(self, x, y, z):
        if not self.nodePath:
            self.makeNodePath()
        if self.treasureFlyTrack:
            self.treasureFlyTrack.finish()
            self.treasureFlyTrack = None
        startPos = None
        goon = self.cr.doId2do[self.goonId]
        if goon:
            startPos = goon.getPos()
        lerpTime = 1
        self.treasureFlyTrack = Sequence(
            Func(self.collNodePath.stash),
            Parallel(
                ProjectileInterval(self.treasure, startPos=Point3(0, 0, 0), endPos=Point3(0, 0, 0), duration=lerpTime, gravityMult=2.0),
                LerpPosInterval(self.nodePath, lerpTime, Point3(x, y, z), startPos=startPos)
            ),
            Func(self.collNodePath.unstash)
        )
        self.treasureFlyTrack.start()
        return
