from direct.gui.DirectGui import DirectLabel, DirectFrame, DirectButton, DirectScrolledList, DGG, OnscreenText, DirectWaitBar
from panda3d.core import TextNode, Vec4, CardMaker, NodePath, TransparencyAttrib

from toontown.toontowngui import ConfirmDialog
from toontown.toonbase import EventGlobals, FontAwesomeGlobals
from toontown.toonbase.ToontownGlobals import getInterfaceFont, getMinnieFont
from toontown.util import TTCardMaker
from toontown.guilds.GuildGlobals import *
from toontown.guilds import GuildQuestGlobals
from toontown.guilds.IconGlobals import *
from toontown.shtiker.GuildLeaderboard import GuildLeaderboard


class GuildPage(DirectFrame):
    SortNone = 0
    SortName = 1
    SortRole = 2
    SortLaff = 3
    SortCont = 4
    SortNameDn = 5
    SortRoleDn = 6
    SortLaffDn = 7
    SortContDn = 8

    def __init__(self, parent):
        self.parent = parent
        self.currentSizeIndex = None
        self.currentScrollIndex = 0
        self.sortedState = self.SortNone
        self.wantShowOffline = False

        DirectFrame.__init__(self, parent=self.parent, relief=None, pos=(0.0, 0.0, 0.0), scale=(1.0, 1.0, 1.0))

        self.leaveGuildDialog = None
        self.leaderboardPage = None
        self.memberObjects = []

        buttonModels = preloader.getModel('phase_3.5/models/gui/inventory_gui')
        upButton = buttonModels.find('**/InventoryButtonUp')
        downButton = buttonModels.find('**/InventoryButtonDown')
        rolloverButton = buttonModels.find('**/InventoryButtonRollover')
        listGui = preloader.getModel('phase_3.5/models/gui/friendslist_gui')
        detailsPlane = preloader.getModel('phase_9/models/gui/guild-top')
        arrowButton = (listGui.find('**/FndsLst_ScrollUp'), listGui.find('**/FndsLst_ScrollDN'), listGui.find('**/FndsLst_ScrollUp_Rllvr'), listGui.find('**/FndsLst_ScrollUp'))
        matchingGameGui = loader.loadModel('phase_3.5/models/gui/matching_game_gui')
        pointingArrowButton = (matchingGameGui.find('**/*minnieArrow'), matchingGameGui.find('**/*minnieArrow'), matchingGameGui.find('**/*minnieArrow'))
        incButtonScale = (1.3, 1.3, -1.3)
        decButtonScale = (1.3, 1.3, 1.3)
        headingTextScale = (0.05, 0.05, 0.05)
        primaryColor = (0.75, 0.85, 1, 1)
        secondaryColor = (0.5, 0.6, 1, 1)
        tertiaryColor = (0.2, 0.5, 0.8, 1)
        self.buttonColor = secondaryColor

        background = TTCardMaker.makeCard('phase_3/maps/curved-gui-square.png')

        self.mainFrame = DirectFrame(self.parent, relief=None, image=background, image_scale=(0.0011, 1, 0.0008), image_color=primaryColor, scale=(0.85, 1.0, 0.73))

        self.seasonFrame = DirectFrame(self.mainFrame, relief=None, image=background, image_scale=(0.0003, 1, 0.0001), image_color=tertiaryColor, pos=(-0.6, 1.0, 0.78))
        self.seasonText = DirectLabel(self.seasonFrame, relief=None, text='', text_align=TextNode.ACenter, text_scale=0.05)

        self.detailsFrame = DirectFrame(self.mainFrame, relief=None, geom=detailsPlane, geom_scale=(0.7, 1.0, 0.3), pos=(-0.6, 0, 0.5))
        self.detailsIcon = DirectButton(self.detailsFrame, relief=None, geom=None, pos=(-0.19, 0.0, 0), state=DGG.DISABLED)
        self.detailsName = DirectLabel(self.detailsFrame, relief=None, text='', pos=(0.1, 0.0, -0.01), text_align=TextNode.ACenter, text_scale=0.055)

        self.rankLabel = DirectLabel(self.mainFrame, relief=None, text='', text_font=getInterfaceFont(), pos=(-0.6, 0.0, 0.3), text_align=TextNode.ACenter, text_scale=0.05)
        self.rpLabel = DirectLabel(self.mainFrame, relief=None, text='', text_font=getInterfaceFont(), pos=(-0.65, 0.0, 0.2), text_align=TextNode.ACenter, text_scale=0.05)
        self.gpLabel = DirectLabel(self.mainFrame, relief=None, text='', text_font=getInterfaceFont(), pos=(-0.65, 0.0, 0.1), text_align=TextNode.ACenter, text_scale=0.05)

        self.questPoster = DirectFrame(self.mainFrame, relief=None, image=background, image_scale=(0.00035, 1, 0.0003), image_color=tertiaryColor, pos=(-0.575, 1.0, -0.3), scale=1.0)
        self.questPosterTitle = DirectLabel(self.questPoster, relief=None, text=TTLocalizer.GuildQuest, text_font=getInterfaceFont(), pos=(0.0, 0.0, 0.2), text_align=TextNode.ACenter, text_scale=0.07)
        self.questPosterDesc = OnscreenText(parent=self.questPoster, text='', font=getInterfaceFont(), align=TextNode.ACenter, scale=0.045, wordwrap=11)
        self.questPosterBar = DirectWaitBar(parent=self.questPoster, text='', text_font=getInterfaceFont(), text_scale=0.035, text_pos=(0.0, -0.01), pos=(0.0, 0.0, -0.2), value=0, range=100, relief=DGG.FLAT, frameColor=primaryColor, barColor=secondaryColor, borderWidth=(0.002, 0.001), frameSize=(-0.23, 0.23, -0.022, 0.022))
        self.questPosterReward = DirectLabel(self.questPosterTitle, relief=None, text='', text_font=getMinnieFont(), pos=(0.0, 0.0, -0.08), text_align=TextNode.ACenter, text_scale=0.045)

        self.nameHeading = DirectButton(self.mainFrame, relief=None, text=TTLocalizer.GuildPageTableName, text_font=getInterfaceFont(), text_scale=headingTextScale, text_align=TextNode.ACenter, pos=(-0.1, 0.0, 0.55), command=self.tableHeadingClicked, extraArgs=[self.SortName])
        self.roleHeading = DirectButton(self.mainFrame, relief=None, text=TTLocalizer.GuildPageTableRole, text_font=getInterfaceFont(), text_scale=headingTextScale, text_align=TextNode.ACenter, pos=(0.2, 0.0, 0.55), command=self.tableHeadingClicked, extraArgs=[self.SortRole])
        self.laffHeading = DirectButton(self.mainFrame, relief=None, text=TTLocalizer.GuildPageTableLaff, text_font=getInterfaceFont(), text_scale=headingTextScale, text_align=TextNode.ACenter, pos=(0.35, 0.0, 0.55), command=self.tableHeadingClicked, extraArgs=[self.SortLaff])
        self.contributionHeading = DirectButton(self.mainFrame, relief=None, text=TTLocalizer.GuildPageTableContribution, text_font=getInterfaceFont(), text_scale=headingTextScale, text_align=TextNode.ACenter, pos=(0.55, 0.0, 0.55), command=self.tableHeadingClicked, extraArgs=[self.SortCont])

        self.leaveGuildButton = DirectButton(self.mainFrame, relief=None, text=TTLocalizer.GuildPageLeave, text_pos=(0.0, -0.01, 0), text_font=getInterfaceFont(), text_scale=0.05, image=background, image_scale=(0.0002, 1, 0.0001), image_color=self.buttonColor, pos=(-0.75, 1.0, -0.85), command=self.openLeaveGuildDialog)
        self.manageGuildButton = DirectButton(self.mainFrame, relief=None, text=TTLocalizer.GuildPageManage, text_pos=(0.0, -0.01, 0), text_font=getInterfaceFont(), text_scale=0.05, image=background, image_scale=(0.0002, 1, 0.0001), image_color=self.buttonColor, pos=(-0.3, 1.0, -0.85))
        self.leaderboardButton = DirectButton(self.mainFrame, relief=None, text=TTLocalizer.GuildPageLeaderboards, text_pos=(-0.01, -0.01, -0.01), text_font=getInterfaceFont(), text_scale=(0.05, 0.06), geom=pointingArrowButton, geom_scale=(1.5, 1, 1), geom_color=self.buttonColor, pos=(0.75, 1.0, -0.85), command=self.openLeaderboard)
        self.leaveGuildButton.bind(DGG.WITHIN, self.__handleEnter, extraArgs=[self.leaveGuildButton])
        self.leaveGuildButton.bind(DGG.WITHOUT, self.__handleExit, extraArgs=[self.leaveGuildButton])
        self.manageGuildButton.bind(DGG.WITHIN, self.__handleEnter, extraArgs=[self.manageGuildButton])
        self.manageGuildButton.bind(DGG.WITHOUT, self.__handleExit, extraArgs=[self.manageGuildButton])
        self.leaderboardButton.bind(DGG.WITHIN, self.__handleEnter, extraArgs=[self.leaderboardButton])
        self.leaderboardButton.bind(DGG.WITHOUT, self.__handleExit, extraArgs=[self.leaderboardButton])

        self.memberList = DirectScrolledList(
            parent=self.mainFrame,
            relief=None,
            pos=(0.3, 0.0, 0.0),
            numItemsVisible=10,
            forceHeight=0.11,
            items=self.memberObjects,
            frameSize= (-0.55, 0.55, -0.6, 0.6),

            incButton_image=arrowButton,
            incButton_relief=None,
            incButton_scale=incButtonScale,
            incButton_pos=(0.0, 0.0, -0.65),
            incButton_image3_color=Vec4(1, 1, 1, 0.2),

            decButton_image=arrowButton,
            decButton_relief=None,
            decButton_scale=decButtonScale,
            decButton_pos=(0.0, 0.0, 0.65),
            decButton_image3_color=Vec4(1, 1, 1, 0.2),

            itemFrame_relief=DGG.SUNKEN,
            itemFrame_frameSize=(-0.55, 0.55, -0.6, 0.5),
            itemFrame_frameColor=(0.85, 0.95, 1, 1),
            itemFrame_borderWidth=(0.0025, 0.0025)
        )

        self.showOfflineButton = DirectButton(
            parent=self.mainFrame,
            relief=None,
            pos=(0.75, 0.0, 0.565),
            text=FontAwesomeGlobals.FAEyeOpen,
            text_scale=0.05,
            text_pos=(0.0, -0.015, 0.0),
            text_font=ToontownGlobals.getFontAwesome(),
            image=(upButton, downButton, rolloverButton),
            image_color=self.buttonColor,
            image_scale=(0.65, 0.75, 0.75),
            command=self.__handleClickedShowOffline
        )
        self.showOfflineButton.bind(DGG.WITHIN, self.__handleEnter, extraArgs=[self.showOfflineButton])
        self.showOfflineButton.bind(DGG.WITHOUT, self.__handleExit, extraArgs=[self.showOfflineButton])

        matchingGameGui.removeNode()
        background.removeNode()

        self.accept(EventGlobals.GuildMemberChanged, self.updateMember)
        self.accept(EventGlobals.GuildsListChanged, self.setupMemberObjects)
        self.accept(EventGlobals.GuildInfoChanged, self.setupPage)
        self.accept(EventGlobals.GuildQuestInfoChanged, self.setupGuildQuest)

        self.setupPage()

    def destroy(self):
        self.ignoreAll()
        self.closeLeaderboard()
        self.parent = None

        for memberObject in self.memberObjects:
            memberObject.destroy()

        del self.memberObjects[:]

        if self.mainFrame is not None:
            self.mainFrame.destroy()
            self.mainFrame = None
        DirectFrame.destroy(self)

    def setupPage(self):
        guild = base.cr.guildManager.guild
        # Don't check if guild is none, if guild is none it tells the page to clear itself
        selectedIndex = self.memberList.getSelectedIndex()

        # Setup page Info
        self.setupMemberObjects(guild)
        self.setupGuildHeader(guild)
        self.setupGuildPoints(guild)
        self.setupGuildQuest(guild)

        self.setupSeasonInfo()

        # Hide manage for non owners
        if guild is not None and guild.getLocalAvatar() is not None:
            if guild.getLocalAvatar().getRole().sortIndex != 0:
                self.manageGuildButton.hide()

        if guild is None:
            # If there is no guild hide these buttons
            self.manageGuildButton.hide()
            self.leaveGuildButton.hide()

        # Attempt to get back to where we were
        self.memberList.scrollTo(selectedIndex)

    def setupMemberObjects(self, guild=None):
        if guild is None:
            guild = base.cr.guildManager.guild
        if len(self.memberObjects):
            self.clearMemberObjects()
        if guild is None:
            return

        for index, member in enumerate(guild.members):
            if not self.wantShowOffline and not member.online:
                continue
            memberObject = GuildPageMember(
                self,
                member.doId,
                member.name,
                member.contribution,
                member.getRole().id,
                member.laff,
                member.online,
                index,
                self.memberList
            )
            self.memberObjects.append(memberObject)

        for item in self.memberObjects:
            self.memberList.addItem(item, refresh=True)
        self.sortMembers()

    def setupGuildHeader(self, guild):
        # Set the name
        if guild is None:
            self.detailsName['text'] = ''
            self.detailsIcon['geom'] = None
            return

        self.detailsName['text'] = guild.name
        if len(guild.name) > 10:
            self.detailsName['text_scale'] = 0.04
        else:
            self.detailsName['text_scale'] = 0.055

        # Set the icon
        iconId = guild.iconId
        model = ICON_ID_TO_MODEL[iconId]
        if model is None:
            self.detailsIcon['geom'] = None
            return
        
        iconModel = loader.loadModel(model)
        self.detailsIcon['geom'] = iconModel.find(ICON_ID_TO_NODE[iconId])
        iconModel.removeNode()

    def setupGuildPoints(self, guild):
        if guild is None:
            rank = TTLocalizer.GuildPageNotInGuild
            rankPoints = TTLocalizer.GuildPageNotInGuild
            guildPoints = TTLocalizer.GuildPageNotInGuild
        else:
            rank = guild.getRank()
            if rank == 0:
                rank = TTLocalizer.GuildPageUnranked
            rankPoints = guild.getRankPoints()
            guildPoints = guild.getGuildPoints()

        self.rankLabel['text'] = TTLocalizer.GuildPageRank % rank
        self.rpLabel['text'] = TTLocalizer.GuildPageRankPoints % rankPoints
        self.gpLabel['text'] = TTLocalizer.GuildPageGuildPoints % guildPoints

    def setupGuildQuest(self, guild=None):
        if guild is None:
            guild = base.cr.guildManager.guild

        description = TTLocalizer.GuildQuestNone
        rewardText = ''
        barText = ''
        barVal = 0

        if guild is not None:
            if guild.quest == GuildQuestGlobals.GUILD_QUEST_EMPTY:
                description = TTLocalizer.GuildQuestDisabled
            else:
                # Fill information with guild info if we belong to a guild
                questId = guild.quest[GuildQuestGlobals.GUILD_QUEST_ID]
                progress = guild.quest[GuildQuestGlobals.GUILD_QUEST_PROGRESS]
                goal = guild.quest[GuildQuestGlobals.GUILD_QUEST_GOAL]
                reward = guild.quest[GuildQuestGlobals.GUILD_QUEST_REWARD]

                description = TTLocalizer.GuildQuestDesc[questId] % goal
                rewardText = str(reward) + ' ' + TTLocalizer.GuildPointsAbbrev
                barText = TTLocalizer.GuildQuestProgress % (progress, goal)
                if goal > 0:
                    barVal = int((float(progress) / float(goal)) * 100)

                if progress == goal:
                    # Looks like this quest is actually done
                    barText = TTLocalizer.GuildQuestCompleted

        # Update GUI elements
        self.questPosterDesc['text'] = description
        self.questPosterBar['text'] = barText
        self.questPosterBar.update(barVal)
        self.questPosterReward['text'] = rewardText

    def setupSeasonInfo(self):
        # TODO: Season Manager stuff for getting current season
        self.seasonText['text'] = TTLocalizer.GuildPageSeasonsNotAvailable

    def clearMemberObjects(self):
        while len(self.memberList['items']):
            for item in self.memberList['items']:
                self.memberList.removeItem(item, refresh=True)

        for memberObject in self.memberObjects:
            memberObject.destroy()

        del self.memberObjects[:]
        self.memberObjects = []

    def goToPlayground(self):
        pass

    def openLeaderboard(self):
        self.mainFrame.hide()
        messenger.send(EventGlobals.WakeUp)
        self.leaderboardPage = GuildLeaderboard(self.parent, TTLocalizer.GuildLeaderboardTitle, pos=(0.0, 0.0, 0.0), scale=(1.03, 1.0, 0.65), backCommand=self.closeLeaderboard)

    def closeLeaderboard(self):
        if self.mainFrame is not None:
            self.mainFrame.show()
        messenger.send(EventGlobals.WakeUp)
        if self.leaderboardPage is not None:
            self.leaderboardPage.destroy()
            self.leaderboardPage = None

    def updateMember(self, memberId):
        guild = base.cr.guildManager.guild
        if guild is None:
            return

        member = guild.getMember(memberId)
        for memberObject in self.memberObjects:
            if memberObject.avId == member.doId:
                memberObject.updateFromMember(member)

        self.sortMembers()

    def tableHeadingClicked(self, index):
        if self.sortedState != index:
            self.sortedState = index
        else:
            # Add the amount of sorting options there are to get the opposing
            self.sortedState = index + 4

        self.sortMembers()

    def sortMembers(self):
        if self.sortedState == self.SortName:
            self.memberObjects = sorted(self.memberObjects, key=lambda member: member.name, reverse=False)
        elif self.sortedState == self.SortNameDn:
            self.memberObjects = sorted(self.memberObjects, key=lambda member: member.name, reverse=True)
        elif self.sortedState == self.SortRole:
            self.memberObjects = sorted(self.memberObjects, key=lambda member: member.roleId, reverse=False)
        elif self.sortedState == self.SortRoleDn:
            self.memberObjects = sorted(self.memberObjects, key=lambda member: member.roleId, reverse=True)
        elif self.sortedState == self.SortLaff:
            self.memberObjects = sorted(self.memberObjects, key=lambda member: member.laff, reverse=False)
        elif self.sortedState == self.SortLaffDn:
            self.memberObjects = sorted(self.memberObjects, key=lambda member: member.laff, reverse=True)
        elif self.sortedState == self.SortCont:
            self.memberObjects = sorted(self.memberObjects, key=lambda member: member.contribution, reverse=False)
        elif self.sortedState == self.SortContDn:
            self.memberObjects = sorted(self.memberObjects, key=lambda member: member.contribution, reverse=True)

        while len(self.memberList['items']) > 0:
            for item in self.memberList['items']:
                self.memberList.removeItem(item, refresh=True)
        for index, item in enumerate(self.memberObjects):
            item.setIndex(index)
            self.memberList.addItem(item, refresh=True)

    def openLeaveGuildDialog(self):
        if self.leaveGuildDialog is not None:
            self.leaveGuildDialog.destroy()
            self.leaveGuildDialog = None

        def cancel():
            self.leaveGuildDialog = None
        self.leaveGuildDialog = ConfirmDialog.ConfirmDialog(parent=self.mainFrame, text=TTLocalizer.GuildLeaveConfirmation, commands=(self.handleLeaveGuild, cancel))

    def handleLeaveGuild(self):
        base.cr.guildManager.d_requestLeaveGuild()

    def __handleEnter(self, button, e):
        button['image_color'] = (1, 1, 0.2, 1.0)
        button['geom_color'] = (1, 1, 0.2, 1.0)

    def __handleExit(self, button, e):
        button['image_color'] = self.buttonColor
        button['geom_color'] = self.buttonColor

    def __handleClickedShowOffline(self, e=None):
        self.wantShowOffline = not self.wantShowOffline
        if self.wantShowOffline:
            self.showOfflineButton['text'] = FontAwesomeGlobals.FAEyeClose
        else:
            self.showOfflineButton['text'] = FontAwesomeGlobals.FAEyeOpen
        self.setupMemberObjects()


