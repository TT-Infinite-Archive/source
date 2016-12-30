import TownLoader
import TPStreet

class TPTownLoader(TownLoader.TownLoader):

    def __init__(self, hood, parentFSM, doneEvent):
        TownLoader.TownLoader.__init__(self, hood, parentFSM, doneEvent)
        self.streetClass = TPStreet.TPStreet
        self.musicFile = 'phase_6/audio/bgm/TLA_SZ.ogg'
        self.activityMusicFile = 'phase_6/audio/bgm/TLA_SZ_activity.ogg'
        self.townStorageDNAFile = 'phase_4/dna/storage_TP_town.pdna'

    def load(self, zoneId):
        TownLoader.TownLoader.load(self, zoneId)
        dnaFile = 'phase_4/dna/toon_palooza_' + str(self.canonicalBranchZone) + '.pdna'
        self.createHood(dnaFile)

    def unload(self):
        TownLoader.TownLoader.unload(self)