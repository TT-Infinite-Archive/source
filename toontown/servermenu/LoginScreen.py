from toontown.toontowngui.TTLabel import TTLabel
from direct.gui.DirectGui import DirectFrame, DirectEntry
from toontown.toonbase import TTLocalizer
from toontown.mainmenu import MainMenuGlobals
from toontown.makeatoon.MakeAToonGUI import MATShuffleButton


class LoginScreen(DirectFrame):
    def __init__(self, serverMenu):
        DirectFrame.__init__(self, serverMenu)

        self.serverMenu = serverMenu

        self.usernameLabel = TTLabel(
            parent=self,
            text=TTLocalizer.Username,
            pos=(0, 0, -0.18),
            **MainMenuGlobals.LABEL_PROPERTIES
        )

        self.passwordLabel = TTLabel(
            parent=self,
            text=TTLocalizer.Password,
            pos=(0, 0, -0.48),
            **MainMenuGlobals.LABEL_PROPERTIES
        )

        self.usernameInput = DirectEntry(
            parent=self,
            pos=(0, 0, -0.60),
            width=10.5,
            **MainMenuGlobals.ENTRY_PROPERTIES
        )

        self.passwordInput = DirectEntry(
            parent=self,
            pos=(0, 0, -0.30),
            width=10.5,
            **MainMenuGlobals.ENTRY_PROPERTIES
        )

        self.logInButton = MATShuffleButton(
            parent=self,
            pos=(0, 0, -0.8),
            text=TTLocalizer.LoginScreenLogin,
            command=lambda: base.cr.loginFSM.request('login'),
            **MainMenuGlobals.BUTTON_PROPERTIES
        )
