from direct.distributed.DistributedObjectAI import DistributedObjectAI
from direct.fsm.FSM import FSM
from direct.showbase.DirectObject import DirectObject

from toontown.strike.DistributedStrikeParticipantAI import DistributedStrikeParticipantAI
from toontown.strike.StrikeWorldAI import StrikeWorldAI


class LoadingBarrier(DirectObject):
    def __init__(self, strike, avIds, callback):
        DirectObject.__init__(self)

        self.strike = strike
        self.avIds = avIds
        self.callback = callback

        for avId in self.avIds:
            event = self.strike.air.getAvatarExitEvent(avId)
            self.acceptOnce(event, self.__handleUnexpectedExit, extraArgs=[avId])

    def remove(self, avId):
        if avId in self.avIds:
            self.avIds.remove(avId)
        self.checkDone()

    def __handleUnexpectedExit(self, avId):
        self.strike.handleUnexpectedExit(avId)
        self.avIds.remove(avId)
        self.checkDone()

    def checkDone(self):
        if len(self.avIds) == 0:
            self.callback()

    def delete(self):
        self.ignoreAll()


class DistributedCorporateStrikeAI(DistributedObjectAI, FSM):
    DROP_POINTS = []
    ROUND_MANAGER = None
    NAVMESH = None

    def __init__(self, air, avIds):
        DistributedObjectAI.__init__(self, air)
        FSM.__init__(self, 'DistributedCorporateStrikeFSM')

        self.avIds = avIds
        self.participants = []
        self.loadingBarrier = None
        self.roundManager = None
        self.world = StrikeWorldAI(self)

    def start(self):
        self.request('Loading')

    def handleUnexpectedExit(self, avId):
        if self.state == 'Loading':
            self.avIds.remove(avId)

    def barrierDone(self):
        if self.state != 'Loading':
            return

        avId = self.air.getAvatarIdFromSender()
        self.sendUpdateToAvatarId(avId, 'setDropPoint', self.DROP_POINTS[self.avIds.index(avId)])
        self.loadingBarrier.remove(avId)

    def enterLoading(self):
        def callback():
            self.loadingBarrier.delete()
            self.loadingBarrier = None
            self.request('Strike')

        self.loadingBarrier = LoadingBarrier(self, self.avIds[:], callback)
        self.d_setState('Loading')

    def exitLoading(self):
        pass

    def enterStrike(self):
        pIds = []

        for avId in self.avIds:
            event = self.air.getAvatarExitEvent(avId)
            self.acceptOnce(event, self.handleUnexpectedExit, extraArgs=[avId])

            p = DistributedStrikeParticipantAI(self.air, self, avId)
            self.world.registerParticipant(p)
            p.generateWithRequired(self.zoneId)
            self.participants.append(p)
            pIds.append(p.doId)

        self.d_setParticipantIds(pIds)
        self.d_setState('Strike')
        taskMgr.doMethodLater(5, self.initalizeRounds, self.uniqueName('init-rounds'))

    def d_setState(self, state):
        self.sendUpdate('setState', [state])

    def d_setParticipantIds(self, pIds):
        self.sendUpdate('setParticipantIds', [pIds])

    def initalizeRounds(self, task):
        # Start our world:
        self.world.start()

        # Create the round manager:
        self.roundManager = self.ROUND_MANAGER(self)
        self.roundManager.initialize()

        # Enter the next round:
        self.roundManager.nextRound()
        return task.done

    def startRound(self, round):
        self.d_setRound(round)

    def d_setRound(self, round):
        self.sendUpdate('setRound', [round])
