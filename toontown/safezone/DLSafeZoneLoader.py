from toontown.safezone import DLPlayground
from toontown.safezone import SafeZoneLoader
from toontown.toonbase import ToontownGlobals


class DLSafeZoneLoader(SafeZoneLoader.SafeZoneLoader):
    def __init__(self, hood, parentFSM, doneEvent):
        SafeZoneLoader.SafeZoneLoader.__init__(self, hood, parentFSM, doneEvent)
        self.playgroundClass = DLPlayground.DLPlayground
        self.musicFile = 'phase_8/audio/bgm/DL_nbrhood.ogg'
        self.activityMusicFile = 'phase_8/audio/bgm/DL_SZ_activity.ogg'
        self.dnaFile = 'phase_8/dna/donalds_dreamland_sz.pdna'
        self.safeZoneStorageDNAFile = 'phase_8/dna/storage_DL_sz.pdna'

    def load(self):
        if ToontownGlobals.DonaldsDreamland in base.cr.zoneManager.modifiedZones:
            self.dnaFile, self.safeZoneStorageDNAFile = base.cr.zoneManager.getDNAFiles(ToontownGlobals.DonaldsDreamland)

        SafeZoneLoader.SafeZoneLoader.load(self)
