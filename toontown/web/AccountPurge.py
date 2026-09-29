from direct.directnotify import DirectNotifyGlobal

from toontown.friends.TTIFriendsManagerUD import RemoveFriendOperation

# Where an account's Toons may have been left over from a legacy claim
RETIRED_PREFIX = 'migrated:'

KICK_REASON = 'Your account has been deleted.'
SETTLE_SECONDS = 5


class AccountPurge:
    """
    Permanently removes a website user's game data once their grace period
    is up: the account, every Toon on it (deleted ones included), and what
    hangs off those Toons.
    """

    notify = DirectNotifyGlobal.directNotify.newCategory('AccountPurge')

    def __init__(self, air, userId, done):
        self.air = air
        self.userId = userId
        self.done = done
        self.objects = air.dbAstronCursor.objects

        self.accounts = []
        self.avIds = []
        self.toons = {}
        self.waiting = 0

    def start(self):
        self.accounts = [
            document for document in self.objects.find(
                {'fields.ACCOUNT_ID': {'$in': [self.userId, RETIRED_PREFIX + self.userId]}})
            if document.get('dclass') == 'Account'
        ]

        if not self.accounts:
            self.done(True, {'found': False})
            return

        for account in self.accounts:
            self.air.csm.killAccount(account['_id'], KICK_REASON)

            fields = account['fields']
            self.avIds += [int(avId) for avId in fields.get('ACCOUNT_AV_SET') or [] if int(avId)]
            self.avIds += [int(entry.get('Avatar') or 0)
                           for entry in fields.get('ACCOUNT_AV_SET_DEL') or []
                           if int(entry.get('Avatar') or 0)]

        self.avIds = sorted(set(self.avIds))

        taskMgr.doMethodLater(SETTLE_SECONDS, self.readToons,
                              'account-purge-read-%s' % self.userId, extraArgs=[])

    def readToons(self):
        if not self.avIds:
            self.detach()
            return

        self.waiting = len(self.avIds)
        for avId in self.avIds:
            self.air.dbInterface.queryObject(
                self.air.dbId, avId,
                lambda dclass, fields, avId=avId: self.handleToon(avId, dclass, fields))

    def handleToon(self, avId, dclass, fields):
        if dclass == self.air.dclassesByName['DistributedToonUD']:
            self.toons[avId] = fields

        self.waiting -= 1
        if self.waiting == 0:
            self.detach()

    def detach(self):
        """
        Takes the Toons out of everything other players still hold, so nothing
        is left pointing at a Toon that no longer exists.
        """
        friends = self.air.globalObjects.get('TTIFriendsManager')
        guilds = self.air.globalObjects.get('GuildManager')

        for avId, fields in self.toons.items():
            for entry in fields.get('setFriendsList', [[]])[0]:
                friendId = int(entry[0])
                if friends is None or friendId in self.toons:
                    continue
                operation = RemoveFriendOperation(friends, self.air, friendId, avId, alert=True)
                friends.operations.append(operation)
                operation.demand('Start')

            guildId = fields.get('setGuildId', [0])[0]
            if guildId and guilds is not None:
                guilds.callWhenLoaded(lambda avId=avId: self.leaveGuild(guilds, avId))

        taskMgr.doMethodLater(SETTLE_SECONDS, self.delete,
                              'account-purge-delete-%s' % self.userId, extraArgs=[])

    def leaveGuild(self, guilds, avId):
        guild = guilds.guilds.get(guilds.avId2GuildId.get(avId))
        if guild is None:
            return

        member = guild.getMember(avId)
        if member is None:
            return

        # A guild whose owner walks out with others still in it has no one left to run it
        others = [other for otherId, other in guild.avId2Member.items()
                  if otherId != avId and otherId not in self.toons]
        if others and member.getRole().sortIndex == 0:
            successor = min(others, key=lambda other: other.getRole().sortIndex)
            guild.transferOwnership(avId, successor.id)

        guild.adminLeave(avId)

    def delete(self):
        ids = list(self.avIds)

        for account in self.accounts:
            ids.append(account['_id'])
            estateId = int(account['fields'].get('ESTATE_ID') or 0)
            if estateId:
                ids.append(estateId)

        for fields in self.toons.values():
            for field in ('setPetId', 'setHouseId'):
                objectId = int(fields.get(field, [0])[0] or 0)
                if objectId:
                    ids.append(objectId)

        removed = self.objects.delete_many({'_id': {'$in': ids}}).deleted_count

        mongodb = self.air.mongodb
        parties = [party['partyId'] for party in
                   mongodb.parties.objects.find({'hostId': {'$in': self.avIds}}, {'partyId': 1})]
        mongodb.parties.objects.delete_many({'partyId': {'$in': parties}})
        mongodb.parties.invites.delete_many(
            {'$or': [{'partyId': {'$in': parties}}, {'guestId': {'$in': self.avIds}}]})
        mongodb.gamedata.gifting.delete_many(
            {'$or': [{'gifteeId': {'$in': self.avIds}}, {'gifterId': {'$in': self.avIds}}]})
        mongodb.crashes.delete_many({'avId': {'$in': self.avIds}})

        self.air.writeServerEvent('account-purged', self.userId, len(self.avIds), removed)
        self.notify.info('Purged %s: %d Toons, %d objects.'
                         % (self.userId, len(self.avIds), removed))

        self.done(True, {'found': True, 'toons': len(self.avIds), 'objects': removed})
