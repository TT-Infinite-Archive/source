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
from toontown.effects.RocketExplosion import RocketExplosion
from direct.actor.Actor import Actor
from direct.distributed import DistributedObject


class TutorialTownLoader(TTTownLoader.TTTownLoader):

    def __init__(self, hood, parentFSM, doneEvent):
        TTTownLoader.TTTownLoader.__init__(self, hood, parentFSM, doneEvent)
        self.streetClass = TutorialStreet.TutorialStreet

        self.prologueIntro = None
        self.islands = []
        self.currentIsland = None
        self.mmPianoLoop = None
        self.rocketTrigger = None
        self.rocketParticleSeq = None
        self.musicFile = 'phase_3.5/audio/bgm/infinite_bgm.ogg'
        self.activityMusicFile = 'phase_3.5/audio/bgm/TC_SZ_activity.ogg'
        self.music = base.loadMusic(self.musicFile)

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
        print 'Loaded TutorialTownLoader'
        TownLoader.TownLoader.load(self, zoneId)
        Suit.loadTutorialSuit()
        dnaFile = 'phase_3.5/dna/tutorial_street.pdna'
        self.createHood(dnaFile, loadStorage=0)
        self.alterDictionaries()
        self.accept(OTPGlobals.ThinkPosHotkey, self.thinkPos)
        # self.loadInfinite()

    def enter(self, zoneId):
        TTTownLoader.TTTownLoader.enter(self, zoneId)

    def enterStreet(self, requestStatus):
        TTTownLoader.TTTownLoader.enterStreet(self, requestStatus)
        base.localAvatar.setCameraFov(52)
        self.music.stop()
        self.ttStreetMusic = loader.loadMusic('phase_3.5/audio/bgm/TC_SZ.ogg')
        self.ttStreetMusic.play()
        self.ttStreetMusic.setLoop(1)
        messenger.send('islands-loaded')

    def exit(self):
        TTTownLoader.TTTownLoader.exit(self)
        self.unloadInfinite()

    def loadBattleAnims(self):
        Toon.loadTutorialBattleAnims()

    def unloadBattleAnims(self):
        Toon.unloadTutorialBattleAnims()

    def alterDictionaries(self):
        zoneId = ZoneUtil.tutorialDict['exteriors'][0]
        self.nodeDict[zoneId] = self.nodeDict[20001]
        del self.nodeDict[20001]

    def enterIntroduction(self):
        nametag2d = render2d.findAllMatches('**/Nametag2d')
        nametag2d.hide()

        self.label.setText(TTLocalizer.PrologueKaldronPresents)
        self.label.setPos(0, self.calcLabelY())
        self.label.reparentTo(aspect2d)

        self.label2.setText(TTLocalizer.PrologueKaldronPresents2)
        self.label2.setPos(0, self.calcLabelY())
        self.label2.reparentTo(aspect2d)

        self.infiniteIntroBGM = loader.loadMusic('phase_3.5/audio/bgm/infinite_intro.ogg')
        self.infiniteDebutBGM = loader.loadMusic('phase_3.5/audio/bgm/infinite_debut.ogg')
        self.infiniteDebutBGM.setLoop(1)
        self.infiniteBGM = loader.loadMusic('phase_3.5/audio/bgm/infinite_bgm.ogg')

        # self.logo = OnscreenImage(
            # parent=base.a2dTopCenter, image='phase_3/maps/toontown-logo.png',
            # scale=(0.9, 1, 0.4), pos=(0, 0, -0.90))
        # self.logo.setTransparency(TransparencyAttrib.MAlpha)

        if self.prologueIntro is not None:
            self.prologueIntro.finish()
            self.prologueIntro = None

        self.prologueIntro = Sequence(
            Func(self.music.stop),
            Func(self.infiniteIntroBGM.play),
            Func(base.transitions.fadeIn, 3),
            Func(base.localAvatar.disableAvatarControls),
            Func(base.localAvatar.detachCamera),
            Func(base.localAvatar.collisionsOff),
            Func(base.localAvatar.stopTrackAnimToSpeed),
            Func(base.localAvatar.stopUpdateSmartCamera),
            Parallel(
                Func(base.camera.setPos, 0, 0, 200),
                Func(base.transitions.fadeIn, 3)),
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
            Wait(2),
            Func(base.transitions.fadeOut, 3),
            Wait(3),
            Func(base.transitions.fadeIn, 3),
            Func(base.localAvatar.attachCamera),
            Func(base.localAvatar.collisionsOn),
            Func(base.localAvatar.startTrackAnimToSpeed),
            Func(base.localAvatar.startUpdateSmartCamera),
            Wait(4),
            Func(base.localAvatar.enableAvatarControls),
            Func(self.infiniteDebutBGM.play)
        )
        self.prologueIntro.start()

    def exitIntroduction(self):
        if self.prologueIntro is not None:
            self.prologueIntro.finish()
            self.prologueIntro = None

        self.label.reparentTo(hidden)
        self.label.setPos(0, 0)
        self.label.setText('')

        self.label2.reparentTo(hidden)
        self.label2.setPos(0, 0)
        self.label2.setText('')

        self.infiniteIntroBGM.stop()
        self.infiniteDebutBGM.stop()
        self.infiniteBGM.stop()

    def loadInfinite(self):
        # We use this space node to put all space objects in it so that we can simulate gravity pulls
        self.space = render.attachNewNode('SpaceNode')
        self.enterIntroduction()
        self.startInfiniteLowGravity()

        render.setColorScale(0.4, 0.4, 0.45, 1)
        base.camLens.setNearFar(ToontownGlobals.InfiniteCameraNear, ToontownGlobals.InfiniteCameraFar)

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

        # Toontown Central Plaza Island
        island = Island(self.space)
        island.setPosHpr(-250, -135, 0, 140, 35, 0)
        island.setIslandName('Toontown Central Plaza', (1.0, 0.5, 0.4, 1.0))
        island.setAtmosphereMusic(self.music, 'phase_4/audio/bgm/TC_nbrhood.ogg')
        island.setup(80, 2)
        self.islands.append(island)
        loader.loadModel('phase_4/models/props/infinite_plaza_platform.bam').reparentTo(island)
        islandBuilding = loader.loadModel('phase_4/models/props/infinite_plaza_buildings.bam')
        islandBuilding.setPosHpr(0, -63, -4, 90, 0, 0)
        islandBuilding.reparentTo(island)

        # Melodyland Island
        # Upon entering this island, unload the infinite and show the tutorial street with the flunky. This is the end of the space course.
        island2 = Island(self.space)
        loader.loadModel('phase_6/models/neighborhoods/minnies_melody_land_inf_island.bam').reparentTo(island2)
        island2.setPosHpr(-479, -53, -25, 150, 35, -20)
        island2.setup(130, 2)
        self.islands.append(island2)

        self.mmHQ = FloatingObject(self.space)
        loader.loadModel('phase_6/models/modules/hqMM.bam').reparentTo(self.mmHQ)
        self.mmHQ.setPosHpr(-500, -20, 0, 205, -25, -30)
        self.mmHQ.setup(3)

        self.mmPiano = FloatingObject(self.space)
        loader.loadModel('phase_6/models/props/MM_Piano.bam').reparentTo(self.mmPiano)
        self.mmPiano.setPosHpr(-475, 0, -20, 0, 0, 0)
        self.mmPiano.setup(3)
        self.mmPianoLoop = self.mmPiano.hprInterval(220, Vec3(360, 0, 0))
        self.mmPianoLoop.loop()

        # The Harbor Boat
        ddBoat = Island(self.space)
        loader.loadModel('phase_6/models/modules/donalds_boat.bam').reparentTo(ddBoat)
        ddBoat.setPosHpr(-340, -135, 50, 215, 0, -65)
        ddBoat.setup(20, 4)
        self.islands.append(ddBoat)

        # Key Blade
        self.keyblade = FloatingObject(self.space)
        loader.loadModel('phase_3.5/models/props/kh_key_blade.bam').reparentTo(self.keyblade)
        self.keyblade.setPosHpr(-63, 21, 3, 50, -45, 55)
        self.keyblade.setScale(0.2)
        self.keyblade.setup(1)

        # Rocket
        self.launchPadModel = loader.loadModel('phase_13/models/parties/launchPad.bam')
        self.launchPadModel.setH(90.0)
        self.launchPadModel.setPos(0.0, -18.0, 0.0)
        self.launchPadModel.reparentTo(hidden)
        railingsCollection = self.launchPadModel.findAllMatches('**/launchPad_mesh/*railing*')
        for i in xrange(railingsCollection.getNumPaths()):
            railingsCollection[i].setAttrib(AlphaTestAttrib.make(RenderAttrib.MGreater, 0.75))
        self.rocketActor = Actor('phase_13/models/parties/rocket_model.bam',
                                 {'launch': 'phase_13/models/parties/rocket_launch.bam'})
        rocketLocator = self.launchPadModel.find('**/rocket_locator')
        self.rocketActor.reparentTo(render)
        self.rocketActor.setPosHpr(75, 0, -1, 140, 0, 0)
        self.rocketActor.node().setBound(OmniBoundingVolume())
        self.rocketActor.node().setFinal(True)
        effectsLocator = self.rocketActor.find('**/joint1')
        self.rocketExplosionEffect = RocketExplosion(effectsLocator, rocketLocator)
        self.rocketParticleSeq = None
        self.launchSound = loader.loadSfx('phase_13/audio/sfx/rocket_launch.ogg')

        # Attempting to create this collision sphere a distributed object but having trouble ~ Markgasus
        self.rocketTriggerEvent = self.uniqueName('rocketTriggerEvent')

        # Collision Sphere around the area where the cutscene is
        self.cutsceneSite = render.attachNewNode('cutsceneSite')
        cn = CollisionNode(self.rocketTriggerEvent)
        cn.setIntoCollideMask(ToontownGlobals.WallBitmask)
        self.cutsceneSphere = self.cutsceneSite.attachNewNode(cn)
        self.cutsceneSphere.setPos(75, 0, 1)
        cs = CollisionSphere(0, 0, 0, 10)
        cs.setTangible(0)
        self.cutsceneSphere.node().addSolid(cs)
        self.cutsceneSphere.show()

        # Accept collisions with the rocket trigger
        self.accept('enter%s' % self.rocketTriggerEvent, self.__enterRocket)
        print 'Hey that tickles!'
        # self.accept('exit%s' % self.__exitRocket)

        # PlacerTool3D(model, increment=5)

    def __enterRocket(self):
        # Rocket cutscene starts here
        print 'Hey that tickles'
        self.launchRocket()

    def launchRocket(self):
        self.rocketParticleSeq = Sequence(Wait(2), Func(base.playSfx, self.launchSound),
                                          Func(self.rocketExplosionEffect.start), Wait(2),
                                          LerpHprInterval(self.rocketActor, 4.0, Vec3(0, 0, -60)),
                                          Func(self.rocketExplosionEffect.end), Func(self.rocketActor.hide))
        self.rocketParticleSeq.start()
        self.rocketActor.play('launch')

    def unloadInfinite(self):
        self.infiniteSky.removeNode()
        self.space.removeNode()
        self.rocketParticleSeq = None

        if self.mmPianoLoop:
            self.mmPianoLoop.finish()
            self.mmPianoLoop = None

        if self.rocketParticleSeq:
            self.rocketParticleSeq.pause()
            self.rocketParticleSeq = None

        self.launchPadModel.removeNode()
        del self.launchPadModel
        self.rocketActor.delete()
        self.rocketExplosionEffect.destroy()

    def startInfiniteLowGravity(self):
        base.localAvatar.controlManager.currentControls.setGravity(32.174 * 0.8)

    def stopInfiniteLowGravity(self):
        base.localAvatar.controlManager.currentControls.setGravity(32.174 * 2.0)

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
