from panda3d.core import ConfigVariableString, Datagram
import semidbm
from direct.distributed.DistributedObjectGlobalUD import DistributedObjectGlobalUD
from direct.distributed.PyDatagram import *
from toontown.friends.TTIFriendsManagerUD import OperationFSM
from toontown.guilds.GuildGlobals import *
from toontown.guilds.GuildUD import *
from toontown.util import ThreadedCall

guildDBPath = ConfigVariableString(
    'guild-db-path', 'astron/databases/guilds',
    'The path to the database that will store Guild IDs.')


class GuildDB:
    def __init__(self):
        self.dbm = semidbm.open(guildDBPath.getValue(), 'c')

    def update(self, guildId, ownerId):
        self.dbm[str(guildId)] = str(ownerId)
        self.dbm.sync()

    def getGuildIds(self):
        return [int(guildId) for guildId in list(self.dbm.keys())]

    def getOwnerIds(self):
        return [int(ownerId) for ownerId in list(self.dbm.values())]

    def getOwnerIdFromGuildId(self, guildId):
        return int(self.dbm[str(guildId)])

    def getGuildIdFromOwnerId(self, ownerId):
        for key, value in list(self.dbm.values()):
            if int(value) == ownerId:
                return int(key)

        return -1


# -- FSMS --
# -- Create Guild --
class CreateGuildOperation(OperationFSM):
    def enterStart(self, name, iconId):
        self.nameStatus = GUILD_NAME_NONE
        self.name = name
        self.iconId = iconId
        self.pendingName = name

        # If a webApi instance exists, then we can assume that we are working
        # in a production environment. Let's set their name status to pending:
        if self.air.webApi is not None:
            self.nameStatus = GUILD_NAME_PENDING
            self.name = 'Unnamed Guild'

        # Create this Guild in the database:
        self.air.dbInterface.createObject(
            self.air.dbId,
            self.air.dclassesByName['Guild'],
            {
                GUILD_FIELD_NAME_STATUS: self.nameStatus,
                GUILD_FIELD_NAME: self.name,
                GUILD_FIELD_PENDING_NAME: self.pendingName,
                GUILD_FIELD_ICON_ID: self.iconId,
                GUILD_FIELD_MEMBERS: [[self.sender, GUILD_ROLE_ID_OWNER, 0]],
                GUILD_FIELD_QUEST: GuildQuestGlobals.GUILD_QUEST_EMPTY,
                GUILD_FIELD_ROLES: GUILD_ROLE_DEFAULTS,
                GUILD_FIELD_BOSS_TIMINGS: [],
                GUILD_FIELD_QUEST_CONTRIBUTIONS: [],
                GUILD_FIELD_QUEST_NUM: 0,
                GUILD_FIELD_UNLOCKED_ITEMS: []
            },
            self.handleCreate
        )

    def handleCreate(self, guildId):
        self.result = guildId

        # Give this Guild a temporary name if its name status is pending:
        if self.nameStatus == GUILD_NAME_PENDING:
            self.name = 'Guild ' + str(guildId)

        guild = GuildUD(
            mgr=self.mgr, id=guildId, nameStatus=self.nameStatus, name=self.name,
            pendingName=self.pendingName, iconId=self.iconId, roles=GUILD_ROLE_DEFAULTS,
            quest=GuildQuestGlobals.GUILD_QUEST_EMPTY)

        # We need to set this before we add the member, because our safety net will remove him if it didnt exist
        self.mgr.guilds[guildId] = guild
        self.mgr.avId2GuildId[self.sender] = guildId

        guild.addNewMember([self.sender, GUILD_ROLE_ID_OWNER, 0], self.name)

        self.mgr.guildDB.update(guildId, self.sender)

        takenNames = self.mgr.getTakenNames(guildId)

        def handleNameAvailable(response):
            # This name is reserved or not reserved, handle it
            if response['reserved']:
                self.mgr.nameResponse(guildId, False)
            else:
                # Submit our name if its not reserved
                if self.air.webApi is not None:
                    payload = {'distribution': ConfigVariableString('distribution').getValue(), 'name': guild.pendingName}
                    self.air.webApi.execute('guilds/%d' % guildId, payload, 'post')
            self.demand('Off')

        def handleNameError():
            # Something went wrong, deny the name for safety
            self.mgr.nameResponse(guildId, False)
            # Go off, we're done!
            self.demand('Off')

        # Check if the name is available via the rpc
        if self.air.webApi is not None:
            payload = {'name': guild.pendingName, 'distribution': ConfigVariableString('distribution').getValue()}
            self.air.webApi.execute('reserved-guilds', payload, 'get', callback=handleNameAvailable,
                                    errback=handleNameError)
        else:
            # No wbRpc exists, just check server names
            self.mgr.nameResponse(guildId, guild.pendingName not in takenNames)
            # Go off, we're done!
            self.demand('Off')


