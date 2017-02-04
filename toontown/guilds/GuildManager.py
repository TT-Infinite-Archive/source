# Guild Manager (Client side)

from direct.distributed.DistributedObjectGlobal import DistributedObjectGlobal
from direct.directnotify.DirectNotifyGlobal import directNotify
from toontown.guilds.Guild import Guild
from toontown.guilds import GuildInvitee, GuildGlobals
from toontown.chat import ChatGlobals
from toontown.toonbase import TTLocalizer, EventGlobals
from toontown.toontowngui.WarningDialog import WarningDialog
from otp.ai.MagicWordGlobal import *


class GuildManager(DistributedObjectGlobal):
    notify = directNotify.newCategory('GuildManager')

    def announceGenerate(self):
        DistributedObjectGlobal.announceGenerate(self)
        self.guild = None

    def delete(self):
        DistributedObjectGlobal.delete(self)

    def disable(self):
        DistributedObjectGlobal.disable(self)

    # Server Responses
    def guildInfo(self, guildInfo):
        self.notify.debug('Received guild info %s' % repr(guildInfo))
        self.guild = Guild()
        self.guild.makeFromInfo(guildInfo)
        
        # Alert anything that might be interested..
        messenger.send(EventGlobals.GuildInfoChanged)

    # - Name Approval

    def alertNameChanged(self, name, nameState, task=None):
        self.notify.debug('Received name changed to %s name state is %s' % (name, nameState))
        localMember = self.guild.getLocalAvatar()
        if localMember is None:
            taskMgr.doMethodLater(10, self.alertNameChanged, 'nameChangedTask', extraArgs=[name, nameState])
        else:
            if nameState == GuildGlobals.GUILD_NAME_ACCEPTED:
                self.guild.name = name
                base.localAvatar.displayWhisper(0, TTLocalizer.GuildNameApproved, ChatGlobals.WTGuild)
            elif nameState == GuildGlobals.GUILD_NAME_REJECTED:
                self.guild.name = name
                self.guild.rejected = True
            if localMember.getRoleId() == 0:
                base.localAvatar.displayWhisper(0, TTLocalizer.GuildNameRejectedOwner, ChatGlobals.WTGuild)
            else:
                base.localAvatar.displayWhisper(0, TTLocalizer.GuildNameRejected, ChatGlobals.WTGuild)

    # - Name Checking
    def checkNameResponse(self, valid):
        messenger.send(EventGlobals.GuildCheckNameResp, [valid])

    # - Leaderboards

    def leaderboardInfo(self, entries):
        self.leaderboardRankEntries = entries
        messenger.send(EventGlobals.GotLeaderboardInfo)

    def enterLeaderboard(self):
        # We entered the leaderboard page, so we want some information
        self.sendUpdate('enterLeaderboard', [])

    def exitLeaderboard(self):
        # We exited the leaderboard page, we don't want anymore information
        self.sendUpdate('exitLeaderboard', [])

    # - Invites
        
    def invited(self, senderName, guildName):
        if senderName == '' and guildName == '':
            # This is an invite that cancels a previous invite
            self.notify.debug('Received a cancelling invite')
            messenger.send(EventGlobals.CancelGuildInvitation)
        else:
            self.notify.debug('Received invite to join guild: %s, from: %s' % (guildName, senderName))
            GuildInvitee.showGuildInvitee(senderName, guildName)

    def invitationResponse(self, response):
        self.notify.debug('Received response for invitation %d' % response)
        messenger.send(EventGlobals.GuildInviteResponse, [response])

    # Management
    def ownershipTransferred(self, avId):
        self.notify.debug('Transferring ownership to %d' % avId)
        # Get the participating members
        member = self.guild.getMember(avId)
        owner = self.guild.getOwner()
        if member is None:
            self.notify.warning('Received ownershipTransferred for non-existing member %d' % avId)
            return

        # Set the new roles
        if owner is None:
            self.notify.warning('Fatal problem: No Owner exists! Proceeding anyways...')
        else:
            owner.setRole(self.guild.getRoleAtPosition(1))
        member.setRole(self.guild.getRoleAtPosition(0))

        name = member.getName()

        # Show the toon that this event happened
        base.localAvatar.displayWhisper(0, TTLocalizer.GuildMemberNewOwner % name, ChatGlobals.WTGuild)

        # Make sure everything knows stuff changed
        messenger.send(EventGlobals.GuildMemberChanged, [member.doId])
        messenger.send(EventGlobals.GuildMemberChanged, [owner.doId])

    def memberOnline(self, avId):
        self.notify.debug('Received memberOnline %d' % avId)
        member = self.guild.getMember(avId)
        if member is None:
            self.notify.warning('Received memberOnline for non existing member %d' % avId)
            return

        name = member.getName()
        
        if not base.cr.isFriend(avId):
            base.localAvatar.displayWhisper(0, TTLocalizer.GuildMemberOnline % name, ChatGlobals.WTGuild)
        self.guild.memberOnline(avId)

        messenger.send(EventGlobals.GuildsListChanged)

    def memberOffline(self, avId):
        self.notify.debug('Received memberOffline %d' % avId)
        member = self.guild.getMember(avId)
        if member is None:
            self.notify.warning('Received memberOffline for non-existing member %d' % avId)
            return
        
        name = member.getName()
        
        if not base.cr.isFriend(avId):
            base.localAvatar.displayWhisper(0, TTLocalizer.GuildMemberOffline % name, ChatGlobals.WTGuild)
        self.guild.memberOffline(avId)

        messenger.send(EventGlobals.GuildsListChanged)
    
    def memberAdded(self, member, adderName):
        self.notify.debug('Received memberAdded %s %s' % (repr(member), adderName))
        # Add the member to the guild object
        self.guild.handleMember(member)
        
        # Alert the player that this member has been added
        name = member[GuildGlobals.GUILD_MEMBER_NAME]
        if adderName != '':
            base.localAvatar.displayWhisper(0, TTLocalizer.GuildMemberAddedBy % (name, adderName), ChatGlobals.WTGuild)
        else:
            base.localAvatar.displayWhisper(0, TTLocalizer.GuildMemberJoined % name, ChatGlobals.WTGuild)

        messenger.send(EventGlobals.GuildsListChanged)
    
    def memberRemoved(self, avId, removerId, removerName):
        self.notify.debug('Received memberRemoved %d %s' % (avId, removerName))
        if avId == base.localAvatar.doId:
            # We're being removed...
            base.localAvatar.setGuildId(0)
            self.guild = None

            if removerId == avId:
                # We removed ourselves, so we were leaving
                base.localAvatar.displayWhisper(0, TTLocalizer.GuildMemberYouLeft, ChatGlobals.WTGuild)
            else:
                # We were kicked...
                base.localAvatar.displayWhisper(0, TTLocalizer.GuildMemberKicked, ChatGlobals.WTGuild)
            # Guild info has changed because you were removed
            messenger.send(EventGlobals.GuildInfoChanged)
        else:
            member = self.guild.getMember(avId)
            if member is None:
                self.notify.warning('Received memberRemoved for non-existing member %d' % avId)
                return

            name = member.getName()
            if member.doId == removerId:
                # This member removed himself
                base.localAvatar.displayWhisper(0, TTLocalizer.GuildMemberLeft % name, ChatGlobals.WTGuild)
            else:
                # This member was kicked...
                base.localAvatar.displayWhisper(0, TTLocalizer.GuildMemberRemovedBy % (name, removerName), ChatGlobals.WTGuild)

            # Remove the member from the guild object
            self.guild.removeMember(avId)
        messenger.send(EventGlobals.GuildsListChanged)

    def memberRoleChanged(self, avId, roleId):
        self.notify.debug('Got memberRoleChanged %d %d' % (avId, roleId))
        # Get the member
        member = self.guild.getMember(avId)
        if member is None:
            self.notify.warning('Received memberRoleChanged for non-existing member %d' % avId)
            return
        name = member.getName()
        
        # Get the new role
        oldRole = member.getRole()
        newRole = self.guild.getRole(roleId)

        # Set the member's role
        member.setRole(newRole)
        
        # Work out whether they have been demoted or promoted
        string = TTLocalizer.GuildDemoted
        if newRole.overpowers(oldRole):
            string = TTLocalizer.GuildPromoted
        
        # Show the whisper
        newRoleString = newRole.name

        if avId == base.localAvatar.doId:
            # We've been promoted/demoted
            base.localAvatar.displayWhisper(0, TTLocalizer.GuildMemberOurRoleChanged % (string, newRoleString), ChatGlobals.WTGuild)
        else:
            base.localAvatar.displayWhisper(0, TTLocalizer.GuildMemberRoleChanged % (name, string, newRoleString), ChatGlobals.WTGuild)

        # Send a message that a member changed
        messenger.send(EventGlobals.GuildMemberChanged, [member.doId])

    def memberContributionChanged(self, avId, contribution):
        self.notify.debug('Changing member %d contribution to %d' % (avId, contribution))
        member = self.guild.getMember(avId)
        if member is None:
            self.notify.warning('Received memberContributionChanged for non-existing member %d' % avId)
            return

        oldContribution = member.getContribution()
        difference = contribution - oldContribution

        member.setContribution(contribution)

        if member.doId == base.localAvatar.getDoId():
            base.localAvatar.displayRewardText(
                TTLocalizer.ContributionPointsGot % difference)

        # Send a message that a member changed
        messenger.send(EventGlobals.GuildMemberChanged, [member.doId])

    # Laff
    def memberLaffChanged(self, avId, laff):
        self.notify.debug('Changing member %d laff to %d' % (avId, laff))
        member = self.guild.getMember(avId)
        if member is None:
            self.notify.warning('Received memberLaffChanged for non-existing member %d' % avId)
            return

        member.setLaff(laff)

        # Send a message that a member changed
        messenger.send(EventGlobals.GuildMemberChanged, [member.doId])

    # Quests

    def alertQuestStarted(self, quest):
        self.notify.debug('Starting quest %s' % repr(quest))
        self.guild.setQuest(quest)
        messenger.send(EventGlobals.GuildQuestInfoChanged)
        
        base.localAvatar.displayWhisper(0, TTLocalizer.GuildQuestStarted, ChatGlobals.WTGuild)

    def alertQuestProgress(self, progress):
        self.notify.debug('Setting progress of quest %s to %d' % (self.guild.quest, progress))
        self.guild.setQuestProgress(progress)
        messenger.send(EventGlobals.GuildQuestInfoChanged)

    def alertQuestFinished(self):
        base.localAvatar.displayWhisper(0, TTLocalizer.GuildQuestFinished, ChatGlobals.WTGuild)
        
    # Points / Ranking

    def setGuildPoints(self, points):
        self.guild.setGuildPoints(points)
        messenger.send(EventGlobals.GuildInfoChanged)

    def setRankPoints(self, points):
        pointsEarned = points - self.guild.getRankPoints()
        base.localAvatar.displayRewardText(
            TTLocalizer.RankPointsGot % pointsEarned)

        self.guild.setRankPoints(points)
        messenger.send(EventGlobals.GuildInfoChanged)

    def setRank(self, rank):
        self.guild.setRank(rank)
        messenger.send(EventGlobals.GuildInfoChanged)

    # Chat

    def receiveTalkWhisperFromGuild(self, senderId, message):
        member = self.guild.getMember(senderId)
        if member is None:
            self.notify.warning('Received whisper from non-existing member %d' % senderId)
            return
        
        name = member.getName()
        base.localAvatar.displayWhisper(0, '[GUILD] %s: %s' % (name, message), ChatGlobals.WTGuild)
        
    def guildError(self, errorId):
        errorText = GuildGlobals.GUILD_ERRORS_TO_STRING[errorId]
        WarningDialog(aspect2d, errorText, TTLocalizer.lOK)
        
        # Anything that wants to know
        messenger.send(EventGlobals.GuildError, [errorId])

    # Client Requests
    def d_invite(self, targetId):
        self.notify.debug('Inviting %d' % targetId)
        self.sendUpdate('requestInvite', [targetId])

    def d_respondToInvite(self, response):
        self.notify.debug('Responding to invite with response %d' % response)
        self.sendUpdate('respondToInvite', [response])

    def d_requestCreateGuild(self, guildName, iconId):
        self.notify.debug('Requesting creating guild %s %d' % (guildName, iconId))
        self.sendUpdate('requestCreateGuildAI', [guildName, iconId])

    def d_requestRenameGuild(self, guildName):
        self.sendUpdate('requestRenameGuild', [guildName])

    def d_requestRemoveMember(self, targetId):
        self.sendUpdate('requestRemoveMember', [targetId])

    def d_requestChangeMemberRole(self, targetId, roleId):
        self.sendUpdate('requestChangeMemberRole', [targetId, roleId])

    def d_requestTransferOwnership(self, targetId):
        self.sendUpdate('requestTransferOwnership', [targetId])

    def d_requestLeaveGuild(self):
        self.sendUpdate('requestRemoveMember', [base.localAvatar.doId])
        
    def d_sendTalkWhisperToGuild(self, message):
        self.sendUpdate('sendTalkWhisperToGuild', [message])
    
    def d_requestCreateRole(self, roleName, rolePermissions):
        self.sendUpdate('requestCreateRole', [roleName, rolePermissions])
        
    def d_requestUpdateRole(self, roleId, roleName, sortIndex, rolePermissions):
        self.sendUpdate('requestUpdateRole', [roleId, roleName, sortIndex, rolePermissions])
        
    def d_requestDeleteRole(self, roleId):
        self.sendUpdate('requestDeleteRole', [roleId])

    def d_requestCheckName(self, guildName):
        self.sendUpdate('requestCheckName', [guildName])


@magicWord(category=CATEGORY_ADMINISTRATOR, types=[str, str])
def guild(command, arg0=''):
    target = spellbook.getTarget()

    if command == 'create':
        name = arg0
        base.cr.guildManager.d_requestCreateGuild(target.doId, name)
        return 'Requested guild with name: %s' % name
    elif command == 'whisper':
        message = arg0
        base.cr.guildManager.d_sendTalkWhisperToGuild(message)
        return ''
    
    return 'Invalid command.'