from pandac.PandaModules import *
import ToonHood
from toontown.town.TPTownLoader import TPTownLoader
from toontown.safezone.TPSafeZoneLoader import TPSafeZoneLoader
from toontown.toonbase import ToontownGlobals

class TPHood(ToonHood.ToonHood):

    ID = ToontownGlobals.ToonPalooza
    TOWNLOADER_CLASS = TPTownLoader
    SAFEZONELOADER_CLASS = TPSafeZoneLoader
    STORAGE_DNA = 'phase_4/dna/storage_TP.pdna'
    SKY_FILE = 'phase_3.5/models/props/BR_sky'
    SPOOKY_SKY_FILE = 'phase_3.5/models/props/BR_sky'
    TITLE_COLOR = (0.38, 0.79, 0.31, 1.0)

    def __init__(self, parentFSM, doneEvent, dnaStore, hoodId):
        ToonHood.ToonHood.__init__(self, parentFSM, doneEvent, dnaStore, hoodId)

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