from toontown.data import Model, Sound
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

CupcakeMissile = Missile(Model.CupcakeModel, Model.TartSplatModel, Sound.SplatSound)
PieSliceMissile = Missile(Model.PieSliceModel, Model.FruitPieSliceSplatModel, Sound.SplatSound02)
GoldenCupcakeMissile = Missile(Model.GoldenCupcakeModel, Model.TartSplatModel, Sound.SplatSound)
RedCupcakeMissile = Missile(Model.RedCupcakeModel, Model.TartSplatModel, Sound.SplatSound)
FruitPieMissile = Missile(Model.PieModel, Model.FruitPieSplatModel, Sound.SplatSound02)
CreamPieSliceMissile = Missile(Model.CreamPieSliceModel, Model.CreamPieSliceSplatModel, Sound.SplatSound02)
CreamPieMissile = Missile(Model.PieModel, Model.CreamPieSplatModel, Sound.SplatSound02)
BirthdayCakeMissile = Missile(Model.BirthdayCakeModel, Model.BirthdayCakeSplatModel, Sound.SplatSound03)

