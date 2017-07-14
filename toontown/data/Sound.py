from toontown.data.DataLoader import DataLoader


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

sdl = DataLoader('resources/data/sounds.xml')
print('Loading Sounds...')
data = sdl.loadData()

SoundDict = {}
NothingSound = Sound(0, 'nothing', None, 0.0)
SoundDict[0] = NothingSound
for item in data:
    SoundDict[int(item['id'])] = Sound(int(item['id']), item['name'], item['filepath'], float(item['duration']))


def getSound(uid):
    return SoundDict.get(uid, NothingSound)
