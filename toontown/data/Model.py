from direct.actor import Actor
from direct.interval.IntervalGlobal import Sequence, ActorInterval, Func
from panda3d.core import VBase4, VBase3
from toontown.data.DataLoader import ModelDataLoader
from direct.directnotify import DirectNotifyGlobal


class ActorFactory:
    notify = DirectNotifyGlobal.directNotify.newCategory('ActorFactory')

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

    def importEvent(self, event, action, arg):
        if action == 'ActorLoop':
            func = lambda actor: actor.loop(arg)
        else:
            self.notify.warning('Unknown action %s' % action)
            return
        self.addEvent(event, func)
        
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

adl = ModelDataLoader('resources/data/actors.xml')
data = adl.loadData()

ModelDict = {}

for item in data:
    actor = ActorFactory(
        item['filepath'],
        item.get('anims', {}),
        float(item.get('scale', 1.0)),
        item.get('color', VBase4(1, 1, 1, 1))
    )
    if item.get('events'):
        for event in item['events']:
            actor.importEvent(event[0], event[1], event[2])
    ModelDict[int(item['id'])] = actor


def getModel(uid):
    return ModelDict.get(uid)
