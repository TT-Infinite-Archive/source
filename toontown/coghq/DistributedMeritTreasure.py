from pandac.PandaModules import Point3

from direct.interval.IntervalGlobal import *

from toontown.safezone.DistributedTreasure import DistributedTreasure
from toontown.coghq import SuitTreasureGlobals


class DistributedMeritTreasure(DistributedTreasure):
    def __init__(self, cr):
        DistributedTreasure.__init__(self, cr)

        self.treasureFlyTrack = None
        self.finalPos = (0, 0, 0)
        self.meritValue = 0

    def loadModel(self):
        modelPath = SuitTreasureGlobals.TreasureModels[self.treasureType]
        model = loader.loadModel(modelPath)
        model.setScale(2.0)

        self.grabSound = loader.loadSfx('phase_4/audio/sfx/SZ_DD_treasure.ogg')
        self.rejectSound = loader.loadSfx(self.rejectSoundPath)

        if self.nodePath is None:
            self.makeNodePath()
        else:
            self.treasure.getChildren().detach()

        model.instanceTo(self.treasure)
        model.setBillboardAxis()
        self.dropShadow.hide()

        # We will hide the nodePath since we don't want merits to be visible when we generate it
        self.nodePath.hide()


    def setFinalPosition(self, x, y, z):
        self.finalPos = (x, y, z)

    def playDropTrack(self):
        if self.nodePath is None:
            self.makeNodePath()

        # We hide this in loadModel so we need to show it if we're going to make it jump
        self.nodePath.show()

        if self.treasureFlyTrack:
            self.treasureFlyTrack.finish()
            self.treasureFlyTrack = None

        lerpTime = 1
        centerPoint = Point3(0, 0, 0)
        dropSound = loader.loadSfx('phase_4/audio/sfx/MG_maze_pickup.ogg')
        self.treasureFlyTrack = Sequence(
            Func(self.collNodePath.stash),
            Parallel(
                ProjectileInterval(self.treasure, centerPoint, centerPoint, lerpTime, gravityMult=2.0),
                LerpPosInterval(self.nodePath, lerpTime, Point3(*self.finalPos), startPos=self.nodePath.getPos()),
                SoundInterval(dropSound, node=self.nodePath)
            ),
            Func(self.collNodePath.unstash),
            Func(self.d_requestGrabberGrab)
        )
        self.treasureFlyTrack.start()

    def d_requestGrabberGrab(self):
        self.sendUpdate('requestGrabberGrab', [])
