from panda3d.core import TextNode, Vec4
from direct.gui.DirectGui import DirectLabel, DirectFrame, DirectButton, DirectScrolledList, DGG
from toontown.building import GroupTrackerGlobals
from toontown.toonbase import TTLocalizer, ToontownGlobals, EventGlobals, FontAwesomeGlobals
from toontown.hood import ZoneUtil
from toontown.toontowngui import WarningDialog, ConfirmDialog
from direct.directnotify.DirectNotifyGlobal import directNotify

SUIT_ICON_COLORS = (Vec4(0.863, 0.776, 0.769, 1.0), Vec4(0.749, 0.776, 0.824, 1.0),
                    Vec4(0.749, 0.769, 0.749, 1.0), Vec4(0.843, 0.745, 0.745, 1.0))

                    
class GroupTrackerGroup(DirectButton):
    def __init__(self, parent, leaderId, leaderName, shardName, shardId, category, memberIds, memberNames, type, zoneId, **kw):
        self.leaderId = leaderId
        self.leaderName = leaderName
        self.shardName = shardName
        self.shardId = shardId
        self.category = category
        self.memberIds = memberIds
        self.memberNames = memberNames
        self.type = type
        self.zoneId = zoneId
        self.playerCount = None

        if parent is None:
            parent = aspect2d

        text = TTLocalizer.GroupTrackerCategoryToText[self.category]
        
        optiondefs = (
            ('text', text, None),
            ('text_fg', (0.0, 0.0, 0.0, 1.0), None),
            ('text_align', TextNode.ALeft, None),
            ('text_pos', (0.0, 0.0, 0.0), None),
            ('text_scale', 0.05, None),
            ('relief', None, None)
        )

        self.defineoptions(kw, optiondefs)
        DirectButton.__init__(self, parent)
        self.initialiseoptions(GroupTrackerGroup)

        self.playerCount = DirectLabel(
            parent=self,
            pos=(0.6, 0, 0),
            relief=None,
            text='',
            text_align=TextNode.ARight,
            text_scale=0.05,
            text_fg=(0, 0, 0, 1)
        )
        self.updatePlayerCount()
        
    def destroy(self):
        DirectButton.destroy(self)
    
    def updatePlayerCount(self):
        if self.playerCount is None:
            return
        maxPlayers = GroupTrackerGlobals.CATEGORY_TO_MAX_PLAYERS[self.category]
        # Get the color of the player count
        if maxPlayers == len(self.memberIds):
            color = (1.0, 0.0, 0.0, 1.0)  # Red
        elif maxPlayers/2 >= len(self.memberIds):
            color = (0.0, 1.0, 0.0, 1.0)  # Green
        else:
            color = (0.0, 0.0, 0.0, 1.0)  # Black
        # Get the string
        if maxPlayers >= 10:
            text = str(len(self.memberIds))
        else:
            text = '%s/%s' % (len(self.memberIds), maxPlayers)
        # Set the properties
        self.playerCount['text'] = text
        self.playerCount['color'] = color
    
    def getLeaderId(self):
        return self.leaderId
        
    def getLeader(self):
        return self.leaderName
    
    def getDistrictName(self):
        return self.shardName

    def getShardId(self):
        return self.shardId
    
    def getTitle(self):
        return TTLocalizer.GroupTrackerCategoryToText[self.category]
    
    def getCurrentPlayers(self):
        return len(self.memberIds)
        
    def getCategory(self):
        return self.category
        
    def getMaxPlayers(self):
        return GroupTrackerGlobals.CATEGORY_TO_MAX_PLAYERS[self.category]
        
    def getMemberNames(self):
        return self.memberNames
    
    def getMemberIds(self):
        return self.memberIds

    def getLocationName(self):
        return ToontownGlobals.HoodIdToName.get(ZoneUtil.getHoodId(self.zoneId), 'Error')


