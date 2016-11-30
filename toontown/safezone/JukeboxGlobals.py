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
    1: ToontownSong(1, TTLocalizer.MusicTcNbrhood, 'phase_4/audio/bgm/TC_nbrhood.ogg', 58),
    2: ToontownSong(2, TTLocalizer.MusicDdNbrhood, 'phase_6/audio/bgm/DD_SZ.ogg', 32)
}

FadeTime = 5
ServerBufferTime = 2


