from toontown.data import Model, Sound
from toontown.data.DataLoader import DataLoader
from direct.interval.IntervalGlobal import Sequence, ActorInterval, Func, Parallel


class Missile:
    def __init__(self, model, deathModel, deathSound=Sound.NothingSound):
        self.model = model
        self.deathModel = deathModel
        self.deathSound = deathSound

    def die(self, parent=None, pos=(0, 0, 0)):
        if self.deathModel is None:
            return
        if parent is None:
            parent = render
        splat = self.deathModel.getActor()
        splat.reparentTo(parent)
        splat.setPos(pos)

        Sequence(
            Parallel(
                ActorInterval(splat, 'death'),
                Func(self.deathSound.playSound)
            ),
            Func(splat.cleanup),
            Func(splat.delete)
        ).start()

mdl = DataLoader('resources/data/missiles.xml')
print('Loading Missiles...')
data = mdl.loadData()

MissileDict = {}
for item in data:
    missile = Missile(
        Model.getModel(int(item['actor'])),
        Model.getModel(int(item['deathactor'])),
        Model.getModel(int(item['deathsound']))
    )
    MissileDict[int(item['id'])] = missile


def getMissile(uid):
    MissileDict.get(uid)
