from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.distributed.ClockDelta import *
from direct.distributed.DistributedObjectAI import DistributedObjectAI
from direct.fsm import ClassicFSM, State
from direct.task import Task, Timer
from panda3d.core import *

from otp.ai.MagicWordGlobal import CATEGORY_PROGRAMMER, magicWord, spellbook
from toontown.battle import BattleAttack
from toontown.battle import BattleGlobals
from toontown.battle import SuitBattleGlobals
from toontown.battle.BattleBase import BattleBase
from toontown.battle.BattleCalculatorAI import BattleCalculatorAI
from toontown.data import Gag
from toontown.toonbase import ToontownGlobals


class DistributedBattleBaseAI(DistributedObjectAI, BattleBase):
    notify = directNotify.newCategory('DistributedBattleBaseAI')

    def __init__(self, air, zoneId, finishCallback=None, maxSuits=4, bossBattle=0, tutorialFlag=0, interactivePropTrackBonus=-1):
        DistributedObjectAI.__init__(self, air)
        BattleBase.__init__(self)
        self.serialNum = 0
        self.zoneId = zoneId
        self.maxSuits = maxSuits
        self.setBossBattle(bossBattle)
        self.tutorialFlag = tutorialFlag
        self.interactivePropTrackBonus = interactivePropTrackBonus
        self.finishCallback = finishCallback
        self.avatarExitEvents = []
        self.responses = {}
        self.adjustingResponses = {}
        self.joinResponses = {}
        self.adjustingSuits = []
        self.adjustingToons = []
        self.numSuitsEver = 0
        self.streetBattle = 1
        self.pos = Point3(0, 0, 0)
        self.initialSuitPos = Point3(0, 0, 0)
        self.toonExp = {}
        self.toonOrigQuests = {}
        self.toonItems = {}
        self.toonOrigMerits = {}
        self.toonMerits = {}
        self.toonParts = {}
        self.battleCalc = BattleCalculatorAI(self, tutorialFlag)
        self.ignoreFaceOffDone = 0
        self.needAdjust = 0
        self.ignoreAdjustingResponses = 0
        self.taskNames = []
        self.exitedToons = []
        self.suitsKilled = []
        self.suitsKilledThisBattle = []
        self.suitsKilledPerFloor = []
        self.newToons = []
        self.newSuits = []
        self.fsm = ClassicFSM.ClassicFSM('DistributedBattleAI', [
            State.State('FaceOff', self.enterFaceOff, self.exitFaceOff, ['WaitForInput', 'Resume']),
            State.State('WaitForJoin', self.enterWaitForJoin, self.exitWaitForJoin, ['WaitForInput', 'Resume']),
            State.State('WaitForInput', self.enterWaitForInput, self.exitWaitForInput, ['Resume', 'MakeMovie']),
            State.State('MakeMovie', self.enterMakeMovie, self.exitMakeMovie, ['PlayMovie', 'Resume']),
            State.State('PlayMovie', self.enterPlayMovie, self.exitPlayMovie, ['ApplyAttacks', 'Resume']),
            State.State('ApplyAttacks', self.enterApplyAttacks, self.exitApplyAttacks, ['WaitForJoin', 'WaitForInput', 'Resume']),
            State.State('Resume', self.enterResume, self.exitResume, []),
            State.State('Off', self.enterOff, self.exitOff, ['FaceOff', 'WaitForJoin', 'Resume'])
        ], 'Off', 'Off')
        self.joinableFsm = ClassicFSM.ClassicFSM('Joinable', [
            State.State('Joinable', self.enterJoinable, self.exitJoinable, ['Unjoinable']),
            State.State('Unjoinable', self.enterUnjoinable, self.exitUnjoinable, ['Joinable'])
        ], 'Unjoinable', 'Unjoinable')
        self.joinableFsm.enterInitialState()
        self.runnableFsm = ClassicFSM.ClassicFSM('Runnable', [
            State.State('Runnable', self.enterRunnable, self.exitRunnable, ['Unrunnable']),
            State.State('Unrunnable', self.enterUnrunnable, self.exitUnrunnable, ['Runnable'])
        ], 'Unrunnable', 'Unrunnable')
        self.runnableFsm.enterInitialState()
        self.adjustFsm = ClassicFSM.ClassicFSM('Adjust', [
            State.State('Adjusting', self.enterAdjusting, self.exitAdjusting, ['NotAdjusting', 'Adjusting']),
            State.State('NotAdjusting', self.enterNotAdjusting, self.exitNotAdjusting, ['Adjusting'])
        ], 'NotAdjusting', 'NotAdjusting')
        self.adjustFsm.enterInitialState()
        self.fsm.enterInitialState()
        self.startTime = globalClock.getRealTime()
        self.adjustingTimer = Timer.Timer()
        self.finalBattle = False

        self.toonAttacks = {}
        self.suitAttacks = {}
        self.toonMovieAttacks = []
        self.suitMovieAttacks = []
        self.movieResponses = {}

    def delete(self):
        self.notify.debug('Deleting...')
        self.ignoreAll()
        self.timer.stop()
        self.adjustingTimer.stop()
        self.battleCalc.cleanup()
        self.__removeAllTasks()
        self.__cleanupJoinResponses()
        self.fsm.request('Off')
        self.fsm = None
        self.joinableFsm = None
        self.runnableFsm = None
        self.adjustFsm = None
        self.timer = None
        self.adjustingTimer = None
        self.battleCalc = None
        self.finishCallback = None
        DistributedObjectAI.delete(self)

    def requestDelete(self):
        if self.fsm:
            self.fsm.request('Off')
        self.__removeTaskName(self.uniqueName('make-movie'))
        DistributedObjectAI.requestDelete(self)

    def clearAttacks(self):
        self.notify.debug('Clearing attacks...')
        self.toonAttacks.clear()
        self.suitAttacks.clear()

    def __removeSuit(self, suit):
        self.notify.debug('Removing suit: %d' % suit.doId)
        self.suits.remove(suit)
        self.activeSuits.remove(suit)
        self.suitGone = 1

    def findSuit(self, id):
        for s in self.suits:
            if s.doId == id:
                return s

        return None

    def __removeTaskName(self, name):
        if name in self.taskNames:
            self.taskNames.remove(name)
            self.notify.debug('Removing task: %s' % name)
            taskMgr.remove(name)

    def __removeAllTasks(self):
        for name in self.taskNames:
            self.__removeTaskName(name)

        self.taskNames = []

    def __removeToonTasks(self, toonId):
        name = self.taskName('running-toon-%d' % toonId)
        self.__removeTaskName(name)
        name = self.taskName('joining-timeout-%d' % toonId)
        self.__removeTaskName(name)

    def getLevelDoId(self):
        return 0

    def getBattleCellId(self):
        return 0

    def setBossBattle(self, bossBattle):
        self.bossBattle = bossBattle

    def getBossBattle(self):
        return self.bossBattle

    def b_setState(self, state):
        self.setState(state)
        self.d_setState(state)

    def d_setState(self, state):
        stime = globalClock.getRealTime() + SuitBattleGlobals.SERVER_BUFFER_TIME
        self.sendUpdate('setState', [state, globalClockDelta.localToNetworkTime(stime)])

    def setState(self, state):
        self.notify.debug('Setting state: %s' % state)
        self.fsm.request(state)

    def getState(self):
        return [self.fsm.getCurrentState().getName(), globalClockDelta.getRealNetworkTime()]

    def d_setMembers(self):
        self.sendUpdate('setMembers', self.getMembers())

    def getMembers(self):
        suits = []
        for s in self.suits:
            suits.append(s.doId)

        joiningSuits = ''
        for s in self.joiningSuits:
            joiningSuits += str(suits.index(s.doId))

        pendingSuits = ''
        for s in self.pendingSuits:
            pendingSuits += str(suits.index(s.doId))

        activeSuits = ''
        for s in self.activeSuits:
            activeSuits += str(suits.index(s.doId))

        toons = []
        for t in self.toons:
            toons.append(t)

        joiningToons = ''
        for t in self.joiningToons:
            joiningToons += str(toons.index(t))

        pendingToons = ''
        for t in self.pendingToons:
            pendingToons += str(toons.index(t))

        activeToons = ''
        for t in self.activeToons:
            activeToons += str(toons.index(t))

        runningToons = ''
        for t in self.runningToons:
            runningToons += str(toons.index(t))

        members = [
            suits,
            joiningSuits,
            pendingSuits,
            activeSuits,
            toons,
            joiningToons,
            pendingToons,
            activeToons,
            runningToons
        ]
        return members + [globalClockDelta.getRealNetworkTime()]

    def d_adjust(self):
        self.sendUpdate('adjust', [globalClockDelta.getRealNetworkTime()])

    def getInteractivePropTrackBonus(self):
        return self.interactivePropTrackBonus

    def getZoneId(self):
        return self.zoneId

    def getTaskZoneId(self):
        return self.zoneId

    def getMovie(self):
        suitIds = [s.doId for s in self.activeSuits]

        p = [
            self.activeToons,
            suitIds,
            self.toonMovieAttacks,
            self.suitMovieAttacks
        ]
        return p

    def d_setChosenToonAttacks(self):
        self.notify.debug('Setting client toon attacks...')
        self.sendUpdate('setChosenToonAttacks', [self.getChosenToonAttacks()])

    def getChosenToonAttacks(self):
        attacks = []
        for ta in self.toonAttacks.values():
            attacks.append(ta.toList())
        return attacks

    def addSuit(self, suit):
        self.notify.debug('Adding suit: %d' % suit.doId)
        self.newSuits.append(suit)
        self.suits.append(suit)
        self.numSuitsEver += 1

    def __joinSuit(self, suit):
        self.notify.debug('Joining suit: %d' % suit.doId)
        self.joiningSuits.append(suit)
        timeout = SuitBattleGlobals.MAX_JOIN_T + SuitBattleGlobals.SERVER_BUFFER_TIME
        taskName = self.uniqueName('joining-timeout-%d' % suit.doId)
        self.__addJoinResponse(suit.doId, taskName)
        self.taskNames.append(taskName)
        taskMgr.doMethodLater(timeout, self.__serverJoinDone, taskName, extraArgs=(suit.doId, taskName))

    def __serverJoinDone(self, avId, taskName):
        self.notify.debug('Joining for av: %d timed out' % avId)
        self.__removeTaskName(taskName)
        self.__makeAvPending(avId)
        return Task.done

    def __makeAvPending(self, avId):
        self.notify.debug('Making av %d pending' % avId)
        self.__removeJoinResponse(avId)
        self.__removeTaskName(self.uniqueName('joining-timeout-%d' % avId))
        if self.toons.count(avId) > 0:
            self.joiningToons.remove(avId)
            self.pendingToons.append(avId)
        else:
            suit = self.findSuit(avId)
            if suit is not None:
                if not suit.isEmpty():
                    if not self.joiningSuits.count(suit) == 1:
                        self.notify.warning('__makeAvPending(%d) in zone: %d' % (avId, self.zoneId))
                        self.notify.warning('toons: %s' % self.toons)
                        self.notify.warning('joining toons: %s' % self.joiningToons)
                        self.notify.warning('pending toons: %s' % self.pendingToons)
                        self.notify.warning('suits: %s' % self.suits)
                        self.notify.warning('joining suits: %s' % self.joiningSuits)
                        self.notify.warning('pending suits: %s' % self.pendingSuits)
                    self.joiningSuits.remove(suit)
                    self.pendingSuits.append(suit)
            else:
                self.notify.warning('makeAvPending() %d not in toons or suits' % avId)
                return
        self.d_setMembers()
        self.needAdjust = 1
        self.__requestAdjust()
        return

    def suitRequestJoin(self, suit):
        self.notify.debug('Suit %d requesting to join' % suit.getDoId())
        if suit in self.suits:
            self.notify.warning('Suit %d already in this battle' % suit.getDoId())
            return 0
        if self.suitCanJoin():
            self.addSuit(suit)
            self.__joinSuit(suit)
            self.d_setMembers()
            suit.prepareToJoinBattle()
            return 1
        else:
            self.notify.warning('suitRequestJoin() - not joinable - joinable state: %s max suits: %d' % (self.joinableFsm.getCurrentState().getName(), self.maxSuits))
            return 0

    def acceptUnexpectedExit(self, avId):
        event = self.air.getAvatarExitEvent(avId)
        self.avatarExitEvents.append(event)
        self.accept(event, self.__handleUnexpectedExit, extraArgs=[avId])

    def acceptSuddenExit(self, avId):
        event = 'inSafezone-%s' % avId
        self.avatarExitEvents.append(event)
        self.accept(event, self.__handleSuddenExit, extraArgs=[avId, 0])

    def addToon(self, avId):
        self.notify.debug('Adding Toon: %d' % avId)
        toon = self.air.doId2do.get(avId)
        if toon is None:
            return False
        toon.stopToonUp()
        self.acceptUnexpectedExit(avId)
        self.acceptSuddenExit(avId)
        self.newToons.append(avId)
        self.toons.append(avId)
        toon.b_setBattleId(self.getDoId())
        messageToonAdded = 'Battle adding toon %s' % avId
        messenger.send(messageToonAdded, [avId])
        self.adjustingResponses[avId] = 0
        return True

    def __handleSuddenExit(self, avId, code):
        self.notify.debug('handleSuddenExit %s %s' % (avId, code))
        self.__removeToon(avId)
        if self.fsm.getCurrentState().getName() in ('PlayMovie', 'MakeMovie'):
            self.exitedToons.append(avId)
        self.d_setMembers()
        if len(self.toons) == 0:
            self.end()
        else:
            self.needAdjust = 1
            self.__requestAdjust()

    def __joinToon(self, avId, pos):
        self.joiningToons.append(avId)
        toPendingTime = SuitBattleGlobals.MAX_JOIN_T + SuitBattleGlobals.SERVER_BUFFER_TIME
        taskName = self.taskName('joining-timeout-%d' % avId)
        self.__addJoinResponse(avId, taskName, toon=1)
        taskMgr.doMethodLater(toPendingTime, self.__serverJoinDone, taskName, extraArgs=(avId, taskName))
        self.taskNames.append(taskName)

    def __makeToonRun(self, toonId, updateAttacks):
        self.activeToons.remove(toonId)
        self.toonGone = 1
        self.runningToons.append(toonId)
        taskName = self.taskName('running-toon-%d' % toonId)
        taskMgr.doMethodLater(SuitBattleGlobals.TOON_RUN_T, self.__serverRunDone, taskName, extraArgs=(toonId, updateAttacks, taskName))
        self.taskNames.append(taskName)

    def __serverRunDone(self, toonId, updateAttacks, taskName):
        self.notify.debug('run for toon: %d timed out on server' % toonId)
        self.__removeTaskName(taskName)
        self.__removeToon(toonId)
        self.d_setMembers()
        if len(self.toons) == 0:
            self.notify.debug('last toon is gone - battle is finished')
            self.b_setState('Resume')
        else:
            if updateAttacks == 1:
                self.d_setChosenToonAttacks()
            self.needAdjust = 1
            self.__requestAdjust()
        return Task.done

    def __requestAdjust(self):
        if not self.fsm:
            return
        cstate = self.fsm.getCurrentState().getName()
        if cstate in ('WaitForInput', 'WaitForJoin', 'ApplyAttacks'):
            if self.adjustFsm.getCurrentState().getName() == 'NotAdjusting':
                if self.needAdjust == 1:
                    self.d_adjust()
                    self.adjustingSuits = []
                    for s in self.pendingSuits:
                        self.adjustingSuits.append(s)

                    self.adjustingToons = []
                    for t in self.pendingToons:
                        self.adjustingToons.append(t)

                    if cstate == 'WaitForJoin':
                        self.b_setState('WaitForInput')

                    self.adjustFsm.request('Adjusting')
                else:
                    self.notify.debug('Did not adjust, no need to')
            else:
                self.notify.debug('Did not adjust, already adjusting')
        else:
            self.notify.debug('Did not adjust, in invalid state: %s' % cstate)

    def __handleUnexpectedExit(self, avId):
        disconnectCode = self.air.getAvatarDisconnectReason(avId)
        self.notify.warning('toon: %d exited unexpectedly, reason %s' % (avId, disconnectCode))
        userAborted = disconnectCode == ToontownGlobals.DisconnectCloseWindow
        self.__removeToon(avId)

    def __removeToon(self, toonId):
        self.notify.debug('__removeToon %s ' % toonId)
        if toonId not in self.toons:
            return
        self.__removeToonTasks(toonId)
        self.toons.remove(toonId)
        self.removeJoiningToon(toonId)
        self.removeAdjustingToon(toonId)
        self.removePendingToon(toonId)
        self.removeActiveToon(toonId)
        event = simbase.air.getAvatarExitEvent(toonId)
        self.avatarExitEvents.remove(event)
        self.ignore(event)
        event = 'inSafezone-%s' % toonId
        self.avatarExitEvents.remove(event)
        self.ignore(event)
        toon = self.air.doId2do.get(toonId)
        if toon:
            toon.b_setBattleId(0)
            messageToonReleased = 'Battle releasing toon %s' % toon.doId
            messenger.send(messageToonReleased, [toon.doId])

    def toonRequestJoin(self, x, y, z):
        toonId = self.air.getAvatarIdFromSender()
        self.notify.debug('Toon requesting to join %d' % toonId)
        self.signupToon(toonId, x, y, z)

    def signupToon(self, toonId, x, y, z):
        if toonId in self.toons:
            self.notify.warning('Failed to signup toon %d, already in toons %s' % (toonId, self.toons))
            return
        if self.toonCanJoin():
            if self.addToon(toonId):
                self.__joinToon(toonId, Point3(x, y, z))
                self.d_setMembers()
        else:
            self.notify.warning('Failed to signup toon %d, unjoinable' % toonId)
            self.d_denyLocalToonJoin(toonId)

    def d_denyLocalToonJoin(self, toonId):
        self.notify.debug('Denying toon join request for toon %d' % toonId)
        self.sendUpdateToAvatarId(toonId, 'denyLocalToonJoin', [])

    def allToonsResponded(self):
        for t in self.toons:
            if self.responses[t] == 0:
                return 0

        return 1

    def attacksSet(self):
        self.notify.debug('attacksSet?\ntoonAttacks: %s\nactiveToons: %s' % (self.toonAttacks, self.activeToons))
        if len(self.toonAttacks.keys()) != len(self.activeToons):
            return False
        for toonId, ta in self.toonAttacks.items():
            if ta.attackId == SuitBattleGlobals.NO_ATTACK:
                # This attack isn't a valid response
                return False
        return True

    def __resetAdjustingResponses(self):
        self.adjustingResponses = {}
        for t in self.toons:
            self.adjustingResponses[t] = 0

        self.ignoreAdjustingResponses = 0

    def __allAdjustingToonsResponded(self):
        for t in self.toons:
            if self.adjustingResponses[t] == 0:
                return 0

        self.ignoreAdjustingResponses = 1
        return 1

    def __removeAdjustingResponse(self, toonId):
        if toonId in self.adjustingResponses:
            del self.adjustingResponses[toonId]
            if self.ignoreAdjustingResponses == 0 and len(self.toons) > 0:
                if self.__allAdjustingToonsResponded():
                    self.__adjustDone()

    def __addJoinResponse(self, avId, taskName, toon = 0):
        if toon == 1:
            for jr in self.joinResponses.values():
                jr[avId] = 0

        self.joinResponses[avId] = {}
        for t in self.toons:
            self.joinResponses[avId][t] = 0

        self.joinResponses[avId]['taskName'] = taskName

    def __removeJoinResponses(self, avId):
        self.__removeJoinResponse(avId)
        removedOne = 0
        for j in self.joinResponses.values():
            if avId in j:
                del j[avId]
                removedOne = 1

        if removedOne == 1:
            for t in self.joiningToons:
                if self.__allToonsRespondedJoin(t):
                    self.__makeAvPending(t)

    def __removeJoinResponse(self, avId):
        if avId in self.joinResponses:
            taskMgr.remove(self.joinResponses[avId]['taskName'])
            del self.joinResponses[avId]

    def __allToonsRespondedJoin(self, avId):
        jr = self.joinResponses[avId]
        for t in self.toons:
            if jr[t] == 0:
                return 0

        return 1

    def __cleanupJoinResponses(self):
        for jr in self.joinResponses.values():
            taskMgr.remove(jr['taskName'])
            del jr

    def adjustDone(self):
        toonId = self.air.getAvatarIdFromSender()
        if self.ignoreAdjustingResponses == 1:
            self.notify.debug('adjustDone() - ignoring toon: %d' % toonId)
            return
        elif self.adjustFsm.getCurrentState().getName() != 'Adjusting':
            self.notify.warning('adjustDone() - in state %s' % self.fsm.getCurrentState().getName())
            return
        elif self.toons.count(toonId) == 0:
            self.notify.warning('adjustDone() - toon: %d not in toon list' % toonId)
            return
        self.adjustingResponses[toonId] += 1
        self.notify.debug('toon: %d done adjusting' % toonId)
        if self.__allAdjustingToonsResponded():
            self.__adjustDone()

    def timeout(self):
        toonId = self.air.getAvatarIdFromSender()
        if self.fsm.getCurrentState().getName() != 'WaitForInput':
            self.notify.warning('timeout() - in state: %s' % self.fsm.getCurrentState().getName())
            return
        elif self.toons.count(toonId) == 0:
            self.notify.warning('timeout() - toon: %d not in toon list' % toonId)
            return
        self.notify.debug('Toon %d timed out' % toonId)
        # Lets make the toon pass since it timed out
        self.toonAttacks[toonId] = BattleAttack.ToonBattleAttack(toonId, Gag.PASS)
        self.d_setChosenToonAttacks()
        if self.attacksSet():
            self.notify.debug('All toons attacked, playing movie now...')
            self.fsm.request('MakeMovie')

    def requestMovieDone(self):
        toonId = self.air.getAvatarIdFromSender()
        currState = self.fsm.getCurrentState()
        if currState.getName() != 'PlayMovie':
            self.notify.warning('Toon %s requested movie done but our state is %s' % (toonId, currState.getName()))
            return
        elif toonId not in self.toons:
            self.notify.warning('Toon %s requested movie done but he\'s not in our toon list %s' % (toonId, self.toons))
            return
        # Add this toon to our movie responses
        self.movieResponses[toonId] = True
        self.notify.debug('Toon: %d is done with movie' % toonId)
        if self.__allMovieReponsesDone():
            self.notify.debug('All toons done with movie, continuing...')
            self.endMovie()
        else:
            self.timer.stop()
            self.timer.startCallback(SuitBattleGlobals.TIMEOUT_PER_USER, self.__serverMovieDone)

    def __resetMovieResponses(self):
        self.movieResponses.clear()

    def __allMovieReponsesDone(self):
        toonCount = len(self.pendingToons) + len(self.activeToons)
        responsesLength = len(self.movieResponses)
        return toonCount >= responsesLength

    def joinDone(self, avId):
        toonId = self.air.getAvatarIdFromSender()
        self.notify.debug('Got join done from %d' % toonId)
        if self.toons.count(toonId) == 0:
            self.notify.warning('joinDone() - toon: %d not in toon list' % toonId)
            return
        if avId not in self.joinResponses:
            self.notify.debug('joinDone() - no entry for: %d - ignoring: %d' % (avId, toonId))
            return
        jr = self.joinResponses[avId]
        if toonId in jr:
            jr[toonId] += 1
        self.notify.debug('client with localToon: %d done joining av: %d' % (toonId, avId))
        if self.__allToonsRespondedJoin(avId):
            self.__makeAvPending(avId)

    def requestAttack(self, attackId, targetId):
        toonId = self.air.getAvatarIdFromSender()
        self.notify.debug('requestAttack: %s' % [toonId, attackId, targetId])
        currState = self.fsm.getCurrentState().getName()
        if currState != 'WaitForInput':
            # Can't request an attack out of this state
            self.notify.warning('Toon %s requested to attack while we were in the %s state' % (toonId, currState))
            return
        elif toonId not in self.activeToons:
            # Can't attack unless you're an active toon
            self.notify.warning('Toon %d tried to attack without being active' % toonId)
            return
        toon = self.air.doId2do.get(toonId)
        if toon is None:
            # No toon
            self.notify.warning('Invalid toon %s' % toonId)
            return
        if not toon.inventory.isEquipped(attackId) and attackId not in Gag.AlwaysEquipped:
            # This attack is not equipped, and needs to be equipped
            self.notify.warning('Toon %s tried to use an attack he doesnt have equipped' % toonId)
            return
        attack = Gag.Gags.get(attackId)
        if attack is None and attackId != SuitBattleGlobals.NO_ATTACK:
            # Invalid attackId
            self.notify.warning('Toon %s tried to use an invalid attack %s' % (toonId, attackId))
            return

        self.toonAttacks[toonId] = BattleAttack.ToonBattleAttack(toonId, attackId, targetId)
        self.d_setChosenToonAttacks()
        self.notify.debug('Toon: %d chose attack: %s' % (toonId, attackId))
        if self.attacksSet():
            self.notify.debug('All toons attacked, making movie now...')
            # All toons have attacked, lets do stuff with them
            self.fsm.request('MakeMovie')

    def clearMovieAttacks(self):
        self.notify.debug('Clearing movie attacks')
        del self.toonMovieAttacks[:]
        del self.suitMovieAttacks[:]
        self.toonMovieAttacks = []
        self.suitMovieAttacks = []

    def suitCanJoin(self):
        return len(self.suits) < self.maxSuits and self.isJoinable()

    def toonCanJoin(self):
        return len(self.toons) < 4 and self.isJoinable()

    def enterOff(self):
        return None

    def exitOff(self):
        return None

    def enterFaceOff(self):
        return None

    def exitFaceOff(self):
        return None

    def enterWaitForJoin(self):
        self.notify.debug('Waiting for join...')
        return None

    def exitWaitForJoin(self):
        self.notify.debug('Done waiting for join.')
        return None

    def enterWaitForInput(self):
        self.notify.debug('Waiting for Input...')
        # Clear the attacks
        self.clearAttacks()
        self.d_setChosenToonAttacks()
        # Allow toons to run or join
        self.joinableFsm.request('Joinable')
        self.runnableFsm.request('Runnable')
        # Adjust cogs and toons
        self.__requestAdjust()

    def exitWaitForInput(self):
        self.timer.stop()

    def __serverTimedOut(self):
        self.notify.debug('Timed out waiting for toon attacks...')
        self.fsm.request('MakeMovie')

    def enterMakeMovie(self):
        self.notify.debug('Making movie...')
        self.runnableFsm.request('Unrunnable')
        # Generate our new movie attacks
        tmas, smas = self.battleCalc.generateMovieAttacks()
        # Set movie attacks we generated
        self.b_setMovieAttacks(tmas, smas)
        # Now play the movie
        self.b_setState('PlayMovie')

    def exitMakeMovie(self):
        pass

    def enterPlayMovie(self):
        self.notify.debug('Playing movie...')
        # Reset movie done responses
        self.__resetMovieResponses()
        # Estimate the time this movie will take
        movieTime = SuitBattleGlobals.TOON_ATTACK_TIME * (len(self.activeToons)) + SuitBattleGlobals.SUIT_ATTACK_TIME * len(self.activeSuits) + SuitBattleGlobals.SERVER_BUFFER_TIME
        self.timer.startCallback(movieTime, self.__serverMovieDone)

    def exitPlayMovie(self):
        self.notify.debug('Exiting Movie...')
        # Stop the server movie timer
        self.timer.stop()
        # Reset movie done responses
        self.__resetMovieResponses()

    def __serverMovieDone(self):
        self.notify.debug('Server\'s movie timed out. Ending movie....')
        self.endMovie()

    def getMovieAttacks(self):
        tmas = []
        smas = []
        for tma in self.toonMovieAttacks:
            tmas.append(tma.toList())
        for sma in self.suitMovieAttacks:
            smas.append(sma.toList())

        return [tmas, smas]

    def b_setMovieAttacks(self, tmas, smas):
        self.setMovieAttacks(tmas, smas)
        self.d_setMovieAttacks()

    def setMovieAttacks(self, tmas, smas):
        self.toonMovieAttacks = tmas
        self.suitMovieAttacks = smas

    def d_setMovieAttacks(self):
        self.sendUpdate('setMovieAttacks', self.getMovieAttacks())

    def endMovie(self):
        self.fsm.request('ApplyAttacks')

    def enterApplyAttacks(self):
        self.notify.debug('Applying attacks...')
        # For each attack
        for tma in self.toonMovieAttacks:
            if not tma.hit:
                continue
            gag = Gag.Gags.get(tma.attackId)
            if gag is None:
                self.notify.warning('Attempted to apply invalid gag with id %s' % tma.attackId)
                return
            targets = []
            # Setup targets
            if gag.requiresTarget():
                targetId = tma.targetId
                if gag.targetType == Gag.Gag.TargetSingleAlly:
                    if targetId in self.activeToons:
                        targets.append(self.air.doId2do.get(targetId))
                    else:
                        self.notify.warning('Invalid target %s for ally attack' % targetId)
                elif gag.targetType == Gag.Gag.TargetSingleEnemy:
                    suit = self.findSuit(targetId)
                    if suit and suit in self.activeSuits:
                        targets.append(suit)
                    else:
                        self.notify.warning('Invalid target %s for enemy attack' % targetId)
            elif gag.targetType == Gag.Gag.TargetEnemies:
                targets += self.activeSuits
            else:
                self.notify.warning('Targeting for target type %s not yet implemented.' % gag.targetType)

            # Apply effects to targets
            for target in targets:
                gag.effect.b_applyTo(target)

        # TODO: Apply suit movie attacks here

        # Check if anyone died
        for suit in self.activeSuits:
            self.notify.debug('Suit %d with %d hp' % (suit.doId, suit.getHp()))
            if suit.getHp() <= 0:
                # Suit died
                self.__removeSuit(suit)
                self.needAdjust = 1
        for toonId in self.activeToons:
            toon = self.air.doId2do.get(toonId)
            if toon and toon.getHp() <= 0:
                # Toon died
                self.__removeToon(toon)
                self.needAdjust = 1

        # Set members in the event some died just now
        self.d_setMembers()
        self.__requestAdjust()

        # Check which state to go into next
        if len(self.activeToons) and len(self.activeSuits):
            # We have toons and suits in the battle, let's allow them to attack each other
            self.b_setState('WaitForInput')
        elif len(self.activeToons) and (len(self.joiningSuits) or len(self.pendingSuits)):
            # We have no suits but a suit is joining, wait for them to join
            self.b_setState('WaitForJoin')
        elif len(self.activeSuits) and (len(self.joiningToons) or len(self.pendingToons)):
            # We have no toons but a toon is joining, wait for them to join
            self.b_setState('WaitForJoin')
        else:
            # We either don't have any suits or toons, this battle is over...
            self.b_setState('Resume')

    def exitApplyAttacks(self):
        # Clear our movie attacks, we're done with them
        self.clearMovieAttacks()
        self.d_setMovieAttacks()

    def enterResume(self):
        self.notify.debug('Resuming...')
        for suit in self.suits:
            self.notify.info('battle done, resuming suit: %d' % suit.doId)
            if suit.isDeleted():
                self.notify.info('whoops, suit %d is deleted.' % suit.doId)
            else:
                suit.resume()

        self.suits = []
        self.joiningSuits = []
        self.pendingSuits = []
        self.adjustingSuits = []
        self.activeSuits = []
        for toonId in self.toons:
            toon = simbase.air.doId2do.get(toonId)
            if toon:
                toon.b_setBattleId(0)
                messageToonReleased = 'Battle releasing toon %s' % toon.doId
                messenger.send(messageToonReleased, [toon.doId])

        for exitEvent in self.avatarExitEvents:
            self.ignore(exitEvent)

        eventMsg = {}
        for encounter in self.suitsKilledThisBattle:
            cog = encounter['type']
            level = encounter['level']
            msgName = '%s%s' % (cog, level)
            if encounter['isSkelecog']:
                msgName += '+'
            if msgName in eventMsg:
                eventMsg[msgName] += 1
            else:
                eventMsg[msgName] = 1

        msgText = ''
        for msgName, count in eventMsg.items():
            if msgText != '':
                msgText += ','
            msgText += '%s%s' % (count, msgName)

        self.air.writeServerEvent('battleCogsDefeated', self.doId, '%s|%s' % (msgText, self.getTaskZoneId()))

    def exitResume(self):
        pass

    def isJoinable(self):
        return self.joinableFsm.getCurrentState().getName() == 'Joinable'

    def enterJoinable(self):
        self.notify.debug('STATE: Joinable')
        return None

    def exitJoinable(self):
        return None

    def enterUnjoinable(self):
        self.notify.debug('STATE: Unjoinable')
        return None

    def exitUnjoinable(self):
        return None

    def isRunnable(self):
        return self.runnableFsm.getCurrentState().getName() == 'Runnable'

    def enterRunnable(self):
        self.notify.debug('STATE: Runnable')
        return None

    def exitRunnable(self):
        return None

    def enterUnrunnable(self):
        self.notify.debug('STATE: Unrunnable')
        return None

    def exitUnrunnable(self):
        return None

    def __estimateAdjustTime(self):
        self.needAdjust = 0
        adjustTime = 0
        if len(self.pendingSuits) > 0 or self.suitGone == 1:
            self.suitGone = 0
            pos0 = BattleGlobals.SuitPendingPoints[0][0]
            pos1 = BattleGlobals.SuitPoints[0][0][0]
            adjustTime = self.calcSuitMoveTime(pos0, pos1)
        if len(self.pendingToons) > 0 or self.toonGone == 1:
            self.toonGone = 0
            if adjustTime == 0:
                pos0 = BattleGlobals.ToonPendingPoints[0][0]
                pos1 = BattleGlobals.ToonPoints[0][0][0]
                adjustTime = self.calcToonMoveTime(pos0, pos1)
        return adjustTime

    def enterAdjusting(self):
        self.notify.debug('Adjusting...')
        self.timer.stop()
        self.__resetAdjustingResponses()
        self.adjustingTimer.startCallback(self.__estimateAdjustTime() + SuitBattleGlobals.SERVER_BUFFER_TIME, self.__serverAdjustingDone)

    def exitAdjusting(self):
        self.notify.debug('Exiting Adjusting...')
        currStateName = self.fsm.getCurrentState().getName()
        if currStateName == 'WaitForInput':
            self.timer.restart()
        elif currStateName == 'WaitForJoin':
            self.b_setState('WaitForInput')
        self.adjustingTimer.stop()

    def __serverAdjustingDone(self):
        if self.needAdjust == 1:
            self.adjustFsm.request('NotAdjusting')
            self.__requestAdjust()
        else:
            self.notify.debug('adjusting timed out on the server')
            self.ignoreAdjustingResponses = 1
            self.__adjustDone()

    def __adjustDone(self):
        for s in self.adjustingSuits:
            self.pendingSuits.remove(s)
            self.activeSuits.append(s)

        self.adjustingSuits = []
        for toon in self.adjustingToons:
            self.removePendingToon(toon)
            self.addActiveToon(toon)

        self.adjustingToons = []
        self.d_setMembers()
        self.adjustFsm.request('NotAdjusting')
        if self.needAdjust == 1:
            self.notify.debug('__adjustDone() - need to adjust again')
            self.__requestAdjust()

    def enterNotAdjusting(self):
        self.notify.debug('Not Adjusting...')
        return None

    def exitNotAdjusting(self):
        return None

    def end(self):
        self.notify.debug('Ending...')
        self.__removeAllTasks()
        self.timer.stop()
        self.adjustingTimer.stop()
        self.b_setState('Resume')

    def addActiveToon(self, toon):
        if toon not in self.activeToons:
            self.activeToons.append(toon)
        else:
            self.notify.warning('Tried to make toon active who was already active %s' % toon)

    def removeActiveToon(self, toon):
        if toon in self.activeToons:
            self.activeToons.remove(toon)

    def removePendingToon(self, toon):
        if toon in self.pendingToons:
            self.pendingToons.remove(toon)

    def removeJoiningToon(self, toon):
        if toon in self.joiningToons:
            self.joiningToons.remove(toon)

    def removeRunningToon(self, toon):
        if toon in self.runningToons:
            self.runningToons.remove(toon)

    def removeAdjustingToon(self, toon):
        if toon in self.adjustingToons:
            self.adjustingToons.remove(toon)

    def getPosition(self):
        return [self.pos[0], self.pos[1], self.pos[2]]

    def d_setInitialSuitPos(self):
        self.sendUpdate('setInitialSuitPos', self.getInitialSuitPos())

    def getInitialSuitPos(self):
        return [
            self.initialSuitPos[0],
            self.initialSuitPos[1],
            self.initialSuitPos[2]
        ]


@magicWord(category=CATEGORY_PROGRAMMER)
def skipMovie():
    invoker = spellbook.getInvoker()
    battleId = invoker.getBattleId()
    if not battleId:
        return 'You are not currently in a battle!'
    battle = simbase.air.doId2do.get(battleId)
    battle.endMovie()
    return 'Battle movie skipped.'
