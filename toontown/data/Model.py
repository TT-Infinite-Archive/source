from direct.actor import Actor
from panda3d.core import VBase4


class Model:
    def __init__(self, name, filepath, animDict, scale=1.0, color=(1.0, 1.0, 1.0, 1.0)):
        self.name = name
        self.filepath = filepath
        self.animDict = animDict
        self.actor = None
        self.scale = scale
        self.color = color
        self.events = {}

    def getActor(self):
        actor = Actor.Actor()
        actor.loadModel(self.filepath)
        actor.loadAnims(self.animDict)
        if self.events.get('load'):
            self.events['load'](actor)
        actor.setName(self.name)
        actor.setScale(self.scale)
        actor.setColorScale(self.color)
        actor.reparentTo(hidden)
        return actor

    def addEvent(self, eventName, func):
        self.events[eventName] = func

CupcakeModel = Model('tart', 'phase_3.5/models/props/tart', {}, 0.6)
GoldenCupcakeModel = Model('tart', 'phase_3.5/models/props/tart', {}, 0.6, color=(1, 0.84, 0.0, 1.0))
RedCupcakeModel = Model('tart', 'phase_3.5/models/props/tart', {}, 0.6, color=(1, 0.2, 0.2, 1.0))
PieSliceModel = Model('pie-slice', 'phase_5/models/props/fruit-pie-slice', {})
CreamPieSliceModel = Model('cream-pie-slice', 'phase_5/models/props/cream-pie-slice', {})
PieModel = Model('pie', 'phase_3.5/models/props/tart', {})
BirthdayCakeModel = Model('cake', 'phase_5/models/props/birthday-cake-mod', {'stand': 'phase_5/models/props/birthday-cake-chan'})
BirthdayCakeModel.addEvent('load', lambda actor: actor.loop('stand'))

TartSplatModel = Model(
    'splat', 'phase_3.5/models/props/splat-mod', {'death': 'phase_3.5/models/props/splat-chan'},
    scale=0.3, color=VBase4(55.0 / 255.0, 40.0 / 255.0, 148.0 / 255.0, 1.0)
)
FruitPieSliceSplatModel = Model(
    'splat', 'phase_3.5/models/props/splat-mod', {'death': 'phase_3.5/models/props/splat-chan'},
    scale=0.5, color=VBase4(55.0 / 255.0, 40.0 / 255.0, 148.0 / 255.0, 1.0)
)
CreamPieSliceSplatModel = Model(
    'splat', 'phase_3.5/models/props/splat-mod', {'death': 'phase_3.5/models/props/splat-chan'},
    scale=0.5, color=VBase4(55.0 / 255.0, 40.0 / 255.0, 148.0 / 255.0, 1.0)
)
FruitPieSplatModel = Model(
    'splat', 'phase_3.5/models/props/splat-mod', {'death': 'phase_3.5/models/props/splat-chan'},
    scale=0.7, color=VBase4(55.0 / 255.0, 40.0 / 255.0, 148.0 / 255.0, 1.0)
)
CreamPieSplatModel = Model(
    'splat', 'phase_3.5/models/props/splat-mod', {'death': 'phase_3.5/models/props/splat-chan'},
    scale=0.7, color=VBase4(250.0 / 255.0, 241.0 / 255.0, 24.0 / 255.0, 1.0)
)
BirthdayCakeSplatModel = Model(
    'splat', 'phase_3.5/models/props/splat-mod', {'death': 'phase_3.5/models/props/splat-chan'},
    scale=0.9, color=VBase4(253.0 / 255.0, 119.0 / 255.0, 220.0 / 255.0, 1.0)
)
