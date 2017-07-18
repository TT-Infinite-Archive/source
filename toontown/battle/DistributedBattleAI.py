from direct.directnotify.DirectNotifyGlobal import directNotify
from toontown.battle.DistributedBattleBaseAI import DistributedBattleBaseAI
from toontown.battle.SuitBattleGlobals import FACEOFF_TAUNT_T, SERVER_BUFFER_TIME, FACEOFF_LOOK_AT_PROP_T


class DistributedBattleAI(DistributedBattleBaseAI):
    notify = directNotify.newCategory('DistributedBattleAI')

    def __init__(self, air, battleMgr, pos, zoneId, finishCallback = None, maxSuits = 4, tutorialFlag = 0, levelFlag = 0, interactivePropTrackBonus = -1):
        DistributedBattleBaseAI.__init__(self, air, zoneId, finishCallback, maxSuits=maxSuits, tutorialFlag=tutorialFlag, interactivePropTrackBonus=interactivePropTrackBonus)
        self.battleMgr = battleMgr
        self.pos = pos
        self.faceOffToon = None
        self.initialSuitPos = None
        self.initialToonPos = None

    def doFaceOff(self, toonId, suit):
        self.faceOffToon = toonId
        self.initialSuitPos = suit.getConfrontPosHpr()[0]
        self.initialToonPos = suit.getConfrontPosHpr()[0]
        self.addToon(toonId)
        self.addSuit(suit)
        self.d_setMembers()
        self.d_setInitialSuitPos()
        self.b_setState('FaceOff')

    def faceOffDone(self):
        toonId = self.air.getAvatarIdFromSender()
        if self.ignoreFaceOffDone == 1:
            self.notify.debug('faceOffDone() - ignoring toon: %d' % toonId)
            return
        elif self.fsm.getCurrentState().getName() != 'FaceOff':
            self.notify.warning('faceOffDone() - in state: %s' % self.fsm.getCurrentState().getName())
            return
        elif self.toons.count(toonId) == 0:
            self.notify.warning('faceOffDone() - toon: %d not in toon list' % toonId)
            return
        self.notify.debug('toon: %d done facing off' % toonId)
        self.handleFaceOffDone()

    def enterFaceOff(self):
        self.notify.debug('Facing off..')
        self.joinableFsm.request('Joinable')
        self.runnableFsm.request('Unrunnable')
        self.suits[0].releaseControl()
        timeForFaceoff = self.calcFaceoffTime(self.pos, self.initialSuitPos) + FACEOFF_TAUNT_T + SERVER_BUFFER_TIME
        self.timer.startCallback(timeForFaceoff, self.__serverFaceOffDone)

    def __serverFaceOffDone(self):
        self.notify.debug('faceoff timed out on server')
        self.ignoreFaceOffDone = 1
        self.handleFaceOffDone()

    def exitFaceOff(self):
        pass

    def handleFaceOffDone(self):
        self.timer.stop()
        self.activeSuits.append(self.suits[0])
        if len(self.toons) == 0:
            self.b_setState('Resume')
        elif self.faceOffToon == self.toons[0]:
            self.addActiveToon(self.toons[0])
            self.d_setMembers()
            self.b_setState('WaitForInput')

    def enterResume(self):
        self.notify.debug('enterResume()')
        self.joinableFsm.request('Unjoinable')
        self.runnableFsm.request('Unrunnable')
        DistributedBattleBaseAI.enterResume(self)
        if self.finishCallback:
            self.finishCallback(self.zoneId)
        self.battleMgr.destroy(self)