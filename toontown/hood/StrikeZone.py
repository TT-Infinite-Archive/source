from panda3d.core import Fog

from toontown.coghq.StrikeZoneCogHQLoader import StrikeZoneCogHQLoader
from toontown.toonbase import ToontownGlobals
from toontown.hood.CogHood import CogHood
from otp.otpbase.OTPGlobals import DefaultCameraFov
from panda3d.core import Vec4, Filename
from toontown.battle import BattleParticles
from toontown.hood import SkyUtil
from direct.actor import Actor
from toontown.util.PlacerTool3D import PlacerTool3D


class StrikeZone(CogHood):
    notify = directNotify.newCategory('StrikeZone')

    ID = ToontownGlobals.StrikeZone
    LOADER_CLASS = StrikeZoneCogHQLoader
    STORAGE_DNA = 'phase_6/dna/storage_SZ.pdna'
    SKY_FILE = 'phase_3.5/models/props/TT_sky'
    TITLE_COLOR = (0.5, 0.5, 0.5, 1.0)

    def __init__(self, parentFSM, doneEvent, dnaStore, hoodId):
        CogHood.__init__(self, parentFSM, doneEvent, dnaStore, hoodId)

        self.rain = None
        self.rainRender = None

    def load(self, *args):
        CogHood.load(self)
        self.fog = Fog('GSZFog')
        self.startRain()
        SkyUtil.startCloudSky(self)
        self.sky.setScale(3)
        base.localAvatar.setCameraFov(ToontownGlobals.CogHQCameraFov)
        base.camLens.setNearFar(ToontownGlobals.StrikeZoneCameraNear, ToontownGlobals.StrikeZoneCameraFar)

        render.setColorScale(Vec4(0.55, 0.35, 0.35, 1))

        if __debug__:
            skyblue2Filename = Filename('../resources/phase_3.5/maps/skyblue2_invasion.jpg')
            middayskyBFilename = Filename('../resources/phase_3.5/maps/middayskyB_invasion.jpg')
            toontown_central_tutorial_palette_4amla_1Filename = Filename(
                '../resources/phase_3.5/maps/toontown_central_tutorial_palette_4amla_1_invasion.jpg')
            toontown_central_tutorial_palette_4amla_1_aFilename = Filename(
                '../resources/phase_3.5/maps/toontown_central_tutorial_palette_4amla_1_a_invasion.rgb')
        else:
            skyblue2Filename = Filename('/phase_3.5/maps/skyblue2_invasion.jpg')
            middayskyBFilename = Filename('/phase_3.5/maps/middayskyB_invasion.jpg')
            toontown_central_tutorial_palette_4amla_1Filename = Filename(
                '/phase_3.5/maps/toontown_central_tutorial_palette_4amla_1_invasion.jpg')
            toontown_central_tutorial_palette_4amla_1_aFilename = Filename(
                '/phase_3.5/maps/toontown_central_tutorial_palette_4amla_1_a_invasion.rgb')

        self.sky.findTexture('skyblue2').read(skyblue2Filename)
        self.sky.findTexture('middayskyB').read(middayskyBFilename)
        self.sky.findTexture('toontown_central_tutorial_palette_4amla_1').read(
            toontown_central_tutorial_palette_4amla_1Filename, toontown_central_tutorial_palette_4amla_1_aFilename, 0,
            0)

        self.hqTelescope = Actor.Actor('phase_4/models/corpstrike/hqTT_telescope_ost', {'animation': 'phase_4/models/corpstrike/hqTT_telescope_ost'})
        self.hqTelescope.loop('animation')
        self.hqTelescope.reparentTo(render)
        self.hqTelescope.setPosHpr(20.5, 29, 16.7, -70, 0, 0)

        # self.statue = loader.loadModel('phase_4/models/corpstrike/pns_statue_body')
        # self.statue.reparentTo(render)
        # PlacerTool3D(self.statue, increment=1)

        # self.painting = loader.loadModel('phase_4/models/corpstrike/gov_philip_painting')
        # self.painting.reparentTo(render)
        # PlacerTool3D(self.painting, increment=1)

        # self.painting2 = loader.loadModel('phase_4/models/corpstrike/gov_philip_painting')
        # self.painting2.reparentTo(render)
        # PlacerTool3D(self.painting2, increment=1)

    def skyTrack(self, task):
        return SkyUtil.cloudSkyTrack(task)

    def unload(self):
        self.stopRain()
        del self.rain
        del self.rainRender

        self.sky.setScale(1)
        self.hqTelescope.removeNode()
        del self.hqTelescope
        self.hqTelescope = None

        if __debug__:
            skyblue2Filename = Filename('../resources/phase_3.5/maps/skyblue2.jpg')
            middayskyBFilename = Filename('../resources/phase_3.5/maps/middayskyB.jpg')
            toontown_central_tutorial_palette_4amla_1Filename = Filename(
                '../resources/phase_3.5/maps/toontown_central_tutorial_palette_4amla_1.jpg')
            toontown_central_tutorial_palette_4amla_1_aFilename = Filename(
                '../resources/phase_3.5/maps/toontown_central_tutorial_palette_4amla_1_a.rgb')
        else:
            skyblue2Filename = Filename('/phase_3.5/maps/skyblue2.jpg')
            middayskyBFilename = Filename('/phase_3.5/maps/middayskyB.jpg')
            toontown_central_tutorial_palette_4amla_1Filename = Filename(
                '/phase_3.5/maps/toontown_central_tutorial_palette_4amla_1.jpg')
            toontown_central_tutorial_palette_4amla_1_aFilename = Filename(
                '/phase_3.5/maps/toontown_central_tutorial_palette_4amla_1_a.rgb')

        self.sky.findTexture('skyblue2').read(skyblue2Filename)
        self.sky.findTexture('middayskyB').read(middayskyBFilename)
        self.sky.findTexture('toontown_central_tutorial_palette_4amla_1').read(
            toontown_central_tutorial_palette_4amla_1Filename, toontown_central_tutorial_palette_4amla_1_aFilename, 0,
            0)

        CogHood.exit(self)
        base.localAvatar.setCameraFov(DefaultCameraFov)

    def startRain(self):
        self.rain = BattleParticles.loadParticleFile('raindisk.ptf')
        self.rain.setPos(0, 0, 20)
        self.rainRender = render.attachNewNode('rainRender')
        self.rainRender.setDepthWrite(0)
        self.rainRender.setBin('fixed', 1)
        self.rain.start(camera, self.rainRender)

    def stopRain(self):
        if self.rain:
            self.rain.cleanup()

    def processTime(self):
        pass