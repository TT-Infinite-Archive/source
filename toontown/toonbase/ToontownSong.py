class ToontownSong:
    def __init__(self, uid, name, path, length):
        self.uid = uid
        self.name = name
        self.path = path
        self.length = length

    def getAudioSound(self):
        music = loader.loadMusic(self.path)
        return music
