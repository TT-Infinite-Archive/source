from direct.gui.DirectGui import DirectFrame
from toontown.toonbase import TTLocalizer
from toontown.toontowngui.TTLabel import TTLabel
from toontown.makeatoon.MakeAToonGUI import MATShuffleButton
from toontown.mainmenu import MainMenuGlobals


class LoginOrSignUpScreen(DirectFrame):
    def __init__(self, mainMenu):
        DirectFrame.__init__(self, mainMenu)

        self.mainMenu = mainMenu

        self.welcomeLabel = TTLabel(
            parent=self,
            text=TTLocalizer.WelcomeMessage,
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
            command=lambda: self.mainMenu.request('LoginScreen'),
            **MainMenuGlobals.BUTTON_PROPERTIES
        )

        self.signUpButton = MATShuffleButton(
            parent=self,
            text=TTLocalizer.LoginScreenSignUp,
            pos=(0, 0, -0.8),
            command=lambda: self.mainMenu.request('SignUpScreen'),
            **MainMenuGlobals.BUTTON_PROPERTIES
        )
