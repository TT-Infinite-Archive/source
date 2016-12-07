from direct.actor import Actor


class Model:
    def __init__(self, uid, name, filepath, animDict, scale=1.0, color=(1.0, 1.0, 1.0, 1.0)):
        self.uid = uid
        self.name = name
        self.filepath = filepath
        self.animDict = animDict
        self.actor = None
        self.scale = scale
        self.color = color

    def getActor(self):
        actor = Actor.Actor()
        actor.loadModel(self.filepath)
        actor.loadAnims(self.animDict)
        actor.setName(self.name)
        actor.setScale(self.scale)
        actor.setColorScale(self.color)
        actor.reparentTo(hidden)
        return actor


class BillboardModel(Model):
    def getActor(self):
        actor = Model.getActor(self)
        scale = actor.getScale()
        actor.setBillboardPointWorld()
        actor.setScale(scale)
        return actor

CupcakeModel = Model(0, 'tart', 'phase_3.5/models/props/tart', {}, 0.6)
GoldenCupcakeModel = Model(0, 'tart', 'phase_3.5/models/props/tart', {}, 0.6, color=(1, 0.84, 0.0, 1.0))
SplatModel = BillboardModel(1, 'splat', 'phase_3.5/models/props/splat-mod', {'death': 'phase_3.5/models/props/splat-chan'}, scale=0.5)