class GroupTrackerPlayer(DirectButton):
    def __init__(self, parent, avId, name, isLeader, **kw):
        self.avId = avId
        self.name = name
        self.isLeader = isLeader
        self.leaderImage = None
        
        if parent is None:
            parent = aspect2d

        text=self.getName()
        
        optiondefs = (
            ('text', text, None),
            ('text_fg', (0.0, 0.0, 0.0, 1.0), None),
            ('text_align', TextNode.ALeft, None),
            ('text_pos', (-0.2, 0.0, 0.0), None),
            ('relief', None, None),
            ('text_scale', 0.05, None),
            ('command', self.loadPlayerDetails, None)
        )

        self.defineoptions(kw, optiondefs)
        DirectButton.__init__(self, parent)
        self.initialiseoptions(GroupTrackerPlayer)
        
        boardingGroupIcons = loader.loadModel('phase_9/models/gui/tt_m_gui_brd_status')
        self.leaderButtonImage = boardingGroupIcons.find('**/tt_t_gui_brd_statusLeader')
        self.leaderImage = DirectButton(parent=self, relief=None, state=DGG.DISABLED, image=(self.leaderButtonImage), image_scale=(0.06, 1.0, 0.06), pos=(-0.26, 0, 0.02), command=None)
        
        self.setLeaderStatus(self.isLeader)
        boardingGroupIcons.removeNode()
    
    def destroy(self):
        DirectButton.destroy(self)
    
    def setLeaderStatus(self, isLeader):
        self.isLeader = isLeader
        
        if self.isLeader:
            self.leaderImage.show()
        if not self.isLeader:
            self.leaderImage.hide()
    
    def getLeader(self):
        return self.isLeader
    
    def getName(self):
        # Lets cap a length so we don't have too long of names
        name = self.name
        if len(name) > 15:
            name = name[:16] + '...'  # Chop the first x characters
        return name
    
    def getId(self):
        return self.avId
        
    def loadPlayerDetails(self):
        # TODO: Load player details based off avId for localAvatar
        pass


