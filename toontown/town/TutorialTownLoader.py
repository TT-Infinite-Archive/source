import TownLoader
import TTTownLoader
import TutorialStreet
from toontown.suit import Suit
from toontown.toon import Toon
from toontown.hood import ZoneUtil
from direct.gui.DirectGui import *
from direct.interval.IntervalGlobal import *
from toontown.battle.BattleProps import *
from toontown.toonbase import TTLocalizer
from toontown.toonbase import ToontownGlobals
from direct.interval.IntervalGlobal import Sequence, Parallel, Wait, Func
from panda3d.core import Vec3


class TutorialTownLoader(TTTownLoader.TTTownLoader):

    def __init__(self, hood, parentFSM, doneEvent):
        TTTownLoader.TTTownLoader.__init__(self, hood, parentFSM, doneEvent)
        self.streetClass = TutorialStreet.TutorialStreet

        self.infiniteSkyLoop = None
        self.prologueIntro = None
        self.musicFile = 'phase_4/audio/bgm/ttc_storm_bgm.ogg'
        self.activityMusicFile = 'phase_3/audio/bgm/toontown_infinite_prologue_1.ogg'

        font = ToontownGlobals.getMinnieFont()

        self.label = OnscreenText(
            '', parent=hidden, font=font, fg=Vec4(1, 1, 1, 1), scale=0.06,
            align=TextNode.ACenter, wordwrap=35)
        self.label.setColorScale(Vec4(0, 0, 0, 0))

        self.label2 = OnscreenText(
            '', parent=hidden, font=font, fg=Vec4(1, 1, 1, 1), scale=0.06,
            align=TextNode.ACenter, wordwrap=35)
        self.label2.setColorScale(Vec4(0, 0, 0, 0))

    def load(self, zoneId):
        TownLoader.TownLoader.load(self, zoneId)
        Suit.loadTutorialSuit()
        dnaFile = 'phase_3.5/dna/tutorial_street.pdna'
        self.createHood(dnaFile, loadStorage=0)
        self.alterDictionaries()

        self.loadInfiniteSky()
        self.startInfiniteLowGravity()
        self.enterIntroduction()
        self.logo.hide()

    def enter(self, zoneId):
        TTTownLoader.TTTownLoader.enter(self, zoneId)
        render.setColorScale(0.3, 0.2, 0.2, 1)


    def exit(self):
        self.unloadInfiniteSky()
        self.stopInfiniteLowGravity()
        TTTownLoader.TTTownLoader.exit(self)

    def loadInfiniteSky(self):
        self.infiniteSky = loader.loadModel('phase_3.5/models/props/Infinite_sky.bam')
        self.infiniteSky.reparentTo(render)
        self.infiniteSkyLoop = self.infiniteSky.hprInterval(200, Vec3(360, 0, 0))
        self.infiniteSkyLoop.loop()

    def unloadInfiniteSky(self):
        self.infiniteSky.removeNode()

        if self.infiniteSkyLoop:
            self.infiniteSkyLoop.finish()
            self.infiniteSkyLoop = None

    def loadBattleAnims(self):
        Toon.loadTutorialBattleAnims()

    def unloadBattleAnims(self):
        Toon.unloadTutorialBattleAnims()

    def alterDictionaries(self):
        zoneId = ZoneUtil.tutorialDict['exteriors'][0]
        self.nodeDict[zoneId] = self.nodeDict[20001]
        del self.nodeDict[20001]

    def startInfiniteLowGravity(self):
        base.localAvatar.controlManager.currentControls.setGravity(32.174 * 1)

    def stopInfiniteLowGravity(self):
        base.localAvatar.controlManager.currentControls.setGravity(32.174 * 2.0)

    def enterIntroduction(self):

        self.label.setText(TTLocalizer.PrologueKaldronPresents)
        self.label.setPos(0, self.calcLabelY())
        self.label.reparentTo(aspect2d)
        
        self.label2.setText(TTLocalizer.PrologueKaldronPresents2)
        self.label2.setPos(0, self.calcLabelY())
        self.label2.reparentTo(aspect2d)

        self.logo = OnscreenImage(
            parent=base.a2dTopCenter, image='phase_3/maps/toontown-logo.png',
            scale=(0.9, 1, 0.4), pos=(0, 0, -0.90))
        self.logo.setTransparency(TransparencyAttrib.MAlpha)

        if self.prologueIntro is not None:
            self.prologueIntro.finish()
            self.prologueIntro = None

        self.prologueIntro = Sequence(
            Func(base.camera.setPos, 0, 0, 100),
            Wait(8),
            LerpColorScaleInterval(
                self.label, 2, Vec4(1, 1, 1, 1), Vec4(0, 0, 0, 0),
                blendType='easeIn'),
            Wait(6),
            LerpColorScaleInterval(
                self.label, 2, Vec4(0, 0, 0, 0), Vec4(1, 1, 1, 1),
                blendType='easeOut'),
            Wait(1),
            LerpColorScaleInterval(
                self.label2, 2, Vec4(1, 1, 1, 1), Vec4(0, 0, 0, 0),
                blendType='easeIn'),
            Wait(8),
            LerpColorScaleInterval(
                self.label2, 2, Vec4(0, 0, 0, 0), Vec4(1, 1, 1, 1),
                blendType='easeOut'),
            Wait(5),
            LerpPosHprInterval(base.camera, 6, Vec3(0, 0, 100), Vec3(0, 0, 0),
                               Vec3(0, 0, -200), Vec3(0, 0, 0), blendType='easeInOut'),
            #Func(self.exitIntroduction())
        )
        self.prologueIntro.start()

    def exitIntroduction(self):
        base.cr.playGame.getPlace().enterWalk()
        if self.prologueIntro is not None:
            self.prologueIntro.finish()
            self.prologueIntro = None

        self.label.reparentTo(hidden)
        self.label.setPos(0, 0)
        self.label.setText('')

        self.label2.reparentTo(hidden)
        self.label2.setPos(0, 0)
        self.label2.setText('')

    def calcLabelY(self):
        sy = self.label.getScale()[1]
        height = self.label.textNode.getHeight()
        return (height * sy) / 2.0