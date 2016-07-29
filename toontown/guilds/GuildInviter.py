from direct.directnotify import DirectNotifyGlobal
from toontown.toonbase import TTLocalizer, EventGlobals
from toontown.friends.FriendInviter import FriendInviter
from toontown.guilds import GuildGlobals
from toontown.suit import Suit
from toontown.pets import Pet
from otp.otpbase import OTPLocalizer
globalFriendInviter = None

def showGuildInviter(avId, avName, avDisableName):
    # We use the same friend inviter to avoid multiple dialog windows
    global globalFriendInviter
    if globalFriendInviter is not None:
        globalFriendInviter.cleanup()
        globalFriendInviter = None
    globalFriendInviter = GuildInviter(avId, avName, avDisableName)


def hideGuildInviter():
    global globalFriendInviter
    if globalFriendInviter is not None:
        globalFriendInviter.cleanup()
        globalFriendInviter = None


def unloadGuildInviter():
    global globalFriendInviter
    if globalFriendInviter is not None:
        globalFriendInviter.cleanup()
        globalFriendInviter = None

class GuildInviter(FriendInviter):
    notify = DirectNotifyGlobal.directNotify.newCategory('GuildInviter')

    def __init__(self, avId, avName, avDisableName):
        FriendInviter.__init__(self, avId, avName, avDisableName)
        self.bCancel['command'] = self.__handleCancel
        self.bOk['command'] = self.__handleOk

    def cleanup(self):
        self.ignore(self.avDisableName)
        self.ignore(EventGlobals.GuildInviteResponse)
        taskMgr.remove('timeOutInvite')
        self.destroy()

    def enterGetNewFriend(self):
        if base.cr.guildManager.guild is None:
            self['text'] = TTLocalizer.GuildInviterNotInGuild
            self.bOk.show()
            self.bCancel.hide()
        else:
            self['text'] = TTLocalizer.GuildInviterClickToon % len(base.cr.guildManager.guild.members)
            self.bCancel.show()
            self.accept(EventGlobals.ClickedNameTag, self.__handleClickedNametag)

    def __handleClickedNametag(self, avatar):
        self.avId = avatar.doId
        self.toonName = avatar.name
        self.avGuildId = avatar.getGuildId()
        if self.avGuildId == -1:
            self['text'] = TTLocalizer.GuildInviterCantProcess
            self.bOk.show()
            self.bCancel.hide()
            return
        self.fsm.request('begin')

    def enterBegin(self):
        # Lets begin
        if base.cr.guildManager.guild is None:
            # We aren't a part of a guild
            self['text'] = TTLocalizer.GuildInviterNotInGuild
            self.bOk.show()
            self.bCancel.hide()
            return
        elif GuildGlobals.GUILD_PERMISSION_INVITE_MEMBERS not in base.cr.guildManager.guild.getLocalAvatar().getRole().permissions:
            # We can't invite people
            self['text'] = TTLocalizer.GuildInviterNoPermissions
            self.bOk.show()
            self.bCancel.hide()
            return
        self.bCancel.setPos(0.35, 0.0, -0.05)
        self.bCancel.show()
        self.fsm.request('check')
        self.accept(self.avDisableName, self.__handleDisableAvatar)

    def exitBegin(self):
        self.ignore(self.avDisableName)
        self.bToon.hide()
        self.bCancel.setPos(0.0, 0.0, -0.1)
        self.bCancel.hide()

    def enterCheck(self):
        # Check if this avatar is valid
        myId = base.localAvatar.doId
        self.accept(self.avDisableName, self.__handleDisableAvatar)
        if self.avId == myId:
            # Can't invite yourself
            self.fsm.request('self')
        elif self.avId in base.cr.guildManager.guild.members:
            # This person is already in our guild
            self['text'] = TTLocalizer.GuildInviterAlreadyInMyGuild
            self.bOk.show()
            self.bCancel.hide()
        elif self.avGuildId:
            # This person is already in a guild
            self['text'] = TTLocalizer.GuildInviterAlreadyInGuild
            self.bOk.show()
            self.bCancel.hide()
            self.bCancel.setPos(0.0, 0.0, -0.16)
        else:
            if len(base.cr.guildManager.guild.members) > GuildGlobals.GUILD_MAX_MEMBER_COUNT:
                text = TTLocalizer.GuildInviterTooMany
                name = self.toonName
                self['text'] = text % name
                self.bOk.show()
                self.bCancel.hide()
                self.bCancel.setPos(0.0, 0.0, -0.16)
            else:
                self.fsm.request('checkAvailability')

    def exitCheck(self):
        self.ignore(self.avDisableName)
        self.bCancel.hide()

    def enterCheckAvailability(self):
        self.accept(self.avDisableName, self.__handleDisableAvatar)
        if self.avId not in base.cr.doId2do:
            self.fsm.request('wentAway')
            return
        else:
            avatar = base.cr.doId2do.get(self.avId)
        if isinstance(avatar, Suit.Suit):
            return
        elif isinstance(avatar, Pet.Pet):
            return
        if not base.cr.guildManager:
            self.notify.warning('No GuildManager available.')
            self.fsm.request('down')
            return
        else:
            base.cr.guildManager.d_invite(self.avId)
            self['text'] = TTLocalizer.GuildInviterCheckAvailability % self.toonName

            self.accept(EventGlobals.GuildInviteResponse, self.__guildResponse)
            self.bCancel.show()

            taskMgr.doMethodLater(20, self.__handleInviteTimedOut, 'timeOutInvite')

    def __guildResponse(self, response):
        self.ignore(EventGlobals.GuildInviteResponse)
        taskMgr.remove('timeOutInvite')
        if response == GuildGlobals.GUILD_INVITE_RESPONSE_ACCEPTED:
            self['text'] = TTLocalizer.GuildInviterSaidYes % self.toonName
            self.bCancel.hide()
            self.bOk.show()
        elif response == GuildGlobals.GUILD_INVITE_RESPONSE_REJECTED:
            self['text'] = TTLocalizer.GuildInviterSaidNo % self.toonName
            self.bCancel.hide()
            self.bOk.show()
        elif response == GuildGlobals.GUILD_INVITE_RESPONSE_ALREADY_IN_GUILD:
            self['text'] = TTLocalizer.GuildInviterAlreadyInGuild
            self.bCancel.hide()
            self.bOk.show()
        elif response == GuildGlobals.GUILD_INVITE_RESPONSE_CANT_PROCESS:
            self['text'] = TTLocalizer.GuildInviterCantProcess
            self.bCancel.hide()
            self.bOk.show()
        elif response == GuildGlobals.GUILD_INVITE_RESPONSE_MAYBE:
            self['text'] = TTLocalizer.GuildInviterMaybe % self.toonName
            self.bCancel.hide()
            self.bOk.show()
        elif response == GuildGlobals.GUILD_INVITE_RESPONSE_FULL:
            self['text'] = TTLocalizer.GuildInviterTooMany
            self.bCancel.hide()
            self.bOk.show()
        elif response == GuildGlobals.GUILD_INVITE_RESPONSE_IM_STAFF:
            self['text'] = TTLocalizer.GuildInviterImStaff
            self.bCancel.hide()
            self.bOk.show()
        elif response == GuildGlobals.GUILD_INVITE_RESPONSE_CANT_INVITE_STAFF:
            self['text'] = TTLocalizer.GuildInviterCantInviteStaff
            self.bCancel.hide()
            self.bOk.show()
        else:
            self.notify.warning('Got unexpected response to guildResponse: %s' % response)
            self['text'] = TTLocalizer.GuildInviterMaybe % self.toonName
            self.bCancel.hide()
            self.bOk.show()

    def exitCheckAvailability(self):
        self.ignore(self.avDisableName)
        self.ignore(EventGlobals.GuildInviteResponse)
        self.bCancel.hide()

    def __handleOk(self):
        unloadGuildInviter()

    def __handleCancel(self):
        # We send 0 to cancel our invite
        base.cr.guildManager.d_invite(0)
        unloadGuildInviter()

    def __handleDisableAvatar(self):
        self.fsm.request('wentAway')
        self.taskMgr.remove('timeOutInvite')

    def __handleInviteTimedOut(self, task=None):
        self.ignore(self.avDisableName)
        self.ignore(EventGlobals.GuildInviteResponse)
        self['text'] = TTLocalizer.GuildInviterTimedOut % self.toonName
        self.bOk.show()
        self.bCancel.hide()
        base.cr.guildManager.d_invite(0)
