from direct.directnotify.DirectNotifyGlobal import directNotify
from toontown.battle.DistributedBattleBaseAI import DistributedBattleBaseAI
from toontown.battle.SuitBattleGlobals import FACEOFF_TAUNT_T, SERVER_BUFFER_TIME, FACEOFF_LOOK_AT_PROP_T


class DistributedBattleAI(DistributedBattleBaseAI):
    notify = directNotify.newCategory('DistributedBattleAI')

    def __init__(self, air, battleMgr, pos, suit, toonId, zoneId, finishCallback = None, maxSuits = 4, tutorialFlag = 0, levelFlag = 0, interactivePropTrackBonus = -1):
        DistributedBattleBaseAI.__init__(self, air, zoneId, finishCallback, maxSuits=maxSuits, tutorialFlag=tutorialFlag, interactivePropTrackBonus=interactivePropTrackBonus)
        self.battleMgr = battleMgr
        self.pos = pos
        self.initialSuitPos = suit.getConfrontPosHpr()[0]
        self.initialToonPos = suit.getConfrontPosHpr()[0]
        self.addSuit(suit)
        self.avId = toonId
        if levelFlag == 0:
            self.addToon(toonId)
        self.faceOffToon = toonId
        self.fsm.request('FaceOff')

    def generate(self):
        DistributedBattleBaseAI.generate(self)
        toon = simbase.air.doId2do.get(self.avId)
        if toon:
            if hasattr(self, 'doId'):
                toon.b_setBattleId(self.doId)
            else:
                toon.b_setBattleId(-1)
        self.avId = None
        return

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
        self.notify.debug('enterFaceOff()')
        self.joinableFsm.request('Joinable')
        self.runnableFsm.request('Unrunnable')
        self.suits[0].releaseControl()
        timeForFaceoff = self.calcFaceoffTime(self.pos, self.initialSuitPos) + FACEOFF_TAUNT_T + SERVER_BUFFER_TIME
        if self.interactivePropTrackBonus >= 0:
            timeForFaceoff += FACEOFF_LOOK_AT_PROP_T
        self.timer.startCallback(timeForFaceoff, self.__serverFaceOffDone)
        return None

    def __serverFaceOffDone(self):
        self.notify.debug('faceoff timed out on server')
        self.ignoreFaceOffDone = 1
        self.handleFaceOffDone()

    def exitFaceOff(self):
        self.timer.stop()
        return None

    def handleFaceOffDone(self):
        self.timer.stop()
        self.activeSuits.append(self.suits[0])
        if len(self.toons) == 0:
            self.b_setState('Resume')
        elif self.faceOffToon == self.toons[0]:
            self.activeToons.append(self.toons[0])
        self.d_setMembers()
        self.b_setState('WaitForInput')

    def localMovieDone(self, needUpdate, deadToons, deadSuits, lastActiveSuitDied):
        if len(self.toons) == 0:
            self.d_setMembers()
            self.b_setState('Resume')
        elif len(self.suits) == 0:
            for toonId in self.activeToons:
                toon = self.getToon(toonId)
                if toon is not None:
                    self.toonItems[toonId] = self.air.questManager.recoverItems(toon, self.suitsKilled, self.zoneId)
                    if toonId in self.helpfulToons:
                        self.toonMerits[toonId] = self.air.promotionMgr.recoverMerits(toon, self.suitsKilled, self.zoneId)
                    else:
                        self.notify.debug('toon %d not helpful, skipping merits' % toonId)

            self.d_setMembers()
        else:
            if needUpdate == 1:
                self.d_setMembers()
                if len(deadSuits) > 0 and lastActiveSuitDied == 0 or len(deadToons) > 0:
                    self.needAdjust = 1
            self.setState('WaitForJoin')

    def enterResume(self):
        self.notify.debug('enterResume()')
        self.joinableFsm.request('Unjoinable')
        self.runnableFsm.request('Unrunnable')
        DistributedBattleBaseAI.enterResume(self)
        if self.finishCallback:
            self.finishCallback(self.zoneId)
        self.battleMgr.destroy(self)