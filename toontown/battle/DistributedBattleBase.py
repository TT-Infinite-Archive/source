from pandac.PandaModules import *
from direct.actor import Actor
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.distributed.ClockDelta import *
from direct.distributed import DistributedNode
from direct.fsm import ClassicFSM
from direct.fsm import State
from direct.interval.IntervalGlobal import *
from direct.task.Task import Task
from otp.avatar import Emote
from toontown.battle import BattleParticles, BattleAttack
from toontown.battle import BattleProps
from toontown.battle import Movie
from toontown.battle import MovieUtil
from toontown.battle.BattleBase import *
from toontown.distributed import DelayDelete
from toontown.nametag import NametagGlobals
from toontown.hood import ZoneUtil
from toontown.suit import Suit
from toontown.toonbase.ToonBaseGlobal import *
from toontown.toonbase import ToontownBattleGlobals
from toontown.toon import InventoryGlobals


class DistributedBattleBase(DistributedNode.DistributedNode, BattleBase):
    notify = directNotify.newCategory('DistributedBattleBase')
    camPos = ToontownBattleGlobals.BattleCamDefaultPos
    camHpr = ToontownBattleGlobals.BattleCamDefaultHpr
    camFov = ToontownBattleGlobals.BattleCamDefaultFov
    camMenuFov = ToontownBattleGlobals.BattleCamMenuFov
    camJoinPos = ToontownBattleGlobals.BattleCamJoinPos
    camJoinHpr = ToontownBattleGlobals.BattleCamJoinHpr
    id = 0

    def __init__(self, cr, townBattle):
        DistributedNode.DistributedNode.__init__(self, cr)
        NodePath.__init__(self)
        self.assign(render.attachNewNode(self.uniqueBattleName('distributed-battle')))
        BattleBase.__init__(self)
        self.bossBattle = 0
        self.townBattle = townBattle
        self.townBattle.setBattle(self)
        self.__battleCleanedUp = 0
        self.activeIntervals = {}
        self.localToonJustJoined = 0
        self.choseAttackAlready = 0
        self.toons = []
        self.exitedToons = []
        self.membersKeep = None
        self.faceOffName = self.uniqueBattleName('faceoff')
        self.localToonBattleEvent = self.uniqueBattleName('localtoon-battle-event')
        self.adjustName = self.uniqueBattleName('adjust')
        self.timerCountdownTaskName = self.uniqueBattleName('timer-countdown')
        self.movie = Movie.Movie(self)
        self.timer = Timer()
        self.needAdjustTownBattle = 0
        self.streetBattle = 1
        self.levelBattle = 0
        self.localToonFsm = ClassicFSM.ClassicFSM('LocalToon', [
            State.State('HasLocalToon', self.enterHasLocalToon, self.exitHasLocalToon, ['NoLocalToon', 'WaitForServer']),
            State.State('NoLocalToon', self.enterNoLocalToon, self.exitNoLocalToon, ['HasLocalToon', 'WaitForServer']),
            State.State('WaitForServer', self.enterWaitForServer, self.exitWaitForServer, ['HasLocalToon', 'NoLocalToon'])
        ], 'WaitForServer', 'WaitForServer')
        self.localToonFsm.enterInitialState()
        self.fsm = ClassicFSM.ClassicFSM('DistributedBattle', [
            State.State('Off', self.enterOff, self.exitOff, ['FaceOff', 'WaitForInput', 'WaitForJoin', 'PlayMovie', 'Resume']),
            State.State('FaceOff', self.enterFaceOff, self.exitFaceOff, ['WaitForInput']),
            State.State('WaitForJoin', self.enterWaitForJoin, self.exitWaitForJoin, ['WaitForInput', 'Resume']),
            State.State('WaitForInput', self.enterWaitForInput, self.exitWaitForInput, ['PlayMovie', 'WaitForJoin', 'Resume']),
            State.State('PlayMovie', self.enterPlayMovie, self.exitPlayMovie, ['WaitForInput', 'WaitForJoin', 'Resume']),
            State.State('Resume', self.enterResume, self.exitResume, [])
        ], 'Off', 'Off')
        self.fsm.enterInitialState()
        self.adjustFsm = ClassicFSM.ClassicFSM('Adjust', [
            State.State('Adjusting', self.enterAdjusting, self.exitAdjusting, ['NotAdjusting']),
            State.State('NotAdjusting', self.enterNotAdjusting, self.exitNotAdjusting, ['Adjusting'])], 'NotAdjusting', 'NotAdjusting')
        self.adjustFsm.enterInitialState()
        self.interactiveProp = None
        self.toonAttacks = {}
        self.toonMovieAttacks = []
        self.suitMovieAttacks = []

    def uniqueBattleName(self, name):
        DistributedBattleBase.id += 1
        return name + '-%d' % DistributedBattleBase.id

    def generate(self):
        self.notify.debug('Generating %s...' % self.doId)
        DistributedNode.DistributedNode.generate(self)
        self.__battleCleanedUp = 0
        self.reparentTo(render)

    def storeInterval(self, interval, name):
        if name in self.activeIntervals:
            ival = self.activeIntervals[name]
            if hasattr(ival, 'delayDelete') or hasattr(ival, 'delayDeletes'):
                self.clearInterval(name, finish=1)
        self.activeIntervals[name] = interval

    def __cleanupIntervals(self):
        for interval in self.activeIntervals.values():
            interval.finish()
            DelayDelete.cleanupDelayDeletes(interval)

        self.activeIntervals = {}

    def clearInterval(self, name, finish = 0):
        if name in self.activeIntervals:
            ival = self.activeIntervals[name]
            if finish:
                ival.finish()
            else:
                ival.pause()
            if name in self.activeIntervals:
                DelayDelete.cleanupDelayDeletes(ival)
                if name in self.activeIntervals:
                    del self.activeIntervals[name]
        else:
            self.notify.debug('interval: %s already cleared' % name)

    def finishInterval(self, name):
        if name in self.activeIntervals:
            interval = self.activeIntervals[name]
            interval.finish()

    def disable(self):
        self.notify.debug('Disabling %s...' % self.doId)
        self.cleanupBattle()
        DistributedNode.DistributedNode.disable(self)

    def battleCleanedUp(self):
        return self.__battleCleanedUp

    def cleanupBattle(self):
        if self.__battleCleanedUp:
            return
        self.notify.debug('Cleaning up battle %s...' % self.doId)
        self.__battleCleanedUp = 1
        self.__cleanupIntervals()
        self.fsm.requestFinalState()
        if self.hasLocalToon():
            self.removeLocalToon()
            base.camLens.setMinFov(ToontownGlobals.DefaultCameraFov/(4./3.))
        self.localToonFsm.request('WaitForServer')
        self.ignoreAll()

        self.suits = []
        self.pendingSuits = []
        self.joiningSuits = []
        self.activeSuits = []
        self.toons = []
        self.joiningToons = []
        self.pendingToons = []
        self.activeToons = []
        self.runningToons = []
        self.__stopTimer()
        self.__cleanupIntervals()
        self._removeMembersKeep()
        return

    def delete(self):
        self.notify.debug('Deleting %s...' % self.doId)
        self.__cleanupIntervals()
        self._removeMembersKeep()
        self.movie.cleanup()
        del self.townBattle
        self.removeNode()
        self.fsm = None
        self.localToonFsm = None
        self.adjustFsm = None
        self.__stopTimer()
        self.timer = None
        DistributedNode.DistributedNode.delete(self)
        return

    def pause(self):
        self.notify.debug('Pausing...')
        self.timer.stop()

    def unpause(self):
        self.notify.debug('Unpausing...')
        self.timer.resume()

    def findSuit(self, suitId):
        for s in self.suits:
            if s.doId == suitId:
                return s

        return None

    def findToon(self, toonId):
        toon = self.cr.doId2do.get(toonId)
        if toon is None:
            return None
        for t in self.toons:
            if t == toon:
                return t

    def getToonIndex(self, toonId):
        toon = self.findToon(toonId)
        return self.activeToons.index(toon)

    def getSuitIndex(self, suitId):
        suit = self.findSuit(suitId)
        return self.activeSuits.index(suit)

    def getActorPosHpr(self, actor, actorList = []):
        if isinstance(actor, Suit.Suit):
            if actorList == []:
                actorList = self.activeSuits
            if actorList.count(actor) != 0:
                numSuits = len(actorList) - 1
                index = actorList.index(actor)
                point = BattleGlobals.SuitPoints[numSuits][index]
                return (Point3(point[0]), VBase3(point[1], 0.0, 0.0))
            else:
                self.notify.warning('getActorPosHpr() - suit not active')
        else:
            if actorList == []:
                actorList = self.activeToons
            if actorList.count(actor) != 0:
                numToons = len(actorList) - 1
                index = actorList.index(actor)
                point = BattleGlobals.ToonPoints[numToons][index]
                return (Point3(point[0]), VBase3(point[1], 0.0, 0.0))
            else:
                self.notify.warning('getActorPosHpr() - toon not active')

    def setLevelDoId(self, levelDoId):
        pass

    def setBattleCellId(self, battleCellId):
        pass

    def setInteractivePropTrackBonus(self, trackBonus):
        self.interactivePropTrackBonus = trackBonus

    def getInteractivePropTrackBonus(self):
        return self.interactivePropTrackBonus

    def setPosition(self, x, y, z):
        self.notify.debug('Setting position (%s, %s, %s)' % (x, y, z))
        pos = Point3(x, y, z)
        self.setPos(pos)

    def setInitialSuitPos(self, x, y, z):
        self.initialSuitPos = Point3(x, y, z)
        self.headsUp(self.initialSuitPos)

    def setZoneId(self, zoneId):
        self.zoneId = zoneId

    def setBossBattle(self, value):
        self.bossBattle = value

    def setState(self, state, timestamp):
        self.notify.debug('Setting state: %s' % state)
        if self.__battleCleanedUp:
            return
        self.fsm.request(state, [globalClockDelta.localElapsedTime(timestamp)])

    def setSuits(self, suits):
        self.notify.debug('Setting suits %s to overwrite %s' % (suits, self.suits))
        # Check for removed suits
        for suit in self.suits:
            # This suit is removed
            if suit.doId not in suits:
                self.__removeSuit(suit)

        # Setup new suits
        del self.suits[:]
        for suitId in suits:
            suit = self.cr.doId2do.get(suitId)
            if suit is None:
                continue
            self.suits.append(suit)

    def setMembers(self, suits, suitsJoining, suitsPending, suitsActive, toons, toonsJoining, toonsPending, toonsActive, toonsRunning, timestamp):
        if self.__battleCleanedUp:
            return
        self.notify.debug('Setting Members: \nSuits: %s Joining: %s Pending: %s Active: %s '
            '\nToons: %s Joining: %s Pending: %s Active: %s Running: %s' % (
            suits,
            suitsJoining,
            suitsPending,
            suitsActive,
            toons,
            toonsJoining,
            toonsPending,
            toonsActive,
            toonsRunning
        ))
        ts = globalClockDelta.localElapsedTime(timestamp)
        self.setSuits(suits)
        for s in suitsJoining:
            suit = self.suits[int(s)]
            if suit not in self.joiningSuits:
                self.makeSuitJoin(suit, ts)

        for s in suitsPending:
            suit = self.suits[int(s)]
            if suit not in self.pendingSuits:
                self.__makeSuitPending(suit)

        activeSuits = []
        for s in suitsActive:
            suit = self.suits[int(s)]
            if suit not in self.activeSuits:
                activeSuits.append(suit)

        oldtoons = self.toons
        self.toons = []
        toonGone = 0
        for t in toons:
            toon = self.cr.doId2do.get(t)
            if toon is None:
                self.notify.warning('setMembers() - toon not in cr!')
                self.toons.append(None)
                toonGone = 1
                continue
            self.toons.append(toon)
            if oldtoons.count(toon) == 0:
                self.notify.debug('setMembers() - add toon: %d' % toon.doId)
                self.__listenForUnexpectedExit(toon)
                toon.stopLookAround()
                toon.stopSmooth()

        for t in oldtoons:
            if self.toons.count(t) == 0:
                if self.__removeToon(t) == 1:
                    self.notify.debug('setMembers() - local toon left battle')
                    return []

        for t in toonsJoining:
            if int(t) < len(self.toons):
                toon = self.toons[int(t)]
                if toon != None and self.joiningToons.count(toon) == 0:
                    self.__makeToonJoin(toon, toonsPending, ts)
            else:
                self.notify.warning('setMembers toonsJoining t=%s not in self.toons %s' % (t, self.toons))

        for t in toonsPending:
            if int(t) < len(self.toons):
                toon = self.toons[int(t)]
                if toon != None and self.pendingToons.count(toon) == 0:
                    self.__makeToonPending(toon, ts)
            else:
                self.notify.warning('setMembers toonsPending t=%s not in self.toons %s' % (t, self.toons))

        for t in toonsRunning:
            toon = self.toons[int(t)]
            if toon != None and self.runningToons.count(toon) == 0:
                self.__makeToonRun(toon, ts)

        activeToons = []
        for t in toonsActive:
            toon = self.toons[int(t)]
            if toon != None and self.activeToons.count(toon) == 0:
                activeToons.append(toon)

        if len(activeSuits) > 0 or len(activeToons) > 0:
            self.__makeAvsActive(activeSuits, activeToons)
        if toonGone == 1:
            validToons = []
            for toon in self.toons:
                if toon != None:
                    validToons.append(toon)

            self.toons = validToons
        currStateName = self.localToonFsm.getCurrentState().getName()
        if self.toons.count(base.localAvatar):
            if oldtoons.count(base.localAvatar) == 0:
                self.notify.debug('setMembers() - local toon just joined')
                if self.streetBattle == 1:
                    base.cr.playGame.getPlace().enterZone(self.zoneId)
                self.localToonJustJoined = 1
            if currStateName != 'HasLocalToon':
                self.localToonFsm.request('HasLocalToon')
        else:
            if oldtoons.count(base.localAvatar):
                self.notify.debug('setMembers() - local toon just ran')
                if self.levelBattle:
                    self.unlockLevelViz()
            if currStateName != 'NoLocalToon':
                self.localToonFsm.request('NoLocalToon')
        return oldtoons

    def adjust(self, timestamp):
        self.notify.debug('Server wants us to adjust')
        if self.__battleCleanedUp:
            self.notify.debug('Battle already cleaned up so we wont adjust.')
            return
        self.adjustFsm.request('Adjusting', [globalClockDelta.localElapsedTime(timestamp)])

    def clearToonAttacks(self):
        self.toonAttacks.clear()

    def clearMovieAttacks(self):
        del self.toonMovieAttacks[:]
        del self.suitMovieAttacks[:]
        self.toonMovieAttacks = []
        self.suitMovieAttacks = []

    def makeMovieAttackFromList(self, list):
        ma = BattleAttack.MovieAttack()
        ma.fromList(list)
        return ma

    def setMovieAttacks(self, toonMovieAttacks, suitMovieAttacks):
        self.notify.debug('Setting movie attacks: %s %s' % (toonMovieAttacks, suitMovieAttacks))
        self.clearMovieAttacks()
        for toonMovieAttack in toonMovieAttacks:
            tma = self.makeMovieAttackFromList(toonMovieAttack)
            self.toonMovieAttacks.append(tma)
        for suitMovieAttack in suitMovieAttacks:
            sma = self.makeMovieAttackFromList(suitMovieAttack)
            self.suitMovieAttacks.append(sma)

    def getMovieAttacks(self):
        toonMovieAttacks = [tma.toList() for tma in self.toonMovieAttacks]
        suitMovieAttacks = [sma.toList() for sma in self.suitMovieAttacks]
        return [toonMovieAttacks, suitMovieAttacks]

    def setChosenToonAttacks(self, toonAttacks):
        self.notify.debug('Setting chosen toon attacks: %s' % toonAttacks)
        self.clearToonAttacks()
        for ta in toonAttacks:
            toonAttack = BattleAttack.ToonBattleAttack()
            toonAttack.fromList(ta)
            self.toonAttacks[toonAttack.attackerId] = toonAttack
        if self.hasLocalToon():
            self.townBattle.updateChosenAttacks()

    def __listenForUnexpectedExit(self, toon):
        self.accept(toon.uniqueName('disable'), self.__handleUnexpectedExit, extraArgs=[toon])
        self.accept(toon.uniqueName('died'), self.__handleDied, extraArgs=[toon])

    def __handleUnexpectedExit(self, toon):
        self.notify.warning('Handling unexpected exit: %d' % toon.doId)
        self.__removeToon(toon, unexpected=1)

    def __handleDied(self, toon):
        self.notify.warning('Handling toon died: %d' % toon.doId)
        if toon == base.localAvatar:
            self.cleanupBattle()

    def delayDeleteMembers(self):
        membersKeep = []
        for t in self.toons:
            membersKeep.append(DelayDelete.DelayDelete(t, 'delayDeleteMembers'))

        for s in self.suits:
            membersKeep.append(DelayDelete.DelayDelete(s, 'delayDeleteMembers'))

        self._removeMembersKeep()
        self.membersKeep = membersKeep

    def _removeMembersKeep(self):
        if self.membersKeep:
            for delayDelete in self.membersKeep:
                delayDelete.destroy()

        self.membersKeep = None

    def __removeSuit(self, suit):
        self.notify.debug('Removing suit: %d' % suit.doId)
        if self.suits.count(suit) != 0:
            self.suits.remove(suit)
        if self.joiningSuits.count(suit) != 0:
            self.joiningSuits.remove(suit)
        if self.pendingSuits.count(suit) != 0:
            self.pendingSuits.remove(suit)
        if self.activeSuits.count(suit) != 0:
            self.activeSuits.remove(suit)
        self.suitGone = 1

    def __removeToon(self, toon, unexpected = 0):
        self.notify.debug('Removing toon: %d' % toon.doId)
        self.exitedToons.append(toon)
        if self.toons.count(toon) != 0:
            self.toons.remove(toon)
        if self.joiningToons.count(toon) != 0:
            self.clearInterval(self.taskName('to-pending-toon-%d' % toon.doId))
            if toon in self.joiningToons:
                self.joiningToons.remove(toon)
        if self.pendingToons.count(toon) != 0:
            self.pendingToons.remove(toon)
        if self.activeToons.count(toon) != 0:
            self.activeToons.remove(toon)
        if self.runningToons.count(toon) != 0:
            self.clearInterval(self.taskName('running-%d' % toon.doId), finish=1)
            if toon in self.runningToons:
                self.runningToons.remove(toon)
        self.ignore(toon.uniqueName('disable'))
        self.ignore(toon.uniqueName('died'))
        self.toonGone = 1
        if toon == base.localAvatar:
            self.removeLocalToon()
            self.__teleportToSafeZone(toon)
            return 1
        return 0

    def removeLocalToon(self):
        if base.cr.playGame.getPlace() is not None:
            base.cr.playGame.getPlace().setState('walk')
        self.localToonFsm.request('NoLocalToon')

    def __createJoinInterval(self, av, destPos, destHpr, name, ts, callback, toon = 0):
        joinTrack = Sequence()
        joinTrack.append(Func(Emote.globalEmote.disableAll, av, 'dbattlebase, createJoinInterval'))
        avPos = av.getPos(self)
        avPos = Point3(avPos[0], avPos[1], 0.0)
        av.setShadowHeight(0)
        plist = self.buildJoinPointList(avPos, destPos, toon)
        if len(plist) == 0:
            joinTrack.append(Func(av.headsUp, self, destPos))
            if toon == 0:
                timeToDest = self.calcSuitMoveTime(avPos, destPos)
                joinTrack.append(Func(av.loop, 'walk'))
            else:
                timeToDest = self.calcToonMoveTime(avPos, destPos)
                joinTrack.append(Func(av.loop, 'run'))
            if timeToDest > BATTLE_SMALL_VALUE:
                joinTrack.append(LerpPosInterval(av, timeToDest, destPos, other=self))
                totalTime = timeToDest
            else:
                totalTime = 0
        else:
            timeToPerimeter = 0
            if toon == 0:
                timeToPerimeter = self.calcSuitMoveTime(plist[0], avPos)
                timePerSegment = 10.0 / BattleBase.suitSpeed
                timeToDest = self.calcSuitMoveTime(BattleBase.posA, destPos)
            else:
                timeToPerimeter = self.calcToonMoveTime(plist[0], avPos)
                timePerSegment = 10.0 / BattleBase.toonSpeed
                timeToDest = self.calcToonMoveTime(BattleBase.posE, destPos)
            totalTime = timeToPerimeter + (len(plist) - 1) * timePerSegment + timeToDest
            if totalTime > MAX_JOIN_T:
                self.notify.warning('__createJoinInterval() - time: %f' % totalTime)
            joinTrack.append(Func(av.headsUp, self, plist[0]))
            if toon == 0:
                joinTrack.append(Func(av.loop, 'walk'))
            else:
                joinTrack.append(Func(av.loop, 'run'))
            joinTrack.append(LerpPosInterval(av, timeToPerimeter, plist[0], other=self))
            for p in plist[1:]:
                joinTrack.append(Func(av.headsUp, self, p))
                joinTrack.append(LerpPosInterval(av, timePerSegment, p, other=self))

            joinTrack.append(Func(av.headsUp, self, destPos))
            joinTrack.append(LerpPosInterval(av, timeToDest, destPos, other=self))
        joinTrack.append(Func(av.loop, 'neutral'))
        joinTrack.append(Func(av.headsUp, self, Point3(0, 0, 0)))
        tval = totalTime - ts
        if tval < 0:
            tval = totalTime
        joinTrack.append(Func(Emote.globalEmote.releaseAll, av, 'dbattlebase, createJoinInterval'))
        joinTrack.append(Func(callback, av, tval))
        if av == base.localAvatar:
            camTrack = Sequence()

            def setCamFov(fov):
                base.camLens.setMinFov(fov/(4./3.))

            camTrack.append(Func(setCamFov, self.camFov))
            camTrack.append(Func(base.camera.wrtReparentTo, self))
            camTrack.append(Func(base.camera.setPos, self.camJoinPos))
            camTrack.append(Func(base.camera.setHpr, self.camJoinHpr))
            return Parallel(joinTrack, camTrack, name=name)
        else:
            return Sequence(joinTrack, name=name)

    def makeSuitJoin(self, suit, ts):
        self.notify.debug('Making suit %d join...' % suit.doId)
        spotIndex = len(self.pendingSuits) + len(self.joiningSuits)
        self.joiningSuits.append(suit)
        suit.setState('Battle')
        openSpot = BattleGlobals.SuitPendingPoints[spotIndex]
        pos = openSpot[0]
        hpr = VBase3(openSpot[1], 0.0, 0.0)
        trackName = self.taskName('to-pending-suit-%d' % suit.doId)
        track = self.__createJoinInterval(suit, pos, hpr, trackName, ts, self.__handleSuitJoinDone)
        track.start(ts)
        track.delayDelete = DelayDelete.DelayDelete(suit, 'makeSuitJoin')
        self.storeInterval(track, trackName)
        if ToontownBattleGlobals.SkipMovie:
            track.finish()

    def __handleSuitJoinDone(self, suit, ts):
        self.notify.debug('Suit %d done joining.' % suit.doId)
        if self.hasLocalToon():
            self.d_joinDone(base.localAvatar.doId, suit.doId)

    def __makeSuitPending(self, suit):
        self.notify.debug('Suit %d pending' % suit.doId)
        self.clearInterval(self.taskName('to-pending-suit-%d' % suit.doId), finish=1)
        if self.joiningSuits.count(suit):
            self.joiningSuits.remove(suit)
        self.pendingSuits.append(suit)

    def __teleportToSafeZone(self, toon):
        self.notify.debug('Teleporting toon %d to safezone' % toon.doId)
        hoodId = ZoneUtil.getCanonicalHoodId(self.zoneId)
        if hoodId in base.localAvatar.hoodsVisited:
            target_sz = ZoneUtil.getSafeZoneId(self.zoneId)
        else:
            target_sz = ZoneUtil.getSafeZoneId(base.localAvatar.defaultZone)
        base.cr.playGame.getPlace().fsm.request('teleportOut', [{'loader': ZoneUtil.getLoaderName(target_sz),
          'where': ZoneUtil.getWhereName(target_sz, 1),
          'how': 'teleportIn',
          'hoodId': target_sz,
          'zoneId': target_sz,
          'shardId': None,
          'avId': -1,
          'battle': 1}])
        return

    def __makeToonJoin(self, toon, pendingToons, ts):
        self.notify.debug('Toon %d joining...' % toon.doId)
        spotIndex = len(pendingToons) + len(self.joiningToons)
        self.joiningToons.append(toon)
        openSpot = BattleGlobals.ToonPendingPoints[spotIndex]
        pos = openSpot[0]
        hpr = VBase3(openSpot[1], 0.0, 0.0)
        trackName = self.taskName('to-pending-toon-%d' % toon.doId)
        track = self.__createJoinInterval(toon, pos, hpr, trackName, ts, self.__handleToonJoinDone, toon=1)
        if toon != base.localAvatar:
            toon.animFSM.request('off')
        track.start(ts)
        track.delayDelete = DelayDelete.DelayDelete(toon, '__makeToonJoin')
        self.storeInterval(track, trackName)

    def __handleToonJoinDone(self, toon, ts):
        self.notify.debug('Toon %d done joining.' % toon.doId)
        if self.hasLocalToon():
            self.d_joinDone(base.localAvatar.doId, toon.doId)

    def __makeToonPending(self, toon, ts):
        self.notify.debug('Toon %d pending...' % toon.doId)
        self.clearInterval(self.taskName('to-pending-toon-%d' % toon.doId), finish=1)
        if self.joiningToons.count(toon):
            self.joiningToons.remove(toon)
        spotIndex = len(self.pendingToons)
        self.pendingToons.append(toon)
        openSpot = BattleGlobals.ToonPendingPoints[spotIndex]
        pos = openSpot[0]
        hpr = VBase3(openSpot[1], 0.0, 0.0)
        toon.loop('neutral')
        toon.setPosHpr(self, pos, hpr)
        if base.localAvatar == toon:
            currStateName = self.fsm.getCurrentState().getName()

    def __makeAvsActive(self, suits, toons):
        self.notify.debug('Making avs active...')
        self.__stopAdjusting()
        for s in suits:
            if self.joiningSuits.count(s):
                self.notify.warning('suit: %d was in joining list!' % s.doId)
                self.joiningSuits.remove(s)
            if self.pendingSuits.count(s):
                self.pendingSuits.remove(s)
            self.notify.debug('__makeAvsActive() - suit: %d' % s.doId)
            self.activeSuits.append(s)

        if len(self.activeSuits) >= 1:
            for suit in self.activeSuits:
                suitPos, suitHpr = self.getActorPosHpr(suit)
                spos = Point3(suitPos[0], suitPos[1], suitPos[2])
                suit.setPosHpr(self, spos, suitHpr)
                suit.loop('neutral')

        for toon in toons:
            if self.joiningToons.count(toon):
                self.notify.warning('toon: %d was in joining list!' % toon.doId)
                self.joiningToons.remove(toon)
            if self.pendingToons.count(toon):
                self.pendingToons.remove(toon)
            self.notify.debug('__makeAvsActive() - toon: %d' % toon.doId)
            if self.activeToons.count(toon) == 0:
                self.activeToons.append(toon)
            else:
                self.notify.warning('makeAvsActive() - toon: %d is active!' % toon.doId)

        if len(self.activeToons) >= 1:
            for toon in self.activeToons:
                toonPos, toonHpr = self.getActorPosHpr(toon)
                toon.setPosHpr(self, toonPos, toonHpr)
                toon.loop('neutral')

        if self.fsm.getCurrentState().getName() == 'WaitForInput' and self.localToonActive() and self.localToonJustJoined == 1:
            self.notify.debug('makeAvsActive() - local toon just joined')
            self.__enterLocalToonWaitForInput()
            self.localToonJustJoined = 0
            self.startTimer()

    def __makeToonRun(self, toon, ts):
        self.notify.debug('Making toon %d run' % toon.doId)
        if self.activeToons.count(toon):
            self.activeToons.remove(toon)
        self.runningToons.append(toon)
        self.toonGone = 1
        self.__stopTimer()
        if self.localToonRunning():
            self.townBattle.setState('Off')
        runMTrack = MovieUtil.getToonTeleportOutInterval(toon)
        runName = self.taskName('running-%d' % toon.doId)
        self.notify.debug('duration: %f' % runMTrack.getDuration())
        runMTrack.start(ts)
        runMTrack.delayDelete = DelayDelete.DelayDelete(toon, '__makeToonRun')
        self.storeInterval(runMTrack, runName)

    def d_toonRequestJoin(self, toonId, pos):
        self.notify.debug('Toon %d requested to join' % toonId)
        self.sendUpdate('toonRequestJoin', [pos[0], pos[1], pos[2]])

    def d_toonRequestRun(self, toonId):
        self.notify.debug('Toon %d requested to run' % toonId)
        self.sendUpdate('toonRequestRun', [])

    def d_faceOffDone(self, toonId):
        self.notify.debug('Toon %d done face off' % toonId)
        self.sendUpdate('faceOffDone', [])

    def d_adjustDone(self, toonId):
        self.notify.debug('Telling server that toon %d done adjusting' % toonId)
        self.sendUpdate('adjustDone', [])

    def d_timeout(self, toonId):
        self.notify.debug('Timed out...')
        self.sendUpdate('timeout', [])

    def d_requestMovieDone(self):
        self.notify.debug('Telling server my movie is done')
        self.sendUpdate('requestMovieDone', [])

    def d_joinDone(self, toonId, avId):
        self.notify.debug('Telling server my %d join finished' % avId)
        self.sendUpdate('joinDone', [avId])

    def d_requestAttack(self, toonId, gagId, targetId):
        self.notify.debug('Telling server my attack id is %d, and I am targeting %d' % (gagId, targetId))
        self.sendUpdate('requestAttack', [gagId, targetId])

    def enterOff(self, ts = 0):
        self.notify.debug('Off..')
        self.localToonFsm.requestFinalState()
        return None

    def exitOff(self):
        return None

    def enterFaceOff(self, ts = 0):
        self.notify.debug('Face off..')
        return None

    def exitFaceOff(self):
        return None

    def enterWaitForJoin(self, ts = 0):
        self.notify.debug('Waiting for join...')
        return None

    def exitWaitForJoin(self):
        return None

    def __enterLocalToonWaitForInput(self):
        self.notify.debug('Local toon waiting for input...')
        self.accept('updateBattleCamera', self.updateCamera)
        self.updateCamera()
        NametagGlobals.setWant2dNametags(False)
        self.townBattle.setState('Attack')
        self.accept(self.localToonBattleEvent, self.__handleLocalToonBattleEvent)

    def updateCamera(self):
        if self.hasLocalToon():
            self.camPos = ToontownBattleGlobals.BattleCamDefaultPos
            heights = [suit.height for suit in self.suits]
            self.camPos.setZ(12.0 + max(heights))
            base.camera.setPosHpr(self.camPos, self.camHpr)
            base.camLens.setMinFov(self.camMenuFov/(4./3.))

    def startTimer(self, ts = 0):
        self.notify.debug('Starting timer...')
        if ts >= CLIENT_INPUT_TIMEOUT:
            self.notify.warning('startTimer() - ts: %f timeout: %f' % (ts, CLIENT_INPUT_TIMEOUT))
            self.__timedOut()
            return
        self.timer.startCallback(CLIENT_INPUT_TIMEOUT - ts, self.__timedOut)
        timeTask = Task.loop(Task(self.__countdown), Task.pause(0.2))
        taskMgr.add(timeTask, self.timerCountdownTaskName)

    def __stopTimer(self):
        self.notify.debug('Stopping timer...')
        self.timer.stop()
        taskMgr.remove(self.timerCountdownTaskName)

    def __countdown(self, task):
        if hasattr(self.townBattle, 'timer'):
            self.townBattle.updateTimer(int(self.timer.getT()))
        else:
            self.notify.warning('__countdown has tried to update a timer that has been deleted. Stopping timer')
            self.__stopTimer()
        return Task.done

    def enterWaitForInput(self, ts = 0):
        self.notify.debug('Waiting for input...')
        if self.interactiveProp:
            self.interactiveProp.gotoBattleCheer()
        self.choseAttackAlready = 0
        if self.localToonActive():
            self.__enterLocalToonWaitForInput()
            self.startTimer(ts)
        if self.hasLocalToon():
            self.townBattle.update()
        return None

    def exitWaitForInput(self):
        self.notify.debug('Done waiting for input.')
        self.ignore('updateBattleCamera')
        if self.localToonActive():
            self.townBattle.setState('Off')
            base.camLens.setMinFov(self.camFov/(4./3.))
            self.ignore(self.localToonBattleEvent)
            self.__stopTimer()
        return None

    def __handleLocalToonBattleEvent(self, response):
        self.notify.debug('__handleLocalToonBattleEvent: %s' % response)
        mode = response['mode']
        if mode == 'UnAttack':
            self.d_requestAttack(base.localAvatar.doId, NO_ATTACK, 0)
        else:
            attackId = response['attackId']
            targetId = response['target']
            self.d_requestAttack(base.localAvatar.doId, attackId, targetId)

    def __timedOut(self):
        if self.choseAttackAlready == 1:
            return
        self.notify.debug('WaitForInput timed out')
        if self.localToonActive():
            self.notify.debug('battle timed out')
            self.d_timeout(base.localAvatar.doId)

    def enterPlayMovie(self, ts):
        self.notify.debug('Playing movie...')
        # self.delayDeleteMembers()
        if self.hasLocalToon():
            NametagGlobals.setWant2dNametags(False)

        self.movie.play(ts, self.__handleMovieDone)

    def __handleMovieDone(self):
        self.notify.debug('Handling movie ending.')
        if self.hasLocalToon():
            self.d_requestMovieDone()
        self.movie.reset()

    def exitPlayMovie(self):
        self.notify.debug('Movie done.')
        self.movie.reset()
        #self._removeMembersKeep()

    def hasLocalToon(self):
        return self.toons.count(base.localAvatar) > 0

    def localToonPendingOrActive(self):
        return self.pendingToons.count(base.localAvatar) > 0 or self.activeToons.count(base.localAvatar) > 0

    def localToonActive(self):
        return self.activeToons.count(base.localAvatar) > 0

    def localToonActiveOrRunning(self):
        return self.activeToons.count(base.localAvatar) > 0 or self.runningToons.count(base.localAvatar) > 0

    def localToonRunning(self):
        return self.runningToons.count(base.localAvatar) > 0

    def enterHasLocalToon(self):
        self.notify.debug('enterHasLocalToon()')
        if base.cr.playGame.getPlace() != None:
            base.cr.playGame.getPlace().setState('battle', self.localToonBattleEvent)
        base.camera.wrtReparentTo(self)
        base.camLens.setMinFov(self.camFov/(4./3.))
        return

    def exitHasLocalToon(self):
        self.ignore(self.localToonBattleEvent)
        self.__stopTimer()
        stateName = None
        place = base.cr.playGame.getPlace()
        if place:
            stateName = place.fsm.getCurrentState().getName()
        if stateName == 'died':
            self.movie.reset()
            base.camera.reparentTo(render)
            base.camera.setPosHpr(localAvatar, 5.2, 5.45, localAvatar.getHeight() * 0.66, 131.5, 3.6, 0)
        else:
            base.camera.wrtReparentTo(base.localAvatar)
            messenger.send('localToonLeftBattle')
        base.camLens.setMinFov(ToontownGlobals.DefaultCameraFov/(4./3.))
        return

    def enterNoLocalToon(self):
        self.notify.debug('enterNoLocalToon()')
        return None

    def exitNoLocalToon(self):
        return None

    def enterWaitForServer(self):
        self.notify.debug('Waiting for server...')
        return None

    def exitWaitForServer(self):
        self.notify.debug('Done waiting for server.')
        return None

    def createAdjustInterval(self, av, destPos, destHpr, toon = 0, run = 0):
        if run == 1:
            adjustTime = self.calcToonMoveTime(destPos, av.getPos(self))
        else:
            adjustTime = self.calcSuitMoveTime(destPos, av.getPos(self))
        self.notify.debug('creating adjust interval for: %d' % av.doId)
        adjustTrack = Sequence()
        if run == 1:
            adjustTrack.append(Func(av.loop, 'run'))
        else:
            adjustTrack.append(Func(av.loop, 'walk'))
        adjustTrack.append(Func(av.headsUp, self, destPos))
        adjustTrack.append(LerpPosInterval(av, adjustTime, destPos, other=self))
        adjustTrack.append(Func(av.setHpr, self, destHpr))
        adjustTrack.append(Func(av.loop, 'neutral'))
        return adjustTrack

    def __adjust(self, ts, callback):
        self.notify.debug('Adjusting...')
        adjustTrack = Parallel()
        if len(self.pendingSuits) > 0 or self.suitGone == 1:
            self.suitGone = 0
            numSuits = len(self.pendingSuits) + len(self.activeSuits) - 1
            index = 0
            for suit in self.activeSuits:
                point = BattleGlobals.SuitPoints[numSuits][index]
                pos = suit.getPos(self)
                destPos = point[0]
                if pos != destPos:
                    destHpr = VBase3(point[1], 0.0, 0.0)
                    adjustTrack.append(self.createAdjustInterval(suit, destPos, destHpr))
                index += 1

            for suit in self.pendingSuits:
                point = BattleGlobals.SuitPoints[numSuits][index]
                destPos = point[0]
                destHpr = VBase3(point[1], 0.0, 0.0)
                adjustTrack.append(self.createAdjustInterval(suit, destPos, destHpr))
                index += 1

        if len(self.pendingToons) > 0 or self.toonGone == 1:
            self.toonGone = 0
            numToons = len(self.pendingToons) + len(self.activeToons) - 1
            index = 0
            for toon in self.activeToons:
                point = BattleGlobals.ToonPoints[numToons][index]
                pos = toon.getPos(self)
                destPos = point[0]
                if pos != destPos:
                    destHpr = VBase3(point[1], 0.0, 0.0)
                    adjustTrack.append(self.createAdjustInterval(toon, destPos, destHpr))
                index += 1

            for toon in self.pendingToons:
                point = BattleGlobals.ToonPoints[numToons][index]
                destPos = point[0]
                destHpr = VBase3(point[1], 0.0, 0.0)
                adjustTrack.append(self.createAdjustInterval(toon, destPos, destHpr))
                index += 1

        if len(adjustTrack) > 0:
            self.notify.debug('creating adjust multitrack')
            e = Func(self.__handleAdjustDone)
            track = Sequence(adjustTrack, e, name=self.adjustName)
            self.storeInterval(track, self.adjustName)
            track.start(ts)
            if ToontownBattleGlobals.SkipMovie:
                track.finish()
        else:
            self.notify.warning('adjust() - nobody needed adjusting')
            self.__adjustDone()

    def __handleAdjustDone(self):
        self.notify.debug('__handleAdjustDone() - client adjust finished')
        self.clearInterval(self.adjustName)
        self.__adjustDone()

    def __stopAdjusting(self):
        self.notify.debug('__stopAdjusting()')
        self.clearInterval(self.adjustName)
        if self.adjustFsm.getCurrentState().getName() == 'Adjusting':
            self.adjustFsm.request('NotAdjusting')

    def __adjustDone(self):
        self.notify.debug('Done Adjusting.')
        if self.hasLocalToon():
            self.d_adjustDone(base.localAvatar.doId)
        self.adjustFsm.request('NotAdjusting')

    def enterAdjusting(self, ts):
        self.notify.debug('Adjusting Battle...')
        if self.localToonActive():
            self.__stopTimer()
        self.delayDeleteMembers()
        self.__adjust(ts, self.__handleAdjustDone)
        return None

    def exitAdjusting(self):
        self.notify.debug('Exiting Adjusting...')
        self.finishInterval(self.adjustName)
        self._removeMembersKeep()
        currStateName = self.fsm.getCurrentState().getName()
        if currStateName == 'WaitForInput' and self.localToonActive():
            self.startTimer()
            self.townBattle.update()
        return None

    def enterNotAdjusting(self):
        return None

    def exitNotAdjusting(self):
        return None

    def visualize(self):
        try:
            self.isVisualized
        except:
            self.isVisualized = 0

        if self.isVisualized:
            self.vis.removeNode()
            del self.vis
            self.detachNode()
            self.isVisualized = 0
        else:
            lsegs = LineSegs()
            lsegs.setColor(0.5, 0.5, 1, 1)
            lsegs.moveTo(0, 0, 0)
            for p in BattleBase.allPoints:
                lsegs.drawTo(p[0], p[1], p[2])

            p = BattleBase.allPoints[0]
            lsegs.drawTo(p[0], p[1], p[2])
            self.vis = self.attachNewNode(lsegs.create())
            self.reparentTo(render)
            self.isVisualized = 1

    def setupCollisions(self, name):
        self.lockout = CollisionTube(0, 0, 0, 0, 0, 9, 9)
        lockoutNode = CollisionNode(name)
        lockoutNode.addSolid(self.lockout)
        lockoutNode.setCollideMask(ToontownGlobals.WallBitmask)
        self.lockoutNodePath = self.attachNewNode(lockoutNode)
        self.lockoutNodePath.detachNode()

    def removeCollisionData(self):
        del self.lockout
        self.lockoutNodePath.removeNode()
        del self.lockoutNodePath

    def enableCollision(self):
        self.lockoutNodePath.reparentTo(self)
        if len(self.toons) < 4:
            self.accept(self.getCollisionName(), self.__handleLocalToonCollision)

    def __handleLocalToonCollision(self, collEntry):
        self.notify.debug('Handling local toon collision...')
        if self.fsm.getCurrentState().getName() == 'Off':
            self.notify.debug('ignoring collision in Off state')
            return
        if not base.localAvatar.wantBattles:
            return
        base.cr.playGame.getPlace().setState('WaitForBattle')
        toon = base.localAvatar
        self.d_toonRequestJoin(toon.doId, toon.getPos(self))
        base.localAvatar.preBattleHpr = base.localAvatar.getHpr(render)
        self.localToonFsm.request('WaitForServer')
        self.onWaitingForJoin()

    def onWaitingForJoin(self):
        pass

    def denyLocalToonJoin(self):
        self.notify.debug('denyLocalToonJoin()')
        place = self.cr.playGame.getPlace()
        if place.fsm.getCurrentState().getName() == 'WaitForBattle':
            place.setState('walk')
        self.localToonFsm.request('NoLocalToon')

    def disableCollision(self):
        self.ignore(self.getCollisionName())
        self.lockoutNodePath.detachNode()

    def openBattleCollision(self):
        if not self.hasLocalToon():
            self.enableCollision()

    def closeBattleCollision(self):
        self.ignore(self.getCollisionName())

    def getCollisionName(self):
        return 'enter' + self.lockoutNodePath.getName()
