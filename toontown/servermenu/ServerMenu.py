from direct.fsm.FSM import FSM
from direct.gui.DirectGui import *
from direct.interval.IntervalGlobal import LerpScaleInterval
from direct.interval.MetaInterval import Sequence
from pandac.PandaModules import *
from toontown.servermenu.SignUpScreen import SignUpScreen

from toontown.mainmenu import MainMenuGlobals
from toontown.makeatoon.MakeAToonGUI import MATShuffleButton
from toontown.servermenu.LoginOrSignUpScreen import LoginOrSignUpScreen
from toontown.servermenu.LoginScreen import LoginScreen
from toontown.toonbase import ToontownGlobals


class ServerMenu(DirectFrame, FSM):
    notify = directNotify.newCategory('ServerMenu')

    def __init__(self):
        DirectFrame.__init__(self, parent=base.aspect2d)
        FSM.__init__(self, 'ServerMenu')

        self.loginOrSignUpScreen = LoginOrSignUpScreen(self)
        self.loginOrSignUpScreen.hide()
        self.loginScreen = LoginScreen(parent=self)
        self.loginScreen.hide()
        self.signUpScreen = SignUpScreen(self)
        self.signUpScreen.hide()

        self.mainMenuElements = []
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
        self.mainMenuElements.append(self.logo)

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
            text="Options",
            **MainMenuGlobals.BUTTON_PROPERTIES_2
        )
        self.mainMenuElements.append(self.bottomLeftButton)

        self.quitButton = MATShuffleButton(
            parent=base.a2dBottomRight,
            pos=(-0.4, 0, .2),
            text="Quit",
            # command=self.__handleQuit,
            **MainMenuGlobals.BUTTON_PROPERTIES_2
        )
        self.mainMenuElements.append(self.quitButton)

        for elements in self.mainMenuElements:
            elements.hide()

        self.flyDownSfx = loader.loadSfx('phase_5/audio/sfx/ENC_propeller_in.ogg')
        self.flyDownSfx.setVolume(0)

    def destroy(self):
        if self.logoScaleTrack is not None:
            self.logoScaleTrack.finish()
            self.logoScaleTrack = None
        for element in self.mainMenuElements:
            element.destroy()
        DirectFrame.destroy(self)

    def enterOff(self):
        if self.optionsScreen is not None:
            self.optionsScreen.unload()
            self.optionsScreen = None

    def enterLoginOrSignUpScreen(self):
        self.show()
        self.loginOrSignUpScreen.show()

        for element in self.mainMenuElements:
            element.show()

        self.bottomLeftButton['command'] = lambda: self.request('Options')
        self.bottomLeftButton['text'] = "Options"

        if (base.cr.music is None) and base.musicManagerIsValid:
            base.cr.music = base.musicManager.getSound('phase_3/audio/bgm/tti_main_menu_theme.ogg')
            if base.cr.music is not None:
                base.cr.music.setLoop(1)
                base.cr.music.setVolume(0.9)
                base.cr.music.play()

    def exitLoginOrSignUpScreen(self):
        self.loginOrSignUpScreen.hide()

    def enterLoginScreen(self):
        self.loginScreen.show()
        self.bottomLeftButton['command'] = lambda: self.request('LoginOrSignUpScreen')
        self.bottomLeftButton['text'] = "Back"

    def exitLoginScreen(self):
        self.loginScreen.hide()

    def enterSignUpScreen(self):
        self.signUpScreen.show()
        self.logo.hide()
        self.bottomLeftButton['command'] = lambda: self.request('LoginOrSignUpScreen')
        self.bottomLeftButton['text'] = "Back"

    def exitSignUpScreen(self):
        self.signUpScreen.hide()
        self.logo.show()

    def enterOptions(self):
        self.optionsScreen.show()
        self.bottomLeftButton.show()
        self.bottomLeftButton['command'] = lambda: self.request('LoginOrSignUpScreen')
        self.bottomLeftButton['text'] = "Back"

    def exitOptions(self):
        self.optionsScreen.hide()
        self.bottomLeftButton.hide()
        self.bottomLeftButton['command'] = lambda: self.request('Options')
        self.bottomLeftButton['text'] = "Options"