from panda3d.core import Vec4, Fog

from toontown.safezone.RGSafeZoneLoader import RGSafeZoneLoader
from toontown.toonbase import ToontownGlobals
from toontown.hood.ToonHood import ToonHood
from otp.otpbase.OTPGlobals import DefaultCameraFov

class RGHood(ToonHood):
    notify = directNotify.newCategory('RGHood')

    ID = ToontownGlobals.ResistanceGrounds
    SAFEZONELOADER_CLASS = RGSafeZoneLoader
    STORAGE_DNA = 'phase_6/dna/storage_RG.pdna'
    SKY_FILE = 'phase_3.5/models/props/TT_sky'
    SPOOKY_SKY_FILE = 'phase_3.5/models/props/BR_sky'
    TITLE_COLOR = (0.38, 0.79, 0.31, 1.0)

    HOLIDAY_DNA = {}

    def __init__(self, parentFSM, doneEvent, dnaStore, hoodId):
        ToonHood.__init__(self, parentFSM, doneEvent, dnaStore, hoodId)

        # Load content pack ambience settings:
        ambience = contentPacksMgr.getAmbience('resistance-grounds')

        color = ambience.get('underwater-color')
        if color is not None:
            try:
                self.underwaterColor = Vec4(color['r'], color['g'], color['b'], color['a'])
            except Exception, e:
                raise ContentPackError(e)
        elif self.underwaterColor is None:
            self.underwaterColor = Vec4(0, 0, 0.6, 1)

    def startSky(self):
        ToonHood.startSky(self)
        self.sky.setScale(4.0)

    def enter(self, requestStatus):
        ToonHood.enter(self, requestStatus)
        base.localAvatar.setCameraFov(ToontownGlobals.RGHoodFov)

    def exit(self):
        ToonHood.exit(self)
        base.localAvatar.setCameraFov(DefaultCameraFov)

    def load(self):
        ToonHood.load(self)
        self.fog = Fog('RGFog')