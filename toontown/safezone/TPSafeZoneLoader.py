from pandac.PandaModules import *
import SafeZoneLoader
import TPPlayground
import random

class TPSafeZoneLoader(SafeZoneLoader.SafeZoneLoader):

    def __init__(self, hood, parentFSM, doneEvent):
        SafeZoneLoader.SafeZoneLoader.__init__(self, hood, parentFSM, doneEvent)
        self.playgroundClass = TPPlayground.TPPlayground
        self.musicFile = random.choice(
            ['phase_13/audio/bgm/party_generic_theme.ogg', 'phase_13/audio/bgm/party_generic_theme_jazzy.ogg',
             'phase_13/audio/bgm/party_original_theme.ogg', 'phase_13/audio/bgm/party_polka_dance.ogg',
             'phase_13/audio/bgm/party_swing_dance.ogg', 'phase_13/audio/bgm/party_waltz_dance.ogg', ])
        self.activityMusicFile = 'phase_13/audio/bgm/party_swing_dance.ogg'
        self.dnaFile = 'phase_4/dna/toon_palooza_sz.pdna'
        self.safeZoneStorageDNAFile = 'phase_4/dna/storage_TP_sz.pdna'

        self.elevator = None

    def load(self):
        SafeZoneLoader.SafeZoneLoader.load(self)

        self.elevator = loader.loadModel('phase_4/models/modules/elevator.bam')
        self.elevator.reparentTo(render)

    def unload(self):
        SafeZoneLoader.SafeZoneLoader.unload(self)

        self.elevator.removeNode()

    def enter(self, requestStatus):
        SafeZoneLoader.SafeZoneLoader.enter(self, requestStatus)

    def exit(self):
        SafeZoneLoader.SafeZoneLoader.exit(self)