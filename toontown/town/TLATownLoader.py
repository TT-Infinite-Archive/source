import TownLoader
import TLAStreet

class TLATownLoader(TownLoader.TownLoader):

    def __init__(self, hood, parentFSM, doneEvent):
        TownLoader.TownLoader.__init__(self, hood, parentFSM, doneEvent)
        self.streetClass = TLAStreet.TLAStreet
        self.musicFile = 'phase_6/audio/bgm/TLA_SZ.ogg'
        self.activityMusicFile = 'phase_6/audio/bgm/TLA_SZ_activity.ogg'
        self.townStorageDNAFile = 'phase_6/dna/storage_LA_town.pdna'

    def load(self, zoneId):
        TownLoader.TownLoader.load(self, zoneId)
        dnaFile = 'phase_6/dna/lost_acre_' + str(self.canonicalBranchZone) + '.pdna'
        self.createHood(dnaFile)

    def unload(self):
        TownLoader.TownLoader.unload(self)