class GroupTrackerPage(DirectFrame):
    notify = directNotify.newCategory('GroupTrackerPage')

    def __init__(self, parent):
        self.parent = parent

        DirectFrame.__init__(self, parent=self.parent, relief=None, pos=(0.0, 0.0, 0.0), scale=(1.0, 1.0, 1.0))
        self.groupWidgets = []
        self.playerWidgets = []
        self.images = []                # image nodes: Possible images to apply on groups
        self.scrollList = None          # DirectScrolledList: Holds the GroupTrackerGroup widgets
        self.scrollTitle = None         # DirectLabel: Title of the list that holds the groups
        self.playerList = None          # DirectScrolledList: Holds players when showing a specific group details
        self.playerListTitle = None     # DirectLabel: Title of the playerList
        self.groupInfoTitle = None      # DirectLabel: holds the group detail title to show on the right
        self.groupInfoDistrict = None   # DirectLabel: shows group detail district on the right
        self.statusMessage = None       # DirectLabel: Shows important messages like Loading... or "No boarding groups available"
        self.groupIcon = None           # DirectButton: Icon to associate with the group ex. sellbot icon or cashbot icon depending on group info
        self.wantGroupToggle = None     # DirectButton: Allows the toon to toggle his listing
        self.specialButton = None        # DirectButton: Used for jellybean fests rn
        self.warning = None             # Dialog
        self.load()

    def load(self):
        self.listXorigin = -0.02
        self.listFrameSizeX = 0.67
        self.listZorigin = -0.96
        self.listFrameSizeZ = 1.04
        self.arrowButtonScale = 1.3
        self.itemFrameXorigin = -0.237
        self.itemFrameZorigin = 0.365
        self.buttonXstart = self.itemFrameXorigin + 0.293
        gui = preloader.getModel('phase_3.5/models/gui/friendslist_gui')
        guiButton = loader.loadModel('phase_3/models/gui/quit_button')
        buttonModels = preloader.getModel('phase_3.5/models/gui/inventory_gui')
        upButton = buttonModels.find('**/InventoryButtonUp')
        downButton = buttonModels.find('**/InventoryButtonDown')
        rolloverButton = buttonModels.find('**/InventoryButtonRollover')
        self.scrollList = DirectScrolledList(
            parent=self,
            relief=None,
            pos=(-0.5, 0, 0),
            incButton_image=(
                gui.find('**/FndsLst_ScrollUp'),
                gui.find('**/FndsLst_ScrollDN'),
                gui.find('**/FndsLst_ScrollUp_Rllvr'),
                gui.find('**/FndsLst_ScrollUp')
            ),
            incButton_relief=None,
            incButton_scale=(self.arrowButtonScale, self.arrowButtonScale, -self.arrowButtonScale),
            incButton_pos=(self.buttonXstart, 0, self.itemFrameZorigin - 0.999),
            incButton_image3_color=Vec4(1, 1, 1, 0.2),
            decButton_image=(
                gui.find('**/FndsLst_ScrollUp'),
                gui.find('**/FndsLst_ScrollDN'),
                gui.find('**/FndsLst_ScrollUp_Rllvr'),
                gui.find('**/FndsLst_ScrollUp')
            ),
            decButton_relief=None,
            decButton_scale=(self.arrowButtonScale, self.arrowButtonScale, self.arrowButtonScale),
            decButton_pos=(self.buttonXstart, 0, self.itemFrameZorigin + 0.227),
            decButton_image3_color=Vec4(1, 1, 1, 0.2),
            itemFrame_pos=(self.itemFrameXorigin, 0, self.itemFrameZorigin),
            itemFrame_scale=1.0,
            itemFrame_relief=DGG.SUNKEN,
            itemFrame_frameSize=(
                self.listXorigin,
                self.listXorigin + self.listFrameSizeX,
                self.listZorigin,
                self.listZorigin + self.listFrameSizeZ
            ),
            itemFrame_frameColor=(0.85, 0.95, 1, 1),
            itemFrame_borderWidth=(0.01, 0.01),
            numItemsVisible=15,
            forceHeight=0.065,
            items=self.groupWidgets
        )
                                            
        self.scrollTitle = DirectFrame(
            parent=self.scrollList,
            text=TTLocalizer.GroupTrackerListTitle,
            text_scale=0.06,
            text_align=TextNode.ACenter,
            relief=None,
            pos=(self.buttonXstart, 0, self.itemFrameZorigin + 0.127)
        )
        
        self.playerList = DirectScrolledList(
            parent=self,
            relief=None,
            pos=(0.45, 0, 0.1),

            incButton_image=(gui.find('**/FndsLst_ScrollUp'),
                             gui.find('**/FndsLst_ScrollDN'),
                             gui.find('**/FndsLst_ScrollUp_Rllvr'),
                             gui.find('**/FndsLst_ScrollUp')
                             ),
            incButton_relief=None,
            incButton_scale=(1.0, 1.0, -1.0),
            incButton_pos=(0, 0, -0.28),
            incButton_image3_color=Vec4(1, 1, 1, 0.05),

            decButton_image=(gui.find('**/FndsLst_ScrollUp'),
                             gui.find('**/FndsLst_ScrollDN'),
                             gui.find('**/FndsLst_ScrollUp_Rllvr'),
                             gui.find('**/FndsLst_ScrollUp')
                             ),
            decButton_relief=None,
            decButton_scale=(1.0, 1.0, 1.0),
            decButton_pos=(0.0, 0, 0.04),
            decButton_image3_color=Vec4(1, 1, 1, 0.25),

            itemFrame_pos=(0, 0, -0.05),
            itemFrame_scale=1.0,
            itemFrame_relief=DGG.SUNKEN,
            itemFrame_frameSize=(-0.3, 0.3,  #x
                                 -0.2, 0.06),  #z
            itemFrame_frameColor=(0.85, 0.95, 1, 1),
            itemFrame_borderWidth=(0.01, 0.01),
            numItemsVisible=4,
            forceHeight=0.05,
            items=self.playerWidgets
        )
                                            
        self.playerListTitle = DirectFrame(
            parent=self.playerList,
            text='',
            text_scale=0.05,
            text_align=TextNode.ACenter,
            relief=None,
            pos=(0, 0, 0.08)
        )
        self.groupInfoTitle = DirectLabel(
            parent=self,
            text='',
            text_scale=0.080,
            text_align=TextNode.ACenter,
            text_wordwrap=15,
            relief=None,
            pos=(0.45, 0, 0.5)
        )
        self.groupInfoDistrict = DirectLabel(
            parent=self,
            text='',
            text_scale=0.050,
            text_align=TextNode.ACenter,
            text_wordwrap=15,
            relief=None,
            pos=(0.45, 0, 0.4)
        )
        self.statusMessage = DirectLabel(
            parent=self,
            text='',
            text_scale=(0.060, 0.060, 1),
            text_align=TextNode.ACenter,
            text_wordwrap=6,
            relief=None,
            pos=(0.45, 0, 0.1)
        )
                                     
        # Group Image:
        self.groupIcon = DirectButton(parent=self, relief=None, state=DGG.DISABLED, image=None, image_scale=(0.35, 1, 0.35), image_color=Vec4(1.0, 1.0, 1.0, 0.75), pos=(0.45, 10, -0.45), command=self.doNothing)
        
        # Group Toggle:
        self.wantGroupToggle = DirectButton(
            parent=self,
            relief=None,
            pos=(-0.15, 0, 0.5),
            text=FontAwesomeGlobals.FAEyeClose,
            text_scale=0.05,
            text_pos=(0.0, -0.015, 0.0),
            text_font=ToontownGlobals.getFontAwesome(),
            image=(upButton, downButton, rolloverButton),
            image_color=(0.5, 0.6, 1, 1),
            image_scale=(0.6, 0.75, 0.75),
            command=self.toggleWantGroup
        )
        self.wantGroupToggle.bind(DGG.WITHIN, self.__handleEnter, extraArgs=[self.wantGroupToggle])
        self.wantGroupToggle.bind(DGG.WITHOUT, self.__handleExit, extraArgs=[self.wantGroupToggle])
        self.updateWantGroupButton(base.localAvatar.wantGroupTracker())

        # Special Button:
        self.specialButton = DirectButton(
            parent=self,
            relief=None,
            pos=(-0.7, 0, 0.5),
            text=FontAwesomeGlobals.FAGift,
            text_scale=0.05,
            text_pos=(0.0, -0.015, 0.0),
            text_font=ToontownGlobals.getFontAwesome(),
            image=(upButton, downButton, rolloverButton),
            image_color=(0.5, 0.6, 1, 1),
            image_scale=(0.6, 0.75, 0.75),
            command=self.__handleClickedSpecialButton
        )
        self.specialButton.bind(DGG.WITHIN, self.__handleEnter, extraArgs=[self.specialButton])
        self.specialButton.bind(DGG.WITHOUT, self.__handleExit, extraArgs=[self.specialButton])

        # Loading possible group icons
        suitIcons = loader.loadModel('phase_3/models/gui/cog_icons')     
        bossbotIcon = suitIcons.find('**/CorpIcon')
        bossbotIcon.setColor(SUIT_ICON_COLORS[0])
        self.images.append(bossbotIcon)
        
        lawbotIcon = suitIcons.find('**/LegalIcon')
        lawbotIcon.setColor(SUIT_ICON_COLORS[1])
        self.images.append(lawbotIcon)
        
        cashbotIcon = suitIcons.find('**/MoneyIcon')
        cashbotIcon.setColor(SUIT_ICON_COLORS[2])
        self.images.append(cashbotIcon)
        
        sellbotIcon = suitIcons.find('**/SalesIcon')
        sellbotIcon.setColor(SUIT_ICON_COLORS[3])
        self.images.append(sellbotIcon)

        jarGui = loader.loadModel('phase_3.5/models/gui/jar_gui')
        jar = jarGui.find('**/Jar')
        self.images.append(jar)
        
        # Clean up
        self.clearGroupInfo()
        self.statusMessage.hide()
        
        suitIcons.removeNode()
        guiButton.removeNode()
        jarGui.removeNode()

        self.accept(EventGlobals.GroupTrackerResponse, self.updatePage)

        self.updateGroups()
        self.setPlayers()
        if not self.scrollList['items']:
            self.statusMessage['text'] = TTLocalizer.GroupTrackerLoading
            self.statusMessage.show()
        base.cr.globalGroupTracker.d_requestGroups()
        taskMgr.doMethodLater(5, self.displayStillTrying, self.uniqueName('timeout'))

    def displayStillTrying(self, task=None):
        self.statusMessage['text'] = TTLocalizer.GroupTrackerStillTrying
        self.statusMessage.show()
        taskMgr.doMethodLater(5, self.displayNoGroups, self.uniqueName('timeout'))

    def displayNoGroups(self, task=None):
        self.statusMessage['text'] = TTLocalizer.GroupTrackerEmpty
        self.statusMessage.show()
        self.clearGroupInfo()

    def updatePage(self):
        taskMgr.remove(self.uniqueName('timeout'))
        self.updateGroups()

    def destroy(self):
        self.ignoreAll()
        taskMgr.remove(self.uniqueName('timeout'))
        base.cr.globalGroupTracker.d_doneRequesting()
        if self.scrollList is not None:
            self.scrollList.destroy()
            self.scrollList = None
        if self.groupInfoDistrict is not None:
            self.groupInfoDistrict.destroy()
            self.groupInfoDistrict = None
        if self.playerList is not None:
            self.playerList.destroy()
            self.playerList = None
        if self.groupInfoTitle is not None:
            self.groupInfoTitle.destroy()
            self.groupInfoTitle = None
        if self.groupIcon is not None:
            self.groupIcon.destroy()
            self.groupIcon = None
        if self.wantGroupToggle is not None:
            self.wantGroupToggle.destroy()
            self.wantGroupToggle = None
        for widget in self.playerWidgets:
            widget.destroy()
        for widget in self.groupWidgets:
            widget.destroy()

        del self.playerWidgets[:]
        del self.groupWidgets[:]
        DirectFrame.destroy(self)

    def handleWithinGroup(self, groupWidget, mouseEvent):
        self.updateGroupInfo(groupWidget)
        groupWidget['text_bg'] = (1.0, 1.0, 0.0, 1.0)

    def handleWithoutGroup(self, groupWidget, mouseEvent):
        groupWidget['text_bg'] = (0.0, 0.0, 0.0, 0.0)

    def handleClickedGroup(self, groupWidget, mouseEvent):
        hoodsVisited = base.localAvatar.hoodsVisited
        hoodId = ZoneUtil.getCanonicalHoodId(groupWidget.zoneId)
        shardId = groupWidget.getShardId()
        leaderId = groupWidget.leaderId
        # Sanity checks
        def handleWarningClose():
            self.warning = None
        if hoodId not in hoodsVisited + ToontownGlobals.HoodsAlwaysVisited:
            if self.warning is None:
                self.warning = WarningDialog.WarningDialog(self, TTLocalizer.TeleportPanelUnknownHood % base.cr.hoodMgr.getFullnameFromId(hoodId), command=handleWarningClose)
            return
        elif hoodId not in base.cr.hoodMgr.getAvailableZones():
            if self.warning is None:
                self.warning = WarningDialog.WarningDialog(self, TTLocalizer.TeleportPanelUnavailableHood % base.cr.hoodMgr.getFullnameFromId(hoodId), command=handleWarningClose)
            return
        elif base.localAvatar.doId in groupWidget.memberIds or leaderId in base.cr.doId2do:
            if self.warning is None:
                self.warning = WarningDialog.WarningDialog(self, TTLocalizer.GroupTrackerAlreadyThere, command=handleWarningClose)
            return
        elif not base.localAvatar.isTeleportAllowed():
            if self.warning is None:
                self.warning = WarningDialog.WarningDialog(self, TTLocalizer.GroupTrackerCannotTeleport, command=handleWarningClose)
            return
        elif not base.localAvatar.hasTeleportAccess(hoodId):
            if self.warning is None:
                self.warning = WarningDialog.WarningDialog(self, TTLocalizer.GroupTrackerNoAccess % base.cr.hoodMgr.getFullnameFromId(hoodId), command=handleWarningClose)
            return
        elif len(groupWidget.memberIds) == GroupTrackerGlobals.CATEGORY_TO_MAX_PLAYERS[groupWidget.category]:
            # This group is full, you would not want to teleport there.
            if self.warning is None:
                self.warning = WarningDialog.WarningDialog(self, TTLocalizer.GroupTrackerFullGroup, command=handleWarningClose)
            return
        elif groupWidget.zoneId in ToontownGlobals.NoTeleportZones:
            # Can't have people teleporting in without suits
            if self.warning is None:
                self.warning = WarningDialog.WarningDialog(self, TTLocalizer.GroupTrackerCannotTeleportThere, command=handleWarningClose)
            return
        if shardId == base.localAvatar.defaultShard:
            shardId = None
        place = base.cr.playGame.getPlace()
        place.requestTeleport(hoodId, groupWidget.zoneId, shardId, leaderId)
        base.cr.globalGroupTracker.d_requestInform(leaderId, base.localAvatar.getName(), GroupTrackerGlobals.INFORM_COMING)
        
    def updateGroupInfo(self, groupWidget):
        # Updates the Right Page of the Group Tracker Page with new Info
        self.statusMessage.hide()

        # Update the Player List
        if groupWidget.type != GroupTrackerGlobals.GROUP_TYPE_JELLYBEAN:
            self.setPlayers(groupWidget)
            self.playerList.show()

            # Update the Player List Title
            self.playerListTitle['text'] = 'Players %s/%s:' % (groupWidget.getCurrentPlayers(), groupWidget.getMaxPlayers())
            self.playerListTitle.show()

        # Update the District
        text = TTLocalizer.BoardingGroupDistrictInformation % {'district': groupWidget.getDistrictName()}
        if groupWidget.type == GroupTrackerGlobals.GROUP_TYPE_JELLYBEAN:
            text += '\n\n\nLocation: \n\n %s' % groupWidget.getLocationName()

        self.groupInfoDistrict['text'] = text
        self.groupInfoDistrict.show()

        # Update the Title
        self.groupInfoTitle['text'] = groupWidget.getTitle()
        self.groupInfoTitle.show()

        # Update the Image
        scale = (0.35, 1, 0.35)
        if groupWidget.type == GroupTrackerGlobals.GROUP_TYPE_JELLYBEAN:
            scale = (1.0, 1.0, 1.0)
        self.groupIcon['image'] = self.images[GroupTrackerGlobals.CATEGORY_TO_IMAGE_ID[groupWidget.getCategory()]]
        self.groupIcon['image_scale'] = scale
        self.groupIcon.show()

    def clearGroupInfo(self):
        # Hide all the information on this page
        if self.playerList is not None:
            self.playerList.hide()

        if self.playerListTitle is not None:
            self.playerListTitle.hide()

        if self.groupInfoDistrict is not None:
            self.groupInfoDistrict.hide()

        if self.groupInfoTitle is not None:
            self.groupInfoTitle.hide()

        if self.groupIcon is not None:
            self.groupIcon.hide()

    def setPlayers(self, groupWidget=None):
        # Clear the Widgets that were held in the listings
        for playerWidget in self.playerWidgets:
            playerWidget.destroy()
        del self.playerWidgets[:]
        self.playerWidgets = []

        # Make a player widget for each player
        if groupWidget:
            leaderId = groupWidget.getLeaderId()
            playerNames = groupWidget.getMemberNames()
            playerIds = groupWidget.getMemberIds()
            for playerName in playerNames:
                playerId = playerIds[playerNames.index(playerName)]
                isLeader = playerId == leaderId
                self.playerWidgets.append(GroupTrackerPlayer(parent=self, avId=playerId, name=playerName, isLeader=isLeader))

        self.updatePlayerList()

    def reconsiderGroupInfo(self, groupWidget):
        # If someone is viewing this info and it was updated, we also want to update the info being viewed
        if self.playerWidgets is None or self.playerList['items'] == []:
            return  # No Info is being viewed at the moment since you cant have an empty group
        
        # We have to update if this group's leader is the leader in the playerlist being viewed right now
        leaderId = groupWidget.getLeaderId()
        
        # Check all the players in the playerList being viewed for the same leader
        for playerWidget in self.playerWidgets:
            if playerWidget.getLeader():
                if leaderId == playerWidget.getId():
                    self.updateGroupInfo(groupWidget)
                    return False
        
        return True
                
    def updateGroups(self, groups=None):
        if groups is None:
            groups = base.cr.globalGroupTracker.leader2Group.items()
        # Clear our Group Widgets
        for group in self.groupWidgets:
            group.destroy()
        del self.groupWidgets[:]
        
        wantReconsiderInfo = True
    
        # Create a new group widget for each group
        for leaderId, group in groups:
            if not group[GroupTrackerGlobals.SHOW] or len(group[GroupTrackerGlobals.MEMBER_IDS]) == 0:
                # Group shouldn't be displayed
                continue
                
            leaderName = group[GroupTrackerGlobals.LEADER_NAME]
            shardName = group[GroupTrackerGlobals.SHARD_NAME]
            shardId = group[GroupTrackerGlobals.SHARD_ID]
            category = group[GroupTrackerGlobals.CATEGORY]
            memberIds = group[GroupTrackerGlobals.MEMBER_IDS]
            memberNames = group[GroupTrackerGlobals.MEMBER_NAMES]
            type = group[GroupTrackerGlobals.TYPE]
            zoneId = group[GroupTrackerGlobals.ZONE_ID]
            
            groupWidget = GroupTrackerGroup(self, leaderId, leaderName, shardName, shardId, category, memberIds, memberNames, type, zoneId)
            groupWidget.bind(DGG.WITHIN, self.handleWithinGroup, extraArgs=[groupWidget])
            groupWidget.bind(DGG.WITHOUT, self.handleWithoutGroup, extraArgs=[groupWidget])
            groupWidget.bind(DGG.B1CLICK, self.handleClickedGroup, extraArgs=[groupWidget])
            self.groupWidgets.append(groupWidget)
            if wantReconsiderInfo:
                wantReconsiderInfo = self.reconsiderGroupInfo(groupWidget)
        
        # Edge case where a group that was removed, info might remain on the screen if it didn't exist any more
        if wantReconsiderInfo:
            self.clearGroupInfo()
        
        # There are no groups, hide the information
        if len(self.groupWidgets) == 0:
            self.displayNoGroups()
        self.updateGroupList()

    def updateGroupList(self): 
        self.statusMessage.hide()
        if self.scrollList is None:
            return
            
        # Clear the Group Listing
        for item in self.scrollList['items']:
            if item:
                self.scrollList.removeItem(item, refresh=True)
        self.scrollList['items'] = []
        
        # Re-populate the Group Listing
        for groupWidget in self.groupWidgets:
            self.scrollList.addItem(groupWidget, refresh=True)
        
        if len(self.groupWidgets) == 0:
            self.displayNoGroups()

    def updatePlayerList(self):
        if self.playerList is None:
            return

        # Clear the Player Listing
        for item in self.playerList['items']:
            if item:
                self.playerList.removeItem(item)
        self.playerList['items'] = []

        # Re-Populate the List
        for playerWidget in self.playerWidgets:
            self.playerList.addItem(playerWidget)

    def toggleWantGroup(self):
        want = not base.localAvatar.wantGroupTracker()
        if base.localAvatar.doId in base.cr.globalGroupTracker.leader2Group.keys():
            base.cr.globalGroupTracker.d_showMe(want)
        # Updates the ai toon so the boarding group AI could know what he wants
        base.localAvatar.setWantGroupTracker(want)
        # Update UI
        self.updateWantGroupButton(want)

    def __handleClickedSpecialButton(self):
        def handleWarningClose():
            self.warning = None

        def handleConfirm():
            self.warning = None
            base.cr.globalGroupTracker.d_requestCreateSpecialGroup(GroupTrackerGlobals.GROUP_TYPE_JELLYBEAN)

        for leaderId, group in base.cr.globalGroupTracker.leader2Group.items():
            if base.localAvatar.doId == leaderId or base.localAvatar.doId in group[GroupTrackerGlobals.MEMBER_IDS]:
                if self.warning is None:
                    self.warning = WarningDialog.WarningDialog(parent=self, text=TTLocalizer.GroupTrackerAlreadyInAGroup, command=handleWarningClose)
                return
        if base.localAvatar.zoneId not in ToontownGlobals.Hoods:
            if self.warning is None:
                self.warning = WarningDialog.WarningDialog(parent=self, text=TTLocalizer.GroupTrackerCantDoThatThere, command=handleWarningClose)
            return
        if not base.localAvatar.resistanceMessages:
            if self.warning is None:
                self.warning = WarningDialog.WarningDialog(parent=self, text=TTLocalizer.GroupTrackerNoJellybeanUnites, command=handleWarningClose)
            return
        allowed = 0
        for message in base.localAvatar.resistanceMessages:
            textId = message[0]
            charges = message[1]
            from toontown.chat.ResistanceChat import getMenuName
            if getMenuName(textId) == TTLocalizer.ResistanceMoneyMenu and charges > 0:
                # This is a jellybean unite, they are allowed to host a jellybean fest
                allowed = 1
        if not allowed:
            if self.warning is None:
                self.warning = WarningDialog.WarningDialog(parent=self, text=TTLocalizer.GroupTrackerNoJellybeanUnites, command=handleWarningClose)
            return
        if self.warning is None:
            self.warning = ConfirmDialog.ConfirmDialog(self, TTLocalizer.GroupTrackerJellbeanFestConfirm, commands=(handleConfirm, handleWarningClose))

    def __handleEnter(self, button, e):
        button['image_color'] = (1, 1, 0.2, 1.0)
        button['geom_color'] = (1, 1, 0.2, 1.0)

    def __handleExit(self, button, e):
        button['image_color'] = (0.5, 0.6, 1, 1)
        button['geom_color'] = (0.5, 0.6, 1, 1)
    
    def updateWantGroupButton(self, want):
        if want:
            self.wantGroupToggle['text'] = FontAwesomeGlobals.FAEyeClose
        else:
            self.wantGroupToggle['text'] = FontAwesomeGlobals.FAEyeOpen
            
    def doNothing(self):
        pass
