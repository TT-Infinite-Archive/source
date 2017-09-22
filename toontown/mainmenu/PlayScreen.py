from direct.fsm.FSM import FSM
from direct.interval.FunctionInterval import Func
from direct.interval.IntervalGlobal import Sequence
from direct.interval.LerpInterval import LerpPosInterval, Point3

from toontown.mainmenu import MainMenuGlobals
from toontown.makeatoon.MakeAToonGUI import MATShuffleButton
from direct.gui.DirectGui import *
from toontown.shtiker.OptionsTabPage import OptionsTabPage
from direct.interval.FunctionInterval import Wait

JOIN_START_POS = Point3(4, 0, 0.3)
JOIN_END_POS = Point3(0.35, 0, 0.3)
HOST_START_POS = Point3(4, 0, 0)
HOST_END_POS = Point3(0.35, 0, 0)
OPTIONS_START_POS = Point3(4, 0, -0.3)
OPTIONS_END_POS = Point3(0.35, 0, -0.3)
QUIT_START_POS = Point3(4, 0, -0.6)
QUIT_END_POS = Point3(0.35, 0, -0.6)


class PlayScreen(DirectFrame, FSM):

    notify = directNotify.newCategory('PlayScreen')

    def __init__(self, mainMenu):
        DirectFrame.__init__(self, mainMenu)
        FSM.__init__(self, 'PlayScreen')

        self.optionsScreen = OptionsTabPage()
        self.optionsScreen.hide()

        self.mainMenu = mainMenu
        self.buttons = []

        self.joinButton = MATShuffleButton(
            parent=self,
            text="Join",
            pos=JOIN_START_POS,
            command=lambda: self.mainMenu.request('JoinScreen'),
            **MainMenuGlobals.BUTTON_PROPERTIES_2
        )
        self.buttons.append(self.joinButton)

        self.hostButton = MATShuffleButton(
            parent=self,
            text="Host",
            pos=HOST_START_POS,
            command=lambda: self.mainMenu.request('HostScreen'),
            **MainMenuGlobals.BUTTON_PROPERTIES_2
        )
        self.buttons.append(self.hostButton)

        self.optionsButton = MATShuffleButton(
            parent=self,
            text="Options",
            pos=OPTIONS_START_POS,
            command=lambda: self.request('Options'),
            **MainMenuGlobals.BUTTON_PROPERTIES_2
        )
        self.buttons.append(self.optionsButton)

        self.quitButton = MATShuffleButton(
            parent=self,
            text="Quit",
            pos=QUIT_START_POS,
            command=self.__handleQuit,
            **MainMenuGlobals.BUTTON_PROPERTIES_2
        )
        self.buttons.append(self.quitButton)

        self.buttonPosInterval = LerpPosInterval(self.joinButton, 0.5, JOIN_END_POS, JOIN_START_POS,
                                                  blendType='easeOut')
        self.buttonPosInterval2 = LerpPosInterval(self.hostButton, 0.5, HOST_END_POS, HOST_START_POS,
                                                 blendType='easeOut')
        self.buttonPosInterval3 = LerpPosInterval(self.optionsButton, 0.5, OPTIONS_END_POS, OPTIONS_START_POS,
                                                 blendType='easeOut')
        self.buttonPosInterval4 = LerpPosInterval(self.quitButton, 0.5, QUIT_END_POS, QUIT_START_POS,
                                                  blendType='easeOut')

        self.buttonPosInterval5 = LerpPosInterval(self.joinButton, 0.5, JOIN_START_POS, JOIN_END_POS,
                                                  blendType='easeOut')
        self.buttonPosInterval6 = LerpPosInterval(self.hostButton, 0.5, HOST_START_POS, HOST_END_POS,
                                                 blendType='easeOut')
        self.buttonPosInterval7 = LerpPosInterval(self.optionsButton, 0.5, OPTIONS_START_POS, OPTIONS_END_POS,
                                                  blendType='easeOut')
        self.buttonPosInterval8 = LerpPosInterval(self.quitButton, 0.5, QUIT_START_POS, QUIT_END_POS,
                                                  blendType='easeOut')
        self.backButton = DirectButton(
            parent=base.a2dBottomLeft,
            pos=(0.12, 0, 0.10),
            command=lambda: self.enter(),
            **MainMenuGlobals.MINIATURE_BACK_BUTTON
        )
        self.backButton.hide()

    def enter(self):
        base.setAspectRatio(16./9.)
        for button in self.buttons:
            button.show()

        self.buttonSequence = Sequence(
            Func(self.buttonPosInterval.start),
            Func(self.buttonPosInterval2.start),
            Func(self.buttonPosInterval3.start),
            Func(self.buttonPosInterval4.start)
        )
        self.buttonSequence.start()
        self.mainMenu.background.hide()
        self.backButton.hide()
        self.optionsScreen.hide()

    def exit(self):
        for button in self.buttons:
            button.show()

        self.buttonSequence = Sequence(
            Func(self.buttonPosInterval5.start),
            Func(self.buttonPosInterval6.start),
            Func(self.buttonPosInterval7.start),
            Func(self.buttonPosInterval8.start)
        )
        self.buttonSequence.start()

    def enterOff(self):
        if self.optionsScreen is not None:
            self.optionsScreen.unload()
            self.optionsScreen = None

    def enterOptions(self):
        base.setAspectRatio(0)
        for button in self.buttons:
            button.hide()
        self.optionsScreen.show()
        self.backButton.show()
        self.mainMenu.background.show()

        self.joinButton.setPos(JOIN_START_POS)
        self.hostButton.setPos(HOST_START_POS)
        self.optionsButton.setPos(OPTIONS_START_POS)
        self.quitButton.setPos(QUIT_START_POS)

    def __handleQuit(self):
        cleanupDialog('globalDialog')
        base.cr.loginFSM.request('shutdown')


