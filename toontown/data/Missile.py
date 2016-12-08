from toontown.data import Model


class Missile:
    def __init__(self, uid, model, deathModel, launchModel=None):
        self.uid = uid
        self.model = model
        self.deathModel = deathModel
        self.launchModel = launchModel

CupcakeMissile = Missile(0, Model.CupcakeModel, Model.SplatModel)
GoldenCupcakeMissile = Missile(0, Model.GoldenCupcakeModel, Model.SplatModel)

