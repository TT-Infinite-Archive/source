import datetime
from direct.directnotify.DirectNotifyGlobal import directNotify
from ..parties.PartyGlobals import EActivityId, EAddPartyErrorCode, EDecorationId, EInviteTheme, EPartyStatus, \
    MaxHostedPartiesPerToon

class ToontownPartyDatabaseUD:
    notify = directNotify.newCategory('ToontownPartyDatabaseUD')

    def __init__(self, air):
        pass

    def getParty(self, partyId: int):
        return None

    def getPartiesOfHost(self, hostId: int):
        return []

    def getPrioritizedParties(self, partyIds: list[int], thresholdTime, slotsLeft,
                              future: bool, cancelled: bool):
        return ()

    def getHostPrioritizedParties(self, hostId: int, thresholdTime, slotsLeft,
                                  future: bool, cancelled: bool):
        return ()

    def getPartiesOfHostThatCanStart(self, hostId: int):
        return []

    def getPartiesAvailableToStart(self, curServerDateTime):
        return []

    def getMultipleParties(self, interruptedParties):
        return []

    def putParty(self, hostId: int, startTime: float, endTime: float, isPrivate: bool,
                 inviteTheme: EInviteTheme, activities: list[EActivityId],
                 decorations: list[EDecorationId], partyStatus: EPartyStatus) -> bool:
        """
        Returns False if the operation failed for any reason
        """
        return False

    def changePrivate(self, partyId: int, newPrivateStatus):
        pass

    def changePartyStatus(self, partyId: int, newPartyStatus):
        pass

    def changeMultiplePartiesStatus(self, interruptedParties, partyStatus):
        pass

    def forceFinishForStarted(self, thresholdTime):
        return []

    def forceNeverStartedForCanStart(self, curServerDateTime):
        return []
