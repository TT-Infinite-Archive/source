from panda3d.core import CollisionNode, CollisionSphere
from toontown.safezone import SafeZoneLoader
from toontown.safezone import TTPlayground
from toontown.toonbase import ToontownGlobals
from toontown.battle import BattleParticles


class TTSafeZoneLoader(SafeZoneLoader.SafeZoneLoader):
    def __init__(self, hood, parentFSM, doneEvent):
        SafeZoneLoader.SafeZoneLoader.__init__(self, hood, parentFSM, doneEvent)
        self.playgroundClass = TTPlayground.TTPlayground

        self.musicFile = 'phase_4/audio/bgm/TC_nbrhood.ogg'
        self.activityMusicFile = 'phase_3.5/audio/bgm/TC_SZ_activity.ogg'
        self.dnaFile = 'phase_4/dna/toontown_central_sz.pdna'
        self.safeZoneStorageDNAFile = 'phase_4/dna/storage_TT_sz.pdna'

    def load(self):
        if ToontownGlobals.ToontownCentral in base.cr.zoneManager.modifiedZones:
            self.dnaFile, self.safeZoneStorageDNAFile = base.cr.zoneManager.getDNAFiles(ToontownGlobals.ToontownCentral)
        SafeZoneLoader.SafeZoneLoader.load(self)

        self.birdSound = map(loader.loadSfx, ['phase_4/audio/sfx/SZ_TC_bird1.ogg',
                                            'phase_4/audio/sfx/SZ_TC_bird2.ogg',
                                            'phase_4/audio/sfx/SZ_TC_bird3.ogg'])
        bank = self.geom.find('**/*toon_landmark_TT_bank_DNARoot')
        doorTrigger = bank.find('**/door_trigger*')
        doorTrigger.setY(doorTrigger.getY() - 1.5)

        self.rain = BattleParticles.loadParticleFile('rain.ptf')
        self.rain.setPos(0, 0, 5)
        self.rainRender = self.geom.attachNewNode('rainRender')
        self.rainRender.setDepthWrite(0)
        self.rainRender.setBin('fixed', 1)

    def enter(self, requestStatus):
        SafeZoneLoader.SafeZoneLoader.enter(self, requestStatus)

    def exit(self):
        SafeZoneLoader.SafeZoneLoader.exit(self)

    def unload(self):
        SafeZoneLoader.SafeZoneLoader.unload(self)
        del self.birdSound

