import TownLoader
import TTTownLoader
import TutorialStreet
from toontown.suit import Suit
from toontown.toon import Toon
from toontown.hood import ZoneUtil
from direct.gui.DirectGui import *
from direct.interval.IntervalGlobal import *
from toontown.toonbase import TTLocalizer
from toontown.toonbase import ToontownGlobals
from direct.interval.IntervalGlobal import Sequence, Parallel, Wait, Func
from pandac.PandaModules import *
from otp.otpbase import OTPGlobals
from toontown.util.PlacerTool3D import PlacerTool3D
from panda3d.core import CollisionNode, CollisionSphere
from toontown.toon import ToonDNA, ToonDNA
from toontown.prologue.Island import Island
from toontown.prologue.FloatingObject import FloatingObject


class TutorialTownLoader(TTTownLoader.TTTownLoader):

    def __init__(self, hood, parentFSM, doneEvent):
        TTTownLoader.TTTownLoader.__init__(self, hood, parentFSM, doneEvent)
        self.streetClass = TutorialStreet.TutorialStreet

        self.infiniteSkyLoop = None
        self.prologueIntro = None
        self.environmentSequences = []
        self.islands = []
        self.musicFile = 'phase_3.5/audio/bgm/infinite_bgm.ogg'
        self.currentIsland = None

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

        self.loadInfinite()
        self.startInfiniteLowGravity()
        # self.enterIntroduction()
        # self.logo.hide()
        self.accept(OTPGlobals.ThinkPosHotkey, self.thinkPos)

    def enter(self, zoneId):
        TTTownLoader.TTTownLoader.enter(self, zoneId)
        render.setColorScale(0.4, 0.4, 0.45, 1)
        base.camLens.setNearFar(ToontownGlobals.InfiniteCameraNear, ToontownGlobals.InfiniteCameraFar)

        dna = ToonDNA.ToonDNA()
        dnaList = ('pls', 'ls', 'l', 'm', 20, 0, 20, 20, 98, 27, 0, 27, 38, 27)
        dna.newToonFromProperties(*dnaList)
        base.localAvatar.setDNA(dna)

        base.localAvatar.setName('Doctor Surlee')
        # base.cr.playGame.getPlace().exitWalk()

        # TODO: Set Surlee's dna color to 9

    def exit(self):
        self.loadInfinite()
        self.stopInfiniteLowGravity()
        TTTownLoader.TTTownLoader.exit(self)

    def loadInfinite(self):
        # We use this space node to put all space objects in it so that we can simulate gravity pulls
        self.space = render.attachNewNode('SpaceNode')

        # Skybox
        self.infiniteSky = loader.loadModel('phase_3.5/models/props/infinite_sky.bam')
        self.infiniteSky.reparentTo(self.space)

        # Plane
        self.infinitePlane = loader.loadModel('phase_3.5/models/props/infinite_plane.bam')
        self.infinitePlane.reparentTo(self.space)
        self.infinitePlane.setPos(0, 0, -800)
        self.infinitePlane.setScale(5)
        self.infinitePlane.hide()

        # Islands

        # Toontown Central Island
        island = Island(self.space)
        loader.loadModel('phase_4/models/props/infinite_plaza_platform.bam').reparentTo(island)
        islandBuilding = loader.loadModel('phase_4/models/props/infinite_plaza_buildings.bam')
        islandBuilding.setPosHpr(0, -63, -4, 90, 0, 0)
        islandBuilding.reparentTo(island)

        island.setPosHpr(-250, -135, 0, 140, 35, 0)
        island.setIslandName('Toontown Central Plaza', (1.0, 0.5, 0.4, 1.0))
        island.setAtmosphereMusic(self.music, 'phase_4/audio/bgm/TC_nbrhood.ogg')
        island.setup(80, 2)
        self.islands.append(island)

        # Tutorial Terrace Island
        island2 = Island(self.space)
        loader.loadModel('phase_3.5/models/props/tutorial_street.bam').reparentTo(island2)
        island2.setPosHpr(-479, -53, -25, 150, 35, -20)
        island2.setup(80, 2)
        self.islands.append(island2)

        # The Docks Island
        ddBoat = Island(self.space)
        loader.loadModel('phase_6/models/modules/donalds_boat.bam').reparentTo(ddBoat)
        ddBoat.setPosHpr(-340, -135, 50, 215, 0, -65)
        ddBoat.setup(20, 4)
        self.islands.append(ddBoat)

        ddPalmtree = FloatingObject(self.space)
        loader.loadModel('phase_6/models/props/palm_tree_topflat.bam').reparentTo(self.space)
        ddPalmtree.setPosHpr(-340, -135, 50, 0, 0, 0)
        ddPalmtree.setup(2)
        self.islands.append(ddPalmtree)

        ddPalmtree2 = FloatingObject(self.space)
        loader.loadModel('phase_6/models/props/palm_tree_topflat.bam').reparentTo(self.space)
        ddPalmtree2.setPosHpr(-340, -135, 50, 0, 0, 0)
        ddPalmtree2.setup(2)
        self.islands.append(ddPalmtree2)

        # trashcan_DD
        # palm_tree_topflat

        # PlacerTool3D(ddPalmtree, increment=5)

        # Misc Objects

        # Key Blade
        self.keyblade = FloatingObject(self.space)
        loader.loadModel('phase_3.5/models/props/kh_key_blade.bam').reparentTo(self.keyblade)
        self.keyblade.setPosHpr(-63, 21, 3, 50, -45, 55)
        self.keyblade.setScale(0.2)
        self.keyblade.setup(1)

        # Meteors

        self.infiniteMeteor = loader.loadModel('phase_3.5/models/props/infinite_meteor.bam')
        self.infiniteMeteor.reparentTo(self.space)
        self.infiniteMeteor.setPosHpr(-190, -90, 40, 0, 0, 0)
        self.infiniteMeteor.setScale(5)

        self.tutorialMeteor = loader.loadModel('phase_3.5/models/props/tutorial_shop_meteor.bam')
        self.tutorialMeteor.reparentTo(self.space)
        self.tutorialMeteor.setPos(-7, 26, -37)
        self.tutorialMeteor.setScale(20)

        # POS INTERVAL

        infiniteMeteorPosInterval1 = LerpPosInterval(
            self.infiniteMeteor,
            duration=10,
            pos=Point3(148.278,  148.132, 25),
            startPos=Point3(-190, -90, 40),
            blendType='easeInOut'
        )

        infiniteMeteorPosInterval2 = LerpPosInterval(
            self.infiniteMeteor,
            duration=10,
            pos=Point3(113.114, -40.519, 25),
            startPos=Point3(148.278,  148.132, 25),
            blendType='easeInOut'
        )

        infiniteMeteorPosInterval3 = LerpPosInterval(
            self.infiniteMeteor,
            duration=10,
            pos=Point3(-190, -90, 40),
            startPos=Point3(113.114, -40.519, 25),
            blendType='easeInOut'
        )

        self.infiniteMeteorPosPace = Sequence(
            infiniteMeteorPosInterval1,
            infiniteMeteorPosInterval2,
            infiniteMeteorPosInterval3,
            name="infiniteMeteorPosPace"
        )

        # HPR INTERVAL

        infiniteMeteorHprInterval1 = LerpHprInterval(
            self.infiniteMeteor,
            duration=10,
            hpr=Vec3(360, 120, 60),
            startHpr=Vec3(0, 0, 0),
            blendType='easeInOut'
        )

        infiniteMeteorHprInterval2 = LerpHprInterval(
            self.infiniteMeteor,
            duration=10,
            hpr=Vec3(0, 0, 0),
            startHpr=Vec3(360, 120, 60),
            blendType='easeInOut'
        )

        self.infiniteMeteorHprPace = Sequence(
            infiniteMeteorHprInterval1,
            infiniteMeteorHprInterval2,
            name="infiniteMeteorHprPace"
        )

        self.environmentSequences.append(self.infiniteMeteor)

        self.infiniteMeteorPosPace.loop()
        self.infiniteMeteorHprPace.loop()

    def unloadInfinite(self):
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
        base.localAvatar.controlManager.currentControls.setGravity(32.174 * 0.8)

    def stopInfiniteLowGravity(self):
        base.localAvatar.controlManager.currentControls.setGravity(32.174 * 2.0)

    def enterIntroduction(self):

        nametag2d = render2d.findAllMatches('**/Nametag2d')
        nametag2d.hide()

        self.label.setText(TTLocalizer.PrologueKaldronPresents)
        self.label.setPos(0, self.calcLabelY())
        self.label.reparentTo(aspect2d)

        self.label2.setText(TTLocalizer.PrologueKaldronPresents2)
        self.label2.setPos(0, self.calcLabelY())
        self.label2.reparentTo(aspect2d)

        self.introductionMusic = loader.loadMusic('phase_3/audio/bgm/toontown_infinite_prologue_1.ogg')
        base.playMusic(self.introductionMusic, looping=0)

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

        self.introductionMusic.stop()

    def calcLabelY(self):
        sy = self.label.getScale()[1]
        height = self.label.textNode.getHeight()
        return (height * sy) / 2.0

    # Only here temporarily for development purposes
    def thinkPos(self):
        pos = base.localAvatar.getPos()
        hpr = base.localAvatar.getHpr()
        serverVersion = base.cr.getServerVersion()
        districtName = base.cr.getShardName(base.localAvatar.defaultShard)
        if hasattr(base.cr.playGame.hood, 'loader') and hasattr(base.cr.playGame.hood.loader, 'place') and base.cr.playGame.getPlace() != None:
            zoneId = base.cr.playGame.getPlace().getZoneId()
        else:
            zoneId = '?'
        strPos = '(%.3f' % pos[0] + '\n %.3f' % pos[1] + '\n %.3f)' % pos[2] + '\nH: %.3f' % hpr[0] + '\nZone: %s' % str(zoneId) + ',\nVer: %s, ' % serverVersion + '\nDistrict: %s' % districtName
        print 'Current position=', strPos.replace('\n', ', ')
        return
