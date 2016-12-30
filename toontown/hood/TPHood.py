from pandac.PandaModules import *
import ToonHood
from toontown.town.TPTownLoader import TPTownLoader
from toontown.safezone.TPSafeZoneLoader import TPSafeZoneLoader
from toontown.toonbase import ToontownGlobals

class TPHood(ToonHood.ToonHood):

    ID = ToontownGlobals.ToonPalooza
    TOWNLOADER_CLASS = TPTownLoader
    SAFEZONELOADER_CLASS = TPSafeZoneLoader
    STORAGE_DNA = 'phase_6/dna/storage_DD.pdna'
    SKY_FILE = 'phase_3.5/models/props/BR_sky'
    SPOOKY_SKY_FILE = 'phase_3.5/models/props/BR_sky'
    TITLE_COLOR = (0.8, 0.6, 0.5, 1.0)

    def __init__(self, parentFSM, doneEvent, dnaStore, hoodId):
        ToonHood.ToonHood.__init__(self, parentFSM, doneEvent, dnaStore, hoodId)
        self.whiteFogColor = Vec4(0.95, 0.95, 0.95, 1)
        self.underwaterFogColor = Vec4(0.0, 0.0, 0.6, 1.0)

    def load(self):
        ToonHood.ToonHood.load(self)
        self.parentFSM.getStateNamed('TPHood').addChild(self.fsm)

    def unload(self):
        self.parentFSM.getStateNamed('TPHood').removeChild(self.fsm)
        ToonHood.ToonHood.unload(self)

    def enter(self, *args):
        ToonHood.ToonHood.enter(self, *args)

    def exit(self):
        ToonHood.ToonHood.exit(self)