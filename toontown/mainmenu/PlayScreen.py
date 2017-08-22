import random
from direct.task import Task
from direct.gui.DirectGui import DirectFrame
from toontown.mainmenu import MainMenuGlobals
from toontown.toonbase import TTLocalizer
from panda3d.core import TransparencyAttrib
from pandac.PandaModules import CompassEffect, NodePath
from toontown.makeatoon.MakeAToonGUI import MATShuffleButton
from direct.interval.LerpInterval import LerpPosInterval, Point3
from direct.interval.IntervalGlobal import Sequence, Parallel
from direct.interval.FunctionInterval import Func, Wait


JOIN_START_POS = Point3(4, 0, 0.1)
JOIN_END_POS = Point3(0.35, 0, 0.1)
HOST_START_POS = Point3(4, 0, -0.2)
HOST_END_POS = Point3(0.35, 0, -0.2)
BACK_START_POS = Point3(4, 0, -0.5)
BACK_END_POS = Point3(0.35, 0, -0.5)


class PlayScreen(DirectFrame):
    def __init__(self, mainMenu):
        DirectFrame.__init__(self, mainMenu)

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

        self.backButton = MATShuffleButton(
            parent=self,
            text=TTLocalizer.OptionsGoBack,
            pos=(BACK_START_POS),
            command=lambda: self.mainMenu.request('HomeScreen'),
            **MainMenuGlobals.BUTTON_PROPERTIES_2
        )
        self.buttons.append(self.backButton)

        self.buttonPosInterval = LerpPosInterval(self.joinButton, 0.5, JOIN_END_POS, JOIN_START_POS,
                                                  blendType='easeOut')
        self.buttonPosInterval2 = LerpPosInterval(self.hostButton, 0.5, HOST_END_POS, HOST_START_POS,
                                                 blendType='easeOut')
        self.buttonPosInterval3 = LerpPosInterval(self.backButton, 0.5, BACK_END_POS, BACK_START_POS,
                                                  blendType='easeOut')

        self.buttonPosInterval4 = LerpPosInterval(self.joinButton, 0.5, JOIN_START_POS, JOIN_END_POS,
                                                  blendType='easeOut')
        self.buttonPosInterval5 = LerpPosInterval(self.hostButton, 0.5, HOST_START_POS, HOST_END_POS,
                                                 blendType='easeOut')
        self.buttonPosInterval6 = LerpPosInterval(self.backButton, 0.5, BACK_START_POS, BACK_END_POS,
                                                  blendType='easeOut')

    def enter(self):
        for button in self.buttons:
            button.show()

        self.buttonSequence = Sequence(
            Func(self.buttonPosInterval.start),
            Func(self.buttonPosInterval2.start),
            Func(self.buttonPosInterval3.start)
        )
        self.buttonSequence.start()

    def exit(self):
        for button in self.buttons:
            button.show()

        self.buttonSequence = Sequence(
            Func(self.buttonPosInterval4.start),
            Func(self.buttonPosInterval5.start),
            Func(self.buttonPosInterval6.start),
        )
        self.buttonSequence.start()


