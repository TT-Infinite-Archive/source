from toontown.suit import Suit
from toontown.town import TTStreet
from toontown.town import TownLoader
from toontown.battle import BattleParticles


class TTTownLoader(TownLoader.TownLoader):
    def __init__(self, hood, parentFSM, doneEvent):
        TownLoader.TownLoader.__init__(self, hood, parentFSM, doneEvent)
        self.streetClass = TTStreet.TTStreet
        self.musicFile = 'phase_3.5/audio/bgm/TC_SZ.ogg'
        self.activityMusicFile = 'phase_3.5/audio/bgm/TC_SZ_activity.ogg'
        self.townStorageDNAFile = 'phase_5/dna/storage_TT_town.pdna'
        
        if base.cr.newsManager.isStormEnabled():
            # Storm: Ambience sound.
            self.musicFile = 'phase_4/audio/bgm/storm_ambience.ogg'

    def load(self, zoneId):
        TownLoader.TownLoader.load(self, zoneId)
        Suit.loadSuits(1)
        dnaFile = 'phase_5/dna/toontown_central_' + str(self.canonicalBranchZone) + '.pdna'
        self.createHood(dnaFile)

        if base.cr.newsManager.isStormEnabled():
            self.rain = BattleParticles.loadParticleFile('rain.ptf')
            self.rain.setPos(0, 0, 5)
            self.rainRender = self.geom.attachNewNode('rainRender')
            self.rainRender.setDepthWrite(0)
            self.rainRender.setBin('fixed', 1)

    def unload(self):
        TownLoader.TownLoader.unload(self)
        Suit.unloadSuits(1)

        if hasattr(self, 'profMoochtopher'):
            self.moochPreSpeech.pause()
            self.profMoochtopher.delete()

    def enter(self, requestStatus):
        TownLoader.TownLoader.enter(self, requestStatus)

        if base.cr.newsManager.isStormEnabled():
            self.rain.start(camera, self.rainRender)

    def exit(self):
        TownLoader.TownLoader.exit(self)

        if base.cr.newsManager.isStormEnabled():
            self.rain.cleanup()
            self.rainRender.removeNode()
