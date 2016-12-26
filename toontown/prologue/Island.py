from pandac.PandaModules import *
from direct.showbase.DirectObject import DirectObject
from toontown.toonbase import ToontownGlobals
from direct.interval.IntervalGlobal import *

class Island(NodePath, DirectObject):
    def __init__(self, parent):
        DirectObject.__init__(self)
        NodePath.__init__(self, 'island-%s' % parent.getNumChildren())
        self.reparentTo(parent)

        self.atmosphereMusic = None
        self.trigger = None
        self.gravityModifier = 0.1
        self.hasLocalToon = False

    def setup(self, atmosphereSize, animationIntensity):
        # Setup the atmosphere trigger
        trigger = CollisionNode(self.getName())
        trigger.setIntoCollideMask(ToontownGlobals.WallBitmask)
        self.trigger = self.attachNewNode(trigger)
        trigger = CollisionSphere(0, 0, 0, atmosphereSize)
        trigger.setTangible(0)
        self.trigger.node().addSolid(trigger)

        # Accept collisions with the atmosphere trigger
        self.accept('enter%s' % self.getName(), self.__enterAtmosphere)
        self.accept('exit%s' % self.getName(), self.__exitAtmosphere)

        # Setup the animation for this island
        pos = self.getPos()
        self.animation = Sequence(
            LerpPosInterval(
                self,
                duration=8,
                pos=pos + Point3(0, 0, animationIntensity),
                blendType='easeInOut'
            ),
            LerpPosInterval(
                self,
                duration=8,
                pos=pos,
                blendType='easeInOut'
            ),
            name="upDown"
        )
        self.animation.loop()

    def destroy(self):
        self.removeNode()
        self.ignore('enter%s' % self.getName())
        self.ignore('exit%s' % self.getName())

        self.animation.finish()
        self.animation = None

    def setAtmosphereMusic(self, path):
        self.atmosphereMusic = loader.loadMusic(path)

    def setGravityModifier(self, gravityModifier):
        self.gravityModifier = gravityModifier

    def __enterAtmosphere(self, e):
        if self.hasLocalToon:
            return
        self.hasLocalToon = True

        pos = base.localAvatar.getPos(self)
        h = base.localAvatar.getH(self)
        s = Sequence(
            Func(base.localAvatar.wrtReparentTo, self),
            Func(base.localAvatar.setPos, pos),
            Func(base.localAvatar.setH, h),
            LerpHprInterval(base.localAvatar, 0.5, (h, 0, 0)),
        )
        s.start()

    def __exitAtmosphere(self, e):
        self.hasLocalToon = False

        pos = base.localAvatar.getPos(render)
        h = base.localAvatar.getH(render)
        s = Sequence(
            Func(base.localAvatar.wrtReparentTo, render),
            Func(base.localAvatar.setPos, pos),
            Func(base.localAvatar.setH, h),
            LerpHprInterval(base.localAvatar, 0.5, (h, 0, 0)),
        )
        s.start()