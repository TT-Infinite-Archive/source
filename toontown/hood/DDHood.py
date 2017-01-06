from panda3d.core import Fog, Vec4

from toontown.safezone.DDSafeZoneLoader import DDSafeZoneLoader
from toontown.town.DDTownLoader import DDTownLoader
from toontown.toonbase import ToontownGlobals
from toontown.hood.ToonHood import ToonHood
from toontown.toonbase.ContentPacksManager import ContentPackError


class DDHood(ToonHood):
    notify = directNotify.newCategory('DDHood')

    ID = ToontownGlobals.DonaldsDock
    TOWNLOADER_CLASS = DDTownLoader
    SAFEZONELOADER_CLASS = DDSafeZoneLoader
    STORAGE_DNA = 'phase_6/dna/storage_DD.pdna'
    SKY_FILE = 'phase_3.5/models/props/BR_sky'
    SPOOKY_SKY_FILE = 'phase_3.5/models/props/BR_sky'
    TITLE_COLOR = (0.8, 0.6, 0.5, 1.0)

    HOLIDAY_DNA = {
      ToontownGlobals.WINTER_DECORATIONS: ['phase_6/dna/winter_storage_DD.pdna'],
      ToontownGlobals.WACKY_WINTER_DECORATIONS: ['phase_6/dna/winter_storage_DD.pdna'],
      ToontownGlobals.HALLOWEEN_PROPS: ['phase_6/dna/halloween_props_storage_DD.pdna'],
      ToontownGlobals.SPOOKY_PROPS: ['phase_6/dna/halloween_props_storage_DD.pdna']}

    def __init__(self, parentFSM, doneEvent, dnaStore, hoodId):
        ToonHood.__init__(self, parentFSM, doneEvent, dnaStore, hoodId)

        # Load content pack ambience settings:
        ambience = contentPacksMgr.getAmbience('donalds-dock')

        color = ambience.get('underwater-color')
        if color is not None:
            try:
                self.underwaterColor = Vec4(color['r'], color['g'], color['b'], color['a'])
            except Exception, e:
                raise ContentPackError(e)
        elif self.underwaterColor is None:
            self.underwaterColor = Vec4(0, 0, 0.6, 1)

        self.fogColor = Vec4(0.3, 0.3, 0.3, 1)

    def load(self):
        ToonHood.load(self)

        self.fog = Fog('DDFog')

    def setWhiteFog(self):
        if base.wantFog:
            self.fog.setColor(self.fogColor)
            self.fog.setExpDensity(0.008)
            render.clearFog()
            render.setFog(self.fog)
            self.sky.clearFog()
            self.sky.setFog(self.fog)

    def processTime(self):
        ToonHood.processTime(self)

        if base.wantFog:
            color = base.cr.shardTimeManager.getTimedColorScale()
            self.underwaterColor[2] = min(max(color[2]-.7, 0.1), 0.6)
            self.fogColor[0] = min(max(color[0]-.7, 0.1), 0.3)
            self.fogColor[1] = min(max(color[1]-.7, 0.1), 0.3)
            self.fogColor[2] = min(max(color[2]-.7, 0.1), 0.3)

            if hasattr(self.loader.place, 'cameraSubmerged'):
                if self.loader.place.cameraSubmerged:
                    self.setUnderwaterFog()
                else:
                    self.setWhiteFog()
            else:
                self.setWhiteFog()
