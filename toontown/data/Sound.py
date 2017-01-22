class Sound:
    def __init__(self, uid, name, filepath, duration):
        self.uid = uid
        self.name = name
        self.filepath = filepath
        self.duration = duration

    def getSound(self):
        if self.filepath is None:
            return None
        sound = loader.loadSfx(self.filepath)
        return sound

    def playSound(self):
        sound = self.getSound()
        if sound:
            sound.play()


NothingSound = Sound(0, 'nothing', None, 0.0)
ThrowSound = Sound(1, 'pie-throw', 'phase_3.5/audio/sfx/AA_pie_throw_only.ogg', 0.412)
CogDeathSound = Sound(2, 'cog-death', 'phase_3.5/audio/sfx/Cog_Death.ogg', 3.183)
CogExplosionSound = Sound(3, 'cog-explosion', 'phase_3.5/audio/sfx/ENC_cogfall_apart.ogg', 1.65)
SplatSound = Sound(4, 'splat', 'phase_3.5/audio/sfx/AA_tart_only.ogg', 1.12)
SplatSound02 = Sound(5, 'splat-2', 'phase_5/audio/sfx/AA_slice_only.ogg', 0.4)
SplatSound03 = Sound(6, 'splat-3', 'phase_4/audio/sfx/AA_wholepie_only.ogg', 0.4)
CannonFireSound = Sound(7, 'kapow', 'phase_4/audio/sfx/MG_cannon_fire_alt.ogg', 1.58)
CannonAdjustSound = Sound(8, 'cannon-adjust', 'phase_4/audio/sfx/MG_cannon_adjust.ogg', 1.22)


