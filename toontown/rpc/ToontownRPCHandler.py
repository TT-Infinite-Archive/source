from panda3d.core import Datagram
import datetime
import re

from direct.distributed.MsgTypes import CLIENTAGENT_EJECT
from direct.distributed.PyDatagram import PyDatagram

from direct.stdpy import threading2

from otp.distributed import OtpDoGlobals
from toontown.distributed.ShardStatusReceiver import ShardStatusReceiver
from toontown.rpc.ToontownRPCHandlerBase import *
from toontown.toon import ToonDNA
from toontown.toonbase import TTLocalizer
from toontown.guilds.GuildGlobals import GUILD_FIELD_NAME_STATUS
from toontown.guilds.GuildGlobals import GUILD_FIELD_NAME, GUILD_NAME_ACCEPTED
from toontown.guilds.GuildGlobals import GUILD_FIELD_PENDING_NAME
from toontown.guilds.GuildGlobals import GUILD_NAME_REJECTED


class ToontownRPCHandler(ToontownRPCHandlerBase):
    def __init__(self, air):
        ToontownRPCHandlerBase.__init__(self, air)
        self.shardStatus = ShardStatusReceiver(air)

    # --- TESTS ---

    @rpcmethod(accessLevel=USER)
    def rpc_ping(self, data):
        """
        Summary:
            Responds with the provided [data]. This method exists for testing
            purposes.

        Parameters:
            [any data] = The data to be given back in response.

        Example response: 'pong'
        """
        return data

    # --- GENERAL ---

    @rpcmethod(accessLevel=SYSTEM_ADMINISTRATOR)
    def rpc_queryObject(self, doId):
        """
        Summary:
            Responds with the values of all database fields associated with the
            provided [doId].

        Parameters:
            [int doId] = The ID of the object to query database fields on.

        Example response:
            On success: ['DistributedObject', {'fieldName': ('arg1', ...), ...}]
            On failure: [None, None]
        """
        result = []
        unblocked = threading2.Event()

        def callback(dclass, fields):
            if dclass is not None:
                dclass = dclass.getName()
            result.extend([dclass, fields])
            unblocked.set()

        self.air.dbInterface.queryObject(self.air.dbId, doId, callback)

        # Block until the callback is executed:
        unblocked.wait()

        return result

    @rpcmethod(accessLevel=SYSTEM_ADMINISTRATOR)
    def rpc_updateObject(self, doId, dclassName, newFields, oldFields=None):
        """
        Summary:
            Update the field(s) in the database of the object associated with
            the provided [doId]. If <oldFields> is provided, then this method
            will fail if the object's current fields don't match.

        Parameters:
            [int doId] = The ID of the object whose fields are to be updated in
                         the database.
            [str dclassName] = The name of the object's DClass.
            [dict newFields] = The new field values.
            <dict oldFields> = The old field values to assert.

        Example response:
            On success: True
            On failure: False
        """
        # Ensure that the provided DClass exists:
        if dclassName not in self.air.dclassesByName:
            dclassName += 'UD'
            if dclassName not in self.air.dclassesByName:
                return False

        dclass = self.air.dclassesByName[dclassName]

        if oldFields is None:
            self.air.dbInterface.updateObject(
                self.air.dbId, doId, dclass, newFields)
            return True

        result = [True]
        unblocked = threading2.Event()

        def callback(fields):
            if fields is not None:
                result[0] = False
            unblocked.set()

        self.air.dbInterface.updateObject(
            self.air.dbId, doId, dclass, newFields, oldFields=oldFields,
            callback=callback)

        # Block until the callback is executed:
        unblocked.wait()

        return result[0]

    @rpcmethod(accessLevel=SYSTEM_ADMINISTRATOR)
    def rpc_setField(self, doId, dclassName, fieldName, args=None):
        """
        Summary:
            Set the value of the field named [fieldName] on the object
            associated with the provided [doId].

        Parameters:
            [int doId] = The ID of the object whose field is being modified.
            [str dclassName] = The name of the object's DClass.
            [str fieldName] = The name of the field to be modified.
            [list args] = The new value for the field.

        Example response:
            On success: True
            On failure: False
        """
        if args is None:
            args = []

        # Ensure that the provided DClass exists:
        if dclassName not in self.air.dclassesByName:
            dclassName += 'UD'
            if dclassName not in self.air.dclassesByName:
                return False

        dclass = self.air.dclassesByName[dclassName]

        datagram = dclass.aiFormatUpdate(
            fieldName, doId, doId, self.air.ourChannel, args)
        self.air.send(datagram)

        return True

    @rpcmethod(accessLevel=SYSTEM_ADMINISTRATOR)
    def rpc_reloadConfig(self, channel):
        """
        Summary:
            Reloads all configuration files on the service associated with the
            provided [channel].

        Parameters:
            [int channel] = The channel associated with the service that is
                going to have its configuration files reloaded.
        """
        if channel == self.air.ourChannel:
            self.air.handleReloadConfig(self.air.ourChannel)
        else:
            self.air.sendNetEvent('reloadConfig', [channel])

    # --- MESSAGES ---

    @rpcmethod(accessLevel=SYSTEM_ADMINISTRATOR)
    def rpc_messageChannel(self, channel, message):
        """
        Summary:
            Broadcasts a [message] to any client whose Client Agent is
            subscribed to the provided [channel].

        Parameters:
            [int channel] = The channel to direct the message to.
            [str message] = The message to broadcast.
        """
        dclass = self.air.dclassesByName['ClientServicesManagerUD']
        datagram = dclass.aiFormatUpdate(
            'systemMessage', OtpDoGlobals.OTP_DO_ID_CLIENT_SERVICES_MANAGER,
            channel, 1000000, [message])
        self.air.send(datagram)

    @rpcmethod(accessLevel=SYSTEM_ADMINISTRATOR)
    def rpc_messageAll(self, message):
        """
        Summary: Broadcasts a [message] to all clients.

        Parameters:
            [str message] = The message to broadcast.
        """
        self.rpc_messageChannel(10, message)

    @rpcmethod(accessLevel=SYSTEM_ADMINISTRATOR)
    def rpc_messageShard(self, shardId, message):
        """
        Summary:
            Broadcasts a [message] to all clients under the provided [shardId].

        Parameters:
            [int shardId] = The ID of the shard to direct the message to.
            [str message] = The message to broadcast.
        """
        # Get the ID of the ToontownDistrict object:
        districtId = shardId + 1

        # Use it to get the uber zone's channel:
        channel = (districtId << 32) | 2

        self.rpc_messageChannel(channel, message)

    @rpcmethod(accessLevel=MODERATOR)
    def rpc_messageStaff(self, message):
        """
        Summary:
            Broadcasts a [message] to any client whose access level is higher
            than that of a standard user.

        Parameters:
            [str message] = The message to broadcast.
        """
        self.rpc_messageChannel(OtpDoGlobals.OTP_STAFF_CHANNEL, message)

    @rpcmethod(accessLevel=MODERATOR)
    def rpc_messageUser(self, userId, message):
        """
        Summary:
            Sends a [message] to the client associated with the provided
            [userId].

        Parameters:
            [int/str userId] = The ID of the user to send the message to.
            [str message] = The message to send.
        """
        accountId = self.rpc_getUserAccountId(userId)
        if accountId is not None:
            self.rpc_messageAccount(accountId, message)

    @rpcmethod(accessLevel=MODERATOR)
    def rpc_messageAccount(self, accountId, message):
        """
        Summary:
            Sends a [message] to the client associated with the provided
            [accountId].

        Parameters:
            [int accountId] = The ID of the account to send the message to.
            [str message] = The message to send.
        """
        channel = accountId + (1003 << 32)
        self.rpc_messageChannel(channel, message)

    @rpcmethod(accessLevel=MODERATOR)
    def rpc_messageAvatar(self, avId, message):
        """
        Summary:
            Sends a [message] to the client associated with the provided
            [avId].

        Parameters:
            [int avId] = The ID of the avatar to send the message to.
            [str message] = The message to send.
        """
        channel = avId + (1001 << 32)
        self.rpc_messageChannel(channel, message)

    # --- KICKS ---

    @rpcmethod(accessLevel=SYSTEM_ADMINISTRATOR)
    def rpc_kickChannel(self, channel, code, reason):
        """
        Summary:
            Kicks any client whose Client Agent is subscribed to the provided
            [channel].

        Parameters:
            [int channel] = The channel to kick.
            [int code] = The code for the kick.
            [str reason] = The reason for the kick.
        """
        datagram = PyDatagram()
        datagram.addServerHeader(channel, self.air.ourChannel,
                                 CLIENTAGENT_EJECT)
        datagram.addUint16(code)
        datagram.addString(reason)
        self.air.send(datagram)

    @rpcmethod(accessLevel=SYSTEM_ADMINISTRATOR)
    def rpc_kickAll(self, code, reason):
        """
        Summary: Kicks all clients.

        Parameters:
            [int code] = The code for the kick.
            [str reason] = The reason for the kick.
        """
        self.rpc_kickChannel(10, code, reason)

    @rpcmethod(accessLevel=SYSTEM_ADMINISTRATOR)
    def rpc_kickShard(self, shardId, code, reason):
        """
        Summary: Kicks all clients under the provided [shardId].

        Parameters:
            [int shardId] = The ID of the shard to kick.
            [int code] = The code for the kick.
            [str reason] = The reason for the kick.
        """
        # Get the ID of the ToontownDistrict object:
        districtId = shardId + 1

        # Use it to get the uber zone's channel:
        channel = (districtId << 32) | 2

        self.rpc_kickChannel(channel, code, reason)

    @rpcmethod(accessLevel=MODERATOR)
    def rpc_kickUser(self, userId, code, reason):
        """
        Summary: Kicks the client associated with the provided [userId].

        Parameters:
            [int/str userId] = The ID of the user to kick.
            [int code] = The code for the kick.
            [str reason] = The reason for the kick.
        """
        accountId = self.rpc_getUserAccountId(userId)
        if accountId is not None:
            self.rpc_kickAccount(accountId, code, reason)

    @rpcmethod(accessLevel=MODERATOR)
    def rpc_kickAccount(self, accountId, code, reason):
        """
        Summary: Kicks the client associated with the provided [accountId].

        Parameters:
            [int accountId] = The ID of the account to kick.
            [int code] = The code for the kick.
            [str reason] = The reason for the kick.
        """
        channel = accountId + (1003 << 32)
        self.rpc_kickChannel(channel, code, reason)

    @rpcmethod(accessLevel=MODERATOR)
    def rpc_kickAvatar(self, avId, code, reason):
        """
        Summary: Kicks the client associated with the provided [avId].

        Parameters:
            [int avId] = The ID of the avatar to kick.
            [int code] = The code for the kick.
            [str reason] = The reason for the kick.
        """
        channel = avId + (1001 << 32)
        self.rpc_kickChannel(channel, code, reason)

    # --- BANS ---

    @rpcmethod(accessLevel=MODERATOR)
    def rpc_banUser(self, userId, duration, reason):
        """
        Summary:
            Bans the user associated with the provided [userId] for the
            specified [duration].

        Parameters:
            [int/str userId] = The ID of the user to ban.
            [int duration] = The ban's duration in days. If this is 0 or less,
                the user will be permanently banned.
            [str reason] = A short description of why this user is being
                banned. This can be one of the following values: 'hacking',
                'language', 'other'.

        Example response:
            On success: True
            On failure: False
        """
        if reason not in ('hacking', 'language', 'other'):
            return False

        expiration = 0
        if duration > 0:
            now = datetime.date.today()
            expiration = time.mktime(
                (now + datetime.timedelta(days=duration)).timetuple())

        self.air.writeServerEvent('ban', userId, expiration, reason)

        self.rpc_kickUser(userId, 152, 'ban-' + str(expiration))

        return True

    @rpcmethod(accessLevel=MODERATOR)
    def rpc_banAccount(self, accountId, duration, reason):
        """
        Summary:
            Bans the user associated with the provided [accountId] for the
            specified [duration].

        Parameters:
            [int accountId] = The ID of the account associated with the user to
                ban.
            [int duration] = The ban's duration in days. If this is 0 or less,
                the user will be permanently banned.
            [str reason] = A short description of why this user is being
                banned. This can be one of the following values: 'hacking',
                'language', 'other'.

        Example response:
            On success: True
            On failure: False
        """
        userId = self.rpc_getAccountUserId(accountId)
        return self.rpc_banUser(userId, duration, reason)

    @rpcmethod(accessLevel=MODERATOR)
    def rpc_banAvatar(self, avId, duration, reason):
        """
        Summary:
            Bans the user associated with the provided [avId] for the specified
            [duration].

        Parameters:
            [int/str avId] = The ID of the avatar associated with the user to
                be banned.
            [int duration] = The ban's duration in days. If this is 0 or less,
                the user will be permanently banned.
            [str reason] = A short description of why this user is being
                banned. This can be one of the following values: 'hacking',
                'language', 'other'.

        Example response:
            On success: True
            On failure: False
        """
        userId = self.rpc_getAvatarUserId(avId)
        return self.rpc_banUser(userId, duration, reason)

    # --- USERS ---

    @rpcmethod(accessLevel=MODERATOR)
    def rpc_getUserAccountId(self, userId):
        """
        Summary:
            Responds with the ID of the account associated with the provided
            [userId].

        Parameters:
            [int/str userId] = The ID of the user to query the account ID on.

        Example response:
            On success: 100000000
            On failure: None
        """
        return self.air.csm.accountDB.lookupUserId(userId)['accountId'] or None

    @rpcmethod(accessLevel=MODERATOR)
    def rpc_getUserAvatars(self, userId):
        """
        Summary:
            Responds with a list of avatar IDs associated with the provided
            [userId].

        Parameters:
            [int/str userId] = The ID of the user to query the avatars on.

        Example response:
            On success: [0, 100000001, 0, 0, 0, 0]
            On failure: None
        """
        accountId = self.rpc_getUserAccountId(userId)
        if accountId is not None:
            return self.rpc_getAccountAvatars(accountId)

    @rpcmethod(accessLevel=MODERATOR)
    def rpc_getUserDeletedAvatars(self, userId):
        """
        Summary:
            Responds with a list of deleted avatar IDs associated with the
            provided [userId], along with the time at which each avatar was
            deleted.

        Parameters:
            [int/str userId] = The ID of the user to query the deleted avatars
                on.

        Example response:
            On success: [[100000001, 1409665000], ...]
            On failure: None
        """
        accountId = self.rpc_getUserAccountId(userId)
        if accountId is not None:
            return self.rpc_getAccountDeletedAvatars(accountId)

    # --- ACCOUNTS ---

    @rpcmethod(accessLevel=MODERATOR)
    def rpc_getAccountUserId(self, accountId):
        """
        Summary:
            Responds with the ID of the user associated with the provided
            [accountId].

        Parameters:
            [int accountId] = The ID of the account to query the user ID on.

        Example response:
            On success: 1
            On failure: None
        """
        dclassName, fields = self.rpc_queryObject(accountId)
        if dclassName == 'Account':
            return fields['ACCOUNT_ID']

    @rpcmethod(accessLevel=MODERATOR)
    def rpc_getAccountAvatars(self, accountId):
        """
        Summary:
            Responds with a list of avatar IDs associated with the provided
            [accountId].

        Parameters:
            [int accountId] = The ID of the account to query the avatar IDs on.

        Example response:
            On success: [0, 100000001, 0, 0, 0, 0]
            On failure: None
        """
        dclassName, fields = self.rpc_queryObject(accountId)
        if dclassName == 'Account':
            return fields['ACCOUNT_AV_SET']

    @rpcmethod(accessLevel=MODERATOR)
    def rpc_getAccountDeletedAvatars(self, accountId):
        """
        Summary:
            Responds with a list of deleted avatar IDs associated with the
            provided [accountId], along with the time at which each avatar was
            deleted.

        Parameters:
            [int accountId] = The ID of the account to query the deleted
                avatars on.

        Example response:
            On success: [[100000001, 1409665000], ...]
            On failure: None
        """
        dclassName, fields = self.rpc_queryObject(accountId)
        if dclassName == 'Account':
            return fields['ACCOUNT_AV_SET_DEL']

    # --- AVATARS ---

    @rpcmethod(accessLevel=MODERATOR)
    def rpc_getAvatarUserId(self, avId):
        """
        Summary:
            Responds with the ID of the user associated with the provided
            [avId].

        Parameters:
            [int avId] = The ID of the avatar to query the user ID on.

        Example response:
            On success: 1
            On failure: None
        """
        accountId = self.rpc_getAvatarAccountId(avId)
        if accountId is not None:
            return self.rpc_getAccountUserId(accountId)

    @rpcmethod(accessLevel=MODERATOR)
    def rpc_getAvatarAccountId(self, avId):
        """
        Summary:
            Responds with the ID of the account associated with the provided
            [avId].

        Parameters:
            [int avId] = The ID of the avatar to query the account ID on.

        Example response:
            On success: 100000000
            On failure: None
        """
        dclassName, fields = self.rpc_queryObject(avId)
        if dclassName == 'DistributedToon':
            return fields['setDISLid'][0]

    @rpcmethod(accessLevel=MODERATOR)
    def rpc_getAvatarAvatars(self, avId):
        """
        Summary:
            Responds with a list of avatar IDs associated with the provided
            [avId].

        Parameters:
            [int avId] = The ID of the avatar to query the avatar IDs on.

        Example response:
            On success: [0, 100000001, 0, 0, 0, 0]
            On failure: None
        """
        accountId = self.rpc_getAvatarAccountId(avId)
        if accountId is not None:
            return self.rpc_getAccountAvatars(accountId)

    @rpcmethod(accessLevel=MODERATOR)
    def rpc_getAvatarDeletedAvatars(self, avId):
        """
        Summary:
            Responds with a list of deleted avatar IDs associated with the
            provided [avId], along with the time at which each avatar was
            deleted.

        Parameters:
            [int avId] = The ID of the avatar to query the deleted avatars on.

        Example response:
            On success: [[100000001, 1409665000], ...]
            On failure: None
        """
        accountId = self.rpc_getAvatarAccountId(avId)
        if accountId is not None:
            return self.rpc_getAccountDeletedAvatars(accountId)

    @rpcmethod(accessLevel=MODERATOR)
    def rpc_getAvatarDetails(self, avId):
        """
        Summary:
            Responds with basic details on the avatar associated with the
            provided [avId].

        Parameters:
            [int avId] = The ID of the avatar to query basic details on.

        Example response:
            On success:
                {
                   'name': 'Toon Name',
                   'species': 'cat',
                   'head-color': '#4d4c59',
                   'max-hp': 15,
                   'online': True,
                   'location': [401000000, 2000]
                }
            On failure: None
        """
        dclassName, fields = self.rpc_queryObject(avId)
        if dclassName != 'DistributedToon':
            return

        result = {}

        result['name'] = fields['setName'][0]
        dna = ToonDNA.ToonDNA()
        dna.makeFromNetString(fields['setDNAString'][0])
        result['species'] = ToonDNA.getSpeciesName(dna.head)
        r, g, b, _ = dna.colorDNA.headColor.getRgb()
        result['head-color'] = '#%02x%02x%02x' % (r * 255, g * 255, b * 255)
        result['max-hp'] = fields['setMaxHp'][0]

        unblocked = threading2.Event()

        def handleGetActivatedResp(doId, activated):
            result['online'] = bool(activated)
            unblocked.set()

        self.air.getActivated(avId, handleGetActivatedResp)

        # Block until the callback is executed:
        unblocked.wait()

        def handleQueryObjectLocationResp(parentId, zoneId):
            result['location'] = [parentId, zoneId]
            unblocked.set()

        if result['online']:
            unblocked.clear()

            self.air.queryObjectLocation(avId, handleQueryObjectLocationResp)

            # Block until the callback is executed:
            unblocked.wait()
        else:
            result['location'] = [-1, -1]

        return result

    @rpcmethod(accessLevel=MODERATOR)
    def rpc_findAvatarsByName(self, needle, detailed=False, skip=0, limit=0,
                              sort=None):
        """
        Summary:
            Responds with the IDs of each avatar whose name matches, or
            contains the provided [needle], along with the total number of
            avatars found.

        Parameters:
            [str needle] = The string to filter avatars by name with. This is
                case insensitive.
            <bool detailed> = When True, the response will not only include the
                IDs of each avatar, but also all of their details returned by
                getAvatarDetails().
            <int skip> = The number of IDs to omit (from the start of the
                result set) when returning the results.
            <int limit> = The maximum number of IDs to return.
            <list sort> = A list of (key, direction) pairs specifying the sort
                order for this query.

        Example response:
            detailed=False: [5, [100000001, ...]]
            detailed=True: [5, [{'id': 100000001, ...}, ...]]
        """
        if not needle:
            return [0, []]

        exp = re.compile('.*%s.*' % needle, re.IGNORECASE)
        cursor = self.air.mongodb.astron.objects.find(
            filter={'fields.setName._0': exp}, projection={}, skip=skip,
            limit=limit, sort=sort)

        if detailed:
            result = []

            for document in cursor:
                _id = document['_id']
                result.append({'id': _id})
                result[-1].update(self.rpc_getAvatarDetails(_id))

            return [cursor.count(), result]
        else:
            return [cursor.count(), [document['_id'] for document in cursor]]

    # --- GUILDS ---

    @rpcmethod(accessLevel=MODERATOR)
    def rpc_approveGuild(self, guildId):
        """
        Summary: Approve the Guild associated with the provided [guildId].

        Parameters:
            [int guildId] = The ID of the Guild that is to be approved.

        Example response:
            On success: True
            On failure: False
        """
        dclassName, fields = self.rpc_queryObject(guildId)
        if dclassName != 'Guild':
            return False

        self.air.dbInterface.updateObject(
            self.air.dbId,
            guildId,
            self.air.dclassesByName['Guild'],
            {GUILD_FIELD_NAME_STATUS: GUILD_NAME_ACCEPTED,
             GUILD_FIELD_NAME: fields[GUILD_FIELD_PENDING_NAME]})

        guildManager = self.air.getGlobalObject('GuildManager')
        guildManager.nameResponse(guildId, 1)

        return True

    @rpcmethod(accessLevel=MODERATOR)
    def rpc_denyGuild(self, guildId):
        """
        Summary: Deny the Guild associated with the provided [guildId].

        Parameters:
            [int guildId] = The ID of the Guild that is to be approved.

        Example response:
            On success: True
            On failure: False
        """
        dclassName, fields = self.rpc_queryObject(guildId)
        if dclassName != 'Guild':
            return False

        self.air.dbInterface.updateObject(
            self.air.dbId,
            guildId,
            self.air.dclassesByName['Guild'],
            {GUILD_FIELD_NAME_STATUS: GUILD_NAME_REJECTED})

        guildManager = self.air.getGlobalObject('GuildManager')
        guildManager.nameResponse(guildId, 0)

        return True

    # --- SHARDS ---

    @rpcmethod(accessLevel=USER)
    def rpc_listShards(self):
        """
        Summary:
            Responds with the current status of each shard that has ever been
            created in the lifetime of the UberDOG.

        Example response:
            {
               401000000: {
                  'name': 'District Name'
                  'available': True,
                  'created': 1409665000,
                  'population': 150,
                  'invasion': {
                     'type': 'Flunky',
                     'flags': 0,
                     'remaining': 1000,
                     'total': 1000,
                     'start': 1409665000
                  }
               },
               ...
            }
        """
        return self.shardStatus.getShards()

    # --- NAME REVIEW ---

    @rpcmethod(accessLevel=MODERATOR)
    def rpc_approveName(self, avId):
        """
        Summary:
            Approve the name of the avatar that is associated with the provided
            [avId].

        Parameters:
            [int avId] = The ID of the avatar whose name is to be approved.

        Example response:
            On success: True
            On failure: False
        """
        dclassName, fields = self.rpc_queryObject(avId)
        if dclassName != 'DistributedToon':
            return False

        self.air.dbInterface.updateObject(
            self.air.dbId,
            avId,
            self.air.dclassesByName['DistributedToonUD'],
            {'WishNameState': ('APPROVED',),
             'setName': (fields['WishName'][0],)})
        self.rpc_setField(avId, 'DistributedToonUD', 'setName',
                          [fields['WishName'][0]])

        self.rpc_messageAvatar(
            avId, 'Congratulations! Your name has been approved by the Toon'
                  ' Council!')

        return True

    @rpcmethod(accessLevel=MODERATOR)
    def rpc_denyName(self, avId):
        """
        Summary:
            Deny the name of the avatar that is associated with the provided
            [avId].

        Parameters:
            [int avId] = The ID of the avatar whose name is to be denied.

        Example response:
            On success: True
            On failure: False
        """
        dclassName, fields = self.rpc_queryObject(avId)
        if dclassName != 'DistributedToon':
            return False

        self.air.dbInterface.updateObject(
            self.air.dbId,
            avId,
            self.air.dclassesByName['DistributedToonUD'],
            {'WishNameState': ('REJECTED',)})

        self.rpc_messageAvatar(
            avId, 'Our apologies! The Toon Council has rejected your name. If'
                  ' you would like to choose a new one, you may do so at the'
                  ' Pick-A-Toon screen.')

        return True

    @rpcmethod(accessLevel=MODERATOR)
    def rpc_revokeName(self, avId):
        """
        Summary:
            Revoke the name of the avatar that is associated with the provided
            [avId].

        Parameters:
            [int avId] = The ID of the avatar whose name is to be revoked.

        Example response:
            On success: True
            On failure: False
        """
        dclassName, fields = self.rpc_queryObject(avId)
        if dclassName != 'DistributedToon':
            return False

        dna = ToonDNA.ToonDNA()
        dna.makeFromNetString(fields['setDNAString'][0])
        colorId = ToonDNA.getColorIdFromColorDna(dna.colorDNA.headColor)
        colorString = TTLocalizer.getColorString(colorId)
        animalType = TTLocalizer.AnimalToSpecies[dna.getAnimal()]
        name = colorString + ' ' + animalType
        self.air.dbInterface.updateObject(
            self.air.dbId,
            avId,
            self.air.dclassesByName['DistributedToonUD'],
            {'WishNameState': ('REJECTED',),
             'setName': (name,)})
        self.rpc_setField(avId, 'DistributedToonUD', 'setName', [name])

        self.rpc_messageAvatar(
            avId, 'Our apologies! The Toon Council has revoked your name. If'
                  ' you would like to choose a new one, you may do so at the'
                  ' Pick-A-Toon screen.')

        return True

    @rpcmethod(accessLevel=SYSTEM_ADMINISTRATOR)
    def rpc_blacklistName(self, name):
        """
        Summary:
            Blacklist the provided [name].

        Parameters:
            [str name] = The name to blacklist.

        Example response: 1
        """
        cursor = self.air.mongodb.astron.objects.find(
            {'dclass': 'DistributedToon', 'fields.setName._0': name})
        revokeCount = cursor.count()
        for document in cursor:
            self.rpc_revokeName(document['_id'])

        return revokeCount

    # --- CHAT LOGS ---

    @rpcmethod(accessLevel=MODERATOR)
    def rpc_queryChatLogs(self, filter, skip=0, limit=0, sort=None):
        """
        Summary:
            Responds with the chat logs which match the provided [filter],
            along with the total number of chat logs found.

        Parameters:
            [dict filter] = A dictionary of fields to filter the chat logs by.
                This functions in the same way that MongoDB filters do. Any
                string filters will be case insensitive.
            <int skip> = The number of chat logs to omit (from the start of the
                result set) when returning the results.
            <int limit> = The maximum number of chat logs to return.
            <list sort> = A list of (key, direction) pairs specifying the sort
                order for this query.

        Example response:
            [
                5,
                {
                    'recipient': 0,
                    'sender': 100000001,
                    'timestamp': 1409665000,
                    'location': [401000001, 2000],
                    'message': 'example',
                    'type': 0
                },
                ...
            ]
        """
        if 'message' in filter:
            filter['message'] = re.compile(
                '.*%s.*' % filter['message'], re.IGNORECASE)

        cursor = self.air.mongodb.chat.messages.find(
            filter=filter, projection={'_id': False}, skip=skip, limit=limit,
            sort=sort)
        return [cursor.count(), [document for document in cursor]]
