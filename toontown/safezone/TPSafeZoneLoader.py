from pandac.PandaModules import *
import SafeZoneLoader
import TPPlayground

class TPSafeZoneLoader(SafeZoneLoader.SafeZoneLoader):

    def __init__(self, hood, parentFSM, doneEvent):
        SafeZoneLoader.SafeZoneLoader.__init__(self, hood, parentFSM, doneEvent)
        self.playgroundClass = TPPlayground.TPPlayground
        self.musicFile = 'phase_6/audio/bgm/TLA_nbrhood.ogg'
        self.activityMusicFile = 'phase_6/audio/bgm/TLA_SZ.ogg'
        self.dnaFile = 'phase_6/dna/lost_acre_sz.pdna'
        self.safeZoneStorageDNAFile = 'phase_6/dna/storage_LA_sz.pdna'

    def load(self):
        SafeZoneLoader.SafeZoneLoader.load(self)

    def unload(self):
        SafeZoneLoader.SafeZoneLoader.unload(self)

    def enter(self, requestStatus):
        SafeZoneLoader.SafeZoneLoader.enter(self, requestStatus)

    def exit(self):
        SafeZoneLoader.SafeZoneLoader.exit(self)