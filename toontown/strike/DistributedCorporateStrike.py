from direct.distributed.DistributedObject import DistributedObject
from direct.fsm.FSM import FSM
from direct.interval.IntervalGlobal import *

from toontown.strike.PointCounter import PointCounter
from toontown.strike.RoundCounter import RoundCounter
from toontown.toonbase import ToontownGlobals

from pandac.PandaModules import CollisionSphere, CollisionNode


class DistributedCorporateStrike(DistributedObject, FSM):
    ROUND_COUNTER = RoundCounter
    SPAWN_SPHERES = None

    def __init__(self, cr):
        DistributedObject.__init__(self, cr)
        FSM.__init__(self, 'DistributedCorporateStrikeFSM')

        self.roundCounter = None
        self.pointCounter = None

        self.geom = None
        self.participants = []
        self.localParticipant = None

    def loadEnvironment(self):
        base.transitions.fadeOut(t=0)

        for k in self.SPAWN_SPHERES:
            self.loadSpawnSphere(k, self.SPAWN_SPHERES[k])

        loader.endBulkLoad('strike')

    def loadSpawnSphere(self, name, data):
        cs = CollisionSphere(*data)
        cs.setTangible(0)

        name += '-cnode'
        cn = CollisionNode(name)
        cn.setCollideMask(ToontownGlobals.WallBitmask)
        cn.addSolid(cs)

        self.accept('enter'+name, self.__enterSpawnSphere)
        self.geom.attachNewNode(cn)

    def __enterSpawnSphere(self, entry):
        name = entry.getIntoNodePath().getName()[:6]
        self.localParticipant.sendUpdate('enterSpawnSphere', [name])

    def setState(self, state):
        self.request(state)

    def setDropPoint(self, x, y, z, h):
        base.localAvatar.setPos(x, y, z)
        base.localAvatar.setH(h)

    def setParticipantIds(self, ids):
        for id in ids:
            p = self.cr.doId2do[id]
            p.setStrike(self)

            if p.avId == base.localAvatar.doId:
                self.localParticipant = p
            else:
                self.participants.append(p)

        self.initializeHud()

    def initializeHud(self):
        self.roundCounter = self.ROUND_COUNTER()
        self.roundCounter.initialize()

        self.pointCounter = PointCounter(self)
        self.pointCounter.initialize()

    def enterLoading(self):
        self.loadEnvironment()
        self.geom.reparentTo(render)

        # We need to teleport in so we can restore nametags
        base.localAvatar.b_setAnimState('TeleportIn', 1)
        self.sendUpdate('barrierDone')

    def exitLoading(self):
        pass

    def enterStrike(self):
        base.localAvatar.b_setParent(ToontownGlobals.SPRender)
        base.localAvatar.b_setAnimState('neutral', 1)

        base.transitions.fadeOut(t=0)
        fadeTrack = base.transitions.getFadeInIval(t=4)

        Sequence(
            Wait(3),
            Func(fadeTrack.start),
            Wait(2),
            Func(base.cr.playGame.hood.place.fsm.request, 'walk'),
            Func(base.localAvatar.nametag3d.show),
            Func(base.localAvatar.dropShadow.show)
        ).start()

    def exitStrike(self):
        pass

    def setRound(self, round):
        self.roundCounter.transitionRound(round)
