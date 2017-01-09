from toontown.safezone import SafeZoneLoader
from toontown.safezone import RGPlayground


class RGSafeZoneLoader(SafeZoneLoader.SafeZoneLoader):
    def __init__(self, hood, parentFSM, doneEvent):
        SafeZoneLoader.SafeZoneLoader.__init__(self, hood, parentFSM, doneEvent)

        self.playgroundClass = RGPlayground.RGPlayground
        self.musicFile = 'phase_6/audio/bgm/RG_nbrhood.ogg'
        self.activityMusicFile = 'phase_3.5/audio/bgm/TC_SZ_activity.ogg'  # TODO: Change music.
        self.dnaFile = 'phase_6/dna/resistance_grounds_sz.pdna'
        self.safeZoneStorageDNAFile = 'phase_6/dna/storage_RG_sz.pdna'


    def load(self):
        SafeZoneLoader.SafeZoneLoader.load(self)

        self.birdSound = map(loader.loadSfx, ['phase_4/audio/sfx/SZ_TC_bird1.ogg',
                                            'phase_4/audio/sfx/SZ_TC_bird2.ogg',
                                            'phase_4/audio/sfx/SZ_TC_bird3.ogg'])
        self.underwaterSound = loader.loadSfx('phase_4/audio/sfx/AV_ambient_water.ogg')
        self.swimSound = loader.loadSfx('phase_4/audio/sfx/AV_swim_single_stroke.ogg')
        self.submergeSound = loader.loadSfx('phase_5.5/audio/sfx/AV_jump_in_water.ogg')
        self.waterSound = loader.loadSfx('phase_6/audio/sfx/SZ_DD_waterlap.ogg')
        water = self.geom.find('**/water')
        water.setTransparency(1)
        water.setColorScale(1, 1, 1, 1)
        water.setBin('water', 51, 1)

    def unload(self):
        SafeZoneLoader.SafeZoneLoader.unload(self)

        del self.birdSound
        del self.underwaterSound
        del self.swimSound
        del self.submergeSound
        del self.waterSound
