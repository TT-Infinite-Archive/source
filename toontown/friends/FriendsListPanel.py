from panda3d.core import Plane, PlaneNode, Point3, TextNode, Vec3, Vec4
from direct.gui.DirectGui import *
from direct.fsm import StateData
from toontown.toon import ToonAvatarPanel
from toontown.friends import ToontownFriendSecret
from toontown.toonbase import ToontownGlobals, EventGlobals, TTLocalizer
from otp.otpbase import OTPGlobals
from toontown.guilds import GuildInviter
FLPPets = 1
FLPOnline = 2
FLPAll = 3
if base.wantGuilds:
    FLPGuildOnline = 4
    FLPGuildAll = 5
    FLPEnemies = 6
else:
    FLPEnemies = 4
globalFriendsList = None

def determineFriendName(friendTuple):
    friendName = None
    if len(friendTuple) == 2:
        avId, flags = friendTuple
        playerId = None
        showType = 0
    elif len(friendTuple) == 3:
        avId, flags, playerId = friendTuple
        showType = 0
    elif len(friendTuple) == 4:
        avId, flags, playerId, showType = friendTuple
    if showType == 1 and playerId:
        playerInfo = base.cr.playerFriendsManager.playerId2Info.get(playerId)
        friendName = playerInfo.playerName
    else:
        hasManager = hasattr(base.cr, 'playerFriendsManager')
        handle = base.cr.identifyFriend(avId)
        if not handle and hasManager:
            handle = base.cr.playerFriendsManager.getAvHandleFromId(avId)
        if handle:
            friendName = handle.getName()
    return friendName


def showFriendsList():
    global globalFriendsList
    if not globalFriendsList:
        globalFriendsList = FriendsListPanel()
    globalFriendsList.enter()


def hideFriendsList():
    if globalFriendsList:
        globalFriendsList.exit()


def showFriendsListTutorial():
    global globalFriendsList
    if not globalFriendsList:
        globalFriendsList = FriendsListPanel()
    globalFriendsList.enter()
    globalFriendsList.closeCommand = globalFriendsList.close['command']
    globalFriendsList.close['command'] = None


def hideFriendsListTutorial():
    if globalFriendsList:
        if hasattr(globalFriendsList, 'closeCommand'):
            globalFriendsList.close['command'] = globalFriendsList.closeCommand
        globalFriendsList.exit()


def isFriendsListShown():
    if globalFriendsList:
        return globalFriendsList.isEntered
    return 0


def unloadFriendsList():
    global globalFriendsList
    if globalFriendsList:
        globalFriendsList.unload()
        globalFriendsList = None


