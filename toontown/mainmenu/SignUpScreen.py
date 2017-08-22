from direct.gui.DirectGui import DirectFrame, DirectEntry
from toontown.toonbase import TTLocalizer
from toontown.toontowngui.TTLabel import TTLabel
from toontown.mainmenu import MainMenuGlobals
from toontown.makeatoon.MakeAToonGUI import MATShuffleButton


class SignUpScreen(DirectFrame):
    def __init__(self, mainMenu):
        DirectFrame.__init__(self, mainMenu)

        self.mainMenu = mainMenu

        self.usernameLabel = TTLabel(
            parent=self,
            text=TTLocalizer.Username,
            pos=(0, 0, 0.62),
            **MainMenuGlobals.LABEL_PROPERTIES
        )

        self.passwordLabel = TTLabel(
            parent=self,
            text=TTLocalizer.Password,
            pos=(0, 0, 0.32),
            **MainMenuGlobals.LABEL_PROPERTIES
        )

        self.birthdayLabel = TTLabel(
            parent=self,
            text=TTLocalizer.Birthday,
            pos=(0, 0, 0.03),
            **MainMenuGlobals.LABEL_PROPERTIES
        )

        self.emailLabel = TTLabel(
            parent=self,
            text=TTLocalizer.Email,
            pos=(0, 0, -0.28),
            **MainMenuGlobals.LABEL_PROPERTIES
        )

        self.warningLabel = TTLabel(
            parent=self,
            text=TTLocalizer.SignUpWarning,
            pos=(0, 0, -0.54),
            **MainMenuGlobals.LABEL_PROPERTIES
        )

        self.usernameInput = DirectEntry(
            parent=self,
            pos=(0, 0, 0.50),
            width=10.5,
            **MainMenuGlobals.ENTRY_PROPERTIES
        )

        self.passwordInput = DirectEntry(
            parent=self,
            pos=(0, 0, 0.20),
            width=10.5,
            **MainMenuGlobals.ENTRY_PROPERTIES
        )

        self.emailInput = DirectEntry(
            parent=self,
            pos=(0, 0, -0.40),
            width=10.5,
            **MainMenuGlobals.ENTRY_PROPERTIES
        )

        self.yearInput = DirectEntry(
            parent=self,
            pos=(0.31, 0, -0.10),
            width=3,
            **MainMenuGlobals.ENTRY_PROPERTIES
        )
        self.yearInput.enterText(TTLocalizer.SignUpYear)

        self.dayInput = DirectEntry(
            parent=self,
            pos=(0, 0, -0.10),
            width=3,
            **MainMenuGlobals.ENTRY_PROPERTIES
        )
        self.dayInput.enterText(TTLocalizer.SignUpDay)

        self.monthInput = DirectEntry(
            parent=self,
            pos=(-0.31, 0, -0.10),
            width=3,
            **MainMenuGlobals.ENTRY_PROPERTIES
        )
        self.monthInput.enterText(TTLocalizer.SignUpMonth)

        self.signUpButton = MATShuffleButton(
            parent=self,
            pos=(-0.5, 0, -0.8),
            text=TTLocalizer.LoginScreenSignUp,
            command=lambda: self.mainMenu.request(''),
            **MainMenuGlobals.BUTTON_PROPERTIES
        )

        self.termsButton = MATShuffleButton(
            parent=self,
            pos=(0.5, 0, -0.8),
            text=TTLocalizer.SignUpTermsOfService,
            text_pos=(0, 0.02, 0),
            wantArrows=False,
            image_scale=(-1.1, 1.1, 1.1),
            image2_scale=(-1.2, 1.2, 1.2),
            image1_scale=(-1.2, 1.2, 1.2),
            text_scale=0.08,
            text2_scale=0.095,
            text1_scale=0.095,
            command=lambda: self.mainMenu.request('')
        )
