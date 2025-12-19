from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.distributed.ClockDelta import *
from toontown.battle import BattleBase
from toontown.building.ElevatorConstants import *
from toontown.cogdominium.DistCogdoGameAI import DistCogdoGameAI
from . import CogdoFlyingGameGlobals as Globals


class DistCogdoFlyingGameAI(DistCogdoGameAI):
    notify = directNotify.newCategory('DistCogdoFlyingGameAI')

    def __init__(self, air):
        DistCogdoGameAI.__init__(self, air)
        self.completed = []
        self.eagles = {}
        self.totalMemos = 0

    def requestAction(self, action, data):
        avId = self.air.getAvatarIdFromSender()
        av = self.air.doId2do.get(avId)
        if not av:
            return

        if action == Globals.EGameAction.LAND_ON_WIN_PLATFORM:
            self.completed.append(avId)
            for toon in self.toons:
                if toon not in self.completed:
                    return

            self.gameDone()
        elif action == Globals.EGameAction.BLADE_LOST:
            self.sendUpdate('toonBladeLost', [avId])
        elif action == Globals.EGameAction.SET_BLADES:
            self.sendUpdate('toonSetBlades', [avId, data])
        elif action == Globals.EGameAction.DIED:
            damage = Globals.AI.SafezoneId2DeathDamage[self.getSafezoneId()]
            self.takeDamage(av, damage)
            self.sendUpdate('toonDied', [avId, globalClockDelta.getRealNetworkTime()])
        elif action == Globals.EGameAction.SPAWN:
            self.sendUpdate('toonSpawn', [avId, globalClockDelta.getRealNetworkTime()])
        elif action == Globals.EGameAction.REQUEST_ENTER_EAGLE_INTEREST:
            if not self.eagles.get(data):
                self.eagles[data] = avId
                self.sendUpdate('toonSetAsEagleTarget', [avId, data, globalClockDelta.getRealNetworkTime()])
        elif action == Globals.EGameAction.REQUEST_EXIT_EAGLE_INTEREST:
            if self.eagles.get(data) == avId:
                self.eagles[data] = 0
                self.sendUpdate('toonClearAsEagleTarget', [avId, data, globalClockDelta.getRealNetworkTime()])
        elif action == Globals.EGameAction.HIT_LEGAL_EAGLE:
            damage = Globals.AI.SafezoneId2LegalEagleDamage[self.getSafezoneId()]
            self.takeDamage(av, damage)
        elif action == Globals.EGameAction.HIT_MINION:
            damage = Globals.AI.SafezoneId2MinionDamage[self.getSafezoneId()]
            self.takeDamage(av, damage)
        elif action == Globals.EGameAction.HIT_WHIRLWIND:
            damage = Globals.AI.SafezoneId2WhirlwindDamage[self.getSafezoneId()]
            self.takeDamage(av, damage)
        elif action == Globals.EGameAction.RAN_OUT_OF_TIME_PENALTY:
            damage = int(20 * self.getDifficulty())
            self.takeDamage(av, damage)
        else:
            self.notify.warning('Client requested unknown action: %s' % action)

    def requestPickUp(self, pickupNum, pickupType):
        avId = self.air.getAvatarIdFromSender()
        av = self.air.doId2do.get(avId)
        if not av:
            return

        if pickupType <= len(Globals.Level.GatherableTypes):
            self.sendUpdate('pickUp', [avId, pickupNum, globalClockDelta.getRealNetworkTime()])
            if pickupType == Globals.EGatherableType.LAFF_POWERUP:
                av.toonUp(int(27 * self.getDifficulty()) + 3)
            if pickupType == Globals.EGatherableType.MEMO:
                self.totalMemos += 1
        else:
            self.notify.warning('Client requested unknown pickup: %s' % pickupType)

    def handleStart(self):
        for toon in self.toons:
            self.acceptOnce(self.air.getAvatarExitEvent(toon), self.handleAvExit, [toon])

    def handleAvExit(self, toon):
        if self.air:
            if toon in self.toons:
                self.toons.remove(toon)
                self.ignore(self.air.getAvatarExitEvent(toon))
                if not self.toons:
                    self.gameDone(failed=True)

    def requestDelete(self):
        DistCogdoGameAI.requestDelete(self)
        self.ignoreAll()

    def removeToon(self, avId):
        if avId not in self.toons:
            return

        self.toons.pop(self.toons.index(avId))
        if len(self.toons) == 0:
            self.gameDone(failed=True)

    def takeDamage(self, av, damage):
        av.takeDamage(damage)
        if av.getHp() < 1:
            self.removeToon(av.doId)

    def getTotalMemos(self):
        return self.totalMemos
