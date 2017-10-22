from direct.fsm.FSM import FSM
from direct.gui.DirectGui import *
from direct.interval.FunctionInterval import Func
from direct.interval.FunctionInterval import Wait
from direct.interval.IntervalGlobal import LerpScaleInterval
from direct.interval.IntervalGlobal import Sequence
from direct.interval.LerpInterval import LerpPosInterval
from pandac.PandaModules import *

from toontown.mainmenu import MainMenuGlobals
from toontown.makeatoon.MakeAToonGUI import MATShuffleButton
from toontown.shtiker.OptionsTabPage import OptionsTabPage
from toontown.util.PlacerTool3D import PlacerTool3D

JOIN_START_POS = Point3(4, 0, 0.3)
JOIN_END_POS = Point3(0.35, 0, 0.3)
HOST_START_POS = Point3(4, 0, 0)
HOST_END_POS = Point3(0.35, 0, 0)
OPTIONS_START_POS = Point3(4, 0, -0.3)
OPTIONS_END_POS = Point3(0.35, 0, -0.3)
QUIT_START_POS = Point3(4, 0, -0.6)
QUIT_END_POS = Point3(0.35, 0, -0.6)
TTI_SERVER_START_POS = Point3(4, 0, -0.15)
TTI_SERVER_END_POS = Point3(1.35, 0, -0.15)
TTI_ICON_START_POS = (4, 0, 0.35)
TTI_ICON_END_POS = (1.3, 0, 0.35)


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
            command=lambda: self.showOptions(),
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

        self.ttiServerButton = MATShuffleButton(
            parent=self,
            text="Join the\nOfficial Server",
            pos=TTI_SERVER_START_POS,
            text_pos=(0, 0.02, 0),
            command=lambda: base.connectToServer('toontowninfinite.com'),
            wantArrows=False,
            image_scale=(-1.4, 1.4, 1.4),
            image2_scale=(-1.5, 1.5, 1.5),
            image1_scale=(-1.5, 1.5, 1.5),
            text_scale=0.10,
            text2_scale=0.105,
            text1_scale=0.105
        )
        self.buttons.append(self.ttiServerButton)

        self.icon = OnscreenImage(
            parent=self,
            image='phase_3/maps/toontown_infinite_icon.png',
            scale=(0.8, 0.35, 0.45), pos=TTI_ICON_START_POS, hpr=(55, 0, 0)
        )
        self.icon.setTransparency(TransparencyAttrib.MAlpha)

        self.iconScaleTrack = Sequence(
            LerpScaleInterval(self.icon, 4, Vec3(0.725, 0.35, 0.40), Vec3(0.70, 0.35, 0.385),
                              blendType='easeInOut'),
            LerpScaleInterval(self.icon, 4, Vec3(0.70, 0.35, 0.385), Vec3(0.725, 0.35, 0.40),
                              blendType='easeInOut')
        )

        self.buttonPosInterval = LerpPosInterval(self.joinButton, 0.5, JOIN_END_POS, JOIN_START_POS,
                                                  blendType='easeOut')
        self.buttonPosInterval2 = LerpPosInterval(self.hostButton, 0.5, HOST_END_POS, HOST_START_POS,
                                                 blendType='easeOut')
        self.buttonPosInterval3 = LerpPosInterval(self.optionsButton, 0.5, OPTIONS_END_POS, OPTIONS_START_POS,
                                                 blendType='easeOut')
        self.buttonPosInterval4 = LerpPosInterval(self.quitButton, 0.5, QUIT_END_POS, QUIT_START_POS,
                                                  blendType='easeOut')
        self.buttonPosInterval5 = LerpPosInterval(self.ttiServerButton, 0.5, TTI_SERVER_END_POS, TTI_SERVER_START_POS,
                                                  blendType='easeOut')

        self.buttonPosInterval6 = LerpPosInterval(self.joinButton, 0.5, JOIN_START_POS, JOIN_END_POS,
                                                  blendType='easeOut')
        self.buttonPosInterval7 = LerpPosInterval(self.hostButton, 0.5, HOST_START_POS, HOST_END_POS,
                                                 blendType='easeOut')
        self.buttonPosInterval8 = LerpPosInterval(self.optionsButton, 0.5, OPTIONS_START_POS, OPTIONS_END_POS,
                                                  blendType='easeOut')
        self.buttonPosInterval9 = LerpPosInterval(self.quitButton, 0.5, QUIT_START_POS, QUIT_END_POS,
                                                  blendType='easeOut')
        self.buttonPosInterval10 = LerpPosInterval(self.ttiServerButton, 0.5, TTI_SERVER_START_POS, TTI_SERVER_END_POS,
                                                  blendType='easeOut')

        self.ttiIconPosInterval = LerpPosInterval(self.icon, 0.5, TTI_ICON_END_POS, TTI_ICON_START_POS,
                                                  blendType='easeOut')
        self.ttiIconPosInterval2 = LerpPosInterval(self.icon, 0.5, TTI_ICON_START_POS, TTI_ICON_END_POS,
                                                  blendType='easeOut')

        self.backButton = DirectButton(
            parent=base.a2dBottomLeft,
            pos=(0.12, 0, 0.10),
            command=lambda: self.hideOptions(),
            **MainMenuGlobals.MINIATURE_BACK_BUTTON
        )
        self.backButton.hide()

    def enter(self):
        base.setAspectRatio(16./8.5)
        self.mainMenu.background.hide()
        self.icon.show()
        self.mainMenu.environment.reparentTo(render)

        if base.initialEntry:
            Sequence(
                Func(self.mainMenu.randomToon.play, 'neutral'),
                Wait(1),
                Func(self.mainMenu.randomToon.play, 'wave'),
                Wait(4.3),
                Func(self.mainMenu.randomToon.play, 'bored'),
                Wait(2.9),
                Func(self.mainMenu.randomToon.pingpong, 'bored', fromFrame=70, toFrame=130)).start()

        if (base.cr.music is None) and base.musicManagerIsValid:
            if not base.wantClassicMusic:
                base.cr.music = base.musicManager.getSound('phase_3.5/audio/bgm/TC_SZ.ogg')
            else:
                base.cr.music = base.musicManager.getSound('phase_3.5/audio/bgm/TC_SZ_og.ogg')
            if base.cr.music is not None:
                base.cr.music.setLoop(1)
                base.cr.music.setVolume(0.9)
                base.cr.music.play()

        def showButtons():
            for button in self.buttons:
                button.show()

        self.buttonSequence = Sequence(
            Func(self.buttonPosInterval.start),
            Func(self.buttonPosInterval2.start),
            Func(self.buttonPosInterval3.start),
            Func(self.buttonPosInterval4.start),
            Func(self.buttonPosInterval5.start),
            Func(self.ttiIconPosInterval.start),
            Func(self.iconScaleTrack.loop))
        self.buttonSequence.start()

        if base.initialEntry:
            base.transitions.fadeIn(2)

        base.camera.setPosHpr(-454.5, -96, 2.7, 215, 0, 0)
        base.camLens.setFov(30)
        showButtons()

    def exit(self):
        base.initialEntry = False
        for button in self.buttons:
            button.show()

        self.buttonSequence2 = Sequence(
            Func(self.iconScaleTrack.finish),
            Func(self.buttonPosInterval6.start),
            Func(self.buttonPosInterval7.start),
            Func(self.buttonPosInterval8.start),
            Func(self.buttonPosInterval9.start),
            Func(self.buttonPosInterval10.start),
            Func(self.ttiIconPosInterval2.start))
        self.buttonSequence2.start()

    def showOptions(self):
        base.initialEntry = False
        base.setAspectRatio(0)
        for button in self.buttons:
            button.hide()
        self.iconScaleTrack.finish()
        self.icon.hide()
        self.optionsScreen.show()
        self.backButton.show()
        self.mainMenu.background.show()

        self.joinButton.setPos(JOIN_START_POS)
        self.hostButton.setPos(HOST_START_POS)
        self.optionsButton.setPos(OPTIONS_START_POS)
        self.quitButton.setPos(QUIT_START_POS)
        self.ttiServerButton.setPos(TTI_SERVER_START_POS)
        self.icon.setPos(TTI_ICON_START_POS)

    def hideOptions(self):
        self.optionsScreen.hide()
        self.backButton.hide()
        self.mainMenu.background.hide()
        self.enter()

    def __handleQuit(self):
        cleanupDialog('globalDialog')
        base.cr.loginFSM.request('shutdown')


