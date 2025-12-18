from panda3d.core import CardMaker
from direct.gui.DirectGui import DirectFrame
from toontown.toonbase import TTLocalizer
from toontown.toontowngui.TTLabel import TTLabel
from toontown.makeatoon.MakeAToonGUI import MATShuffleButton
from toontown.mainmenu import MainMenuGlobals
from direct.gui.DirectGui import DGG
from toontown.toonbase.ColorGlobals import CGray
from toontown.util import TTCardMaker

class ServerMenuHomeScreen(DirectFrame):
    def __init__(self, serverMenu):
        DirectFrame.__init__(self, serverMenu)

        self.serverMenu = serverMenu

        self.lockImage = TTCardMaker.makeCard('phase_3/maps/lock_icon.png')
        self.lockImage.reparentTo(self)
        self.lockImage.setScale(0.0007, 0.0007, 0.0007)
        self.lockImage.setPos(0.35, 0, -0.79)

        self.welcomeLabel = TTLabel(
            parent=self,
            text='',
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
            wantArrows=False,
            image_scale=(-1.1, 1.1, 1.1),
            image2_scale=(-1.2, 1.2, 1.2),
            image1_scale=(-1.2, 1.2, 1.2),
            text_scale=0.08,
            text2_scale=0.085,
            text1_scale=0.085
        )

        self.serverInfoButton = MATShuffleButton(
            parent=self,
            text=TTLocalizer.ServerInformation,
            pos=(0, 0, -0.8),
            text_pos=(0, 0.02, 0),
            state=DGG.DISABLED,
            command=lambda: self.serverMenu.request('ServerInformationScreen'),
            **MainMenuGlobals.BUTTON_PROPERTIES_3
        )
        self.serverInfoButton.setColorScale(CGray)