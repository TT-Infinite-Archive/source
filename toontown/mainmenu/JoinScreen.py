from direct.gui.DirectGui import DirectFrame
from panda3d.core import Point3
from direct.interval.IntervalGlobal import Sequence, Parallel, Func, Wait
from toontown.makeatoon.MakeAToonGUI import MATShuffleButton
from toontown.toonbase import TTLocalizer, ToontownGlobals
from toontown.mainmenu import MainMenuGlobals
from toontown.util.PlacerTool3D import PlacerTool3D
from panda3d.core import TextNode
from direct.gui.DirectGui import DirectFrame, DirectEntry, DGG, DirectButton
from direct.fsm.FSM import FSM

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

        self.backButton = MATShuffleButton(
            parent=self,
            text=TTLocalizer.OptionsGoBack,
            command=lambda: self.request('Back'),
            **MainMenuGlobals.BUTTON_PROPERTIES_2
        )
        self.backButton.hide()

        self.connectButton = MATShuffleButton(
            parent=self,
            pos=(-0.35, 0, -0.75),
            text="Connect",
            command=self.__submitIP,
            **MainMenuGlobals.BUTTON_PROPERTIES
        )
        self.connectButton.hide()

        self.serverBrowserButton = MATShuffleButton(
            parent=self,
            text="Server\nBrowser",
            pos=(4, 0, -0.3),
            text_pos=(0, 0.02, 0),
            command=lambda: self.mainMenu.request('DirectConnect'),
            **MainMenuGlobals.BUTTON_PROPERTIES_3
        )
        self.serverBrowserButton.hide()

        self.enterPosInterval = camera.posInterval(2, Point3(CAMENDPOS), startPos=Point3(CAMSTARTPOS))
        self.enterHprInterval = camera.hprInterval(2, Point3(CAMENDHPR), startHpr=Point3(CAMSTARTHPR))

        self.enterPosInterval2 = camera.posInterval(2, Point3(CAMPOS2), startPos=Point3(CAMENDPOS))

        self.exitPosInterval = camera.posInterval(2, Point3(CAMSTARTPOS), startPos=Point3(CAMENDPOS))
        self.exitHprInterval = camera.hprInterval(2, Point3(CAMSTARTHPR), startHpr=Point3(CAMENDHPR))

        self.door = loader.loadModel('phase_3.5/models/modules/doors_practical')
        self.door.reparentTo(render)
        self.door.setPosHpr(-392.2, -247, 4, -175, 0, 0)

        self.leftDoor = self.door.find('**/door_double_square_ur_left')
        self.rightDoor = self.door.find('**/door_double_square_ur_right')

        self.leftDoorOpenInterval = self.leftDoor.hprInterval(2, Point3(-90, 0, 0), startHpr=Point3(0, 0, 0))
        self.rightDoorOpenInterval = self.rightDoor.hprInterval(2, Point3(90, 0, 0), startHpr=Point3(0, 0, 0))

        self.leftDoorCloseInterval = self.leftDoor.hprInterval(2, Point3(0, 0, 0), startHpr=Point3(-90, 0, 0))
        self.rightDoorCloseInterval = self.rightDoor.hprInterval(2, Point3(0, 0, 0), startHpr=Point3(90, 0, 0))

        self.buildingInterior = loader.loadModel('phase_5.5/models/estate/tt_m_ara_int_estateHouseC')
        self.buildingInterior.reparentTo(render)
        self.buildingInterior.setPosHpr(-388.5, -307, -20, 185, 0, 0)

        # PlacerTool3D(self.buildingInterior, increment=1)

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

        # Load the image for the ip input bar for Multiplayer
        cdrGui = loader.loadModel('phase_3.5/models/gui/tt_m_gui_sbk_codeRedemptionGui')

        # Load the ip input bar
        self.ipInput = DirectEntry(
            parent=self,
            relief=DGG.GROOVE,
            scale=0.1,
            pos=(0, 0, -0.50),
            borderWidth=(0.05, 0.05),
            frameColor=((1, 1, 1, 1),
                        (1, 1, 1, 1),
                        (0.5, 0.5, 0.5, 0.5)),
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
            autoCapitalize=0,
            command=self.__submitIP)
        self.ipInput.hide()

        # self.arrow = loader.loadModel('phase_3/models/props/arrow')
        # self.arrow.reparentTo(hidden)
        # self.arrow.setPos(-401.5, -308, -14.4)

    def enter(self):
        # PlacerTool3D(self.arrow, increment=1)
        # base.oobe()
        # PlacerTool3D(self.backButton, increment=1)
        # base.camera.setPosHpr(-401.5, -308, -14.4, 305, 0, 0)
        # self.showDirectConnect()
        # self.connectButton.show()
        # self.backButton.show()
        # self.serverBrowserButton.show()
        # base.oobe()
        # base.camLens.setFov(55)
        Sequence(
            Parallel(
                self.enterPosInterval,
                self.enterHprInterval),
            Parallel(
                Func(base.transitions.fadeOut, 2),
                self.enterPosInterval2,
                self.leftDoorOpenInterval,
                self.rightDoorOpenInterval),
            Wait(1),
            Func(base.camLens.setFov, 55),
            Func(self.showDirectConnect),
            Func(self.connectButton.show),
            Func(self.serverBrowserButton.show),
            Func(self.backButton.show),
            Func(base.transitions.fadeIn, 1)).start()

        # base.camera.setPosHpr(-400, -193, 6.6, 192, 0, 0)
        # PlacerTool3D(camera, increment=1)

    def enterBack(self):
        Sequence(
            Func(base.transitions.fadeOut, 2),
            Func(base.camLens.setFov, 30),
            Wait(2),
            Func(base.transitions.fadeOut, 0),
            Func(self.hideDirectConnect),
            Func(self.connectButton.hide),
            Func(self.serverBrowserButton.hide),
            Func(self.backButton.hide),
            Parallel(
                Func(base.transitions.fadeIn, 2),
                self.exitPosInterval,
                self.exitHprInterval,
                self.leftDoorCloseInterval,
                self.rightDoorCloseInterval),
            Func(self.mainMenu.request, 'PlayScreen')).start()

    def exit(self):
        self.hideDirectConnect()
        self.connectButton.hide()
        self.serverBrowserButton.hide()
        self.backButton.hide()

    def showDirectConnect(self):
        self.ipInput.show()
        self.__enableIPEntry()
        self.ipInput.enterText('')
        self.ipInput.setTransparency(1)
       #  self.connectButton.show()
        # self.addToBookmarksButton.show()

    def hideDirectConnect(self):
        self.ipInput.hide()
        self.__disableIPEntry()
        # self.connectButton.hide()
        # self.addToBookmarksButton.hide()

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
        self.mainMenu.request('StartDirectConnect')

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
            self.serverNameInput = DirectEntry(
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
            self.serverNameInput.setTransparency(1)

        def addToBookmarks(self):
            if hasattr(self, 'ipInput'):
                if self.ipInput.get() == '':
                    return
                try: # This wants to crash so i'll do this for now
                    if self.serverNameInput.get() == '':
                        if self.ipInput != '':
                            self.name = self.ipInput.get()
                        else:
                            return
                except:
                    return
                name = self.serverNameInput.get()
                address = self.ipInput.get()
                resp = self.bookmarkMgr.addBookmark(address, name)
                if resp == 1:
                    base.showNotification("Bookmark added! (IP: %s, Name: %s)" %(self.ipInput.get(), self.serverNameInput.get()))
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
                base.showNotification("Bookmark removed! (IP: %s, Name: %s)" %(address, name))
            elif resp == 2:
                base.showNotification("Error: A bookmark for %s doesn't exist, so it can't be deleted!" %address)
            else:
                base.showNotification("Error: Unknown error removing bookmark! Please report this to the developers!")

                def __submitIP(self, input=None):
                    if input is None:
                        input = self.ipInput.get()
                        self.ipInput['focus'] = 1

                    if input == '':
                        return
                    self.targetIp = input
                    messenger.send('wakeup')
                    self.request('StartDirectConnect')