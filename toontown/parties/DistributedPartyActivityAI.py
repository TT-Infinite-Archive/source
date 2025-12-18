from direct.distributed.DistributedObjectAI import DistributedObjectAI
from direct.distributed.ClockDelta import globalClockDelta

from toontown.toonbase.HolidayGlobals import JELLYBEAN_PARTIES_HOLIDAY, JELLYBEAN_PARTIES_HOLIDAY_MONTH
from toontown.parties import PartyGlobals, PartyUtils


class DistributedPartyActivityAI(DistributedObjectAI):
    notify = directNotify.newCategory("DistributedPartyActivityAI")
    MAX_PLAYERS = 0

    def __init__(self, air, party, activityInfo):
        DistributedObjectAI.__init__(self, air)

        self.party = party
        self.state = None

        self.x = PartyUtils.convertDistanceFromPartyGrid(activityInfo[1], 0)
        self.y = PartyUtils.convertDistanceFromPartyGrid(activityInfo[2], 1)
        self.h = activityInfo[3] * PartyGlobals.PartyGridHeadingConverter

        self.toonsPlaying = {}

    def getX(self):
        return self.x

    def getY(self):
        return self.y

    def getH(self):
        return self.h

    def getPartyDoId(self):
        return self.party.doId

    def updateToonsPlaying(self):
        self.sendUpdate('setToonsPlaying', [list(self.toonsPlaying.keys())])

    def toonJoinRequest(self):
        avId = self.air.getAvatarIdFromSender()
        if avId not in self.air.doId2do:
            self.notify.warning('Unknown avatar %s tried to join!' % avId)
            return

        if avId in self.toonsPlaying:
            self.notify.warning('Avatar %s tried to join twice!' % avId)
            return

        self.toonsPlaying[avId] = False
        self.acceptOnce(self.air.getAvatarExitEvent(avId), self.handleUnexpectedExit, extraArgs=[avId])

    def handleUnexpectedExit(self, avId):
        if avId in self.toonsPlaying:
            del self.toonsPlaying[avId]

    def toonExitRequest(self):
        avId = self.air.getAvatarIdFromSender()
        if avId not in self.toonsPlaying:
            self.notify.warning('Unknown avatar %s tried to leave!' % avId)
            return

        del self.toonsPlaying[avId]

    def toonExitDemand(self):
        avId = self.air.getAvatarIdFromSender()
        if avId not in self.toonsPlaying:
            self.notify.warning('Unknown avatar %s tried to leave!' % avId)
            return

        del self.toonsPlaying[avId]

    def toonReady(self):
        avId = self.air.getAvatarIdFromSender()
        if avId not in self.toonsPlaying:
            self.notify.warning('Unknown avatar %s tried to become ready!' % avId)
            return

        self.toonsPlaying[avId] = True

        if self.allToonsReady():
            self.balancePlayers()
            self.setState('Active')

    def balancePlayers(self):
        pass

    def allToonsReady(self):
        for status in list(self.toonsPlaying.values()):
            if status is False:
                return False

        return True

    def setState(self, state):
        self.state = state
        self.sendUpdate('setState', [state, globalClockDelta.getRealNetworkTime()])

    def showJellybeanReward(self, earnedAmount, jarAmount, message):
        self.sendUpdate('showJellybeanReward', [earnedAmount, jarAmount, message])

    def activityIsFull(self):
        return len(self.toonsPlaying) >= self.MAX_PLAYERS

    def joinRequestDenied(self, avId, reason):
        self.sendUpdateToAvatarId(avId, 'joinRequestDenied', [reason])

    def exitRequestDenied(self, avId, reason):
        self.sendUpdateToAvatarId(avId, 'exitRequestDenied', [reason])

    def isDoubleJelleybeans(self):
        return self.air.holidayManager.areHolidaysRunning([JELLYBEAN_PARTIES_HOLIDAY, JELLYBEAN_PARTIES_HOLIDAY_MONTH])
