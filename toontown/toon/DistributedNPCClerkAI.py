from direct.distributed.ClockDelta import globalClockDelta
from otp.ai.AIBaseGlobal import *
from direct.task.Task import Task
from toontown.toon.DistributedNPCToonBaseAI import DistributedNPCToonBaseAI
from toontown.toon import NPCToons


class DistributedNPCClerkAI(DistributedNPCToonBaseAI):
    def __init__(self, air, npcId):
        DistributedNPCToonBaseAI.__init__(self, air, npcId)
        self.timedOut = 0

    def delete(self):
        taskMgr.remove(self.uniqueName('clearMovie'))
        self.ignoreAll()
        DistributedNPCToonBaseAI.delete(self)

    def avatarEnter(self):
        avId = self.air.getAvatarIdFromSender()
        av = self.air.doId2do.get(avId)
        if av is None:
            self.notify.warning('Toon %s tried to enter but not in air.' % avId)
            return
        if self.isBusy():
            # I'm busy, go away
            self.freeAvatar(avId)
        else:
            # Not busy, I'll tend to you
            self.acceptOnce(self.air.getAvatarExitEvent(avId), self.__handleUnexpectedExit, extraArgs=[avId])
            self.sendStartMovie(avId)

    def sendStartMovie(self, avId):
        self.busy = avId
        self.sendUpdate('setMovie', [
            NPCToons.PURCHASE_MOVIE_START, self.npcId, avId, globalClockDelta.getRealNetworkTime()])
        taskMgr.doMethodLater(
            NPCToons.CLERK_COUNTDOWN_TIME, self.sendTimeoutMovie, self.uniqueName('clearMovie'))

    def sendTimeoutMovie(self, task=None):
        self.timedOut = 1
        self.d_setMovie(NPCToons.PURCHASE_MOVIE_TIMEOUT)
        self.sendClearMovie()
        return Task.done

    def sendClearMovie(self, task=None):
        self.ignore(self.air.getAvatarExitEvent(self.busy))
        self.busy = 0
        self.timedOut = 0
        self.d_setMovie(NPCToons.PURCHASE_MOVIE_CLEAR)
        return Task.done

    def sendDone(self, avId):
        self.busy = avId
        self.d_setMovie(NPCToons.PURCHASE_MOVIE_COMPLETE)
        self.sendClearMovie()

    def d_setMovie(self, mode):
        self.sendUpdate('setMovie', [mode, self.npcId, self.busy, globalClockDelta.getRealNetworkTime()])

    def acceptUnexpectedExit(self, avId):
        self.acceptOnce(self.air.getAvatarExitEvent(avId), self.__handleUnexpectedExit, extraArgs=[avId])

    def ignoreUnexpectedExit(self, avId):
        self.ignore(self.air.getAvatarExitEvent(avId))

    def __handleUnexpectedExit(self, avId):
        self.notify.warning('avatar: %s has exited unexpectedly' % avId)
        self.sendTimeoutMovie()
