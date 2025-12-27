from otp.ai.AIBaseGlobal import *
from direct.task.Task import Task
from direct.distributed import ClockDelta
from .DistributedNPCToonBaseAI import DistributedNPCToonBaseAI
from . import NPCToons


class DistributedNPCToonAI(DistributedNPCToonBaseAI):

    def __init__(self, air, npcId, questCallback = None, hq = 0):
        DistributedNPCToonBaseAI.__init__(self, air, npcId, questCallback)
        # Am I a hq toon? Maybe this should be a subclass?
        self.hq = hq
        # Am I part of the tutorial?
        self.tutorial = 0
        # Initialize the pendingAvId to None in case we get any rogue messages
        self.pendingAvId = None
        self.task = None

    def getTutorial(self):
        return self.tutorial

    def setTutorial(self, val):
        # If you are in the tutorial you have no timeouts
        self.tutorial = val

    def getHq(self):
        return self.hq

    def avatarEnter(self):
        avId = self.air.getAvatarIdFromSender()
        if self.isBusy():
            self.freeAvatar(avId)
            return
        # this avatar has come within range
        self.air.questManager.requestInteract(avId, self)
        self.acceptOnce(self.air.getAvatarExitEvent(avId), self.__handleUnexpectedExit, extraArgs=[avId])

        self.clearTasks()
        if not self.tutorial:
            self.task = self.uniqueName('clearMovie')
            taskMgr.doMethodLater(20, self.sendTimeoutMovie, self.task)
        DistributedNPCToonBaseAI.avatarEnter(self)

    def chooseQuest(self, questId):
        avId = self.air.getAvatarIdFromSender()
        self.notify.debug('chooseQuest: avatar %s choseQuest %s' % (avId, questId))
        # Sanity check, this should not happen
        if not self.pendingAvId:
            self.notify.warning('chooseQuest: not expecting an answer from any avatar: %s' % avId)
            return
        if self.pendingAvId != avId:
            self.notify.warning('chooseQuest: not expecting an answer from this avatar: %s' % avId)
            return
        if self.pendingQuests is None:
            self.notify.warning('chooseQuest: not expecting a quest choice from this avatar: %s' % avId)
            self.air.writeServerEvent('suspicious', avId, 'unexpected chooseQuest')
            return
        # See if the avatar cancelled
        if questId == 0:
            self.pendingAvId = None
            self.pendingQuests = None
            self.air.questManager.avatarCancelled(self)
            self.cancelChoseQuest(avId)
            return
        if questId == 401:
            av = self.air.getDo(avId)
            if not av:
                self.notify.warning('chooseQuest: av not present: %s' % avId)
                return
         # See if the avatar chose any of the quests offered
        for quest in self.pendingQuests:
            if questId == quest[0]:
                self.pendingAvId = None
                self.pendingQuests = None
                self.air.questManager.avatarChoseQuest(avId, self, *quest)
                return
        # If we got here, something is wrong, handle it gracefully
        self.notify.warning('chooseQuest: avatar: %s chose a quest not offered: %s' % (avId, questId))
        # Clear the pendings
        self.pendingAvId = None
        self.pendingQuests = None

    def chooseTrack(self, trackId):
        avId = self.air.getAvatarIdFromSender()
        self.notify.debug('chooseTrack: avatar %s choseTrack %s' % (avId, trackId))
        if not self.pendingAvId:
            self.notify.warning('chooseTrack: not expecting an answer from any avatar: %s' % avId)
            return
        if self.pendingAvId != avId:
            self.notify.warning('chooseTrack: not expecting an answer from this avatar: %s' % avId)
            return
        if self.pendingTracks is None:
            self.notify.warning('chooseTrack: not expecting a track choice from this avatar: %s' % avId)
            self.air.writeServerEvent('suspicious', avId, 'unexpected chooseTrack')
            return
        # See if the avatar cancelled
        if trackId == -1:
            # Clear the pendings
            self.pendingAvId = None
            self.pendingTracks = None
            self.pendingTrackQuest = None
            # Tell the Quest Manager the avatar cancelled
            self.air.questManager.avatarCancelled(avId)
            # Tell the avatar goodbye and allow him to finish the movie
            self.cancelChoseTrack(avId)
            return
        # See if the avatar chose any of the tracks offered
        for track in self.pendingTracks:
            if trackId == track:
                # Let the quest manager figure out what to do from here on
                self.air.questManager.avatarChoseTrack(avId, self, self.pendingTrackQuest, trackId)
                # Clear the pendings
                self.pendingAvId = None
                self.pendingTracks = None
                self.pendingTrackQuest = None
                return

        # If we got here, something is wrong, handle it gracefully
        self.notify.warning('chooseTrack: avatar: %s chose a track not offered: %s' % (avId, trackId))
        # Clear the pendings
        self.pendingAvId = None
        self.pendingTracks = None
        self.pendingTrackQuest = None

    def sendTimeoutMovie(self, task):
        # Clear the movie
        self.pendingAvId = None
        self.pendingQuests = None
        self.pendingTracks = None
        self.pendingTrackQuest = None
        self.sendUpdate('setMovie', [NPCToons.QUEST_MOVIE_TIMEOUT,
         self.npcId,
         self.busy,
         [],
         ClockDelta.globalClockDelta.getRealNetworkTime()])
        self.sendClearMovie(None)
        self.busy = 0
        return Task.done

    def sendClearMovie(self, task):
        self.pendingAvId = None
        self.pendingQuests = None
        self.pendingTracks = None
        self.pendingTrackQuest = None
        self.busy = 0
        self.sendUpdate('setMovie', [NPCToons.QUEST_MOVIE_CLEAR,
         self.npcId,
         0,
         [],
         ClockDelta.globalClockDelta.getRealNetworkTime()])
        return Task.done

    def rejectAvatar(self, avId):
        self.busy = avId
        # Send a movie to reject the avatar with time stamp
        self.sendUpdate('setMovie', [NPCToons.QUEST_MOVIE_REJECT,
         self.npcId,
         avId,
         [],
         ClockDelta.globalClockDelta.getRealNetworkTime()])
        # We need a long pause here - people need to read the text before
        # clearMovie wipes it
        if not self.tutorial:
            taskMgr.doMethodLater(5.5, self.sendClearMovie, self.uniqueName('clearMovie'))

    def rejectAvatarTierNotDone(self, avId):
        self.busy = avId
        # Send a movie to reject the avatar with time stamp
        self.sendUpdate('setMovie', [NPCToons.QUEST_MOVIE_TIER_NOT_DONE,
         self.npcId,
         avId,
         [],
         ClockDelta.globalClockDelta.getRealNetworkTime()])
        # We need a long pause here - people need to read the text before
        # clearMovie wipes it
        if not self.tutorial:
            self.clearTasks()
            self.task = self.uniqueName('clearMovie')
            taskMgr.doMethodLater(5.5, self.sendClearMovie, self.task)

    def completeQuest(self, avId, questId, rewardId):
        self.busy = avId
        # nextQuestId will be the npc for the next visiting quest (visitNpcId)
        self.sendUpdate('setMovie', [NPCToons.QUEST_MOVIE_COMPLETE,
         self.npcId,
         avId,
         [questId, rewardId, 0],
         ClockDelta.globalClockDelta.getRealNetworkTime(bits=16)])
        # Timeout
        if not self.tutorial:
            self.clearTasks()
            self.task = self.uniqueName('clearMovie')
            taskMgr.doMethodLater(540.0, self.sendTimeoutMovie, self.task)

    def incompleteQuest(self, avId, questId, completeStatus, toNpcId):
        self.busy = avId
        self.sendUpdate('setMovie', [NPCToons.QUEST_MOVIE_INCOMPLETE,
         self.npcId,
         avId,
         [questId, completeStatus, toNpcId],
         ClockDelta.globalClockDelta.getRealNetworkTime()])
        # Timeout
        if not self.tutorial:
            self.clearTasks()
            self.task = self.uniqueName('clearMovie')
            taskMgr.doMethodLater(540.0, self.sendTimeoutMovie, self.task)

    def assignQuest(self, avId, questId, rewardId, toNpcId):
        self.busy = avId
        # Call the quest callback now. We could wait until the movie
        # is over, but I don't think we need to.
        if self.questCallback:
            self.questCallback()
        self.sendUpdate('setMovie', [NPCToons.QUEST_MOVIE_ASSIGN,
         self.npcId,
         avId,
         [questId, rewardId, toNpcId],
         ClockDelta.globalClockDelta.getRealNetworkTime()])
        # Timeout
        if not self.tutorial:
            self.clearTasks()
            self.task = self.uniqueName('clearMovie')
            taskMgr.doMethodLater(540.0, self.sendTimeoutMovie, self.task)

    def presentQuestChoice(self, avId, quests):
        self.busy = avId
        self.pendingAvId = avId
        self.pendingQuests = quests
        flatQuests = []
        for quest in quests:
            flatQuests.extend(quest)

        self.sendUpdate('setMovie', [NPCToons.QUEST_MOVIE_QUEST_CHOICE,
         self.npcId,
         avId,
         flatQuests,
         ClockDelta.globalClockDelta.getRealNetworkTime()])
        # Timeout
        if not self.tutorial:
            self.clearTasks()
            self.task = self.uniqueName('clearMovie')
            taskMgr.doMethodLater(20.0, self.sendTimeoutMovie, self.task)

    def presentTrackChoice(self, avId, questId, tracks):
        self.busy = avId
        self.pendingAvId = avId
        self.pendingTracks = tracks
        self.pendingTrackQuest = questId
        # Send a movie to present the choice to the avatar
        # Instead of quests, we send the trackIds
        self.sendUpdate('setMovie', [NPCToons.QUEST_MOVIE_TRACK_CHOICE,
         self.npcId,
         avId,
         tracks,
         ClockDelta.globalClockDelta.getRealNetworkTime()])
        # Timeout
        if not self.tutorial:
            self.clearTasks()
            self.task = self.uniqueName('clearMovie')
            taskMgr.doMethodLater(20.0, self.sendTimeoutMovie, self.task)

    def cancelChoseQuest(self, avId):
        self.busy = avId
        self.sendUpdate('setMovie', [NPCToons.QUEST_MOVIE_QUEST_CHOICE_CANCEL,
         self.npcId,
         avId,
         [],
         ClockDelta.globalClockDelta.getRealNetworkTime()])
        if not self.tutorial:
            self.clearTasks()
            self.task = self.uniqueName('clearMovie')
            taskMgr.doMethodLater(60.0, self.sendTimeoutMovie, self.task)

    def cancelChoseTrack(self, avId):
        self.busy = avId
        # Send a movie to present the choice to the avatar
        self.sendUpdate('setMovie', [NPCToons.QUEST_MOVIE_TRACK_CHOICE_CANCEL,
         self.npcId,
         avId,
         [],
         ClockDelta.globalClockDelta.getRealNetworkTime()])
        # Timeout
        if not self.tutorial:
            self.clearTasks()
            self.task = self.uniqueName('clearMovie')
            taskMgr.doMethodLater(60.0, self.sendTimeoutMovie, self.task)

    def setMovieDone(self):
        avId = self.air.getAvatarIdFromSender()
        self.notify.debug('setMovieDone busy: %s avId: %s' % (self.busy, avId))
        if self.busy == avId:
             # Kill all pending doLaters that will clear the movie 
            self.clearTasks()
            self.sendClearMovie(None)
        elif self.busy:
            self.air.writeServerEvent('suspicious', avId, 'DistributedNPCToonAI.setMovieDone busy with %s' % self.busy)
            self.notify.warning('somebody called setMovieDone that I was not busy with! avId: %s' % avId)

    def __handleUnexpectedExit(self, avId):
        self.notify.warning('avatar:' + str(avId) + ' has exited unexpectedly')
        self.notify.warning('not busy with avId: %s, busy: %s ' % (avId, self.busy))
        self.clearTasks()
        taskMgr.remove(self.uniqueName('clearMovie'))
        self.sendClearMovie(None)

    def clearTasks(self):
        if self.task:
            taskMgr.remove(self.task)

        self.task = None
