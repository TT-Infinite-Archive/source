from direct.gui.DirectGui import DirectFrame
from toontown.mainmenu import MainMenuGlobals
from toontown.makeatoon.MakeAToonGUI import MATShuffleButton
from toontown.toontowngui.TTLabel import TTLabel
from toontown.toonbase import TTLocalizer, ToontownGlobals, ColorGlobals


class HomeScreen(DirectFrame):
    def __init__(self, mainMenu):
        DirectFrame.__init__(self, mainMenu)

        self.mainMenu = mainMenu

        self.singlePlayerButton = MATShuffleButton(
            parent=self,
            pos=(0, 0, -0.2),
            text=TTLocalizer.HomeScreenPlay,
            command=lambda: self.mainMenu.request('PlayScreen'),
            **MainMenuGlobals.BUTTON_PROPERTIES_2
        )

        self.modsButton = MATShuffleButton(
            parent=self,
            pos=(0, 0, -0.5),
            text=TTLocalizer.HomeScreenMods,
            **MainMenuGlobals.BUTTON_PROPERTIES
        )

        self.signOutButton = MATShuffleButton(
            parent=self,
            pos=(0, 0, -0.8),
            text=TTLocalizer.HomeScreenSignOut,
            command=lambda: self.mainMenu.request('ServerMenuHomeScreen'),
            **MainMenuGlobals.BUTTON_PROPERTIES_2
        )

        self.userName = TTLabel(
            parent=self,
            pos=(1.45, 0, 0.9),
            text=TTLocalizer.HomeScreenLoggedIn,
            text_fg=ColorGlobals.CBlack,
            text_font=ToontownGlobals.getToonFont(),
            text_size=TTLabel.MediumSize,
            text_wordwrap=25
        )
