import DistributedSuitBase
from direct.directnotify import DirectNotifyGlobal
from direct.fsm import ClassicFSM, State
from direct.fsm import State
from pandac.PandaModules import *
from toontown.distributed.DelayDeletable import DelayDeletable


class DistributedTutorialSuit(DistributedSuitBase.DistributedSuitBase, DelayDeletable):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedTutorialSuit')

    def __init__(self, cr):
        try:
            self.DistributedSuit_initialized
        except:
            self.DistributedSuit_initialized = 1
            DistributedSuitBase.DistributedSuitBase.__init__(self, cr)
            self.fsm = ClassicFSM.ClassicFSM('DistributedSuit', [State.State('Off', self.enterOff, self.exitOff, ['Walk', 'Battle']),
             State.State('Walk', self.enterWalk, self.exitWalk, ['WaitForBattle', 'Battle']),
             State.State('Battle', self.enterBattle, self.exitBattle, []),
             State.State('WaitForBattle', self.enterWaitForBattle, self.exitWaitForBattle, ['Battle'])], 'Off', 'Off')
            self.fsm.enterInitialState()

    def generate(self):
        DistributedSuitBase.DistributedSuitBase.generate(self)

    def announceGenerate(self):
        DistributedSuitBase.DistributedSuitBase.announceGenerate(self)
        # Reparent this suit to the plaza island
        self.accept('islands-loaded', self.__handleIslandsLoaded)
        self.setPos(0, 0, 0)
        self.setState('Walk')

    def disable(self):
        self.notify.debug('DistributedSuit %d: disabling' % self.getDoId())
        self.setState('Off')
        self.ignore('islands-loaded')
        DistributedSuitBase.DistributedSuitBase.disable(self)

    def delete(self):
        try:
            self.DistributedSuit_deleted
        except:
            self.DistributedSuit_deleted = 1
            self.notify.debug('DistributedSuit %d: deleting' % self.getDoId())
            del self.fsm
            DistributedSuitBase.DistributedSuitBase.delete(self)

    def __handleIslandsLoaded(self, e=None):
        self.reparentTo(base.cr.playGame.hood.loader.islands[1])

    def d_requestBattle(self, pos, hpr):
        self.cr.playGame.getPlace().setState('WaitForBattle')
        self.sendUpdate('requestBattle', [pos[0], pos[1], pos[2], hpr[0], hpr[1], hpr[2]])

    def __handleToonCollision(self, collEntry):
        toonId = base.localAvatar.getDoId()
        self.notify.debug('Distributed suit: requesting a Battle with ' + 'toon: %d' % toonId)
        self.d_requestBattle(self.getPos(), self.getHpr())
        self.setState('WaitForBattle')

    def enterWalk(self):
        #self.reparentTo(base.cr.playGame.hood.loader.islands[0])
        self.enableBattleDetect('walk', self.__handleToonCollision)
        self.loop('walk', 0)
        pathPoints = [
            Point3(8.318, -22.948, 0.025),
            Point3(7.968, 27.224, 0.025),
            Point3(-12.919, 26.818, 0.025),
            Point3(-12.561, -23.045, 0.025),
            Point3(8.318, -22.948, 0.025)
        ]
        self.tutWalkTrack = self.makePathTrack(self, pathPoints, 4.5, 'tutFlunkyWalk')
        self.tutWalkTrack.loop()

    def exitWalk(self):
        self.disableBattleDetect()
        self.tutWalkTrack.finish()
        self.tutWalkTrack = None

    def subclassManagesParent(self):
        return 1
