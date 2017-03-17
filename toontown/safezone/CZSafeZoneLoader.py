from toontown.safezone import SafeZoneLoader
from toontown.safezone import CZPlayground
from pandac.PandaModules import *


class CZSafeZoneLoader(SafeZoneLoader.SafeZoneLoader):

    def __init__(self, hood, parentFSM, doneEvent):
        SafeZoneLoader.SafeZoneLoader.__init__(self, hood, parentFSM, doneEvent)
        self.playgroundClass = CZPlayground.CZPlayground
        self.musicFile = 'phase_4/audio/corpstrike/cs_ost_bgm_2.ogg'
        self.activityMusicFile = 'phase_3.5/audio/bgm/TC_SZ_activity.ogg'  # TODO: Change music.
        self.dnaFile = 'phase_6/dna/construction_zone_sz.pdna'
        self.safeZoneStorageDNAFile = 'phase_6/dna/storage_CZ_sz.pdna'


    def load(self):
        SafeZoneLoader.SafeZoneLoader.load(self)

    def unload(self):
        SafeZoneLoader.SafeZoneLoader.unload(self)
