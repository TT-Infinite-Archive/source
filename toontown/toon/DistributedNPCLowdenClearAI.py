from DistributedNPCToonBaseAI import *
from toontown.toon import GuildMasterGlobals

class DistributedNPCLowdenClearAI(DistributedNPCToonBaseAI):
    notify = directNotify.newCategory('DistributedNPCLowdenClearAI')

    def __init__(self, air, npcId, questCallback=None, hq=0):
        DistributedNPCToonBaseAI.__init__(self, air, npcId, questCallback)
        self.hq = hq
        self.pendingAvId = None
        self.dialogIndex = 0
        self.busy = 0

    def avatarEnter(self, rename):
        avId = self.air.getAvatarIdFromSender()
        self.notify.debug('Avatar %d entered' % avId)
        if self.busy:
            self.notify.debug('I was busy, so I rejected him.')
            self.rejectAvatar(avId)
            return
        self.busy = avId
        self.dialogIndex = 0

        av = self.air.doId2do.get(avId)
        if av is None:
            return
        if av.getMoney() < GuildMasterGlobals.GUILD_COST and not self.air.wantFreeGuilds and not rename:
            self.setMovie(GuildMasterGlobals.GUILD_MOVIE_REJECT_NO_BEANS)
            return

        if rename:
            self.setMovie(GuildMasterGlobals.GUILD_MOVIE_RENAME)
        else:
            self.setMovie(GuildMasterGlobals.GUILD_MOVIE_START)
        self.acceptOnce(self.air.getAvatarExitEvent(avId), self.__handleUnexpectedExit, extraArgs=[avId])

    def requestDialog(self, dialogIndex):
        avId = self.air.getAvatarIdFromSender()
        self.notify.debug('Avatar %d requested dialog %d' % (avId, dialogIndex))
        if dialogIndex <= self.dialogIndex:
            self.notify.debug('We already handled that dialog, ignoring.')
            self.rejectAvatar(avId)
            return

        if dialogIndex >= GuildMasterGlobals.GUILD_MOVIE_DONE:
            if self.busy:
                self.sendDoneMovie()
            else:
                self.rejectAvatar(avId)
        else:
            self.dialogIndex = dialogIndex
            self.setMovie(dialogIndex)

    def setMovie(self, movieIndex):
        self.notify.debug('Setting movie %d' % movieIndex)
        if taskMgr.hasTaskNamed(self.uniqueName('timeoutMovie')):
            taskMgr.remove(self.uniqueName('timeoutMovie'))

        avId = self.busy

        if movieIndex != GuildMasterGlobals.GUILD_MOVIE_REJECT_NO_BEANS:
            taskMgr.doMethodLater(60, self.sendTimeoutMovie, self.uniqueName('timeoutMovie'))
        else:
            self.busy = 0

        self.sendUpdate('setMovie', [movieIndex, avId, ClockDelta.globalClockDelta.getRealNetworkTime()])

    def rejectNextDialog(self):
        self.notify.debug('Avatar %d rejected my next dialog')
        self.sendRejectMovie()
        self.ignoreAll()

    def sendTimeoutMovie(self, task=None):
        self.notify.debug('Timing out Avatar %d' % self.busy)
        self.pendingAvId = None
        self.sendUpdate('setMovie', [GuildMasterGlobals.GUILD_MOVIE_TIMEOUT, self.busy, ClockDelta.globalClockDelta.getRealNetworkTime()])
        self.busy = 0
        self.dialogIndex = 0

        self.clearTasks()

        taskMgr.doMethodLater(7, self.sendClearMovie, self.uniqueName('clearMovie'))

        if task is not None:
            return task.done
        self.ignoreAll()

    def sendClearMovie(self, task=None, av=0):
        self.sendUpdate('setMovie', [GuildMasterGlobals.GUILD_MOVIE_CLEAR, av, ClockDelta.globalClockDelta.getRealNetworkTime()])

        if task is not None:
            return task.done

    def sendDoneMovie(self):
        self.notify.debug('Sending doneMovie')
        self.sendUpdate('setMovie', [GuildMasterGlobals.GUILD_MOVIE_DONE, self.busy, ClockDelta.globalClockDelta.getRealNetworkTime()])
        self.busy = 0
        self.dialogIndex = 0

        self.clearTasks()

        taskMgr.doMethodLater(7, self.sendClearMovie, self.uniqueName('clearMovie'))
        self.ignoreAll()

    def sendRejectMovie(self):
        self.sendUpdate('setMovie', [GuildMasterGlobals.GUILD_MOVIE_DENY, self.busy, ClockDelta.globalClockDelta.getRealNetworkTime()])
        self.busy = 0
        self.dialogIndex = 0

        self.clearTasks()

        taskMgr.doMethodLater(7, self.sendClearMovie, self.uniqueName('clearMovie'))
        self.ignoreAll()

    def rejectAvatar(self, avId):
        self.sendUpdate('setMovie', [GuildMasterGlobals.GUILD_MOVIE_REJECT, avId, ClockDelta.globalClockDelta.getRealNetworkTime()])

    def __handleUnexpectedExit(self, avId):
        self.notify.warning('Avatar %d has exited unexpectedly' % avId)
        self.busy = 0
        self.dialogIndex = 0
        self.clearTasks()
        self.sendTimeoutMovie()

    def clearTasks(self):
        if taskMgr.hasTaskNamed(self.uniqueName('timeoutMovie')):
            taskMgr.remove(self.uniqueName('timeoutMovie'))
        if taskMgr.hasTaskNamed(self.uniqueName('clearMovie')):
            taskMgr.remove(self.uniqueName('clearMovie'))
