"""
Author: Leo
Created: Jan 2026

Purpose: ToontownPartyDatabaseUD handles the storage
         and retrival of long-term party data.
"""
from datetime import datetime
from pymongo.collection import ReturnDocument
from typing import Any, TYPE_CHECKING

from direct.directnotify.DirectNotifyGlobal import directNotify

from ..parties.PartyGlobals import EActivityId, EDecorationId, EInviteTheme, EPartyStatus, MaxHostedPartiesPerToon

if TYPE_CHECKING:
    from ..uberdog.ToontownUberRepository import ToontownUberRepository


class ToontownPartyDatabaseUD:
    notify = directNotify.newCategory('ToontownPartyDatabaseUD')

    def __init__(self, air: 'ToontownUberRepository'):
        self.air = air
        self.objects = self.air.mongodb.parties.objects
        self.globals = self.air.mongodb.parties.globals

    # === Party ID Allocation ==

    def allocatePartyId(self) -> int:
        """
        Returns a unique identifier for a new party.

        Note: Toontown Online does not appear to have any form of ID Recycling
              Hence, this is purely incremental for now.
        """
        result = self.globals.find_one_and_update({'_id': 'GLOBALS'},
                                                  {'$inc': {'nextPartyId': 1}},
                                                  upsert=True,
                                                  return_document=ReturnDocument.AFTER)
        return result['nextPartyId'] - 1

    # === Database Retrieval ===

    def getParty(self, partyId: int) -> dict[str, Any] | None:
        """
        Retrieves a party object from the database by the given partyId.
        """
        result = self.objects.find_one({'partyId': partyId})
        return result

    def getMultipleParties(self, partyIds: list[int]) -> tuple[dict[str, Any], ...]:
        """
        Retrieves all parties of the given partyIds.
        """
        result = self.objects.find({'partyId': {'$in': partyIds}})
        return tuple(result)

    def getPartiesOfHost(self, hostId: int) -> tuple[dict[str, Any], ...]:
        """
        Retrieves all parties being hosted by the given hostId.
        """
        results = self.objects.find({'hostId': hostId})
        return tuple(results)

    def getPartiesOfHostThatCanStart(self, hostId: int) -> tuple[dict[str, Any], ...]:
        """
        Retrieves all parties of the host that can start.
        """
        results = self.objects.find({'hostId': hostId, 'statusId': EPartyStatus.CAN_START})
        return tuple(results)

    def getPartiesAvailableToStart(self, thresholdTime: datetime) -> tuple[dict[str, Any], ...]:
        """
        Retrieves and updates all parties that are ready to start.
        """
        query = {'statusId': EPartyStatus.PENDING, 'startTime': {'$lte': thresholdTime}}
        result = tuple(self.objects.find(query))
        if result:
            self.objects.update_many(query,
                                     {'$set': {'statusId': EPartyStatus.CAN_START}})
        return result

    def getPrioritizedPartiesOfQuery(self, query: dict[str, Any], thresholdTime: datetime, slotsLeft: int,
                                     future: bool, cancelled: bool) -> tuple[dict[str, Any], ...]:
        """
        A helper function that retrieves at most [slotsLeft] parties matching the query information alongside
        the provided thresholdTime; sorted by time and filtered by status.
        """
        if future:
            query['startTime'] = {'$gte': thresholdTime}
            sortOrder = 1
        else:
            query['startTime'] = {'$lt': thresholdTime}
            sortOrder = -1

        if cancelled:
            # We only want to retrieve a party if it is cancelled
            query['statusId'] = EPartyStatus.CANCELLED
        else:
            # As long as the status isn't cancelled, we are happy to consider this party
            query['statusId'] = {'$ne': EPartyStatus.CANCELLED}

        results = self.objects.find(query).sort('startTime', sortOrder).limit(slotsLeft)
        return tuple(results)

    def getPrioritizedParties(self, partyIds: list[int], thresholdTime: datetime, slotsLeft: int,
                              future: bool, cancelled: bool) -> tuple[dict[str, Any], ...]:
        """
        Retrieve at most [slotsLeft] parties of the given partyIds that match the provided thresholdTime;
        sorted by time and filtered by status
        """
        query = {'partyId': {'$in': partyIds}}
        return self.getPrioritizedPartiesOfQuery(query, thresholdTime, slotsLeft, future, cancelled)

    def getHostPrioritizedParties(self, hostId: int, thresholdTime: datetime, slotsLeft: int,
                                  future: bool, cancelled: bool) -> tuple[dict[str, Any], ...]:
        """
        Retrieve at most [slotsLeft] parties of the given host that match the provided thresholdTime;
        sorted by time and filtered by status
        """
        query = {'hostId': hostId}
        return self.getPrioritizedPartiesOfQuery(query, thresholdTime, slotsLeft, future, cancelled)

    # === Database Updates ===

    def putParty(self, hostId: int, startTime: str, endTime: str, isPrivate: bool,
                 inviteTheme: EInviteTheme, activities: list[EActivityId],
                 decorations: list[EDecorationId], status: EPartyStatus) -> bool:
        """
        Attempts to put a new party into the database.

        Returns False if the operation failed for any reason.
        """
        self.notify.debug(
            f'putParty(): hostId={hostId}, startTime={startTime}, endTime={endTime}, isPrivate={isPrivate} '
            f'inviteTheme={inviteTheme}, activities={activities}, decorations={decorations}, status={status}'
        )

        # We need to make sure our host is not hosting too many parties at once
        numHostedParties = self.objects.count_documents({'hostId': hostId, 'statusId': EPartyStatus.PENDING})
        if numHostedParties >= MaxHostedPartiesPerToon:
            self.notify.debug(f"{hostId} can't host another party. limit={MaxHostedPartiesPerToon}")
            return False

        # We're all good to go, try to put the party into the database
        try:
            partyData = {
                'partyId': self.allocatePartyId(),
                'hostId': hostId,
                'startTime': datetime.strptime(startTime, "%Y-%m-%d %H:%M:%S").astimezone(self.air.toontownTimeManager.serverTimeZone),
                'endTime': datetime.strptime(endTime, "%Y-%m-%d %H:%M:%S").astimezone(self.air.toontownTimeManager.serverTimeZone),
                'isPrivate': isPrivate,
                'inviteTheme': inviteTheme,
                'activities': activities,
                'decorations': decorations,
                'statusId': status
            }
            self.objects.insert_one(partyData)
            return True
        except Exception as e:
            self.notify.warning(f'Encountered an error while putting party into database: {e}')
            return False

    def changePrivate(self, partyId: int, newPrivateStatus: bool):
        """
        Attempts to change the party's private status of the new one provided.
        """
        self.objects.find_one_and_update({'partyId': partyId},
                                         {'$set': {'isPrivate': newPrivateStatus}})

    def changePartyStatus(self, partyId: int, newStatus: EPartyStatus):
        """
        Attempts to change the party's status to the new one provided.
        """
        self.objects.find_one_and_update({'partyId': partyId},
                                         {'$set': {'statusId': newStatus}})

    def changeMultiplePartiesStatus(self, partyIds: list[int], newStatus: EPartyStatus):
        """
        Attempts to change the status of the given partyIds to the new one provided.
        """
        self.objects.update_many({'partyId': {'$in': partyIds}},
                                 {'$set': {'statusId': newStatus}})

    def forceStatusForStatus(self, currStatus: EPartyStatus, newStatus: EPartyStatus,
                             thresholdTime: datetime) -> tuple[dict[str, Any, ...], ...]:
        """
        Attempts to force any parties currently of a status to a new status
        if it's within the threshold time.

        If updated, return a tuple of the updated parties
        """
        query = {
            'statusId': currStatus,
            'endTime': {'$lte': thresholdTime}
        }
        results = tuple(self.objects.find(query))
        if results:
            self.objects.update_many(query,
                                     {'$set': {'statusId': newStatus}})
        return results

    def forceFinishForStarted(self, thresholdTime: datetime) -> tuple[dict[str, Any, ...], ...]:
        """
        Attempts to finish any started parties if
        it's within the threshold time

        If updated, return a tuple of the updated parties
        """
        return self.forceStatusForStatus(EPartyStatus.STARTED, EPartyStatus.FINISHED, thresholdTime)

    def forceNeverStartedForCanStart(self, thresholdTime: datetime) -> tuple[dict[str, Any, ...], ...]:
        """
        Attempts to mark any ready parties as "never started"
        if it's within the threshold time

        If updated, return a tuple of the updated parties
        """
        return self.forceStatusForStatus(EPartyStatus.CAN_START, EPartyStatus.NEVER_STARTED, thresholdTime)
