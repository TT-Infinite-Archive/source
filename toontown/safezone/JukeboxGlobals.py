from toontown.toonbase import TTLocalizer


class ToontownSong:
    def __init__(self, uid, name, path, length):
        self.uid = uid
        self.name = name
        self.path = path
        self.length = length

    def getAudioSound(self):
        music = loader.loadMusic(self.path)
        return music

    def getLength(self):
        return self.length

Songs = {
    0: None,
    1: ToontownSong(1, TTLocalizer.MusicThemeSong, 'phase_3/audio/bgm/tti_theme.ogg', 90),
    2: ToontownSong(2, TTLocalizer.MusicMakeAToon, 'phase_3/audio/bgm/create_a_toon.ogg', 175),
    3: ToontownSong(3, TTLocalizer.MusicTcNbrhood, 'phase_4/audio/bgm/TC_nbrhood.ogg', 58),
    4: ToontownSong(4, TTLocalizer.MusicDdNbrhood, 'phase_6/audio/bgm/DD_SZ.ogg', 32)
}

FadeTime = 5
ServerBufferTime = 2