class FriendsListPanel(DirectFrame, StateData.StateData):

    def __init__(self):
        self.leftmostPanel = FLPPets

        self.rightmostPanel = FLPEnemies
        DirectFrame.__init__(self, relief=None)
        self.listScrollIndex = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.initialiseoptions(FriendsListPanel)
        StateData.StateData.__init__(self, 'friends-list-done')
        self.friends = {}
        self.textRolloverColor = Vec4(1, 1, 0, 1)
        self.textDownColor = Vec4(0.5, 0.9, 1, 1)
        self.textDisabledColor = Vec4(0.4, 0.8, 0.4, 1)
        self.panelType = FLPOnline

    def load(self):
        if self.isLoaded:
            return None
        self.isLoaded = 1
        gui = loader.loadModel('phase_3.5/models/gui/friendslist_gui')
        auxGui = loader.loadModel('phase_3.5/models/gui/avatar_panel_gui')
        self.title = DirectLabel(parent=self, relief=None, text='', text_scale=TTLocalizer.FLPtitle, text_fg=(0, 0.1, 0.4, 1), pos=(0.007, 0.0, 0.2))
        self['image'] = gui.find('**/FriendsBox_Open')
        self.reparentTo(base.a2dTopRight)
        self.setPos(-0.233, 0, -0.46)
        scrollButtonImage = (gui.find('**/FndsLst_ScrollUp'), gui.find('**/FndsLst_ScrollDN'), gui.find('**/FndsLst_ScrollUp_Rllvr'), gui.find('**/FndsLst_ScrollUp'))
        self.scrollList = DirectScrolledList(parent=self, relief=None,
                                             incButton_image=scrollButtonImage, incButton_relief=None, incButton_pos=(0.0, 0.0, -0.316), incButton_image3_color=Vec4(0.6, 0.6, 0.6, 0.6), incButton_scale=(1.0, 1.0, -1.0),
                                             decButton_image=scrollButtonImage, decButton_relief=None, decButton_pos=(0.0, 0.0, 0.117), decButton_image3_color=Vec4(0.6, 0.6, 0.6, 0.6),
                                             itemFrame_pos=(-0.17, 0.0, 0.06), itemFrame_relief=None, numItemsVisible=8, items=[])
        clipper = PlaneNode('clipper')
        clipper.setPlane(Plane(Vec3(-1, 0, 0), Point3(0.2, 0, 0)))
        clipNP = self.scrollList.attachNewNode(clipper)
        closeImage = (auxGui.find('**/CloseBtn_UP'), auxGui.find('**/CloseBtn_DN'), auxGui.find('**/CloseBtn_Rllvr'))
        horizontalArrow = (gui.find('**/Horiz_Arrow_UP'), gui.find('**/Horiz_Arrow_DN'), gui.find('**/Horiz_Arrow_Rllvr'), gui.find('**/Horiz_Arrow_UP'))
        newFriend = (auxGui.find('**/Frnds_Btn_UP'), auxGui.find('**/Frnds_Btn_DN'), auxGui.find('**/Frnds_Btn_RLVR'))
        self.scrollList.setClipPlane(clipNP)
        self.close = DirectButton(parent=self, relief=None, image=closeImage, pos=(0.01, 0, -0.38), command=self.__close)
        self.left = DirectButton(parent=self, relief=None, image=horizontalArrow, image3_color=Vec4(0.6, 0.6, 0.6, 0.6), pos=(-0.15, 0.0, -0.38), scale=(-1.0, 1.0, 1.0), command=self.__left)
        self.right = DirectButton(parent=self, relief=None, image=horizontalArrow, image3_color=Vec4(0.6, 0.6, 0.6, 0.6), pos=(0.17, 0, -0.38), command=self.__right)
        self.newFriend = DirectButton(parent=self, relief=None, pos=(-0.14, 0.0, 0.14), image=newFriend, text=('', TTLocalizer.FriendsListPanelNewFriend, TTLocalizer.FriendsListPanelNewFriend), text_scale=TTLocalizer.FLPnewFriend, text_fg=(0, 0, 0, 1), text_bg=(1, 1, 1, 1), text_pos=(0.1, -0.085), textMayChange=1, command=self.__newFriend)
        self.secrets = DirectButton(parent=self, relief=None, pos=TTLocalizer.FLPsecretsPos, image=(auxGui.find('**/ChtBx_ChtBtn_UP'), auxGui.find('**/ChtBx_ChtBtn_DN'), auxGui.find('**/ChtBx_ChtBtn_RLVR')), text=('', TTLocalizer.FriendsListPanelSecrets, TTLocalizer.FriendsListPanelSecrets, ''), text_scale=TTLocalizer.FLPsecrets, text_fg=(0, 0, 0, 1), text_bg=(1, 1, 1, 1), text_pos=(-0.04, -0.085), textMayChange=0, command=self.__secrets)
        gui.removeNode()
        auxGui.removeNode()

    def unload(self):
        if not self.isLoaded:
            return None
        self.isLoaded = 0
        self.exit()
        del self.title
        del self.scrollList
        del self.close
        del self.left
        del self.right
        del self.friends
        DirectFrame.destroy(self)
        return None

    def makeFriendButton(self, friendTuple, colorChoice=None, bold=0):
        playerName = None
        toonName = None
        playerId = None
        if len(friendTuple) == 1:
            avId = friendTuple[0]
            playerId = None
            showType = 0
        elif len(friendTuple) == 2:
            avId, flags = friendTuple
            playerId = None
            showType = 0
        elif len(friendTuple) == 3:
            avId, flags, playerId = friendTuple
            showType = 0
        elif len(friendTuple) == 4:
            avId, flags, playerId, showType = friendTuple
        command = self.__choseFriend

        if playerId:
            playerInfo = base.cr.playerFriendsManager.playerId2Info.get(playerId, None)
            if playerInfo is not None:
                playerName = playerInfo.playerName
        hasManager = hasattr(base.cr, 'playerFriendsManager')
        handle = base.cr.identifyFriend(avId)
        if not handle and hasManager:
            handle = base.cr.playerFriendsManager.getAvHandleFromId(avId)
        if handle:
            toonName = handle.getName()
        if showType == 1 and playerId:
            if not playerName:
                return
            friendName = playerName
            rolloverName = toonName
        else:
            if not toonName:
                base.cr.fillUpFriendsMap()
                return
            friendName = toonName
            if playerName:
                rolloverName = playerName
            else:
                rolloverName = 'Unknown'
        if playerId:
            command = self.__chosePlayerFriend
            thing = playerId
        else:
            thing = avId
        fg = ToontownGlobals.ColorNoChat
        if flags & ToontownGlobals.FriendChat:
            fg = ToontownGlobals.ColorAvatar
        if playerId:
            fg = ToontownGlobals.ColorPlayer
        if colorChoice:
            fg = colorChoice
        fontChoice = ToontownGlobals.getToonFont()
        fontScale = 0.04
        bg = None
        if colorChoice and bold:
            fontScale = 0.04
            colorS = 0.7
            bg = (colorChoice[0] * colorS,
             colorChoice[1] * colorS,
             colorChoice[2] * colorS,
             colorChoice[3])
        db = DirectButton(relief=None, text=friendName, text_scale=fontScale, text_align=TextNode.ALeft, text_fg=fg, text_shadow=bg, text1_bg=self.textDownColor, text2_bg=self.textRolloverColor, text3_fg=self.textDisabledColor, text_font=fontChoice, textMayChange=0, command=command, extraArgs=[thing, showType])
        if playerId:
            accountName = DirectLabel(parent=db, pos=Vec3(-0.02, 0, 0), text=rolloverName, text_fg=(0, 0, 0, 1), text_bg=(1, 1, 1, 1), text_pos=(0, 0), text_scale=0.045, text_align=TextNode.ARight)
            accountName.reparentTo(db.stateNodePath[2])
        return db
        
    def makeGuildieButton(self, member, colorChoice=None, bold=0):
        command = self.__choseFriend
        if member is None:
            return

        friendName = member.getName()
        
        fg = ToontownGlobals.ColorAvatar
        if colorChoice:
            fg = colorChoice
        fontChoice = ToontownGlobals.getToonFont()
        fontScale = 0.04
        bg = None
        if colorChoice and bold:
            fontScale = 0.04
            colorS = 0.7
            bg = (colorChoice[0] * colorS,
             colorChoice[1] * colorS,
             colorChoice[2] * colorS,
             colorChoice[3])
        db = DirectButton(relief=None, text=friendName, text_scale=fontScale, text_align=TextNode.ALeft, text_fg=fg, text_shadow=bg, text1_bg=self.textDownColor, text2_bg=self.textRolloverColor, text3_fg=self.textDisabledColor, text_font=fontChoice, textMayChange=0, command=command, extraArgs=[member.doId, 0])
        return db

    def enter(self):
        if self.isEntered == 1:
            return None
        self.isEntered = 1
        if self.isLoaded == 0:
            self.load()
        base.localAvatar.obscureFriendsListButton(1)
        if ToonAvatarPanel.ToonAvatarPanel.currentAvatarPanel:
            ToonAvatarPanel.ToonAvatarPanel.currentAvatarPanel.cleanup()
            ToonAvatarPanel.ToonAvatarPanel.currentAvatarPanel = None
        self.__updateScrollList()
        self.__updateTitle()
        self.__updateArrows()
        self.__updateButtons()
        self.show()
        self.accept('friendOnline', self.__friendOnline)
        self.accept('friendOffline', self.__friendOffline)
        self.accept('friendsListChanged', self.__friendsListChanged)
        self.accept(EventGlobals.GuildsListChanged, self.__guildListChanged)
        self.accept('ignoreListChanged', self.__ignoreListChanged)
        self.accept('friendsMapComplete', self.__friendsListChanged)
        self.accept(OTPGlobals.PlayerFriendAddEvent, self.__friendsListChanged)
        self.accept(OTPGlobals.PlayerFriendUpdateEvent, self.__friendsListChanged)

    def exit(self):
        if not self.isEntered:
            return None
        self.isEntered = 0
        self.listScrollIndex[self.panelType] = self.scrollList.index
        self.hide()
        base.cr.cleanPetsFromFriendsMap()
        self.ignore('friendOnline')
        self.ignore('friendOffline')
        self.ignore('guildieOnline')
        self.ignore('guildieOffline')
        self.ignore('friendsListChanged')
        self.ignore('guildsListChanged')
        self.ignore('ignoreListChanged')
        self.ignore('friendsMapComplete')
        self.ignore(OTPGlobals.PlayerFriendAddEvent)
        self.ignore(OTPGlobals.PlayerFriendUpdateEvent)
        base.localAvatar.obscureFriendsListButton(-1)
        messenger.send(self.doneEvent)
        return None

    def __close(self):
        messenger.send('wakeup')
        self.exit()

    def __left(self):
        messenger.send('wakeup')
        self.listScrollIndex[self.panelType] = self.scrollList.index
        if self.panelType > self.leftmostPanel:
            self.panelType -= 1
        self.__updateScrollList()
        self.__updateTitle()
        self.__updateArrows()
        self.__updateButtons()

    def __right(self):
        messenger.send('wakeup')
        self.listScrollIndex[self.panelType] = self.scrollList.index
        if self.panelType < self.rightmostPanel:
            self.panelType += 1
        self.__updateScrollList()
        self.__updateTitle()
        self.__updateArrows()
        self.__updateButtons()

    def __secrets(self):
        messenger.send('wakeup')
        ToontownFriendSecret.showFriendSecret(ToontownFriendSecret.AvatarSecret)

    def __newFriend(self):
        messenger.send('wakeup')
        if base.wantGuilds and self.panelType in (FLPGuildOnline, FLPGuildAll):
            GuildInviter.showGuildInviter(None, None, None)
        else:
            messenger.send('friendAvatar', [None, None, None])

    def __choseFriend(self, friendId, showType = 0):
        messenger.send('wakeup')
        hasManager = hasattr(base.cr, 'playerFriendsManager')
        handle = base.cr.identifyFriend(friendId)
        if not handle and hasManager:
            handle = base.cr.playerFriendsManager.getAvHandleFromId(friendId)
        if handle:
            self.notify.info("Clicked on name in friend's list. doId = %s" % handle.doId)
            messenger.send('clickedNametag', [handle])

    def __chosePlayerFriend(self, friendId, showType = 1):
        messenger.send('wakeup')
        hasManager = hasattr(base.cr, 'playerFriendsManager')
        playerFriendInfo = base.cr.playerFriendsManager.playerId2Info.get(friendId)
        handle = base.cr.identifyFriend(playerFriendInfo.avatarId)
        if not handle and hasManager:
            handle = base.cr.playerFriendsManager.getAvHandleFromId(playerFriendInfo.avatarId)
        if playerFriendInfo != None:
            self.notify.info("Clicked on name in player friend's list. Id = %s" % friendId)
            messenger.send('clickedNametagPlayer', [handle, friendId, showType])

    def __updateScrollList(self):
        newFriends = []
        petFriends = []
        freeChatOneRef = []
        speedChatOneRef = []
        freeChatDouble = []
        speedChatDouble = []
        offlineFriends = []
        guildMembers = []
        guildMembersOnline = []

        if self.panelType == FLPAll:
            if base.friendMode == 0:
                for friendPair in base.localAvatar.friendsList:
                    playerId = 0
                    if hasattr(base.cr, 'playerFriendsManager'):
                        playerId = base.cr.playerFriendsManager.findPlayerIdFromAvId(friendPair[0])
                        if playerId:
                            if friendPair[1] & ToontownGlobals.FriendChat:
                                freeChatDouble.insert(0, (friendPair[0],
                                 friendPair[1],
                                 playerId,
                                 0))
                            else:
                                speedChatDouble.insert(0, (friendPair[0],
                                 friendPair[1],
                                 playerId,
                                 0))
                        elif base.cr.isFriendOnline(friendPair[0]):
                            if friendPair[1] & ToontownGlobals.FriendChat:
                                freeChatOneRef.insert(0, (friendPair[0],
                                 friendPair[1],
                                 0,
                                 0))
                            else:
                                speedChatOneRef.insert(0, (friendPair[0],
                                 friendPair[1],
                                 0,
                                 0))
                        elif friendPair[1] & ToontownGlobals.FriendChat:
                            freeChatOneRef.insert(0, (friendPair[0],
                             friendPair[1],
                             0,
                             0))
                        else:
                            speedChatOneRef.insert(0, (friendPair[0],
                             friendPair[1],
                             0,
                             0))
                    else:
                        offlineFriends.append((friendPair[0],
                         friendPair[1],
                         playerId,
                         0))

                if hasattr(base.cr, 'playerFriendsManager'):
                    for avatarId in base.cr.playerFriendsManager.getAllOnlinePlayerAvatars():
                        playerId = base.cr.playerFriendsManager.findPlayerIdFromAvId(avatarId)
                        playerFriendInfo = base.cr.playerFriendsManager.playerId2Info.get(playerId)
                        if not base.cr.playerFriendsManager.askAvatarKnownElseWhere(avatarId):
                            if playerFriendInfo.understandableYesNo:
                                freeChatDouble.insert(0, (avatarId,
                                 0,
                                 playerId,
                                 0))
                            else:
                                speedChatDouble.insert(0, (avatarId,
                                 0,
                                 playerId,
                                 0))

            elif base.friendMode == 1:
                for friendId in base.cr.avatarFriendsManager.avatarFriendsList:
                    playerId = base.cr.playerFriendsManager.findPlayerIdFromAvId(friendId)
                    newFriends.append((friendId,
                     0,
                     playerId,
                     0))

        if self.panelType == FLPOnline:
            if base.friendMode == 0:
                for friendPair in base.localAvatar.friendsList:
                    if hasattr(base.cr, 'playerFriendsManager') and base.cr.isFriendOnline(friendPair[0]):
                        playerId = base.cr.playerFriendsManager.findPlayerIdFromAvId(friendPair[0])
                        if playerId:
                            if friendPair[1] & ToontownGlobals.FriendChat:
                                freeChatDouble.insert(0, (friendPair[0],
                                 friendPair[1],
                                 playerId,
                                 0))
                            else:
                                speedChatDouble.insert(0, (friendPair[0],
                                 friendPair[1],
                                 playerId,
                                 0))
                        elif friendPair[1] & ToontownGlobals.FriendChat:
                            freeChatOneRef.insert(0, (friendPair[0],
                             friendPair[1],
                             0,
                             0))
                        else:
                            speedChatOneRef.insert(0, (friendPair[0],
                             friendPair[1],
                             0,
                             0))
                    elif base.cr.isFriendOnline(friendPair[0]):
                        offlineFriends.append((friendPair[0],
                         friendPair[1],
                         0,
                         0))

                if hasattr(base.cr, 'playerFriendsManager'):
                    for avatarId in base.cr.playerFriendsManager.getAllOnlinePlayerAvatars():
                        playerId = base.cr.playerFriendsManager.findPlayerIdFromAvId(avatarId)
                        playerFriendInfo = base.cr.playerFriendsManager.playerId2Info.get(playerId)
                        if not base.cr.playerFriendsManager.askAvatarKnownElseWhere(avatarId):
                            if playerFriendInfo.understandableYesNo:
                                freeChatDouble.insert(0, (avatarId,
                                 0,
                                 playerId,
                                 0))
                            else:
                                speedChatDouble.insert(0, (avatarId,
                                 0,
                                 playerId,
                                 0))

            elif base.friendMode == 1:
                for friendId in base.cr.avatarFriendsManager.avatarFriendsList:
                    friendInfo = base.cr.avatarFriendsManager.avatarId2Info[friendId]
                    playerId = base.cr.playerFriendsManager.findPlayerIdFromAvId(friendPair[0])
                    if friendInfo.onlineYesNo:
                        newFriends.insert(0, (friendId, 0, playerId, 0))

        if base.wantGuilds and self.panelType == FLPGuildAll:
            myGuild = base.cr.guildManager.guild
            if myGuild is not None:
                for member in myGuild.members:
                    if member.doId != base.localAvatar.doId:
                        guildMembers.append((member.doId, member.name))
        elif base.wantGuilds and self.panelType == FLPGuildOnline:
            myGuild = base.cr.guildManager.guild
            if myGuild is not None:
                for member in myGuild.members:
                    if member.online and member.doId != base.localAvatar.doId:
                        guildMembersOnline.append((member.doId, member.name))

        if self.panelType == FLPPets:
            for objId, obj in list(base.cr.doId2do.items()):
                from toontown.pets import DistributedPet
                if isinstance(obj, DistributedPet.DistributedPet):
                    friendPair = (objId, 0)
                    petFriends.append(friendPair)

        if self.panelType == FLPEnemies:
            for ignored in base.cr.ttiFriendsManager.ignoreList:
                newFriends.append((ignored, 0))

        if self.panelType == FLPAll or self.panelType == FLPOnline:
            if base.wantPets and base.localAvatar.hasPet():
                petFriends.insert(0, (base.localAvatar.getPetId(), 0))

        for friendPair in list(self.friends.keys()):
            friendButton = self.friends[friendPair]
            self.scrollList.removeItem(friendButton, refresh=0)
            friendButton.destroy()
            del self.friends[friendPair]

        newFriends.sort(key=lambda f: determineFriendName(f))
        petFriends.sort(key=lambda f: determineFriendName(f))
        freeChatOneRef.sort(key=lambda f: determineFriendName(f))
        speedChatOneRef.sort(key=lambda f: determineFriendName(f))
        freeChatDouble.sort(key=lambda f: determineFriendName(f))
        speedChatDouble.sort(key=lambda f: determineFriendName(f))
        offlineFriends.sort(key=lambda f: determineFriendName(f))
        if len(guildMembers) > 1:
            guildMembers.sort(key=lambda g: g[1])
        if len(guildMembersOnline) > 1:
            guildMembersOnline.sort(key=lambda g: g[1])
        for friendPair in newFriends:
            if friendPair not in self.friends:
                friendButton = self.makeFriendButton(friendPair)
                if friendButton:
                    self.scrollList.addItem(friendButton, refresh=0)
                    self.friends[friendPair] = friendButton

        for friendPair in petFriends:
            if friendPair not in self.friends:
                friendButton = self.makeFriendButton(friendPair, ToontownGlobals.ColorNoChat, 0)
                if friendButton:
                    self.scrollList.addItem(friendButton, refresh=0)
                    self.friends[friendPair] = friendButton

        for friendPair in freeChatDouble:
            if friendPair not in self.friends:
                friendButton = self.makeFriendButton(friendPair, ToontownGlobals.ColorFreeChat, 1)
                if friendButton:
                    self.scrollList.addItem(friendButton, refresh=0)
                    self.friends[friendPair] = friendButton

        for friendPair in freeChatOneRef:
            if friendPair not in self.friends:
                friendButton = self.makeFriendButton(friendPair, ToontownGlobals.ColorFreeChat, 0)
                if friendButton:
                    self.scrollList.addItem(friendButton, refresh=0)
                    self.friends[friendPair] = friendButton

        for friendPair in speedChatDouble:
            if friendPair not in self.friends:
                friendButton = self.makeFriendButton(friendPair, ToontownGlobals.ColorSpeedChat, 1)
                if friendButton:
                    self.scrollList.addItem(friendButton, refresh=0)
                    self.friends[friendPair] = friendButton

        for friendPair in speedChatOneRef:
            if friendPair not in self.friends:
                friendButton = self.makeFriendButton(friendPair, ToontownGlobals.ColorSpeedChat, 0)
                if friendButton:
                    self.scrollList.addItem(friendButton, refresh=0)
                    self.friends[friendPair] = friendButton

        for friendPair in offlineFriends:
            if friendPair not in self.friends:
                friendButton = self.makeFriendButton(friendPair, ToontownGlobals.ColorNoChat, 0)
                if friendButton:
                    self.scrollList.addItem(friendButton, refresh=0)
                    self.friends[friendPair] = friendButton

        for guildMemberPair in guildMembers:
            guildMemberId = guildMemberPair[0]
            if guildMemberId not in self.friends:
                guild = base.cr.guildManager.guild
                if guild is None:
                    continue
                memberInfo = guild.getMember(guildMemberId)
                if memberInfo.online:
                    friendButton = self.makeGuildieButton(memberInfo, ToontownGlobals.ColorGuildMemberOnline, 0)
                else:
                    friendButton = self.makeGuildieButton(memberInfo, ToontownGlobals.ColorGuildMember, 0)

                if friendButton:
                    self.scrollList.addItem(friendButton, refresh=0)
                    self.friends[guildMemberId] = friendButton

        for guildMemberPair in guildMembersOnline:
            guildMemberId = guildMemberPair[0]
            if guildMemberId not in self.friends:
                guild = base.cr.guildManager.guild
                if guild is None:
                    continue
                memberInfo = guild.getMember(guildMemberId)
                if memberInfo is None:
                    continue
                friendButton = self.makeGuildieButton(memberInfo, ToontownGlobals.ColorGuildMemberOnline, 0)
                if friendButton:
                    self.scrollList.addItem(friendButton, refresh=0)
                    self.friends[guildMemberId] = friendButton


        self.scrollList.index = self.listScrollIndex[self.panelType]
        self.scrollList.refresh()

    def __updateTitle(self):
        if self.panelType == FLPOnline:
            self.title['text'] = TTLocalizer.FriendsListPanelOnlineFriends
        elif self.panelType == FLPAll:
            self.title['text'] = TTLocalizer.FriendsListPanelAllFriends
        elif self.panelType == FLPPets:
            self.title['text'] = TTLocalizer.FriendsListPanelPets
        elif base.wantGuilds and self.panelType == FLPGuildAll:
            self.title['text'] = TTLocalizer.FriendsListPanelGuildAll
        elif base.wantGuilds and self.panelType == FLPGuildOnline:
            self.title['text'] = TTLocalizer.FriendsListPanelGuildOnline
        else:
            self.title['text'] = TTLocalizer.FriendsListPanelIgnoredFriends
        self.title.resetFrameSize()

    def __updateArrows(self):
        if self.panelType == self.leftmostPanel:
            self.left['state'] = 'inactive'
        else:
            self.left['state'] = 'normal'
        if self.panelType == self.rightmostPanel:
            self.right['state'] = 'inactive'
        else:
            self.right['state'] = 'normal'

    def __updateButtons(self):
        if base.wantGuilds and self.panelType in (FLPGuildOnline, FLPGuildAll):
            # New friend will now be new guildie
            self.newFriend['text'] = ('', TTLocalizer.FriendsListPanelNewGuildie, TTLocalizer.FriendsListPanelNewGuildie, '')
            self.newFriend.setText()
            self.secrets.hide()
        else:
            # Default new friend button
            self.newFriend['text'] = ('', TTLocalizer.FriendsListPanelNewFriend, TTLocalizer.FriendsListPanelNewFriend)
            self.newFriend.setText()
            self.secrets.show()

    def __friendOnline(self, doId, commonChatFlags, whitelistChatFlags):
        if self.panelType == FLPOnline:
            self.__updateScrollList()

    def __friendOffline(self, doId):
        if self.panelType == FLPOnline:
            self.__updateScrollList()

    def __friendsListChanged(self, arg1 = None, arg2 = None):
        if self.panelType != FLPEnemies:
            self.__updateScrollList()

    def __guildListChanged(self):
        if base.wantGuilds and self.panelType in (FLPGuildOnline, FLPGuildAll):
            self.__updateScrollList()

    def __ignoreListChanged(self):
        if self.panelType == FLPEnemies:
            self.__updateScrollList()

