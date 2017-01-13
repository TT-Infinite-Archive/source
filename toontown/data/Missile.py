from toontown.data import Model, Sound
from direct.interval.IntervalGlobal import Sequence, ActorInterval, Func, Parallel


class Missile:
    def __init__(self, uid, model, deathModel, deathSound=Sound.NothingSound):
        self.uid = uid
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

CupcakeMissile = Missile(0, Model.CupcakeModel, Model.SplatModel, Sound.SplatSound)
PieSliceMissile = Missile(0, Model.PieSliceModel, Model.SplatModel, Sound.SplatSound)
GoldenCupcakeMissile = Missile(0, Model.GoldenCupcakeModel, Model.SplatModel, Sound.SplatSound)
RedCupcakeMissile = Missile(0, Model.RedCupcakeModel, Model.SplatModel, Sound.SplatSound)

