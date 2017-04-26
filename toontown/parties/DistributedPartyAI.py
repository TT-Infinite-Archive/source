from direct.distributed.DistributedObjectAI import DistributedObjectAI
from direct.directnotify import DirectNotifyGlobal

from toontown.parties.DistributedPartyCogActivityAI import DistributedPartyCogActivityAI
from toontown.parties.DistributedPartyTugOfWarActivityAI import DistributedPartyTugOfWarActivityAI
from toontown.parties.DistributedPartyCannonActivityAI import DistributedPartyCannonActivityAI
from toontown.parties.DistributedPartyTrampolineActivityAI import DistributedPartyTrampolineActivityAI
from toontown.parties.DistributedPartyJukeboxActivityAI import DistributedPartyJukeboxActivityAI
from toontown.parties.DistributedPartyJukebox40ActivityAI import DistributedPartyJukebox40ActivityAI
from toontown.parties.DistributedPartyDanceActivityAI import DistributedPartyDanceActivityAI
from toontown.parties.DistributedPartyDance20ActivityAI import DistributedPartyDance20ActivityAI
from toontown.parties.DistributedPartyCatchActivityAI import DistributedPartyCatchActivityAI
from toontown.parties.DistributedPartyFireworksActivityAI import DistributedPartyFireworksActivityAI
from toontown.parties.DistributedPartyCannonAI import DistributedPartyCannonAI
from toontown.parties import PartyGlobals
from toontown.parties import PartyUtils
from toontown.parties.ToontownTimeZone import ToontownTimeZone

from datetime import datetime
from toontown.parties.PartyGlobals import ActivityIds, PartyGridHeadingConverter


class DistributedPartyAI(DistributedObjectAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedPartyAI')

    ACTIVITIES = {
        PartyGlobals.ActivityIds.PartyCog: DistributedPartyCogActivityAI,
        PartyGlobals.ActivityIds.PartyTugOfWar: DistributedPartyTugOfWarActivityAI,
        PartyGlobals.ActivityIds.PartyCannon: DistributedPartyCannonAI,
        PartyGlobals.ActivityIds.PartyTrampoline: DistributedPartyTrampolineActivityAI,
        PartyGlobals.ActivityIds.PartyJukebox: DistributedPartyJukeboxActivityAI,
        PartyGlobals.ActivityIds.PartyJukebox40: DistributedPartyJukebox40ActivityAI,
        PartyGlobals.ActivityIds.PartyDance: DistributedPartyDanceActivityAI,
        PartyGlobals.ActivityIds.PartyDance20: DistributedPartyDance20ActivityAI,
        PartyGlobals.ActivityIds.PartyCatch: DistributedPartyCatchActivityAI,
        PartyGlobals.ActivityIds.PartyFireworks: DistributedPartyFireworksActivityAI     
    }

    def __init__(self, air, hostId, zoneId, partyInfo):
        DistributedObjectAI.__init__(self, air)

        self.hostId = hostId
        self.zoneId = zoneId
        self.partyInfo = partyInfo

        self.startTime = datetime.strftime(datetime.now(ToontownTimeZone()), '%Y-%m-%d %H:%M:%S')
        self.partyState = PartyGlobals.PartyStatus.Pending
        self.participants = []

        for activity in self.partyInfo['activities']:
            if activity[0] == PartyGlobals.ActivityIds.PartyClock:
                self.partyClockInfo = (activity[1], activity[2], activity[3])

        self.hostName = ''
        self.cannonActivityGenerated = 0

        host = self.air.doId2do.get(self.hostId)
        if host is not None:
            self.hostName = host.getName()
        else:
            self.air.dbInterface.queryObject(self.air.dbId, self.hostId, self.__gotHost)

        self.activities = []

    def __gotHost(self, dclass, fields):
        if dclass != self.air.dclassesByName['DistributedToonAI']:
            self.notify.warning('Got object of wrong type!')
            return

        self.hostName = fields['setName'][0]

    def generate(self):
        DistributedObjectAI.generate(self)

        for activityInfo in self.partyInfo['activities']:

            if activityInfo[0] not in self.ACTIVITIES:
                self.notify.warning('Tried to generate invalid activity %s' % activityInfo[0])
                continue

            if activityInfo[0] == PartyGlobals.ActivityIds.PartyCannon:
                if not self.cannonActivityGenerated:
                    self.cannonActivity = DistributedPartyCannonActivityAI(self.air, self, activityInfo)
                    self.cannonActivity.generateWithRequired(self.zoneId)
                    self.cannonActivityGenerated = 1

                activity = DistributedPartyCannonAI(self.air)
                activity.setActivityDoId(self.cannonActivity.doId)
                x = PartyUtils.convertDistanceFromPartyGrid(activityInfo[1], 0)
                y = PartyUtils.convertDistanceFromPartyGrid(activityInfo[2], 1)
                h = activityInfo[3] * PartyGlobals.PartyGridHeadingConverter
                activity.setPosHpr(x, y, 0, h, 0, 0)
            else:
                activity = self.ACTIVITIES[activityInfo[0]](self.air, self, activityInfo)

            if isinstance(activity, DistributedPartyCogActivityAI):
                activity.setCanSwitchTeams(1)

            activity.generateWithRequired(self.zoneId)
            self.activities.append(activity)

    def delete(self):
        for activity in self.activities:
            activity.requestDelete()

        DistributedObjectAI.delete(self)

    def getPartyClockInfo(self):
        return self.partyClockInfo

    def getInviteeIds(self):
        return self.partyInfo.get('inviteeIds', [])

    def getPartyState(self):
        return self.partyState

    def setPartyState(self, partyState):
        self.partyState = partyState
        self.sendUpdate('setPartyState', [partyState])

    def getPartyInfoTuple(self):
        return DistributedPartyAI.formatPartyInfo(self.partyInfo)

    def getAvIdsAtParty(self):
        return self.participants

    def getPartyStartedTime(self):
        return self.startTime

    def getHostName(self):
        return self.hostName

    def enteredParty(self):
        avId = self.air.getAvatarIdFromSender()
        if avId not in self.air.doId2do:
            self.notify.warning('Unknown avatar %s tried to enter the party!' % avId)
            return

        if avId in self.participants:
            self.notify.warning('Avatar %s tried to enter the party twice!' % avId)
            return

        self.air.globalPartyMgr.d_toonJoinedParty(self.partyInfo['partyId'], avId)
        self.participants.append(avId)
        self.acceptOnce(self.air.getAvatarExitEvent(avId), self.handleUnexpectedExit, extraArgs=[avId])

    def handleUnexpectedExit(self, avId):
        if avId in self.participants:
            if self.air and self.partyInfo:
                self.air.globalPartyMgr.d_toonLeftParty(self.partyInfo['partyId'], avId)
            self.participants.remove(avId)

    def removeAvatar(self, avId):
        if avId not in self.participants:
            self.notify.warning('Unknown avatar %s tried to leave the party!' % avId)
            return

        self.air.globalPartyMgr.d_toonLeftParty(self.partyInfo['partyId'], avId)
        self.participants.remove(avId)

    @staticmethod
    def formatPartyInfo(partyInfo, status=PartyGlobals.PartyStatus.Started):
        start = partyInfo['start']
        end = partyInfo['end']
        return [partyInfo['partyId'], partyInfo['hostId'], start.year, start.month, start.day, start.hour, start.minute,
                end.year, end.month, end.day, end.hour, end.minute, partyInfo['isPrivate'], partyInfo['inviteTheme'],
                partyInfo['activities'], partyInfo['decorations'], status]
