from direct.distributed.ClockDelta import globalClockDelta

from toontown.parties.DistributedPartyActivityAI import DistributedPartyActivityAI
from toontown.parties import PartyGlobals

import random

LEFT_TEAM = PartyGlobals.TeamActivityTeams.LeftTeam
RIGHT_TEAM = PartyGlobals.TeamActivityTeams.RightTeam


class DistributedPartyTeamActivityAI(DistributedPartyActivityAI):
    notify = directNotify.newCategory('DistributedPartyTeamActivityAI')

    MAX_PLAYERS = 8
    MIN_PLAYERS_PER_TEAM = 1
    MAX_PLAYERS_PER_TEAM = 4

    COUNTDOWN_TIME = 15
    DURATION = 90

    def __init__(self, air, party, activityInfo):
        DistributedPartyActivityAI.__init__(self, air, party, activityInfo)

        self.canSwitchTeams = 0

        self.leftTeam = []
        self.rightTeam = []

        self.teamDict = {}

    def generate(self):
        DistributedPartyActivityAI.generate(self)

        self.setState('WaitForEnough')

    def setCanSwitchTeams(self, canSwitch):
        self.canSwitchTeams = canSwitch

    def getCanSwitchTeams(self):
        return self.canSwitchTeams

    def toonJoinRequest(self, team):
        avId = self.air.getAvatarIdFromSender()
        if avId not in self.air.doId2do:
            self.notify.warning('Unknown avatar %s tried to join!' % avId)
            return

        if not self.isValidTeam(team):
            self.notify.warning('Avatar %s tried to join an invalid team!' % avId)

        if avId in self.toonsPlaying:
            self.notify.warning('Avatar %s tried to join twice!' % avId)
            return

        if self.isTeamFull(team):
            self.joinRequestDenied(avId, PartyGlobals.DenialReasons.Full)
            return

        if team == LEFT_TEAM:
            self.leftTeam.append(avId)
        elif team == RIGHT_TEAM:
            self.rightTeam.append(avId)

        self.toonsPlaying[avId] = False

        self.updateToonsPlaying()

        self.acceptOnce(self.air.getAvatarExitEvent(avId), self.handleUnexpectedExit, extraArgs=[avId, team])

        if self.areEnoughPlayers():
            self.setState('WaitToStart')
            self.startCountdown()

    def handleUnexpectedExit(self, avId, team):
        DistributedPartyActivityAI.handleUnexpectedExit(self, avId)
        if avId in self.leftTeam:
            self.leftTeam.remove(avId)
        if avId in self.rightTeam:
            self.rightTeam.remove(avId)
        self.updateToonsPlaying()

    def toonExitRequest(self, team):
        avId = self.air.getAvatarIdFromSender()
        if avId not in self.air.doId2do:
            self.notify.warning('Unknown avatar %s tried to exit!' % avId)
            return

        if not self.isValidTeam(team):
            self.notify.warning('Avatar %s tried to exit an invalid team!' % avId)
            return

        if avId not in self.toonsPlaying:
            self.notify.warning('Avatar %s tried to leave a game he wasnt playing!' % avId)
            return

        if avId not in self.getTeam(team):
            self.notify.warning('Avatar %s tried to leave a team he wasnt on!' % avId)
            return

        if team == LEFT_TEAM:
            self.leftTeam.remove(avId)
        elif team == RIGHT_TEAM:
            self.rightTeam.remove(avId)

        del self.toonsPlaying[avId]

        self.updateToonsPlaying()

        if not self.areEnoughPlayers():
            self.setState('WaitForEnough')
            self.cancelCountdown()

    def toonSwitchTeamRequest(self):
        avId = self.air.getAvatarIdFromSender()
        if not self.canSwitchTeams:
            self.notify.warning('Avatar %s tried to switch teams when it was disabled!' % avId)
            return

        if avId not in self.toonsPlaying:
            self.notify.warning('Unknown avatar %s tried to switch teams!' % avId)
            return

        if avId in self.leftTeam:
            if self.isTeamFull(self.rightTeam):
                self.switchTeamRequestDenied(avId, PartyGlobals.DenialReasons.Full)
                return

            self.leftTeam.remove(avId)
            self.rightTeam.append(avId)
        elif avId in self.rightTeam:
            if self.isTeamFull(self.leftTeam):
                self.switchTeamRequestDenied(avId, PartyGlobals.DenialReasons.Full)
                return

            self.rightTeam.remove(avId)
            self.leftTeam.append(avId)

        self.updateToonsPlaying()

    def getPlayersPerTeam(self):
        return self.MIN_PLAYERS_PER_TEAM, self.MAX_PLAYERS_PER_TEAM

    def getDuration(self):
        return self.DURATION

    def setState(self, state, data=[0]):
        self.state = state
        self.sendUpdate('setState', [state, globalClockDelta.getRealNetworkTime(), data])

    def getToonsPlaying(self):
        return self.leftTeam, self.rightTeam

    def setAdvantage(self, todo0):
        pass

    def switchTeamRequestDenied(self, avId, reason):
        self.sendUpdateToAvatarId(avId, 'switchTeamRequestDenied', [reason])

    def updateToonsPlaying(self):
        self.sendUpdate('setToonsPlaying', [self.leftTeam, self.rightTeam])

    def balancePlayers(self):
        lowTeam = self.leftTeam if len(self.leftTeam) < len(self.rightTeam) else self.rightTeam
        highTeam = self.rightTeam if len(self.leftTeam) < len(self.rightTeam) else self.leftTeam

        while len(highTeam) >= len(lowTeam) + 2:
            avId = random.choice(highTeam)

            highTeam.remove(avId)
            lowTeam.append(avId)

        self.updateToonsPlaying()

    def areEnoughPlayers(self):
        return len(self.leftTeam) + len(self.rightTeam) >= 2

    def isTeamFull(self, team):
        if isinstance(team, int):
            team = self.getTeam(team)
        return len(team) >= self.MAX_PLAYERS_PER_TEAM

    def getTeam(self, teamNum):
        if teamNum == LEFT_TEAM:
            return self.leftTeam
        elif teamNum == RIGHT_TEAM:
            return self.rightTeam
        return None

    def startCountdown(self):
        taskMgr.doMethodLater(self.COUNTDOWN_TIME, self.countdownFinished, self.uniqueName('countdown'))

    def cancelCountdown(self):
        taskMgr.remove(self.uniqueName('countdown'))

    def countdownFinished(self, task):
        self.teamDict = {
            LEFT_TEAM: self.leftTeam,
            RIGHT_TEAM: self.rightTeam
        }
        self.setState('Rules')

    def clearGame(self):
        self.leftTeam = []
        self.rightTeam = []

        self.toonsPlaying = {}
        self.teamDict = {}

        self.updateToonsPlaying()

        self.setState('WaitForEnough')

    @staticmethod
    def isValidTeam(team):
        return (team == PartyGlobals.TeamActivityTeams.LeftTeam) or (team == PartyGlobals.TeamActivityTeams.RightTeam)
