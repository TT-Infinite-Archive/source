from panda3d.core import Vec4, Fog

from toontown.safezone.SZSafeZoneLoader import SZSafeZoneLoader
from toontown.toonbase import ToontownGlobals
from toontown.hood.ToonHood import ToonHood
from otp.otpbase.OTPGlobals import DefaultCameraFov
from panda3d.core import Vec4, Filename
from toontown.battle import BattleParticles

class SZHood(ToonHood):
    notify = directNotify.newCategory('SZHood')

    ID = ToontownGlobals.StrikeZone
    SAFEZONELOADER_CLASS = SZSafeZoneLoader
    STORAGE_DNA = 'phase_6/dna/storage_SZ.pdna'
    SKY_FILE = 'phase_3.5/models/props/TT_sky'
    SPOOKY_SKY_FILE = 'phase_3.5/models/props/BR_sky'
    TITLE_COLOR = (0.5, 0.5, 0.5, 1.0)
    NIGHTSKY_FILE = None
    SUNSKY_FILE = None

    HOLIDAY_DNA = {}

    def __init__(self, parentFSM, doneEvent, dnaStore, hoodId):
        ToonHood.__init__(self, parentFSM, doneEvent, dnaStore, hoodId)

        self.nightSkyFile = self.NIGHTSKY_FILE
        self.sunSkyFile = self.SUNSKY_FILE
        self.titleColor = self.TITLE_COLOR
        self.rain = None
        self.rainRender = None

    def load(self):
        ToonHood.load(self)
        self.fog = Fog('SZFog')
        self.startRain()
        base.localAvatar.setCameraFov(ToontownGlobals.CogHQCameraFov)
        base.camLens.setNearFar(ToontownGlobals.StrikeZoneCameraNear, ToontownGlobals.StrikeZoneCameraFar)

        render.setColorScale(Vec4(0.55, 0.35, 0.35, 1))
        self.sky.setScale(3)

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

    def unload(self):
        self.stopRain()
        del self.rain
        del self.rainRender

        ToonHood.exit(self)
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