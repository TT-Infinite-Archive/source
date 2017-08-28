from direct.gui.DirectGui import DirectFrame
from toontown.toonbase import TTLocalizer
from toontown.toontowngui.TTLabel import TTLabel
from toontown.makeatoon.MakeAToonGUI import MATShuffleButton
from toontown.mainmenu import MainMenuGlobals
from panda3d.core import URLSpec


class LoginOrSignUpScreen(DirectFrame):
    def __init__(self, serverMenu):
        DirectFrame.__init__(self, serverMenu)

        self.serverMenu = serverMenu
        self.welcomeLabel = TTLabel(
            parent=self,
            text=TTLocalizer.WelcomeMessage % 'GAMESERVER',
            pos=(0, 0, -0.13),
            **MainMenuGlobals.LABEL_PROPERTIES
        )

        self.LoginScreenGreetingLabel = TTLabel(
            parent=self,
            text=TTLocalizer.LoginScreenGreeting,
            text_scale=0.05,
            pos=(0, 0, -0.23),
            **MainMenuGlobals.LABEL_PROPERTIES
        )

        self.LoginScreenGreetingLabel2 = TTLabel(
            parent=self,
            text=TTLocalizer.LoginScreenGreeting2,
            text_scale=0.05,
            pos=(0, 0, -0.31),
            **MainMenuGlobals.LABEL_PROPERTIES
        )

        self.logInButton = MATShuffleButton(
            parent=self,
            text=TTLocalizer.LoginScreenLogin,
            pos=(0, 0, -0.5),
            command=lambda: self.serverMenu.request('LoginScreen'),
            **MainMenuGlobals.BUTTON_PROPERTIES
        )

        self.signUpButton = MATShuffleButton(
            parent=self,
            text=TTLocalizer.LoginScreenSignUp,
            pos=(0, 0, -0.8),
            command=lambda: self.serverMenu.request('SignUpScreen'),
            **MainMenuGlobals.BUTTON_PROPERTIES
        )