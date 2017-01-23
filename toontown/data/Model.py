from direct.actor import Actor
from direct.interval.IntervalGlobal import Sequence, ActorInterval, Func
from panda3d.core import VBase4, VBase3


class ActorFactory:
    def __init__(self, model=None, anims=None, scale=VBase3(1, 1, 1), color=VBase4(1, 1, 1, 1)):
        self.model = model
        self.scale = scale
        self.color = color
        self.events = {}
        if anims is None:
            self.anims = {}
        else:
            self.anims = anims

    def getActor(self):
        actor = TTActor(self.model, self.anims, self.events)
        actor.setScale(self.scale)
        actor.setColorScale(self.color)
        return actor
        
    def addEvent(self, eventName, func):
        self.events[eventName] = func


class TTActor(Actor.Actor):
    def __init__(self, model, anims, events):
        Actor.Actor.__init__(self, model, anims)
        self.events = events
        if anims is None:
            anims = {}
        self.anims = anims
        if self.events.get('create'):
            self.events['create'](self)

    def destroy(self, deathAnim=True):
        if self.anims.get('death') and deathAnim:
            self.hide()
            deathActor = TTActor(self.model, self.anims, {})
            deathActor.copyActor(self, True)
            Sequence(
                ActorInterval(deathActor, 'death'),
                Func(deathActor.destroy, False)
            ).start()
        self.delete()

    def delete(self):
        if self.events.get('destroy'):
            self.events['destroy'](self)
        Actor.Actor.delete(self)
            

CupcakeModel = ActorFactory('phase_3.5/models/props/tart', {}, 0.6)
GoldenCupcakeModel = ActorFactory('phase_3.5/models/props/tart', {}, 0.6, color=(1, 0.84, 0.0, 1.0))
RedCupcakeModel = ActorFactory('phase_3.5/models/props/tart', {}, 0.6, color=(1, 0.2, 0.2, 1.0))
PieSliceModel = ActorFactory('phase_5/models/props/fruit-pie-slice', {})
CreamPieSliceModel = ActorFactory('phase_5/models/props/cream-pie-slice', {})
FruitPieModel = ActorFactory('phase_3.5/models/props/tart', {}, 0.75)
CreamPieModel = ActorFactory('phase_3.5/models/props/tart', {}, 0.85)
BirthdayCakeModel = ActorFactory('phase_5/models/props/birthday-cake-mod', {'stand': 'phase_5/models/props/birthday-cake-chan'})
BirthdayCakeModel.addEvent('create', lambda actor: actor.loop('stand'))
ButtonModel = ActorFactory('phase_3.5/models/props/button')
CannonModel = ActorFactory('phase_4/models/minigames/toon_cannon')
KapowModel = ActorFactory(
    'phase_5/models/props/kapow-mod',
    {'kapow': 'phase_5/models/props/kapow-chan'},
    scale=0.25
)
BikeHornModel = ActorFactory('phase_5/models/props/bikehorn', scale=0.4)
MegaphoneModel = ActorFactory('phase_5/models/props/megaphone')

TartSplatModel = ActorFactory(
    'phase_3.5/models/props/splat-mod', {'death': 'phase_3.5/models/props/splat-chan'},
    scale=0.3, color=VBase4(55.0 / 255.0, 40.0 / 255.0, 148.0 / 255.0, 1.0)
)
FruitPieSliceSplatModel = ActorFactory(
    'phase_3.5/models/props/splat-mod', {'death': 'phase_3.5/models/props/splat-chan'},
    scale=0.5, color=VBase4(55.0 / 255.0, 40.0 / 255.0, 148.0 / 255.0, 1.0)
)
CreamPieSliceSplatModel = ActorFactory(
    'phase_3.5/models/props/splat-mod', {'death': 'phase_3.5/models/props/splat-chan'},
    scale=0.5, color=VBase4(55.0 / 255.0, 40.0 / 255.0, 148.0 / 255.0, 1.0)
)
FruitPieSplatModel = ActorFactory(
    'phase_3.5/models/props/splat-mod', {'death': 'phase_3.5/models/props/splat-chan'},
    scale=0.7, color=VBase4(55.0 / 255.0, 40.0 / 255.0, 148.0 / 255.0, 1.0)
)
CreamPieSplatModel = ActorFactory(
    'phase_3.5/models/props/splat-mod', {'death': 'phase_3.5/models/props/splat-chan'},
    scale=0.7, color=VBase4(250.0 / 255.0, 241.0 / 255.0, 24.0 / 255.0, 1.0)
)
BirthdayCakeSplatModel = ActorFactory(
    'phase_3.5/models/props/splat-mod', {'death': 'phase_3.5/models/props/splat-chan'},
    scale=0.9, color=VBase4(253.0 / 255.0, 119.0 / 255.0, 220.0 / 255.0, 1.0)
)
