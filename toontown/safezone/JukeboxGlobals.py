from toontown.toonbase import TTLocalizer


class ToontownSong:
    def __init__(self, uid, name, path, length=None):
        self.uid = uid
        self.name = name
        self.path = path
        self.length = length

    def getAudioSound(self):
        music = loader.loadMusic(self.path)
        return music

    def getLength(self):
        if self.length is None:
            music = self.getAudioSound()
            self.length = music.length()
            loader.unloadSfx(music)
        return self.length

Songs = {
    0: None,
    1: ToontownSong(0, TTLocalizer.MusicTcNbrhood, 'phase_4/audio/bgm/TC_nbrhood.ogg'),
    2: ToontownSong(1, TTLocalizer.MusicDdNbrhood, 'phase_6/audio/bgm/DD_SZ.ogg')
}


