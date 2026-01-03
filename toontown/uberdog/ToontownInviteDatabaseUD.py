"""
Author: Leo
Created: Jan 2026

Purpose: ToontownInviteDatabaseUD handles the storage
         and retrival of long-term party invite data.
"""
from pymongo.collection import ReturnDocument
from typing import Any, TYPE_CHECKING

from direct.directnotify.DirectNotifyGlobal import directNotify

from ..parties.PartyGlobals import EInviteStatus

if TYPE_CHECKING:
    from ..uberdog.ToontownUberRepository import ToontownUberRepository


class ToontownInviteDatabaseUD:
    notify = directNotify.newCategory('ToontownInviteDatabaseUD')

    def __init__(self, air: 'ToontownUberRepository'):
        self.air = air
        self.objects = self.air.mongodb.parties.invites
        self.globals = self.air.mongodb.parties.globals

    # === Invite ID Allocation ==

    def allocateInviteId(self) -> int:
        """
        Returns a unique identifier for a new party.

        Note: Toontown Online does not appear to have any form of ID Recycling
              Hence, this is purely incremental for now.
        """
        result = self.globals.find_one_and_update({'_id': 'GLOBALS'},
                                                  {'$inc': {'nextInviteId': 1}},
                                                  upsert=True,
                                                  return_document=ReturnDocument.AFTER)
        return result['nextInviteId'] - 1

    # === Database Retrieval ===

    def getOneInvite(self, inviteId: int) -> dict[str, Any] | None:
        """
        Attempts to get an invite for the given invite key

        If any records are found, a tuple is returned containing the invite
        """
        result = self.objects.find_one({'inviteId': inviteId})
        return result

    def getInvites(self, avatarId: int) -> tuple[dict[str, Any], ...]:
        """
        Attempts to get all invites for the given avatar ID

        If records are found, a tuple is returned containing the invite(s)

        If none are found, an empty tuple is returned
        """
        results = self.objects.find({'guestId': avatarId})
        return tuple(results)

    def getInviteesOfParty(self, partyId: int) -> tuple[dict[str, int], ...]:
        """
        Attempts to get all invites for the given party ID

        If records are found, a tuple is returned containing the invite(s)

        If none are found, an empty tuple is returned
        """
        results = self.objects.find({'partyId': partyId}, {'guestId': 1, '_id': 0})
        return tuple(results)

    def getReplies(self, partyId: int) -> tuple[dict[str, Any], ...]:
        """
        Attempts to get all replies for the invites for the given party ID

        If records are found, a tuple is returned containing the invite(s)

        If none are found, an empty tuple is returned
        """
        results = self.objects.find({'partyId': partyId})
        return tuple(results)

    # === Database Updates ===

    def putInvite(self, partyId: int, inviteeId: int):
        """
        Attempts to put a new invite into the database.
        """
        self.notify.debug(f'putInvite(): partyId={partyId}, inviteeId={inviteeId}')

        # Try to put the invite into the database
        try:
            inviteData = {
                'inviteId': self.allocateInviteId(),
                'partyId': partyId,
                'guestId': inviteeId,
                'statusId': EInviteStatus.NOT_READ
            }
            self.objects.insert_one(inviteData)
        except Exception as e:
            self.notify.warning(f'Encountered an error while putting invite into database: {e}')

    def updateInvite(self, inviteId: int, newStatus: EInviteStatus):
        """
        Attempts to update an invite for the given invite key to the new status given

        If records are updated, a tuple is returned containing the invite(s)

        If non are updated, an empty tuple is returned
        """
        self.objects.find_one_and_update({'inviteId': inviteId},
                                         {'$set': {'statusId': newStatus}})
