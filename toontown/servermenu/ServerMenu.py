from panda3d.core import NodePath, TransparencyAttrib, Vec3, Vec4
from direct.fsm.FSM import FSM
from direct.gui.DirectGui import *
from direct.interval.IntervalGlobal import LerpScaleInterval
from direct.interval.MetaInterval import Sequence
from toontown.servermenu.ServerInformationScreen import ServerInformationScreen

from toontown.mainmenu import MainMenuGlobals
from toontown.makeatoon.MakeAToonGUI import MATShuffleButton
from toontown.servermenu.ServerMenuHomeScreen import ServerMenuHomeScreen
from toontown.servermenu.LoginScreen import LoginScreen
from toontown.toonbase import ToontownGlobals
from toontown.shtiker.OptionsTabPage import OptionsTabPage
from toontown.toontowngui.LocalServerStarter import LocalServerStarter
from direct.interval.FunctionInterval import Func, Wait

class ServerMenu(DirectFrame, FSM):
    notify = directNotify.newCategory('ServerMenu')

    def __init__(self):
        DirectFrame.__init__(self, parent=base.aspect2d)
        FSM.__init__(self, 'ServerMenu')

        base.setBackgroundColor(Vec4(0, 0, 0, 0))

        self.backgroundNodePath = render2d.attachNewNode('background', 0)
        self.background = OnscreenImage(
            parent=self.backgroundNodePath,
            image='phase_3.5/maps/blueprint.png'
        )
        self.background.setTransparency(TransparencyAttrib.MAlpha)
        self.background.hide()

        self.ServerMenuHomeScreen = ServerMenuHomeScreen(self)
        self.ServerMenuHomeScreen.hide()
        self.loginScreen = LoginScreen(parent=self)
        self.loginScreen.hide()
        self.ServerInformationScreen = ServerInformationScreen(self)
        self.ServerInformationScreen.hide()
        self.optionsScreen = OptionsTabPage()
        self.optionsScreen.hide()
        self.localServerStarter = LocalServerStarter()

        self.serverMenuElements = []
        if ToontownGlobals.HALLOWEEN_PROPS in base.clientHolidayIdList:
            ToontownGlobals.getNametagFont(10)
        else:
            ToontownGlobals.getMinnieFont()

        self.logo = OnscreenImage(
            parent=base.a2dTopCenter,
            image='phase_3/maps/toontown_infinite_logo.png',
            scale=(0.8, 0.35, 0.45), pos=(0, 0, -0.6)
        )
        self.logo.setTransparency(TransparencyAttrib.MAlpha)
        self.serverMenuElements.append(self.logo)

        self.logoScaleTrack = Sequence(
            LerpScaleInterval(self.logo, 4, Vec3(0.725, 0.35, 0.40), Vec3(0.70, 0.35, 0.385),
                              blendType='easeInOut'),
            LerpScaleInterval(self.logo, 4, Vec3(0.70, 0.35, 0.385), Vec3(0.725, 0.35, 0.40),
                              blendType='easeInOut')
        )
        self.logoScaleTrack.loop()
        self.bottomLeftButton = MATShuffleButton(
            parent=base.a2dBottomLeft,
            pos=(0.4, 0, 0.2),
            text="",
            **MainMenuGlobals.BUTTON_PROPERTIES
        )
        self.serverMenuElements.append(self.bottomLeftButton)

        self.optionsButton = MATShuffleButton(
            parent=base.a2dBottomRight,
            pos=(-0.4, 0, .2),
            text="Options",
            command=lambda: self.request('Options'),
            **MainMenuGlobals.BUTTON_PROPERTIES_2
        )
        self.serverMenuElements.append(self.optionsButton)

        for elements in self.serverMenuElements:
            elements.hide()

        self.connectionSuccessfulSfx = loader.loadSfx('phase_3/audio/sfx/server_menu_connection_successful.ogg')

    def destroy(self):
        if self.logoScaleTrack is not None:
            self.logoScaleTrack.finish()
            self.logoScaleTrack = None
        for element in self.serverMenuElements:
            element.destroy()
        self.backgroundNodePath.removeNode()
        self.background.removeNode()
        if self.optionsScreen is not None:
            self.optionsScreen.unload()
            self.optionsScreen = None
        taskMgr.remove('mainMenuTask')
        DirectFrame.destroy(self)

    def enterServerMenuHomeScreen(self):
        self.show()
        self.background.show()
        self.ServerMenuHomeScreen.show()

        if base.initialEntry:
            successfulConnectionSfx = base.loadSfx('phase_4/audio/sfx/MG_pairing_match_bonus_both.ogg')
            base.playSfx(successfulConnectionSfx)

        def mainMenuTask(task):
            base.initialEntry = False
            self.bottomLeftButton['command'] = lambda: base.cr.loginFSM.request('mainMenu')

        for element in self.serverMenuElements:
            element.show()

        if (base.isHosting or base.wantSinglePlayer):
            self.bottomLeftButton['text'] = "Disconnect"
        else:
            self.bottomLeftButton['text'] = "Leave Server"
        taskMgr.doMethodLater(0.1, mainMenuTask, 'mainMenuTask')
        self.bottomLeftButton['text_scale']= 0.085
        self.bottomLeftButton['text1_scale'] = 0.09
        self.bottomLeftButton['text2_scale'] = 0.09

    def exitServerMenuHomeScreen(self):
        base.initialEntry = False
        self.ServerMenuHomeScreen.hide()
        self.background.hide()

    def enterLoginScreen(self):
        self.loginScreen.show()
        self.bottomLeftButton['command'] = lambda: self.request('ServerMenuHomeScreen')
        self.bottomLeftButton['text'] = "Back"
        self.bottomLeftButton['text_scale']= 0.10
        self.bottomLeftButton['text1_scale'] = 0.105
        self.bottomLeftButton['text2_scale'] = 0.105
        self.background.show()

    def exitLoginScreen(self):
        self.loginScreen.hide()
        self.background.hide()

    def enterServerInformationScreen(self):
        self.ServerInformationScreen.show()
        self.logo.hide()
        self.bottomLeftButton['command'] = lambda: self.request('ServerMenuHomeScreen')
        self.bottomLeftButton['text'] = "Back"
        self.bottomLeftButton['text_scale']= 0.10
        self.bottomLeftButton['text1_scale'] = 0.105
        self.bottomLeftButton['text2_scale'] = 0.105
        self.background.show()

    def exitServerInformationScreen(self):
        self.ServerInformationScreen.hide()
        self.logo.show()
        self.background.hide()

    def enterOptions(self):
        self.logo.hide()
        self.optionsButton.hide()
        self.background.show()
        self.optionsScreen.show()
        self.bottomLeftButton.show()
        self.bottomLeftButton['command'] = lambda: self.request('ServerMenuHomeScreen')
        self.bottomLeftButton['text'] = "Back"
        self.bottomLeftButton['text_scale']= 0.10
        self.bottomLeftButton['text1_scale'] = 0.105
        self.bottomLeftButton['text2_scale'] = 0.105

    def exitOptions(self):
        self.logo.show()
        self.background.hide()
        self.optionsButton.show()
        self.optionsScreen.hide()
        self.bottomLeftButton.hide()
        self.bottomLeftButton['command'] = lambda: self.request('LogOut')
        self.bottomLeftButton['text'] = "Leave\nServer"

    def enterLogOut(self):
        pass

    def __handleQuit(self):
        cleanupDialog('globalDialog')
        base.cr.loginFSM.request('shutdown')