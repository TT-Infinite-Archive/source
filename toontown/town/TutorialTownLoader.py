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


class TutorialTownLoader(TTTownLoader.TTTownLoader):

    def __init__(self, hood, parentFSM, doneEvent):
        TTTownLoader.TTTownLoader.__init__(self, hood, parentFSM, doneEvent)
        self.streetClass = TutorialStreet.TutorialStreet

        self.infiniteSkyLoop = None
        self.prologueIntro = None
        self.environmentSequences = []
        self.musicFile = 'phase_4/audio/bgm/ttc_storm_bgm.ogg'
        self.activityMusicFile = ''

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
        self.enterIntroduction()
        self.logo.hide()
        self.accept(OTPGlobals.ThinkPosHotkey, self.thinkPos)

    def enter(self, zoneId):
        TTTownLoader.TTTownLoader.enter(self, zoneId)
        render.setColorScale(0.3, 0.2, 0.2, 1)
        # base.cr.playGame.getPlace().exitWalk()


    def exit(self):
        self.loadInfinite()
        self.stopInfiniteLowGravity()
        TTTownLoader.TTTownLoader.exit(self)

    def loadInfinite(self):

        # Spaaaaaaace

        self.infiniteSky = loader.loadModel('phase_3.5/models/props/Infinite_sky.bam')
        self.infiniteSky.reparentTo(render)
        self.infiniteSkyLoop = self.infiniteSky.hprInterval(300, Vec3(360, 0, 0))
        self.infiniteSkyLoop.loop()

        # Floating objects!

        self.tutorialStreet = loader.loadModel('phase_3.5/models/props/tutorial_street.bam')
        self.tutorialStreet.reparentTo(render)
        self.tutorialStreet.setPosHpr(-229, -53, 5, 150, 35, -20)
        self.tutorialStreet.setScale(0.5)


        tutorialStreetPosInterval1 = LerpPosInterval(self.tutorialStreet,
                                                  duration=9,
                                                  pos=Point3(-229, -53, 6),
                                                  startPos=Point3(-229, -53, 0),
                                                  blendType='easeInOut')

        tutorialStreetPosInterval2 = LerpPosInterval(self.tutorialStreet,
                                                  duration=9,
                                                  pos=Point3(-229, -53, 0),
                                                  startPos=Point3(-229, -53, 6),
                                                  blendType='easeInOut')

        self.environmentSequences.append(self.tutorialStreet)

        self.tutorialStreetPace = Sequence(tutorialStreetPosInterval1,
                                        tutorialStreetPosInterval2,
                                        name="tutorialStreetPace")

        self.tutorialStreetPace.loop()

        self.keyBlade = loader.loadModel('phase_3.5/models/props/kh_key_blade.bam')
        self.keyBlade.reparentTo(render)
        self.keyBlade.setPosHpr(-63, 21, 3, 50, -45, 55)
        self.keyBlade.setScale(0.2)
        PlacerTool3D(self.keyBlade, increment=3)


        keyBladePosInterval1 = LerpPosInterval(self.keyBlade,
                                                  duration=6,
                                                  pos=Point3(-63, 21, 4),
                                                  startPos=Point3(-63, 21, 2),
                                                  blendType='easeInOut')

        keyBladePosInterval2 = LerpPosInterval(self.keyBlade,
                                                  duration=6,
                                                  pos=Point3(-63, 21, 2),
                                                  startPos=Point3(-63, 21, 4),
                                                  blendType='easeInOut')

        self.environmentSequences.append(self.keyBlade)

        self.keyBladePace = Sequence(keyBladePosInterval1,
                                        keyBladePosInterval2,
                                        name="keyBladePace")

        self.keyBladePace.loop()



        # self.plazaPlatform = loader.loadModel('')

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
        base.localAvatar.controlManager.currentControls.setGravity(32.174 * 1)

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