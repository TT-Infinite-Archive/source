from pandac.PandaModules import *
from toontown.prologue.FloatingObject import FloatingObject
from direct.showbase.DirectObject import DirectObject
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import TTLocalizer
from direct.interval.IntervalGlobal import *
from direct.gui.DirectGui import *


class Island(FloatingObject, DirectObject):
    def __init__(self, parent):
        DirectObject.__init__(self)
        FloatingObject.__init__(self, parent)
        self.setName('island-%s' % parent.getNumChildren())

        self.atmosphereMusic = None
        self.musicBefore = None
        self.trigger = None
        self.gravityModifier = 0.8
        self.gravityBefore = 0.0
        self.hasLocalToon = False
        self.titleText = None
        self.titleTextSeq = None
        self.islandName = ''
        self.islandNameColor = (1.0, 0.5, 0.4, 1.0)

    def setup(self, atmosphereSize, animationIntensity):
        FloatingObject.setup(self, animationIntensity)

        # Setup the atmosphere trigger
        trigger = CollisionNode(self.getName())
        trigger.setIntoCollideMask(ToontownGlobals.WallBitmask)
        self.trigger = self.attachNewNode(trigger)
        trigger = CollisionSphere(0, 0, 0, atmosphereSize)
        trigger.setTangible(0)
        self.trigger.show()
        self.trigger.node().addSolid(trigger)

        # Accept collisions with the atmosphere trigger
        self.accept('enter%s' % self.getName(), self.__enterAtmosphere)
        self.accept('exit%s' % self.getName(), self.__exitAtmosphere)

        # Setup the title text
        self.titleText = OnscreenText(
            self.islandName, fg=self.islandNameColor, font=ToontownGlobals.getSignFont(), pos=(0, -0.5),
            scale=TTLocalizer.HtitleText, drawOrder=0, mayChange=1)
        self.titleText.hide()

    def destroy(self):
        FloatingObject.destroy(self)
        self.ignore('enter%s' % self.getName())
        self.ignore('exit%s' % self.getName())

        if self.titleText is not None:
            self.titleText.cleanup()
            self.titleText = None

        if self.titleTextSeq is not None:
            self.titleTextSeq.finish()
            self.titleTextSeq = None

    def setAtmosphereMusic(self, before, path):
        self.musicBefore = before
        if self.atmosphereMusic is not None:
            self.atmosphereMusic.stop()
        self.atmosphereMusic = loader.loadMusic(path)

    def setGravityModifier(self, gravityModifier):
        self.gravityModifier = gravityModifier

    def setIslandName(self, name, color):
        self.islandName = name
        self.islandNameColor = color

    def _doTitleText(self):
        self.titleText.setText(self.islandName)
        self.titleText.show()
        self.titleText.setColor(Vec4(*self.islandNameColor))
        self.titleText.clearColorScale()
        self.titleText.setFg(self.islandNameColor)
        self.titleTextSeq = Sequence(Wait(0.1), Wait(4.0),
                                     self.titleText.colorScaleInterval(0.5, Vec4(1.0, 1.0, 1.0, 0.0)),
                                     Func(self.titleText.hide))
        self.titleTextSeq.start()

    def __enterAtmosphere(self, e):
        if self.hasLocalToon:
            return
        self.hasLocalToon = True

        # Does this island have a name?
        if self.islandName != '':
            self._doTitleText()

        # Do we have atmosphere music?
        if self.atmosphereMusic is not None:
            base.playMusic(self.atmosphereMusic, looping=1)

        # Set the gravity
        self.gravityBefore = base.localAvatar.controlManager.currentControls.getGravity(0)
        base.localAvatar.controlManager.currentControls.setGravity(32.174 * self.gravityModifier)

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

        # Did we set the music when we entered?
        if self.atmosphereMusic is not None:
            base.playMusic(self.musicBefore, looping=1)

        # Set the gravity to what it was before
        base.localAvatar.controlManager.currentControls.setGravity(self.gravityBefore)

        pos = base.localAvatar.getPos(render)
        h = base.localAvatar.getH(render)
        s = Sequence(
            Func(base.localAvatar.wrtReparentTo, render),
            Func(base.localAvatar.setPos, pos),
            Func(base.localAvatar.setH, h),
            LerpHprInterval(base.localAvatar, 0.5, (h, 0, 0)),
        )
        s.start()