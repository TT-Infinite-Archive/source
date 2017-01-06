from pandac.PandaModules import *

from toontown.guilds.GuildRoleUD import GuildRoleUD
from toontown.guilds.GuildMemberUD import GuildMemberUD
from toontown.guilds.GuildQuestUD import GuildQuestUD
from toontown.guilds.GuildGlobals import *
from toontown.guilds import GuildQuestGlobals

from direct.distributed.ClockDelta import *


class GuildUD:
    notify = directNotify.newCategory('GuildUD')
    
    def __init__(self, mgr, **kwargs):
        self.mgr = mgr

        self.id = kwargs.get('id', 0)

        self.nameStatus = kwargs.get('nameStatus', GUILD_NAME_NONE)
        self.name = kwargs.get('name', 'Guild ' + str(self.id))
        self.pendingName = kwargs.get('pendingName', 'Guild ' + str(self.id))

        self.members = []
        self.avId2Member = {}
        self.avId2MemberIndex = {}
        
        self.iconId = kwargs.get('iconId', 0)
        self.guildPoints = kwargs.get('guildPoints', 0)
        self.rankPoints = kwargs.get('rankPoints', 0)
        
        self.quest = kwargs.get('quest', GuildQuestGlobals.GUILD_QUEST_EMPTY)
        self.buffs = kwargs.get('buffs', [])
        
        self.roles = kwargs.get('roles', GUILD_ROLE_DEFAULTS)
        self.roleId2Role = {}
        for role in self.roles:
            self.addExistingRole(role)

        self.bossTimings = kwargs.get('bossTimings', [])
        questContributions = kwargs.get('questContributions', [])
        self.questContributions = {}
        for contributor in questContributions:
            self.questContributions[contributor[0]] = contributor[1]

        self.questNum = kwargs.get('questNum', 0)
        self.unlockedItems = kwargs.get('unlockedItems', [])

        self.rank = 0
        self.questInst = None

        self.startQuest()
        
    # Property setter
    def makeFromFields(self, guildId, fields):
        self.id = guildId

        self.nameStatus = fields[GUILD_FIELD_NAME_STATUS]
        self.name = fields[GUILD_FIELD_NAME]
        self.pendingName = fields[GUILD_FIELD_PENDING_NAME]

        self.members = fields[GUILD_FIELD_MEMBERS]
        self.avId2Member = {}
        for member in self.members:
            self.addExistingMember(member)

        self.iconId = fields[GUILD_FIELD_ICON_ID]
        self.guildPoints = fields[GUILD_FIELD_GUILD_POINTS]
        self.rankPoints = fields[GUILD_FIELD_RANK_POINTS]

        self.quest = fields[GUILD_FIELD_QUEST]

        self.buffs = fields[GUILD_FIELD_BUFFS]
        for buff in self.buffs:
            self.startBuff(buff)

        self.roles = fields[GUILD_FIELD_ROLES]
        self.roleId2Role = {}
        for role in self.roles:
            self.addExistingRole(role)

        self.bossTimings = fields[GUILD_FIELD_BOSS_TIMINGS]

        questContributions = fields.get(GUILD_FIELD_QUEST_CONTRIBUTIONS, [])
        self.questContributions = {}
        for contributor in questContributions:
            self.questContributions[contributor[0]] = contributor[1]

        self.questNum = fields.get(GUILD_FIELD_QUEST_NUM, 0)
        self.unlockedItems = fields.get(GUILD_FIELD_UNLOCKED_ITEMS, [])

        self.startQuest()

        # Save the guild
        self.saveGuild()

    # Destruction
    def destroy(self):
        self.mgr.handleDestroy(self.id)

    # Name Functions
    def approveName(self):
        # Alert all members that the guilds name has changed
        self.sendUpdate('alertNameChanged', [self.pendingName, GUILD_NAME_ACCEPTED])
        
        # Set the name on our side
        self.name = self.pendingName
        self.pendingName = ''
        self.nameStatus = GUILD_NAME_ACCEPTED

        # Make all the members have the new guild name
        for avId in self.avId2Member:
            if self.avId2Member[avId] is None:
                continue
            self.avId2Member[avId].saveFieldToDB('setGuildName', self.name)
        
        # Save the guild
        self.saveGuild()

    def rejectName(self):
        # Set the name on our side
        self.name = 'Guild ' + str(self.id)
        self.pendingName = ''
        self.nameStatus = GUILD_NAME_REJECTED

        # Alert all members that the guilds name has changed
        self.sendUpdate('alertNameChanged', [self.name, GUILD_NAME_REJECTED])

        # Make all the members have the new guild name
        for avId in self.avId2Member:
            if self.avId2Member[avId] is None:
                continue
            self.avId2Member[avId].saveFieldToDB('setGuildName', self.name)

        # Save the guild
        self.saveGuild()

    def startQuest(self):
        if not config.GetBool('want-guild-quests', True):
            # We don't want quests right now, shut it all down
            quest = GuildQuestGlobals.GUILD_QUEST_EMPTY
            self.questContributions = {}
        elif self.quest == GuildQuestGlobals.GUILD_QUEST_EMPTY:
            # We don't have a quest, start the one we need
            quest = GuildQuestGlobals.getQuestFromNum(self.questNum)
            self.questContributions = {}
        else:
            # We have a quest, lets make sure this quest actually exists (safety-net)
            if self.quest[GuildQuestGlobals.GUILD_QUEST_ID] not in GuildQuestGlobals.GuildQuestDict.keys():
                # Something went wrong with this quest, get a new one
                quest = GuildQuestGlobals.getQuestFromNum(self.questNum)
                self.questContributions = {}
            elif self.quest[GuildQuestGlobals.GUILD_QUEST_PROGRESS] >= self.quest[GuildQuestGlobals.GUILD_QUEST_GOAL]:
                # We have a quest, but it's done. Get a new one.
                quest = GuildQuestGlobals.getQuestFromNum(self.questNum)
                self.questContributions = {}
            else:
                # This guild quest is fine, use it
                quest = self.quest

        # Make our quest instance from the data we determined above
        self.questInst = GuildQuestUD(self)
        self.questInst.makeFromField(quest)
        self.quest = self.questInst.asStruct()

    def progressQuest(self, avIds, category, possibleObjectives):
        # Get how much a guild member would get for doing this
        cpReward = GuildQuestGlobals.GuildQuestDict[self.questInst.questId][2] / len(avIds)
        
        # Attempt to progress quest with task
        prevProgress = self.questInst.progress
        self.questInst.attemptProgress(category, possibleObjectives)
        self.quest = self.questInst.asStruct()

        if self.questInst.progress > prevProgress:
            # This quest progressed, lets add contribution for the members
            for avId in avIds:
                if avId in self.questContributions:
                    self.questContributions[avId] += cpReward
                else:
                    self.questContributions[avId] = cpReward

        if self.questInst.progress >= self.questInst.goal:
            taskMgr.remove(self.getUniqueName('guildQuestUpdateLater'))
            self.sendUpdate('alertQuestProgress', [self.questInst.progress])
            self.finishQuest()
        else:
            taskMgr.remove(self.getUniqueName('guildQuestUpdateLater'))
            taskMgr.doMethodLater(2, self.sendQuestUpdateLater, self.getUniqueName('guildQuestUpdateLater'))

        # Save the guild
        self.saveGuild()

    def getUniqueName(self, msg):
        return '%s-%s' % (self.id, msg)

    def sendQuestUpdateLater(self, task=None):
        if len(self.members) != 0:
            self.sendUpdate('alertQuestProgress', [self.questInst.progress])
        if task is not None:
            return task.done

    def finishQuest(self):
        # Give them their points!
        reward = self.questInst.reward
        self.addPoints(reward)

        # Add contributions
        total = 0

        highestContribution = 0
        highestContributor = 0
        for memberId in self.questContributions:
            contributionPoints = self.questContributions[memberId]
            if contributionPoints > highestContribution:
                highestContribution = contributionPoints
                highestContributor = memberId
            contributionPoints = math.floor(contributionPoints)
            total += contributionPoints

            self.addContributionPointsToMember(memberId, contributionPoints)

        if highestContributor != 0:
            remainder = reward - total
            self.addContributionPointsToMember(highestContributor, remainder)

        self.questContributions = {}
        
        # Tell everyone the quest is completed
        self.sendUpdate('alertQuestFinished')

        # Update our quest struct
        self.questInst.progress = self.questInst.goal
        self.quest = self.questInst.asStruct()

        # Increment the amount of quests we've done today
        self.questNum += 1

        # Start a new quest immediately
        self.startQuest()

        # Alert all members that we have a new quest
        self.sendUpdate('alertQuestStarted', [self.quest])

        # Save the guild
        self.saveGuild()

    # Buffs Functions
    def startBuff(self, buff):
        pass

    def finishBuff(self, buffIndex):
        pass

    # Points
    def addPoints(self, points):
        # Update the list for the db
        self.guildPoints += points
        self.rankPoints += points
        self.saveGuild()
        
        self.sendUpdate('setGuildPoints', [self.guildPoints])
        self.sendUpdate('setRankPoints', [self.rankPoints])

        # Points changed, ud has to re-rank
        self.mgr.calculateRanksThreaded()
        
    def addContributionPointsToMember(self, memberId, points):
        # Get the member
        member = self.getMember(memberId)
        if member is None:
            return

        # Add the members contribution points
        memberIndex = self.getMemberIndex(member)
        if memberIndex is None:
            self.notify.warning('Member %s not in members: %s' % (member.asEntry(), self.members))
            return

        # Add the points
        member.addContribution(points)

        # Update the list for the db
        self.members[memberIndex] = member.asEntry()
        self.saveGuild()

        # Update everyone in the Guild with this guy's points
        self.sendUpdate('memberContributionChanged', [memberId, member.contribution])

    # Rank
    def setRank(self, rank):
        self.rank = rank

    def updateRank(self, rank):
        self.setRank(rank)
        self.sendUpdate('setRank', [self.rank])

    # Member Functions
    def addExistingMember(self, fields):
        def memberReady():
            # Check the members online status
            # (I don't know how this could happen but just in-case?)
            def handleGetActivatedResp(doId, activated):
                if activated:
                    member.goOnline(self.mgr.GetPuppetConnectionChannel(doId))

                # Add him to our maps
                self.avId2Member[member.id] = member
                self.avId2MemberIndex[member.id] = self.members.index(fields)

                # Check if this guild is ready
                for avId, _member in self.avId2Member.items():
                    if _member is None:
                        return

                # This guild is ready!
                self.mgr.guildReady(self)

            simbase.air.getActivated(member.id, handleGetActivatedResp)

        # Make a new member object
        member = GuildMemberUD(self)
        member.makeFromEntryFields(fields, memberReady)

        # Safety net to be sure that all our members are in our guild
        member.saveFieldToDB('setGuildId', self.id)
        member.saveFieldToDB('setGuildName', self.name)
        member.saveFieldToDB('setGuildIcon', self.iconId)
        
        # Temporary add for the retrieve on our manager
        if member.id not in self.avId2Member:
            self.avId2Member[member.id] = None

    def addNewMember(self, fields, adderName):
        def memberReady():
            # Add him to the guild
            self.members.append(member.asEntry())
            self.avId2Member[member.id] = member
            self.avId2MemberIndex[member.id] = self.members.index(member.asEntry())

            # Check the new members online status
            def handleGetActivatedResp(doId, activated):
                if activated:
                    member.goOnline(self.mgr.GetPuppetConnectionChannel(doId))

                # Set the member's data
                member.saveFieldToDB('setGuildId', self.id)
                member.saveFieldToDB('setGuildName', self.name)
                member.saveFieldToDB('setGuildIcon', self.iconId)

                # Alert all members that this member has joined
                self.sendUpdate('memberAdded', [member.asStruct(), adderName])

                # Save the guild
                self.saveGuild()

            simbase.air.getActivated(member.id, handleGetActivatedResp)

        # Make a new member object
        member = GuildMemberUD(self)
        member.makeFromEntryFields(fields, memberReady)

    def removeMember(self, avId, senderId):
        # Get the members we're removing
        target = self.getMember(avId)
        sender = self.getMember(senderId)
        
        if target is None:
            self.notify.warning('Avatar %d is trying to remove non-existent member %d' % (senderId, avId))
            return
            
        if sender is None:
            self.notify.warning('Non member avatar %d is trying to remove member %d' % (senderId, avId))
            return
        
        # Get their roles
        senderRole = sender.getRole()
        targetRole = target.getRole()

        # Check if the owner is trying to leave
        if target is sender:
            if targetRole.sortIndex == 0:
                # If the owner is the last person
                if len(self.avId2Member) == 1:
                    self.destroy()
                else:
                    self.mgr.sendUpdateToAvatarId(senderId, 'guildError', [GUILD_CANT_LEAVE_ERROR])
                    return
                
        # Is this someone trying to kick someone else?
        if target is not sender:
            # Do they have permission to kick?
            if GUILD_PERMISSION_KICK_MEMBERS not in senderRole.permissions:
                # Tell the sender that they do not have permission to do this
                self.mgr.sendUpdateToAvatarId(senderId, 'guildError', [GUILD_BAD_PERMISSIONS_ERROR])
                
                # Log this as a warning
                self.notify.warning('Avatar %d trying to kick a member without permissions' % senderId)
                return

            # Do they overpower the target member?
            if not senderRole.overpowers(targetRole):
                # Tell the sender that they do not have permission to do this
                self.mgr.sendUpdateToAvatarId(senderId, 'guildError', [GUILD_BAD_PERMISSIONS_ERROR])
                
                # Log this as a warning
                self.notify.warning('Avatar %d trying to kick a member of equal or greater permissions %d' % (senderId, avId))
                return

        # Debugging logs
        self.notify.debug('Avatar %d is kicking guild member %d' % (senderId, avId))

        # Alert all members that this member has left
        removerName = sender.name
        self.sendUpdate('memberRemoved', [avId, senderId, removerName])

        # Clear the channel, etc
        target.leaveGuild()

        # Remove him from our side
        targetIndex = self.getMemberIndex(target)
        if targetIndex is None:
            self.notify.warning('Trying to delete member %s not in guild with members: %s' % (target.asEntry(), repr(self.members)))
            return
        self.members.remove(self.members[targetIndex])

        # They should be, but just in-case...
        if avId in self.avId2Member:
            del self.avId2Member[avId]
        if avId in self.avId2MemberIndex:
            del self.avId2MemberIndex[avId]
        if avId in self.mgr.avId2GuildId:
            del self.mgr.avId2GuildId[avId]

        # Calculate the guilds rank
        self.mgr.calculateRanksThreaded()

        # Save the guild to the database
        self.saveGuild()

    def adminLeave(self, avId):
        # Get the admin we're removing
        target = self.getMember(avId)

        if target is None:
            self.notify.warning('Avatar %d is trying to leave but he isnt in the guild' % avId)
            return

        # Remove him from our side
        targetIndex = self.getMemberIndex(target)
        if targetIndex is None:
            self.notify.warning('Trying to delete member %s not in guild with members: %s' % (target.asEntry(), repr(self.members)))
            return
        self.members.remove(self.members[targetIndex])
        self.sendUpdate('memberRemoved', [avId, avId, ''])

        # Clear the channel, etc
        target.leaveGuild()

        # They should be, but just in-case...
        if avId in self.avId2Member:
            del self.avId2Member[avId]
        if avId in self.avId2MemberIndex:
            del self.avId2MemberIndex[avId]
        if avId in self.mgr.avId2GuildId:
            del self.mgr.avId2GuildId[avId]

        # Calculate the guilds rank
        self.mgr.calculateRanksThreaded()

        # Save the guild to the database
        self.saveGuild()

    def memberOnline(self, avId, clientChannel):
        # Check if this avatar is even in the guild
        if avId not in self.avId2Member:
            self.notify.warning('CSM called memberOnline for avId that was not found in avId2Member. (%d)' % avId)
            return

        # Alert all members that this member has come online
        self.sendUpdate('memberOnline', [avId])

        # Set online status
        self.avId2Member[avId].goOnline(clientChannel)

    def memberOffline(self, avId):
        # Check if this avatar is even in the guild
        if avId not in self.avId2Member:
            self.notify.warning('CSM called memberOffline for avId that was not found in avId2Member. (%d)' % avId)
            return

        # Set online status
        self.avId2Member[avId].goOffline()

        # Alert all members that this member has gone offline
        self.sendUpdate('memberOffline', [avId])

    def generateMembers(self):
        # We use GenerateMembers so that updated online status can be sent over..
        members = []

        for avId in self.avId2Member:
            if self.avId2Member[avId] is None:
                continue
            members.append(self.avId2Member[avId].asStruct())

        return members
        
    def getMember(self, avId):
        return self.avId2Member.get(avId)

    def getMemberCount(self):
        return len(self.avId2Member.keys())

    def getMemberIndex(self, member):
        if member.asEntry() not in self.members:
            # Something went wrong, try to find him
            targetIndex = -1
            targetId = member.asEntry()[0]
            for index, memberEntry in enumerate(self.members):
                if memberEntry[0] == targetId:
                    targetIndex = index
                    break
            if targetIndex != -1:
                # Found them
                self.notify.debug('Found member %s at %d' % (member.asEntry(), targetIndex))
                return targetIndex
        else:
            self.notify.debug('Found member %s at %d' % (member.asEntry(), self.members.index(member.asEntry())))
            return self.members.index(member.asEntry())
        self.notify.debug('Did not find member %s in %s' % (member.asEntry(), repr(self.members)))
        return None
        
    # Role Functions
    def addExistingRole(self, role):
        # Make the role instance
        roleInstance = GuildRoleUD(self.mgr, self)
        roleInstance.makeFromRoleFields(role)
        
        # Add the role to our map
        self.roleId2Role[roleInstance.id] = roleInstance
        
    def addNewRole(self, role):
        # Make the role instance
        roleInstance = GuildRoleUD(self.mgr, self)
        roleInstance.makeFromRoleFields(role)
        
        roleInstance.id = len(self.roles)
        roleInstance.sortIndex = len(self.roles)
        
        # Add the role to our map
        self.roleId2Role[roleInstance.id] = roleInstance
        self.roles.append(roleInstance.asStruct())
        
        # Alert all the members that a new role exists
        self.sendUpdate('roleCreated', roleInstance.asStruct())
        
        # Save the guild
        self.saveGuild()
        
        # Return the new role
        return roleInstance
        
    def updateRole(self, roleId, roleName, roleSortIndex, rolePermissions):
        # Get the role
        roleInstance = self.getRole(roleId)
        if roleInstance is None:
            return
        
        # Get the index of the role for saving
        roleIndex = self.roles.index(roleInstance.asStruct())
        
        # Update the role
        roleInstance.name = roleName
        roleInstance.sortIndex = roleSortIndex
        roleInstance.permissions = rolePermissions
        
        # Update the list for the db
        self.roles[roleIndex] = roleInstance.asStruct()
        
        # Alert all the members that this role has been updated
        self.sendUpdate('roleUpdated', [roleId, roleName, roleSortIndex, rolePermissions])
        
        # Save the guild
        self.saveGuild()
        
        # Return the edited role
        return roleInstance
        
    def changeMemberRole(self, avId, senderId, roleId):
        # Get the members we're changing
        sender = self.getMember(senderId)
        target = self.getMember(avId)
        
        if target is None:
            self.notify.warning('Avatar %d is trying to change non-existent member %d' % (senderId, avId))
            return
            
        if sender is None:
            self.notify.warning('Non member avatar %d is trying to change member %d' % (senderId, avId))
            return
        
        # Get their roles
        senderRole = sender.getRole()
        targetRole = target.getRole()

        # Do they have permission to modify member roles?
        if GUILD_PERMISSION_MODIFY_MEMBER_ROLE not in senderRole.permissions:
            # Tell the sender that they do not have permission to do this
            self.mgr.sendUpdateToAvatarId(senderId, 'guildError', [GUILD_BAD_PERMISSIONS_ERROR])
            
            # Log this as a warning
            self.notify.warning('Avatar %d trying to change a member without permissions' % senderId)
            return

        if not senderRole.overpowers(targetRole):
            # Tell the sender that they do not have permission to do this
            self.mgr.sendUpdateToAvatarId(senderId, 'guildError', [GUILD_BAD_PERMISSIONS_ERROR])
            
            # Log this as a warning
            self.notify.warning('Avatar %d trying to change a member %d of equal or greater permissions.' % (senderId, avId))
            return

        self.notify.debug('Avatar %d is changing member %d role to %d' % (senderId, avId, roleId))
        
        # Get the role
        role = self.roleId2Role.get(roleId, None)
        if role is None:
            return
        
        # Set the member's role to the new one
        targetIndex = self.getMemberIndex(target)
        if targetIndex is None:
            self.notify.warning('Member: %s not in members: %s' % (target.asEntry(), repr(self.members)))
            return
        target.setRole(role)
        
        # Update the list for the db
        self.members[targetIndex] = target.asEntry()
        
        # Alert everyone of the change
        self.sendUpdate('memberRoleChanged', [avId, roleId])
        
        # Save the guild
        self.saveGuild()

    def transferOwnership(self, senderId, targetId):
        # Get the member objects
        sender = self.getMember(senderId)
        target = self.getMember(targetId)

        if sender is None:
            self.notify.warning('Avatar %d is trying to transfer ownership for a guild they aren\'t in' % senderId)
            return
        if target is None:
            self.notify.warning('Avatar %d tried to transfer ownership to an avatar not in the guild %d' % (senderId, targetId))
            return

        # Get the sender role for validation
        senderRole = sender.getRole()

        if senderRole.getIndex() != 0:
            self.notify.warning('Non owner %d trying to transfer ownership of a guild %d' % (senderId, self.id))
            return

        # Get the indexes
        targetIndex = self.getMemberIndex(target)
        senderIndex = self.getMemberIndex(sender)
        if targetIndex is None:
            self.notify.warning('Trying to transfer ownership to : %s who isnt in guild of %s' % (target.asEntry(), repr(self.members)))
            return
        if senderIndex is None:
            self.notify.warning('Trying to transfer ownership to : %s who isnt in guild of %s' % (sender.asEntry(), repr(self.members)))
            return

        # Set the target's role to owner
        target.setRole(self.getRoleAtSortIndex(0))
        # Set the sender (previous owner) to one below owner
        sender.setRole(self.getRoleAtSortIndex(1))

        # Update the member lists
        self.members[targetIndex] = target.asEntry()
        self.members[senderIndex] = sender.asEntry()

        # Alert everyone of the change
        self.sendUpdate('ownershipTransferred', [targetId])

        # Save the guild
        self.saveGuild()
        
    def getRole(self, roleId):
        # Return the role, or None if it doesn't exist
        return self.roleId2Role.get(roleId, None)
    
    def getRoleAtSortIndex(self, sortIndex):
        for roleId in self.roleId2Role:
            if self.roleId2Role[roleId].sortIndex == sortIndex:
                return self.roleId2Role[roleId]
        return None
        
    def getHighestRole(self):
        return self.roleId2Role[0]
        
    def getLowestRole(self):
        return self.roleId2Role.get(len(self.roles) - 1, None)

    def changeMemberLaff(self, avId, laff):
        member = self.getMember(avId)
        if member is None:
            return
        # Set the member's laff to the new one
        member.setLaff(laff)

        self.sendUpdate('memberLaffChanged', [avId, laff])
        
    # Whisper Functions
    def handleTalkWhisper(self, sender, message):
        # Check if this avatar is even in the guild
        if sender not in self.avId2Member:
            return

        # Alert all members of this whisper.
        self.sendUpdate('receiveTalkWhisperFromGuild', [sender, message])

    # Send updates
    def sendUpdate(self, field, args=None):
        if args is None:
            args = []
        if len(self.members) == 0:
            # No reason to sendUpdate if we have no members
            return
        self.mgr.sendUpdateToChannel(self.id, field, args)

    # Arguments for field update
    def asInfo(self):
        struct = (
            self.name,
            self.generateMembers(),
            self.iconId,
            self.guildPoints,
            self.rankPoints,
            self.buffs,
            self.quest,
            self.roles,
            self.bossTimings
        )

        return struct

    # Saving
    def saveGuild(self):
        questContributions = []
        for contributor in self.questContributions:
            questContributions.append([contributor, self.questContributions[contributor]])
            
        simbase.air.dbInterface.updateObject(
            simbase.air.dbId,
            self.id,
            simbase.air.dclassesByName['Guild'],
            {
                GUILD_FIELD_NAME_STATUS: self.nameStatus,
                GUILD_FIELD_NAME: self.name,
                GUILD_FIELD_PENDING_NAME: self.pendingName,
                GUILD_FIELD_ICON_ID: self.iconId,
                GUILD_FIELD_MEMBERS: self.members,
                GUILD_FIELD_QUEST: self.quest,
                GUILD_FIELD_GUILD_POINTS: self.guildPoints,
                GUILD_FIELD_RANK_POINTS: self.rankPoints,
                GUILD_FIELD_BUFFS: self.buffs,
                GUILD_FIELD_ROLES: self.roles,
                GUILD_FIELD_QUEST_CONTRIBUTIONS: questContributions,
                GUILD_FIELD_QUEST_NUM: self.questNum,
                GUILD_FIELD_UNLOCKED_ITEMS: self.unlockedItems,
            }
        )
