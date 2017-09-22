from direct.fsm.FSM import FSM
from direct.gui import DirectGuiGlobals
from direct.gui.DirectGui import DirectFrame, DirectEntry, DGG, DirectButton
from direct.gui.DirectGui import DirectLabel
from direct.gui.OnscreenImage import OnscreenImage
from direct.interval.IntervalGlobal import Sequence, Parallel, Func, Wait
from direct.interval.LerpInterval import LerpFunc
from panda3d.core import Point3
from panda3d.core import TextNode
from pandac.PandaModules import Vec3

from toontown.mainmenu import MainMenuGlobals
from toontown.makeatoon.MakeAToonGUI import MATShuffleButton
from toontown.serverbrowser.BookmarkManager import BookmarkManager
from toontown.toonbase import TTLocalizer, ToontownGlobals
from toontown.toonbase.DirectScrolledList import DirectScrolledList
from toontown.toontowngui import TTDialog
from toontown.toontowngui import TTTooltip
from toontown.util.PlacerTool3D import PlacerTool3D


class JoinScreen(DirectFrame, FSM):
    def __init__(self, mainMenu):
        DirectFrame.__init__(self, mainMenu)
        FSM.__init__(self, 'JoinScreen')

        CAMSTARTPOS = (-454.5, -96, 2.7)
        CAMENDPOS = (-399, -193, 6.6)
        CAMPOS2 = (-393, -245, 8.6)
        CAMSTARTHPR = (215, 0, 0)
        CAMENDHPR = (189, 0, 0)

        self.mainMenu = mainMenu
        self.serverBrowserElements = []
        self.bookmarkInfoDialog = None
        self.bookmarkMgr = BookmarkManager()

        self.backButton = DirectButton(
            parent=base.a2dBottomLeft,
            command=lambda: self.request('Back'),
            **MainMenuGlobals.MINIATURE_BACK_BUTTON
        )
        self.backButton.hide()

        self.connectButton = MATShuffleButton(
            parent=self,
            pos=(-0.35, 0, -0.29),
            text="Connect",
            command=self.__submitIP,
            **MainMenuGlobals.BUTTON_PROPERTIES
        )
        self.connectButton.hide()

        self.addToBookmarksButton = MATShuffleButton(
            parent=self,
            pos=(0.35, 0, -0.30),
            text="Bookmark",
            command=self.createBookmark,
            **MainMenuGlobals.BUTTON_PROPERTIES
        )
        self.addToBookmarksButton.hide()

        self.joinButton = DirectButton(
            parent=self,
            pos=(0.91, 0, 0.47),
            command=lambda: self.mainMenu.request(''),
            text_align = TextNode.ARight,
            **MainMenuGlobals.START_BUTTON
        )
        self.serverBrowserElements.append(self.joinButton)

        gui = preloader.getModel('phase_3/models/gui/pick_a_toon_gui.bam')
        if gui is not None:
            gui2 = preloader.getModel('phase_3/models/gui/quit_button.bam')
            newGui = preloader.getModel(
                'phase_3/models/gui/tt_m_gui_pat_mainGui.bam')
        else:
            gui = loader.loadModel('phase_3/models/gui/pick_a_toon_gui.bam')
            gui2 = loader.loadModel('phase_3/models/gui/quit_button.bam')
            newGui = loader.loadModel(
                'phase_3/models/gui/tt_m_gui_pat_mainGui.bam')

        quitHover = gui.find('**/QuitBtn_RLVR')

        self.ipConnectButton = DirectButton(
            image=(quitHover, quitHover, quitHover), relief=None,
            text='IP Connect',
            text_font=ToontownGlobals.getSignFont(),
            text_fg=(0.977, 0.816, 0.133, 1),
            text_pos=(0, -0.015),
            text_scale=TTLocalizer.ACleaveButton, image_scale=1,
            image1_scale=1.05, image2_scale=1.05, scale=1.05,
            pos=(-0.55, 0, -0.935),
            command=self.showIPConnect)
        self.ipConnectButton.hide()

        self.bookmarksButton = DirectButton(
            image=(quitHover, quitHover, quitHover), relief=None,
            text='Bookmarks',
            text_font=ToontownGlobals.getSignFont(),
            text_fg=(0.977, 0.816, 0.133, 1),
            text_pos=(0, -0.015),
            text_scale=TTLocalizer.ACleaveButton, image_scale=1,
            image1_scale=1.05, image2_scale=1.05, scale=1.05,
            pos=(0.55, 0, -0.935),
            command=self.showBookmarks)
        self.bookmarksButton.hide()

        self.serverNameLabel = DirectLabel(parent=self, relief=None, text='Server Name', pos=(-0.9, 0, 0.6), text_fg=(1, 1, 1, 1),
                                   text_font=ToontownGlobals.getToonFont(), text_scale=0.09, text_wordwrap=25)
        self.serverBrowserElements.append(self.serverNameLabel)

        self.gameModeLabel = DirectLabel(parent=self, relief=None, text='Game Mode', pos=(-0.2, 0, 0.6), text_fg=(1, 1, 1, 1),
                                   text_font=ToontownGlobals.getToonFont(), text_scale=0.09, text_wordwrap=25)
        self.serverBrowserElements.append(self.gameModeLabel)

        self.playersLabel = DirectLabel(parent=self, relief=None, text='Players', pos=(0.4, 0, 0.6), text_fg=(1, 1, 1, 1),
                                   text_font=ToontownGlobals.getToonFont(), text_scale=0.09, text_wordwrap=25)
        self.serverBrowserElements.append(self.playersLabel)

        self.connectLabel = DirectLabel(parent=self, relief=None, text='Connect', pos=(0.9, 0, 0.6), text_fg=(1, 1, 1, 1),
                                   text_font=ToontownGlobals.getToonFont(), text_scale=0.09, text_wordwrap=25)
        self.serverBrowserElements.append(self.connectLabel)
        
        self.ipConnectLabel = DirectLabel(parent=self, relief=None, text='Enter an IP Address', pos=(0, 0, 0.3), text_fg=(1, 1, 1, 1),
                                   text_font=ToontownGlobals.getToonFont(), text_scale=0.12, text_wordwrap=25)
        self.ipConnectLabel.hide()

        for button in self.serverBrowserElements:
            button.hide()

        self.fetchingLabel = DirectLabel(parent=self, relief=None, text='Fetching Servers.', text_fg=(1, 1, 1, 1),
                                   text_font=ToontownGlobals.getToonFont(), text_scale=0.09, text_wordwrap=25)
        self.fetchingLabel.hide()

        self.fetchingLabel2 = DirectLabel(parent=self, relief=None, text='Fetching Servers..', text_fg=(1, 1, 1, 1),
                                   text_font=ToontownGlobals.getToonFont(), text_scale=0.09, text_wordwrap=25)
        self.fetchingLabel2.hide()

        self.fetchingLabel3 = DirectLabel(parent=self, relief=None, text='Fetching Servers...', text_fg=(1, 1, 1, 1),
                                   text_font=ToontownGlobals.getToonFont(), text_scale=0.09, text_wordwrap=25)
        self.fetchingLabel3.hide()

        self.noServers = DirectLabel(parent=self, relief=None, text='No Servers Found.', pos=(0.9, 0, 0.7), text_fg=(1, 1, 1, 1),
                                   text_font=ToontownGlobals.getToonFont(), text_scale=0.09, text_wordwrap=25)
        self.noServers.hide()

        self.enterPosInterval = camera.posInterval(2, Point3(CAMENDPOS), startPos=Point3(CAMSTARTPOS), blendType = 'easeIn') 
        self.enterHprInterval = camera.hprInterval(2, Point3(CAMENDHPR), startHpr=Point3(CAMSTARTHPR), blendType = 'easeIn')

        self.enterPosInterval2 = camera.posInterval(2, Point3(CAMPOS2), startPos=Point3(CAMENDPOS), blendType = 'easeOut')

        self.exitPosInterval = camera.posInterval(2, Point3(CAMSTARTPOS), startPos=Point3(CAMENDPOS), blendType = 'easeInOut') 
        self.exitHprInterval = camera.hprInterval(2, Point3(CAMSTARTHPR), startHpr=Point3(CAMENDHPR), blendType = 'easeInOut')

        self.interiorFovZoomIn = LerpFunc(base.camLens.setFov, 1, 50, 35, 'easeOut', [], "zoom")
        self.interiorFovZoomOut = LerpFunc(base.camLens.setFov, 1, 35, 50, 'easeOut', [], "zoom")

        self.door = loader.loadModel('phase_3.5/models/modules/doors_practical')
        self.door.reparentTo(render)
        self.door.setPosHpr(-392.2, -247, 4, -175, 0, 0)

        self.leftDoor = self.door.find('**/door_double_square_ur_left')
        self.rightDoor = self.door.find('**/door_double_square_ur_right')

        self.leftDoorOpenInterval = self.leftDoor.hprInterval(2, Point3(-90, 0, 0), startHpr=Point3(0, 0, 0))
        self.rightDoorOpenInterval = self.rightDoor.hprInterval(2, Point3(90, 0, 0), startHpr=Point3(0, 0, 0))

        self.leftDoorCloseInterval = self.leftDoor.hprInterval(2, Point3(0, 0, 0), startHpr=Point3(-90, 0, 0))
        self.rightDoorCloseInterval = self.rightDoor.hprInterval(2, Point3(0, 0, 0), startHpr=Point3(90, 0, 0))

        self.fetchingSequence = Sequence(
            Parallel(
                Func(self.fetchingLabel3.hide),
                Func(self.fetchingLabel.show)),
            Wait(0.7),
            Parallel(
                Func(self.fetchingLabel.hide),
                Func(self.fetchingLabel2.show)),
            Wait(0.7),
            Parallel(
                Func(self.fetchingLabel2.hide),
                Func(self.fetchingLabel3.show)),
            Wait(0.7)
        )

        self.buildingInterior = loader.loadModel('phase_3.5/models/modules/HQ_interior')
        self.buildingInterior.reparentTo(render)
        self.buildingInterior.setPos(-374.5, -293, -25)

        # Our Door
        # self.door.find('**/door_double_square_ur').removeNode()

        # self.door.find('**/door_double_square_ur_flat').hide()

        # flat stays hidden during door animation, but the problem is, it hides the door's border too

        self.door.find('**/door_double_pillars').removeNode()
        self.door.find('**/door_double_square_ul').removeNode()
        self.door.find('**/door_double_curved').removeNode()
        self.door.find('**/door_double_round').removeNode()
        self.door.find('**/door_double_clothshop').removeNode()
        self.door.find('**/door_skyler_round').removeNode()

        cdrGui = loader.loadModel('phase_3.5/models/gui/tt_m_gui_sbk_codeRedemptionGui')

        self.ipInput = DirectEntry(parent=self, relief=DGG.GROOVE, scale=0.1,
            pos=(0, 0, 0), borderWidth=(0.05, 0.05),
            frameColor=((1, 1, 1, 0), (1, 1, 1, 0), (0.5, 0.5, 0.5, 0)),
            image = "phase_3/maps/input_box.png", image_scale = (4.6, 0, 1),
            image_pos = (0, 0, .2), state=DGG.NORMAL, text_align=TextNode.ACenter,
            text_scale=TTLocalizer.OPCodesInputTextScale, width=10.5, numLines=1,
            focus=1, backgroundFocus=0, cursorKeys=1, text_fg=(0, 0, 0, 1),
            suppressMouse=1, autoCapitalize=0, command=self.__submitIP)
        self.ipInput.setTransparency(1)
        self.ipInput.hide()

        self.bookmarksBackground = OnscreenImage(
            parent=render2d, image='phase_3.5/maps/big_book.jpg', pos=(0, 0, 0))
        self.bookmarksBackground.setBin('background', 0)
        self.bookmarksBackground.setScale(render2d, Vec3(1))
        self.bookmarksBackground.hide()

        bookmarkGUI = loader.loadModel('phase_3.5/models/gui/friendslist_gui')

        if not hasattr(self, 'bookmarksList'):
            self.bookmarksList = DirectScrolledList(
                parent=self, decButton_pos=(0, 0, 0.9),
                decButton_image=(bookmarkGUI.find('**/FndsLst_ScrollUp'),
                                 bookmarkGUI.find('**/FndsLst_ScrollDN'),
                                 bookmarkGUI.find('**/FndsLst_ScrollUp_Rllvr'),
                                 bookmarkGUI.find('**/FndsLst_ScrollUp')),
                decButton_relief=None, decButton_scale=(1.5, 1.5, 1.5),
                incButton_pos=(0, 0, -0.9),
                incButton_image=(bookmarkGUI.find('**/FndsLst_ScrollUp'),
                                 bookmarkGUI.find('**/FndsLst_ScrollDN'),
                                 bookmarkGUI.find('**/FndsLst_ScrollUp_Rllvr'),
                                 bookmarkGUI.find('**/FndsLst_ScrollUp')),
                incButton_relief=None, incButton_scale=(1.5, 1.5, -1.5),
                items=[], numItemsVisible=16, forceHeight=.096,
                itemFrame_frameSize=(-.6, .6, -1.5, .1),
                itemFrame_pos=(0, 0, .7),
                itemFrame_frameColor=(0.85, 0.95, 1, 1)
                )
            self.bookmarksList.setPos(0.8, 0, 0)
            self.bookmarksList.hide()

        self.bookOpenSfx = loader.loadSfx('phase_3.5/audio/sfx/GUI_stickerbook_open.ogg')
        self.bookCloseSfx = loader.loadSfx('phase_3.5/audio/sfx/GUI_stickerbook_delete.ogg')

    def enter(self):
        Sequence(
            Parallel(
                self.enterPosInterval,
                self.enterHprInterval),
            Parallel(
                Func(base.transitions.fadeOut, 1),
                self.enterPosInterval2,
                self.leftDoorOpenInterval,
                self.rightDoorOpenInterval),
            Wait(1),
            Parallel(
                Func(base.camera.setH, 186),
                Func(base.transitions.fadeIn, 1),
                Func(base.camera.setPosHpr, -380, -263, -16.6, 90, 0, 0),
                self.interiorFovZoomIn),
            Parallel(
                Func(self.ipConnectButton.show),
                Func(self.bookmarksButton.show),
                Func(self.fetchServers))).start()
        self.bookCloseSfx.setVolume(0)

    def enterBack(self):
        Sequence(
            Parallel(
                self.interiorFovZoomOut,
                Func(base.transitions.fadeOut, 1),
                Func(self.backButton.hide),
                Func(self.ipConnectButton.hide),
                Func(self.bookmarksButton.hide),
                Func(self.finishFetchingServers)),
            Wait(0.5),
            Func(base.transitions.fadeOut, 0),
            Func(base.camLens.setFov, 30),
            Parallel(
                Func(base.transitions.fadeIn, 1),
                self.exitPosInterval,
                self.exitHprInterval,
                self.leftDoorCloseInterval,
                self.rightDoorCloseInterval),
            Func(self.mainMenu.request, 'PlayScreen')).start()

    def exit(self):
        self.hideIPConnect()
        self.connectButton.hide()
        self.backButton.hide()
        self.ipConnectButton.hide()
        self.bookmarksButton.hide()
        self.hideServerBrowser()
        self.finishFetchingServers()

    def fetchServers(self):
        self.fetchingSequence.loop()

        self.hideBookmarks()
        self.hideIPConnect()
        self.backButton.setPos(0.12, 0, 0.10)
        self.backButton.show()
        self.backButton['command'] = lambda: self.request('Back')

        # Fetch Servers here:

        # Finish server fetching:
        # self.finishFetchingServers()

    def finishFetchingServers(self):
        # When fetching is complete, finish the sequence:
        self.fetchingSequence.finish()
        self.fetchingLabel.hide()
        self.fetchingLabel2.hide()
        self.fetchingLabel3.hide()

        # If servers are found, show browser: self.showServerBrowser()

        # else

        # If servers aren't found, say so:
        # No servers found.
        # Refresh button: self.fetchServers()

    def showServerBrowser(self):
        self.showServerBrowserElements()

        # Display found servers here:

    def hideServerBrowser(self):
        self.hideServerBrowserElements()

    def showServerBrowserElements(self):
        for button in self.serverBrowserElements:
            button.show()

    def hideServerBrowserElements(self):
        for button in self.serverBrowserElements:
            button.hide()

    def showIPConnect(self):
        self.finishFetchingServers()
        self.ipInput.show()
        self.__enableIPEntry()
        self.ipInput.enterText('')
        self.connectButton.show()
        self.addToBookmarksButton.show()
        self.ipConnectButton.hide()
        self.bookmarksButton.hide()
        self.ipConnectLabel.show()
        self.bookCloseSfx.setVolume(0)
        self.mainMenu.background.show()
        self.backButton['command'] = lambda: self.fetchServers()

    def hideIPConnect(self):
        self.ipInput.hide()
        self.__disableIPEntry()
        self.connectButton.hide()
        self.addToBookmarksButton.hide()
        self.ipConnectLabel.hide()
        self.mainMenu.background.hide()
        self.backButton.hide()

    def showBookmarks(self):
        self.finishFetchingServers()
        self.bookOpenSfx.play()
        self.bookmarksList.show()
        self.makeBookmarksButtons()
        self.bookmarksBackground.show()
        self.ipConnectButton.hide()
        self.bookmarksButton.hide()
        self.bookCloseSfx.setVolume(1)
        self.backButton['command'] = lambda: self.fetchServers()
        # self.backButton.setPos(0.32, 0, 0.14)
        self.backButton.show()

    def hideBookmarks(self):
        self.bookmarksList.hide()
        self.bookOpenSfx.stop()
        self.bookCloseSfx.play()
        self.bookmarksBackground.hide()
        self.ipConnectButton.show()
        self.bookmarksButton.show()
        self.backButton.hide()
        if self.bookmarkInfoDialog:
            self.bookmarkInfoDialog.hide()

    def __enableIPEntry(self):
        self.ipInput['state'] = DGG.NORMAL
        self.ipInput['focus'] = 1

    def __disableIPEntry(self):
        self.ipInput['state'] = DGG.DISABLED

    def __submitIP(self, input=None):
        if input is None:
            input = self.ipInput.get()
            self.ipInput['focus'] = 1

        if input == '':
            return
        self.targetIp = input
        messenger.send('wakeup')
        self.request('StartIPConnect')

    def enterStartIPConnect(self):
        base.isHosting = False
        self.backButton.hide()
        if not hasattr(self, 'targetIp'):
            ip = self.joinScreen.ipInput.get()
        else:
            ip = self.targetIp
        if ':' in ip:
            ip, port = ip.split(':')
            try:
                port = int(port)
            except:
                # TODO: Better handle invalid addresses
                port = 7000
            base.connectToServer(ip, port)
        else:
            base.connectToServer(ip)

    def makeBookmarksButtons(self):
        self.bookmarksList.removeAllItems()
        bookmarks = self.bookmarkMgr.getBookmarks()
        for bookmark in bookmarks:
            address = bookmark
            name = bookmarks.get(address)
            button = DirectButton(
                relief = None,
                text="%s" %(name),
                text_scale = 0.082,
                text2_scale = 0.087,
                text1_scale = 0.087,
                text_fg = (0, 0, 0, 1),
                command = self.showBookmarkInfo,
                extraArgs = [name, address])
            button.bind(DirectGuiGlobals.ENTER, self.showTooltip, extraArgs = ["Name: %s\nAddress: %s" %(name, address)])
            button.bind(DirectGuiGlobals.EXIT, self.killTooltip)

            self.bookmarksList.addItem(button)

    def createBookmark(self):
        if self.ipInput.get() == '':
            return
        def done():
            if self.addToBookmarksDialog.doneStatus == 'ok':
                self.addToBookmarks()
            self.addToBookmarksDialog.hide()
            base.transitions.noFade()
        self.addToBookmarksDialog = TTDialog.TTGlobalDialog(
                    dialogName='AddToBookmarkDialog', doneEvent='addBookmark', style=TTDialog.TwoChoice,
                    text="Choose a name for this bookmark", text_wordwrap=24,
                    text_pos=(0, 0), suppressKeys = True, suppressMouse = True
                )
        base.transitions.fadeScreen(.5)
        scale = self.addToBookmarksDialog.component('image0').getScale()
        scale.setX(((scale[0] * 2.5) / base.getAspectRatio()) * 1.2)
        scale.setZ(scale[2] * 2.5)
        self.addToBookmarksDialog.component('image0').setScale(scale)
        self.addToBookmarksDialog.accept('addBookmark', done)
        self.serverNameLabelInput = DirectEntry(
            parent=self.addToBookmarksDialog,
            relief=DGG.GROOVE,
            scale=0.1,
            pos=(0, 0, 0.2),
            borderWidth=(0.05, 0.05),
            frameColor=((1, 1, 1, 0),
                        (1, 1, 1, 0),
                        (0.5, 0.5, 0.5, 0)),
            image = "phase_3/maps/input_box.png",
            image_scale = (4.6, 0, 1),
            image_pos = (0, 0, .2),
            state=DGG.NORMAL,
            text_align=TextNode.ACenter,
            text_scale=TTLocalizer.OPCodesInputTextScale,
            width=10.5,
            numLines=1,
            focus=1,
            backgroundFocus=0,
            cursorKeys=1,
            text_fg=(0,
                     0,
                     0,
                     1),
            suppressMouse=1,
            autoCapitalize=0)
        self.serverNameLabelInput.setTransparency(1)

    def showBookmarkInfo(self, name, address):
        buttonScale = (-1.1, 1.1, 1.1)
        buttonScale_clickhover = (-1.2, 1.2, 1.2)
        if self.bookmarkInfoDialog:
            self.bookmarkInfoDialog.removeNode()
            self.bookmarkInfoDialog = None
        def done():
            self.bookmarkInfoDialog.hide()
            self.__submitIP(address)

        if not self.bookmarkInfoDialog:

            self.bookmarkInfoDialog = self.attachNewNode('bookmarkInfoDialog')
            self.bookmarkInfoDialog.setPos(-0.8, 0, 0)

            infoTitle = DirectLabel(relief = None, parent = self.bookmarkInfoDialog, pos = (0, 0, 0.5),
                                    text_align = TextNode.ACenter, text_font = ToontownGlobals.getToonFont(),
                                    text_scale = 0.1, text_wordwrap = 25, text = "Bookmark Information")
            nameLabel = DirectLabel(relief = None, parent = self.bookmarkInfoDialog, pos = (-.5, 0, 0.2),
                                    text_fg = (0, 0, 0, 1), text_align = TextNode.ALeft,
                                    text_font = ToontownGlobals.getToonFont(), text_scale = 0.06,
                                    text_wordwrap = 25, text = "\1candidate_inactive\1Name:\2 %s" %name)
            addressLabel = DirectLabel(relief = None, parent = self.bookmarkInfoDialog, pos = (-.5, 0, 0.1),
                                       text_fg = (0, 0, 0, 1), text_align = TextNode.ALeft,
                                       text_font = ToontownGlobals.getToonFont(), text_scale = 0.06,
                                       text_wordwrap = 25, text = "\1candidate_inactive\1Address:\2 %s" %address)
            connectButton = MATShuffleButton(parent = self.bookmarkInfoDialog, pos=(0, 0, -0.3), text="Connect", wantArrows=False,
            image_scale=buttonScale, image2_scale=buttonScale_clickhover,
            image1_scale=buttonScale_clickhover, text_scale=0.082, text2_scale=0.087,
            text1_scale=0.087, command=done)

            trashcanGui = loader.loadModel('phase_3/models/gui/trashcan_gui.bam')
            deleteButton = DirectButton(parent = self.bookmarkInfoDialog,
                geom = (trashcanGui.find('**/TrashCan_CLSD'),
                    trashcanGui.find('**/TrashCan_OPEN'),
                    trashcanGui.find('**/TrashCan_RLVR')),
                text = ('',
                    TTLocalizer.AvatarChoiceDelete,
                    TTLocalizer.AvatarChoiceDelete,
                    ''),
                text_fg = (1, 1, 1, 1),
                text_shadow = (0, 0, 0, 1),
                text_scale = 0.15,
                text_pos = (0, -0.1),
                relief = None,
                scale = .4,
                command = self.deleteFromBookmarks,
                extraArgs = [name, address],
                pos = (.4, 0, -.3))

            deleteButton.bind(DirectGuiGlobals.ENTER, self.showTooltip, extraArgs = ["This will PERMENANTLY delete this bookmark. This action is not reversable!"])
            deleteButton.bind(DirectGuiGlobals.EXIT, self.killTooltip)

    def addToBookmarks(self):
        if hasattr(self, 'ipInput'):
            if self.ipInput.get() == '':
                return
            try: # This wants to crash so i'll do this for now
                if self.serverNameLabelInput.get() == '':
                    if self.ipInput != '':
                        self.name = self.ipInput.get()
                    else:
                        return
            except:
                return
            name = self.serverNameLabelInput.get()
            address = self.ipInput.get()
            resp = self.bookmarkMgr.addBookmark(address, name)
            if resp == 1:
                base.showNotification("Bookmark added! (IP: %s, Name: %s)" %(self.ipInput.get(), self.serverNameLabelInput.get()))
            elif resp == 2:
                base.showNotification("Error: A bookmark for the IP %s already exists!" %self.ipInput.get())
            elif resp == 3:
                base.showNotification("Error: Please specify an IP!")
            else:
                base.showNotification("Error: Unknown error adding bookmark! Please report this to the developers!")

    def deleteFromBookmarks(self, name, address):
        if self.bookmarkInfoDialog:
            self.bookmarkInfoDialog.hide()
        resp = self.bookmarkMgr.removeBookmark(address)
        if resp == 1:
            base.showNotification("Bookmark removed! (IP: %s, Name: %s)" % (address, name))
        elif resp == 2:
            base.showNotification("Error: A bookmark for %s doesn't exist, so it can't be deleted!" % address)
        else:
            base.showNotification(
                "Error: Unknown error removing bookmark! Please report this to the developers!")
        self.makeBookmarksButtons()

    def showTooltip(self, text, event):
        self.currentTooltip = TTTooltip.TTTooltip(description = text)

    def killTooltip(self, event):
        if hasattr(self, 'currentTooltip'):
            self.currentTooltip.destroy()

    def destroyModels(self):
        self.door.removeNode()
        self.buildingInterior.removeNode()
        self.bookmarksBackground.removeNode()