from direct.directnotify import DirectNotifyGlobal
from toontown.cogdominium.DistCogdoGameAI import DistCogdoGameAI
import CogdoMazeGameGlobals
from direct.distributed.ClockDelta import *
from direct.task import Timer
from toontown.battle import BattleBase
from toontown.building.ElevatorConstants import *


class DistCogdoMazeGameAI(DistCogdoGameAI):
    notify = DirectNotifyGlobal.directNotify.newCategory("DistCogdoMazeGameAI")

    def __init__(self, air):
        DistCogdoGameAI.__init__(self, air)
        self.numSuits = (0, 0, 0)
        self.timer = Timer.Timer()
        self.doorRevealed = False
        self.toonsInDoor = []
        self.bosses = {}
        self.fastMinions = {}
        self.slowMinions = {}
        self.suitTypes = [self.bosses, self.fastMinions, self.slowMinions]
        self.numJokes = {}

    def announceGenerate(self):
        DistCogdoGameAI.announceGenerate(self)
        self.setupSuits()

    def setupSuits(self):
        bossHp = CogdoMazeGameGlobals.SuitData[0]['hp']
        fastMiniHp = CogdoMazeGameGlobals.SuitData[1]['hp']
        slowMiniHp = CogdoMazeGameGlobals.SuitData[2]['hp']
        serialNum = 0

        for i in xrange(self.numSuits[0]):
            self.bosses[serialNum] = bossHp
            serialNum += 1
        for i in xrange(self.numSuits[1]):
            self.fastMinions[serialNum] = fastMiniHp
            serialNum += 1
        for i in xrange(self.numSuits[2]):
            self.slowMinions[serialNum] = slowMiniHp
            serialNum += 1

    def setNumSuits(self, num):
        self.numSuits = num

    def getNumSuits(self):
        return self.numSuits

    def requestUseGag(self, x, y, h, timestamp):
        avId = self.air.getAvatarIdFromSender()
        self.sendUpdate('toonUsedGag', [avId, x, y, h, globalClockDelta.getRealNetworkTime()])

    def requestSuitHitByGag(self, suitType, suitNumber):
        avId = self.air.getAvatarIdFromSender()
        hit = self.hitSuit(suitType, suitNumber)

        if not hit:
            self.notify.warning('Cannot hit suit!')
            return

        self.sendUpdate('suitHitByGag', [avId, suitType, suitNumber])

    def requestHitBySuit(self, suitType, suitNum, networkTime):
        avId = self.air.getAvatarIdFromSender()
        av = self.air.doId2do.get(avId)
        suit = CogdoMazeGameGlobals.SuitData[suitType]
        if av:
            damage = suit['toonDamage'] * self.getDifficulty() * 10
            av.takeDamage(damage)

            self.sendUpdate('toonHitBySuit', [avId, suitType, suitNum, globalClockDelta.getRealNetworkTime()])
            if av.getHp() < 1:
                self.toonWentSad(avId)

    def requestHitByDrop(self):
        avId = self.air.getAvatarIdFromSender()
        av = self.air.doId2do.get(avId)

        if av:
            av.takeDamage(CogdoMazeGameGlobals.DropDamage)
            self.sendUpdate('toonHitByDrop', [avId])

    def requestPickUp(self, pickupNum):
        avId = self.air.getAvatarIdFromSender()
        av = self.air.doId2do.get(avId)

        if av:
            if avId in self.numJokes:
                self.numJokes[avId] += 1
            else:
                self.numJokes[avId] = 1

            self.sendUpdate('pickUp', [avId, pickupNum, globalClockDelta.getRealNetworkTime()])

    def requestGag(self, coolerIndex):
        avId = self.air.getAvatarIdFromSender()
        self.sendUpdate('hasGag', [avId, globalClockDelta.getRealNetworkTime()])

    def hitSuit(self, suitType, suitNum):
        cogKey = None
        for cogNum in self.suitTypes[suitType].keys():
            if cogNum == suitNum:
                cogKey = cogNum
                break

        if cogKey is None:
            return False

        cogHp = self.suitTypes[suitType][cogKey] - 1
        self.suitTypes[suitType][cogKey] = cogHp

        if cogHp <= 0:
            del self.suitTypes[suitType][cogKey]
        return True

    def handleStart(self):
        taskMgr.add(self.__checkGameDone, self.taskName('check-game-done'))
        taskMgr.add(self.__checkPlayersTask, self.taskName('check-players-task'))

        self.timer.startCallback(CogdoMazeGameGlobals.SecondsUntilTimeout + 1.0, self.__handleGameOver)
        taskMgr.doMethodLater(1.0, self.clientCountdown, self.taskName('client_countdown'))
        taskMgr.add(self.__timeWarningTask, self.taskName('time-warning-task'))

    def clientCountdown(self, task):
        self.doAction(CogdoMazeGameGlobals.GameActions.Countdown, 0)
        return task.done

    def __handleGameOver(self):
        self.removeAll()
        self.gameDone(failed=True)

    def __checkGameDone(self, task):
        if len(self.bosses) == 0:
            self.timer.stop()
            self.doAction(CogdoMazeGameGlobals.GameActions.OpenDoor, 0)
            self.__startTimeout()
            return task.done
        return task.again

    def __startTimeout(self):
        self.timer.startCallback(CogdoMazeGameGlobals.SecondsUntilGameEnds, self.__handleTimeout)

    def __handleTimeout(self):
        for toon in self.toons:
            if toon not in self.toonsInDoor:
                self.killToon(toon)
        self.removeAll()
        self.gameDone()

    def __timeWarningTask(self, task):
        if self.timer.getT() <= CogdoMazeGameGlobals.SecondsForTimeAlert:
            self.doAction(CogdoMazeGameGlobals.GameActions.TimeAlert, 0)
            return task.done
        return task.again

    def killToon(self, avId):
        av = self.air.doId2do.get(avId)
        if av:
            if av.getHp() > 0:
                av.takeDamage(av.getHp())
            self.toonWentSad(avId)
        self.__playerDisconnected(avId)

    def __checkPlayersTask(self, task):
        for toonId in self.toons:
            toon = self.air.doId2do.get(toonId)
            if not toon:
                self.__playerDisconnected(toonId)
        return task.again

    def __playerDisconnected(self, avId):
        self.sendUpdate('setToonDisconnect', [avId])
        self.toons.pop(self.toons.index(avId))
        if len(self.toons) == 0:
            self.removeAll()
            self.gameDone(failed=True)

    def doAction(self, action, data):
        self.sendUpdate('doAction', [action, data, globalClockDelta.getRealNetworkTime()])

    def requestAction(self, action, data):
        avId = self.air.getAvatarIdFromSender()

        if action == CogdoMazeGameGlobals.GameActions.RevealDoor:
            if not self.doorRevealed:
                self.doAction(action, avId)
                self.doorRevealed = True
            else:
                self.notify.warning('Toon tried to reveal door but it\'s already revealed! Ignoring.')

        elif action == CogdoMazeGameGlobals.GameActions.EnterDoor:
            if avId not in self.toonsInDoor:
                self.doAction(action, avId)
                self.toonsInDoor.append(avId)
                self.toonUpToon(avId)
            else:
                self.notify.warning('Toon tried to enter into door but already entered! Ignoring.')
                return

            if len(self.toonsInDoor) >= len(self.toons):
                self.__handleAllAboard()
        else:
            self.notify.warning('Client requested unknown action \'%s\'' %action)

    def __handleAllAboard(self):
        if len(self.toonsInDoor) != len(self.toons):
            self.notify.warning('__handleAllAboard expect all toons aboard!')
            return

        self.removeAll()
        taskMgr.doMethodLater(3.7, lambda t: self.gameDone(), self.taskName('all-aboard-delay'))

    def toonUpToon(self, toonId):
        if toonId in self.toonsInDoor:
            toon = self.air.doId2do.get(toonId)
            if toon:
                val = min(15 * self.numJokes.get(toonId, 0), toon.getMaxHp())
                toon.toonUp(val)

    def removeAll(self):
        taskMgr.remove(self.taskName('check-game-done'))
        taskMgr.remove(self.taskName('check-players-task'))
        taskMgr.remove(self.taskName('time-warning-task'))
        taskMgr.remove(self.taskName('all-aboard-delay'))
        self.timer.stop()

    def disable(self):
        DistCogdoGameAI.disable(self)
        self.removeAll()
