from panda3d.core import Vec4, Fog

from toontown.safezone.SZSafeZoneLoader import SZSafeZoneLoader
from toontown.toonbase import ToontownGlobals
from toontown.hood.ToonHood import ToonHood
from otp.otpbase.OTPGlobals import DefaultCameraFov

class SZHood(ToonHood):
    notify = directNotify.newCategory('SZHood')

    ID = ToontownGlobals.StrikeZone
    SAFEZONELOADER_CLASS = SZSafeZoneLoader
    STORAGE_DNA = 'phase_6/dna/storage_SZ.pdna'
    SKY_FILE = 'phase_3.5/models/props/TT_sky'
    SPOOKY_SKY_FILE = 'phase_3.5/models/props/BR_sky'
    TITLE_COLOR = (0.38, 0.79, 0.31, 1.0)

    HOLIDAY_DNA = {}

    def __init__(self, parentFSM, doneEvent, dnaStore, hoodId):
        ToonHood.__init__(self, parentFSM, doneEvent, dnaStore, hoodId)

    def startSky(self):
        ToonHood.startSky(self)
        self.sky.setScale(4.0)

    def enter(self, requestStatus):
        ToonHood.enter(self, requestStatus)
        base.localAvatar.setCameraFov(ToontownGlobals.CogHQCameraFov)

        render.setColorScale(Vec4(0.55, 0.35, 0.35, 1))

        base.cr.shardTimeManager.setCurrentTime(1000)

    def processTime(self):
        pass

    def exit(self):
        ToonHood.exit(self)
        base.localAvatar.setCameraFov(DefaultCameraFov)

    def load(self):
        ToonHood.load(self)
        self.fog = Fog('SZFog')