# Manager
class GuildManagerUD(DistributedObjectGlobalUD):
    notify = directNotify.newCategory('GuildManagerUD')

    def announceGenerate(self):
        DistributedObjectGlobalUD.announceGenerate(self)
        self.notify.setInfo(True)

        self.operations = []
        self.guilds = {}
        self.avId2GuildId = {}
        self.invites = {}
        self.guildDB = GuildDB()
        self.topTen = []
        self.leaderboardListeners = []
        taskMgr.add(self.retrieveGuilds, 'guildManagerUD-retrieveTask')

    def retrieveGuilds(self, task=None):
        self.notify.info('Retrieving Guilds...')
        guildIds = self.guildDB.getGuildIds()

        def finishRetrieved():
            self.notify.info('Done Retrieving Guilds! There is/are %d Guild(s) on this server...' % len(self.guilds))
            # Calculate ranks after retrieving all guilds
            self.calculateRanksThreaded()

        if not guildIds:
            finishRetrieved()
            return

        for guildId in guildIds:
            callback = None
            if guildId == guildIds[-1]:
                callback = finishRetrieved

            self.retrieveGuild(guildId, callback)

    def retrieveGuild(self, guildId, callback=None):
        def handleRetrieved(dclass, fields):
            # Check if the DO we retrieved was a Guild
            if dclass != self.air.dclassesByName['Guild']:
                self.notify.warning('dclass is not a Guild Instance')
                if callback is not None:
                    callback()
                return

            guild = GuildUD(self)
            guild.makeFromFields(guildId, fields)
            self.guilds[guildId] = guild

            for avId in guild.avId2Member:
                self.avId2GuildId[avId] = guildId

            if callback is not None:
                callback()

        # Request the Guild object from the db
        self.air.dbInterface.queryObject(self.air.dbId, guildId, handleRetrieved)

    def handleDestroy(self, guildId):
        self.notify.debug('Handling the destruction of guild %d' % guildId)
        # Re-sync the rankings TODO: Uncomment this when implemented the features below
        # self.calculateRanks()
        # TODO: Delete this guild from the db then remove it from self.guilds

    # Handling Toon online status
    def toonOnline(self, avId, guildId):
        self.notify.debug('Handling Avatar %d coming online in guild %d' % (avId, guildId))
        if guildId not in self.guilds and guildId != 0:
            self.notify.warning('GuildId %d isn\'t in self.guilds removing...' % guildId)
            guildId = 0
        if guildId == 0:
            # TODO: Remove this
            dg = self.air.dclassesByName['DistributedToonUD'].aiFormatUpdate(
                'setGuildId', avId, avId, self.air.ourChannel, [0]
            )
            self.air.send(dg)
            dg = self.air.dclassesByName['DistributedToonUD'].aiFormatUpdate(
                'setGuildName', avId, avId, self.air.ourChannel, ['']
            )
            self.air.send(dg)
            dg = self.air.dclassesByName['DistributedToonUD'].aiFormatUpdate(
                'setGuildIcon', avId, avId, self.air.ourChannel, [0]
            )
            self.air.send(dg)
            if avId in self.avId2GuildId:
                self.notify.warning('Guild Manager UD is crazy, we\'re hack fixing him %d' % avId)
                del self.avId2GuildId[avId]
            return

        clientChannel = self.GetPuppetConnectionChannel(avId)

        # Post removes just in-case the client uncleanly disconnects
        dgcleanup = self.dclass.aiFormatUpdate('toonOffline', self.doId, self.doId, self.air.ourChannel, [avId])
        dg = PyDatagram()
        dg.addServerHeader(clientChannel, self.air.ourChannel, CLIENTAGENT_ADD_POST_REMOVE)
        dg.addString(dgcleanup.getMessage())
        self.air.send(dg)

        # Tell the guild that this member is online
        self.avId2GuildId[avId] = guildId
        self.guilds[guildId].memberOnline(avId, clientChannel)

    def toonOffline(self, avId):
        self.notify.debug('Handling Avatar %d going offline' % avId)
        guildId = self.avId2GuildId.get(avId)
        if guildId is None:
            self.notify.debug('Avatar %d that went offline is not a part of a guild. Doing nothing.' % avId)
            return
        if guildId not in self.guilds:
            self.notify.warning('Avatar %d has guildId %d but no guild of that id exists.' % (avId, guildId))
            return

        # Tell the guild that this member is off-line
        self.guilds[guildId].memberOffline(avId)

        # Check if he's still listening for leaderboards
        if avId in self.leaderboardListeners:
            self.leaderboardListeners.remove(avId)

    def nameResponse(self, guildId, response):
        self.notify.debug('Received name response %s for guildId %d' % (response, guildId))
        guild = self.guilds[guildId]
        if guild is None:
            self.notify.warning('Tried to respond to non existent guild %d' % guildId)
            return

        if response:
            if guild.nameStatus == GUILD_NAME_ACCEPTED:
                self.notify.warning('Attempted to respond to an already approved guild %d' % guildId)
                return
            guild.approveName()
        else:
            guild.rejectName()

    # Whispers
    def sendTalkWhisperToGuild(self, message):
        avId = self.air.getAvatarIdFromSender()
        guildId = self.avId2GuildId.get(avId, None)

        if guildId is None:
            return

        guild = self.guilds.get(guildId, None)
        if guild is None:
            self.sendUpdateToAvatarId(avId, 'guildError', [GUILD_FATAL_ERROR])
            return

        guild.handleTalkWhisper(avId, message)

    # Client Requests
    def requestCreateGuild(self, avId, name, iconId):
        if avId in self.avId2GuildId:
            # Does the guild even exist? (Safety-net)
            if self.avId2GuildId[avId] in self.guilds:
                # Tell the avatar that they are already in a guild
                self.sendUpdateToAvatarId(avId, 'guildError', [GUILD_ALREADY_IN_GUILD_ERROR])

                # Log this as a warning
                self.notify.warning('Avatar %d requested a new guild yet they are already part of one: %d' % (
                    avId, self.avId2GuildId[avId]))
                return

        def handleCreated(avId, guildId):
            self.notify.info('Avatar %d successfully created guild %d!' % (avId, guildId))

        # Log that an avatar is creating a guild
        self.notify.info('Avatar %d requested a guild!' % avId)

        # Create an async db operation
        operation = CreateGuildOperation(self, self.air, avId, callback=handleCreated)
        operation.demand('Start', name, iconId)

        # Append the operation so that the garbage collector doesn't destroy it
        self.operations.append(operation)

    def requestRenameGuild(self, guildName):
        avId = self.air.getAvatarIdFromSender()

        if avId not in self.avId2GuildId:
            self.notify.warning('Avatar %d tried to rename a guild but they are not in one' % avId)
            return

        guildId = self.avId2GuildId[avId]
        guild = self.guilds.get(guildId)
        if guild is None:
            # Tell the sender to contact support..
            self.sendUpdateToAvatarId(avId, 'guildError', [GUILD_FATAL_ERROR])

            # Log this as a warning
            self.notify.warning('Avatar %d has guildId %d but that guild doesnt exist' % (avId, guildId))
            return

        if guild.nameStatus != GUILD_NAME_REJECTED:
            # Currently, we don't support renaming unless your guild name was rejected
            self.notify.warning(
                'Avatar %d tried to rename guild of guildId %d but that was not rejected.' % (avId, guildId))
            return

        guild.pendingName = guildName
        guild.nameStatus = GUILD_NAME_PENDING

        takenNames = self.getTakenNames(guildId)

        def handleNameAvailable(reserved):
            # This name is reserved or not reserved, handle it
            self.notify.debug('WebApi replied with %s' % reserved)
            if reserved['reserved'] or guildName in takenNames:
                self.nameResponse(guildId, False)

            if self.air.webApi is not None:
                payload = {'distribution': ConfigVariableString('distribution').getValue(), 'name': guild.pendingName}
                self.air.webApi.execute('guilds/%d' % guildId, payload, 'post')

        def handleNameError():
            # Something went wrong, deny the name for safety
            self.notify.debug('Something went wrong with webApi returning False')
            self.nameResponse(guildId, False)

        # Check if the name is available via the rpc
        if self.air.webApi is not None:
            self.notify.debug('Asking webApi if guild name is taken')
            payload = {'name': guild.pendingName, 'distribution': ConfigVariableString('distribution').getValue()}
            self.air.webApi.execute('reserved-guilds', payload, 'get', callback=handleNameAvailable,
                                    errback=handleNameError)
        else:
            # No wbRpc exists, just check server names
            self.notify.debug('No webApi exists. Checking if guild name is taken')
            self.nameResponse(guildId, guildName not in takenNames)

    def requestRemoveMember(self, avId):
        senderId = self.air.getAvatarIdFromSender()

        # Get the guild
        guildId = self.avId2GuildId.get(senderId)
        if guildId is None:
            # Tell the sender that they're not in a guild..
            self.sendUpdateToAvatarId(senderId, 'guildError', [GUILD_NO_GUILD_ERROR])

            # Log this as a warning
            self.notify.warning('Avatar %d tried to remove member but they\'re not in a guild!' % senderId)
            return

        guild = self.guilds.get(guildId)
        if guild is None:
            # Tell the sender to contact support..
            self.sendUpdateToAvatarId(senderId, 'guildError', [GUILD_FATAL_ERROR])

            # Log this as a warning
            self.notify.warning('Avatar %d has guildId %d but that guild doesnt exist' % (senderId, guildId))
            return

        removee = guild.getMember(avId)
        if removee is None:
            # The target isn't in our guild...
            self.sendUpdateToAvatarId(senderId, 'guildError', [GUILD_CANT_PROCESS_ERROR])

            # Log this as a warning
            self.notify.warning('Avatar %d tried to remove %d but they are not in the same guild.' % (senderId, avId))
            return

        # Tell the guild to remove the member
        guild.removeMember(avId, senderId)

    def requestChangeMemberRole(self, avId, roleId):
        senderId = self.air.getAvatarIdFromSender()

        # Get the guild
        guildId = self.avId2GuildId.get(senderId)
        if guildId is None:
            # Tell the sender that they're not in a guild..
            self.sendUpdateToAvatarId(senderId, 'guildError', [GUILD_NO_GUILD_ERROR])

            # Log this as a warning
            self.notify.warning('Avatar %d tried to change member but they\'re not in a guild!' % senderId)
            return

        guild = self.guilds.get(guildId)
        if guild is None:
            # Tell the sender to contact support..
            self.sendUpdateToAvatarId(senderId, 'guildError', [GUILD_FATAL_ERROR])

            # Log this as a warning
            self.notify.warning('Avatar %d has guildId %d but that guild doesnt exist' % (senderId, guildId))
            return

        # Tell the guild to change the member's role
        guild.changeMemberRole(avId, senderId, roleId)

    def requestTransferOwnership(self, targetId):
        senderId = self.air.getAvatarIdFromSender()

        # Get the guild
        guildId = self.avId2GuildId.get(senderId)
        if guildId is None:
            # Tell the sender that they're not in a guild
            self.sendUpdateToAvatarId(senderId, 'guildError', [GUILD_NO_GUILD_ERROR])

            # Log this as a warning
            self.notify.warning('Avatar %d tried to transfer ownership but they\'re not in a guild!' % senderId)
            return

        guild = self.guilds.get(guildId)
        if guild is None:
            # Tell the sender something went wrong
            self.sendUpdateToAvatarId(senderId, 'guildError', [GUILD_FATAL_ERROR])

            # Log this as a warning
            self.notify.warning('Avatar %d has guildId %d but that guild doesnt exist' % (senderId, guildId))
            return

        # Tell the guild to transfer ownership
        guild.transferOwnership(senderId, targetId)

    # Points

    def handleGuildPoints(self, guildId, points):
        self.notify.debug('Handling %d points for Guild %d' % (points, guildId))
        guild = self.guilds.get(guildId)
        if guild is None:
            self.notify.warning('Received \'handleGuildPoints\' for Guild that does not exist! (%d)' % (guildId))
            return

        guild.addPoints(points)
        self.calculateRanksThreaded()

    def handleContributionPoints(self, avId, points):
        self.notify.debug('Handling %d points for Avatar %d' % (points, avId))
        guildId = self.avId2GuildId.get(avId)
        if guildId is None:
            self.notify.warning('Attempted to handle points for a member not in guild %d' % avId)
            return
        guild = self.guilds.get(guildId)
        if guild is None:
            self.notify.warning('Avatar %d has guildId %d but no guild exists for that id' % (avId, guildId))
            return

        guild.addContributionPointsToMember(avId, points)

    def calculateRanksThreaded(self):
        threadedFunc = ThreadedCall.ThreadedCall(self.calculateRanks)
        threadedFunc.start()

    def calculateRanks(self):
        self.notify.debug('Calculating Ranks for Guilds...')
        descendingGuilds = sorted(self.guilds, key=lambda guildId: self.guilds[guildId].rankPoints, reverse=True)
        deadGuildCount = 0
        self.topTen = []
        for index, guildId in enumerate(descendingGuilds):
            guild = self.guilds.get(guildId)
            if guild is None or guild.name == 'Infinite Staff' or len(guild.members) == 0 or guild.rankPoints == 0:
                # This guild does not count, do not rank it
                deadGuildCount += 1
                continue

            rank = index + 1 - deadGuildCount
            self.notify.debug('Setting %s with %d points as #%d' % (guild.name, guild.rankPoints, rank))
            guild.updateRank(rank)
            if rank <= 10:
                self.topTen.append((guild.id, guild.name, guild.rankPoints))

        self.notify.debug('Ranks Calculated! %s' % repr(descendingGuilds))
        self.sendLeaderboardInfo()

    # Name Checking
    def requestCheckName(self, guildName):
        avId = self.air.getAvatarIdFromSender()
        self.notify.debug('Avatar %d requesting to check name %s' % (avId, guildName))
        takenNames = self.getTakenNames()

        def handleNameAvailable(reserved):
            # This name is reserved or not reserved, handle it
            self.notify.debug('WebApi replied with %s' % reserved)
            valid = (not reserved['reserved']) and (guildName not in takenNames)
            self.checkNameResponse(avId, valid)

        def handleNameError():
            # Something went wrong, deny the name for safety
            self.notify.debug('Something went wrong with webApi returning False')
            self.checkNameResponse(avId, False)

        # Check if the name is available via the rpc
        if self.air.webApi is not None:
            self.notify.debug('Asking webApi if guild name is taken')
            payload = {'name': guildName, 'distribution': ConfigVariableString('distribution').getValue()}
            self.air.webApi.execute('reserved-guilds', payload, 'get', callback=handleNameAvailable,
                                    errback=handleNameError)
        else:
            # No wbRpc exists, just check server names
            self.notify.debug('No webApi exists. Checking if guild name is taken')
            self.checkNameResponse(avId, guildName not in takenNames)

    def getTakenNames(self, guildId=0):
        takenNames = []
        for guild in self.guilds:
            # Check all the existing guilds' names
            if self.guilds[guild].id == guildId:
                continue
            takenNames.append(self.guilds[guild].name)
            takenNames.append(self.guilds[guild].pendingName)
        self.notify.debug('Got all taken names %s' % takenNames)
        return takenNames

    def checkNameResponse(self, avId, valid):
        self.sendUpdateToAvatarId(avId, 'checkNameResponse', [valid])

    # Leaderboards
    def enterLeaderboard(self):
        # A player is looking at his leaderboard page, we need to accommodate him
        senderId = self.air.getAvatarIdFromSender()
        if senderId not in self.leaderboardListeners:
            self.leaderboardListeners.append(senderId)
        self.sendLeaderboardInfoToId(senderId)

    def exitLeaderboard(self):
        # A player is no longer looking at his leaderboard page, so we don't care about him
        senderId = self.air.getAvatarIdFromSender()
        if senderId in self.leaderboardListeners:
            self.leaderboardListeners.remove(senderId)

    def sendLeaderboardInfo(self):
        # Our information has updated, lets send new info to all listeners
        for listener in self.leaderboardListeners:
            self.sendLeaderboardInfoToId(listener)

    def sendLeaderboardInfoToId(self, avId):
        self.sendUpdateToAvatarId(avId, 'leaderboardInfo', [self.topTen])

    # Quests
    def attemptProgressQuest(self, guildId, avIds, category, possibleObjectives):
        guild = self.guilds.get(guildId)
        if guild is None:
            self.notify.warning('Could not retrieve matching guild for id %d' % guildId)
            return

        for avId in avIds:
            if guild.getMember(avId) is None:
                self.notify.warning('Avatar %d not in guild but tried to get in this quest' % avId)
                avIds.remove(avId)

        if len(avIds) == 0:
            self.notify.warning('No Avatars to proceed with Guild Quest %d' % guildId)
            return

        self.notify.debug(
            'Checking if quest can be progressed for guild %d. Using: %d %s' % (guildId, category, possibleObjectives))
        guild.progressQuest(avIds, category, possibleObjectives)

    def completeQuest(self, avId, guildId):
        self.notify.warning('COMMAND: Avatar %d calling complete quest' % avId)
        guild = self.guilds.get(guildId)
        if guild is None:
            self.notify.warning('Could not retrieve matching guild for id %d' % guildId)
            return

        guild.finishQuest()

    def progressQuest(self, avId, guildId, amount):
        self.notify.warning('COMMAND: Avatar %d calling progress quest' % avId)
        guild = self.guilds.get(guildId)
        if guild is None:
            self.notify.warning('Could not retrieve matching guild for id %d' % guildId)
            return

        for i in range(0, amount):
            quest = GuildQuestGlobals.GuildQuestDict[guild.questInst.questId]
            category = quest[0]
            objective = quest[1]
            guild.progressQuest([avId], category, objective)

    # Invites

    def invite(self, senderId, targetId):
        self.notify.debug('Received request to invite %d from %d' % (targetId, senderId))
        self.notify.debug('Current invites %s' % (repr(self.invites)))

        if targetId == 0:
            # This is a request to cancel an invite
            for otherTargetId, otherSenderId in self.invites.items():
                # Check if we have an invite pending
                if senderId == otherSenderId:
                    # Tell the target we no longer want them
                    self.sendUpdateToAvatarId(otherTargetId, 'invited', ['', ''])
                    # Destroy this invite
                    del self.invites[otherTargetId]
                    self.notify.debug('Successfully cancelled invite for %d from %d' % (otherTargetId, senderId))
                    self.notify.debug('Current invites %s' % (repr(self.invites)))
                    return

        # Get the guild
        guildId = self.avId2GuildId.get(senderId)
        if guildId is None:
            # Tell the sender that they're not in a guild..
            self.sendUpdateToAvatarId(senderId, 'invitationResponse', [GUILD_INVITE_RESPONSE_CANT_PROCESS])

            # Log this as a warning
            self.notify.warning('Avatar %d tried to invite member but they\'re not in a guild!' % senderId)
            return

        guild = self.guilds.get(guildId)
        if guild is None:
            # Tell the sender to contact support..
            self.sendUpdateToAvatarId(senderId, 'invitationResponse', [GUILD_INVITE_RESPONSE_CANT_PROCESS])
            self.sendUpdateToAvatarId(senderId, 'guildError', [GUILD_FATAL_ERROR])

            # Log this as a warning
            self.notify.warning('Avatar %d has guildId %d but that guild doesnt exist' % (senderId, guildId))
            return

        if self.avId2GuildId.get(targetId) is not None:
            # Tell the sender that this player is in a guild already
            self.notify.debug('Avatar %d already in guild, cannot accept invite.' % (targetId))
            self.sendUpdateToAvatarId(senderId, 'invitationResponse', [GUILD_INVITE_RESPONSE_ALREADY_IN_GUILD])
            return

        if guild.getMemberCount() >= GUILD_MAX_MEMBER_COUNT:
            self.notify.debug('Guild %d is too full.' % guildId)
            self.sendUpdateToAvatarId(senderId, 'invitationResponse', [GUILD_INVITE_RESPONSE_FULL])
            return

        # Check if the target is already handling an invite
        if targetId in self.invites:
            # Tell the sender that this player is busy with another invite
            self.notify.warning('Avatar %d who is in self.invites was invited. For now we will remove him.' % targetId)
            del self.invites[targetId]

        # Get the sender
        sender = guild.getMember(senderId)

        # Does this member have permission to invite members?
        if GUILD_PERMISSION_INVITE_MEMBERS in sender.getRole().permissions:
            # Add the invite
            self.invites[targetId] = senderId

            # Tell our target they were invited
            self.notify.debug('Invite sent to %d invites: %s' % (targetId, repr(self.invites)))
            self.sendUpdateToAvatarId(targetId, 'invited', [sender.name, guild.name])
        else:
            self.notify.warning('Avatar %d without invite permissions attempted to invite %d' % (senderId, targetId))

    def respondToInvite(self, response):
        senderId = self.air.getAvatarIdFromSender()
        inviterId = self.invites.get(senderId)

        # Check if this invite exists
        if inviterId is None:
            # Tell the invitee something went wrong with their invite
            self.sendUpdateToAvatarId(senderId, 'guildError', [GUILD_CANT_PROCESS_ERROR])
            self.notify.warning('Tried to respond to non-existent invite %d' % senderId)
            return

        if response != GUILD_INVITE_RESPONSE_ACCEPTED:
            # We don't want your invite
            # Tell the inviter that we don't want them / couldn't reply to them
            self.sendUpdateToAvatarId(inviterId, 'invitationResponse', [response])
            self.notify.debug('Rip Invite, someone told us they do not want a guild.')
            del self.invites[senderId]
            return

        # At this point, we wanted to join, but we don't know if that is possible yet

        # Get the sender's guildId
        guildId = self.avId2GuildId.get(senderId)
        if guildId is not None:
            # Tell the inviter that they're already in a guild
            self.sendUpdateToAvatarId(inviterId, 'invitationResponse', [GUILD_INVITE_RESPONSE_ALREADY_IN_GUILD])
            # Kill this invite
            self.notify.debug('Rip Invite, we are already in a guild.')
            del self.invites[senderId]
            return

        # Get the inviter's guild
        inviterGuildId = self.avId2GuildId.get(inviterId)
        inviterGuild = self.guilds.get(inviterGuildId)
        if inviterGuild is None:
            self.notify.warning('Invite has guildId but no matching guild exists %d' % inviterGuildId)
            # Something is wrong with this guild, destroy this invite
            del self.invites[senderId]
            # Tell the inviter that something went wrong
            self.sendUpdateToAvatarId(inviterId, 'invitationResponse', [GUILD_INVITE_RESPONSE_CANT_PROCESS])
            self.sendUpdateToAvatarId(inviterId, 'guildError', [GUILD_FATAL_ERROR])
            return

        if len(inviterGuild.members) == 0:
            # Tell the invitee something went wrong with their invite
            # We cant have people joining an empty guild, because it should be abandoned
            self.sendUpdateToAvatarId(senderId, 'guildError', [GUILD_CANT_PROCESS_ERROR])
            # Tell the inviter something went wrong with their invite
            self.sendUpdateToAvatarId(inviterId, 'invitationResponse', [GUILD_INVITE_RESPONSE_CANT_PROCESS])
            # Remove this invite
            self.notify.debug('Rip Invite, there are no members in that guild.')
            del self.invites[senderId]
            return

        if len(inviterGuild.members) >= GUILD_MAX_MEMBER_COUNT:
            # There are too many members in this guild to accept this invite...
            # Tell the invitee they cant accept this
            self.sendUpdateToAvatarId(senderId, 'guildError', [GUILD_CANT_PROCESS_ERROR])
            # Tell the inviter something went wrong with their invite
            self.sendUpdateToAvatarId(inviterId, 'invitationResponse', [GUILD_INVITE_RESPONSE_CANT_PROCESS])
            # Remove this invite
            self.notify.debug('Rip Invite, there are too many members in that guild')
            del self.invites[senderId]
            return

        # Tell the inviter he WANTS and COULD join
        self.sendUpdateToAvatarId(inviterId, 'invitationResponse', [GUILD_INVITE_RESPONSE_ACCEPTED])

        # Get the inviter
        inviter = inviterGuild.getMember(inviterId)
        if inviter is None:
            self.notify.warning('Found no inviter %d in guildMembers but found guild from inviter' % inviterId)
            self.sendUpdateToAvatarId(senderId, 'guildError', [GUILD_CANT_PROCESS_ERROR])
            del self.invites[senderId]
            return
        # He checked out, add him to the guild.
        self.avId2GuildId[senderId] = inviterGuildId
        inviterGuild.addNewMember(
            [senderId, inviterGuild.getLowestRole().id, 0], inviter.name)

        # Remove this invite
        del self.invites[senderId]
        self.notify.debug('Invite responded to, removing %d. Invites: %s' % (senderId, repr(self.invites)))

    def guildReady(self, guild):
        # Do any future safety nets for broken guilds here
        if guild.name == '' and guild.pendingName == '' and len(guild.members) != 0:
            # This guild is broken, lets reset them
            guild.rejectName()

    def toonLaffChanged(self, avId, laff):
        guildId = self.avId2GuildId.get(avId)
        guild = self.guilds.get(guildId)
        if guild is None:
            self.notify.warning('Cannot change laff for av %d not in guild' % avId)
            return

        guild.changeMemberLaff(avId, laff)

    def adminJoinGuild(self, avId, guildId):
        beforeGuildId = self.avId2GuildId.get(avId)
        beforeGuild = self.guilds.get(beforeGuildId)
        if beforeGuild is not None:
            self.sendUpdateToAvatarId(avId, 'guildError', [GUILD_CANT_PROCESS_ERROR])
            return

        guild = self.guilds.get(guildId)
        if guild is None:
            self.sendUpdateToAvatarId(avId, 'guildError', [GUILD_CANT_PROCESS_ERROR])
            return

        self.avId2GuildId[avId] = guildId
        guild.addNewMember([avId, guild.getHighestRole().id, 0], '')

    def adminLeaveGuild(self, avId):
        guildId = self.avId2GuildId.get(avId)
        guild = self.guilds.get(guildId)
        if guild is None:
            self.notify.warning('Av %d tried to force leave non existent guild %s' % (avId, guildId))
            self.sendUpdateToAvatarId(avId, 'guildError', [GUILD_CANT_PROCESS_ERROR])
            return

        guild.adminLeave(avId)