class GuildPageMember(DirectButton):
    def __init__(self, parent, avId, name, contribution, roleId, laff, online, index, listObject):
        self.parent = parent
        self.avId = avId
        self.name = name
        self.contribution = contribution
        self.roleId = roleId
        self.laff = laff
        self.online = online
        self.index = index

        # Settings
        self.onlineTextColor = (0, 0, 0, 1)
        self.offlineTextColor = (0, 0, 0, 0.2)
        self.guild = base.cr.guildManager.guild
        self.role = self.guild.getRole(self.roleId)
        self.listObject = listObject

        textColor = self.offlineTextColor
        textScale = (0.042, 0.042, 0.042)
        if self.online:
            textColor = self.onlineTextColor
        chatGui = preloader.getModel('phase_3/models/gui/chat_button_gui')
        guildGui = preloader.getModel('phase_9/models/gui/guild-remove')
        arrowImage = (chatGui.find('**/*Horiz_Arrow_DN'), chatGui.find('**/*Horiz_Arrow_Rllvr'), chatGui.find('**/*Horiz_Arrow_UP'))
        removeImage = guildGui.find('**/*guild-remove')
        listFrameSize = listObject['frameSize']

        DirectButton.__init__(self, listObject, relief=None, frameSize=listFrameSize)
        self.mainFrame = DirectFrame(parent=self, relief=DGG.SUNKEN, pos=(0.0, 0.0, 0.45), borderWidth=(0.001, 0.001), frameSize=(listFrameSize[0], listFrameSize[1], -0.05, 0.05), frameColor=(0.0, 0.0, 0.0, 0.0))
        self.nameLabel = DirectLabel(self.mainFrame, text=self.getShortenedName(), relief=None, text_fg=textColor, text_scale=textScale, text_align=TextNode.ABoxedLeft, pos=(-0.525, 0.0, -0.01))
        self.roleLabel = DirectLabel(self.mainFrame, text=self.role.name, relief=None, text_fg=textColor, text_scale=textScale, text_align=TextNode.ACenter, pos=(-0.1, 0.0, -0.01))
        self.laffLabel = DirectLabel(self.mainFrame, text=str(laff), relief=None, text_fg=textColor, text_scale=textScale, text_align=TextNode.ACenter, pos=(0.05, 0.0, -0.01))
        self.contLabel = DirectLabel(self.mainFrame, text=str(contribution), relief=None, text_fg=textColor, text_scale=textScale, text_align=TextNode.ACenter, pos=(0.25, 0.0, -0.01))

        self.promoteButton = DirectButton(self.mainFrame, relief=None, image=arrowImage, image_scale=0.5, pos=(0.4, 0.0, 0.0), command=self.handlePromote)
        self.promoteButton.setR(270)
        self.demoteButton = DirectButton(self.mainFrame, relief=None, image=arrowImage, image_scale=0.5, pos=(0.45, 0.0, 0.0), command=self.handleDemote)
        self.demoteButton.setR(90)
        self.kickButton = DirectButton(self.mainFrame, relief=None, image=removeImage, image_scale=(0.045, 1.0, 0.02), pos=(0.5, 0.0, 0.0), command=self.openKickDialog)

        self.transferOwnershipDialog = None
        self.kickDialog = None

        # Cleanup
        self.updateColor()
        self.updateButtonStates()

    def destroy(self):
        self.ignoreAll()

        self.mainFrame.destroy()
        del self.mainFrame

        DirectButton.destroy(self)

    def setIndex(self, index):
        self.index = index

    def updateColor(self):
        frameColor = (0.5, 0.6, 1, 0.2)
        if self.index % 2 == 0:
            frameColor = (0.5, 0.6, 1, 0.1)

        self.mainFrame['frameColor'] = frameColor

    def updateFromMember(self, member):
        self.name = member.name
        self.contribution = member.contribution
        self.roleId = member.getRole().id
        self.laff = member.laff
        if member.online:
            self.setOnline()
        else:
            self.setOffline()
        self.setRoleId(self.roleId)
        self.updateLabels()

    def updateLabels(self):
        self.nameLabel['text'] = self.getShortenedName()
        self.roleLabel['text'] = self.role.name
        self.laffLabel['text'] = str(self.laff)
        self.contLabel['text'] = str(self.contribution)

    def getShortenedName(self):
        maxLength = 15
        name = self.name
        if len(name) > maxLength:
            name = name[:maxLength]
            name += '...'
        return name

    def openKickDialog(self):
        if self.kickDialog is not None:
            self.kickDialog.destroy()
            self.kickDialog = None

        def cancel():
            self.kickDialog = None
        self.kickDialog = ConfirmDialog.ConfirmDialog(self.listObject, TTLocalizer.GuildKickConfirmation % self.name, commands=(self.handleKick, cancel))

    def openTransferOwnershipDialog(self):
        if self.transferOwnershipDialog is not None:
            self.transferOwnershipDialog.destroy()
            self.transferOwnershipDialog = None

        def cancel():
            self.transferOwnershipDialog = None
        self.transferOwnershipDialog = ConfirmDialog.ConfirmDialog(self.listObject, TTLocalizer.GuildTransferOwnershipConfirmation % self.name, commands=(self.handleTransfer, cancel))

    def handlePromote(self):
        messenger.send(EventGlobals.WakeUp)
        oldRolePosition = self.role.sortIndex

        newRolePosition = oldRolePosition - 1
        if newRolePosition == 0:
            # Promoting to owner, lets ask him if they really want to pass ownership
            self.openTransferOwnershipDialog()
            return

        newRole = self.guild.getRoleAtPosition(newRolePosition)
        if newRole is None:
            return
        roleId = newRole.id

        base.cr.guildManager.d_requestChangeMemberRole(self.avId, roleId)

    def handleDemote(self):
        messenger.send(EventGlobals.WakeUp)
        oldRolePosition = self.role.sortIndex
        if oldRolePosition == 255:
            return

        newRolePosition = oldRolePosition + 1
        newRole = self.guild.getRoleAtPosition(newRolePosition)
        if newRole is None:
            return

        roleId = newRole.id

        base.cr.guildManager.d_requestChangeMemberRole(self.avId, roleId)

    def handleKick(self):
        messenger.send(EventGlobals.WakeUp)
        self.kickDialog = None
        base.cr.guildManager.d_requestRemoveMember(self.avId)

    def handleTransfer(self):
        messenger.send(EventGlobals.WakeUp)
        self.transferOwnershipDialog = None
        base.cr.guildManager.d_requestTransferOwnership(self.avId)

    def updateButtonStates(self):
        localMember = self.guild.getLocalAvatar()
        if localMember is None:
            return

        role = localMember.getRole()
        permissions = role.permissions

        if GUILD_PERMISSION_MODIFY_MEMBER_ROLE in permissions:
            self.setButtonState(True, demoteButton=True, promoteButton=True)

        if GUILD_PERMISSION_KICK_MEMBERS in permissions:
            self.setButtonState(True, kickButton=True)

        if self.role.overpowers(role):
            # This member overpowers localAvatar, don't let them do anything..
            self.setButtonState(False, demoteButton=True, promoteButton=True, kickButton=True)

        if self.role.sortIndex == self.guild.getHighestSortedRole():
            # No one can be demoted past this
            self.setButtonState(False, demoteButton=True)

        if localMember.getRole().sortIndex == self.role.sortIndex:
            # Cant edit similar level members
            self.setButtonState(False, promoteButton=True, demoteButton=True, kickButton=True)

        if localMember.doId == self.avId:
            # You cant edit yourself
            self.setButtonState(False, promoteButton=True, demoteButton=True, kickButton=True)

    def setButtonState(self, enable, demoteButton=False, promoteButton=False, kickButton=False):
        if enable:
            if demoteButton:
                self.demoteButton['state'] = DGG.NORMAL
                self.demoteButton['image_color'] = (1.0, 1.0, 1.0, 1.0)
            if promoteButton:
                self.promoteButton['state'] = DGG.NORMAL
                self.promoteButton['image_color'] = (1.0, 1.0, 1.0, 1.0)
            if kickButton:
                self.kickButton['state'] = DGG.NORMAL
                self.kickButton['image_color'] = (1.0, 1.0, 1.0, 1.0)
        else:
            if demoteButton:
                self.demoteButton['state'] = DGG.DISABLED
                self.demoteButton['image_color'] = (1.0, 1.0, 1.0, 0.2)
            if promoteButton:
                self.promoteButton['state'] = DGG.DISABLED
                self.promoteButton['image_color'] = (1.0, 1.0, 1.0, 0.2)
            if kickButton:
                self.kickButton['state'] = DGG.DISABLED
                self.kickButton['image_color'] = (1.0, 1.0, 1.0, 0.2)

    def setOnline(self):
        self.online = True
        self.nameLabel['text_fg'] = self.onlineTextColor
        self.laffLabel['text_fg'] = self.onlineTextColor
        self.roleLabel['text_fg'] = self.onlineTextColor
        self.contLabel['text_fg'] = self.onlineTextColor

    def setOffline(self):
        self.online = False
        self.nameLabel['text_fg'] = self.offlineTextColor
        self.laffLabel['text_fg'] = self.offlineTextColor
        self.roleLabel['text_fg'] = self.offlineTextColor
        self.contLabel['text_fg'] = self.offlineTextColor

    def setRoleId(self, roleId):
        self.roleId = roleId
        self.roleLabel['text'] = self.guild.getRole(roleId).name
        self.updateButtonStates()
