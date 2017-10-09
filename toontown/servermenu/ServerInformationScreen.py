from direct.gui.DirectGui import DirectFrame, DirectEntry
from toontown.toonbase import TTLocalizer
from toontown.toontowngui.TTLabel import TTLabel
from toontown.mainmenu import MainMenuGlobals
from toontown.makeatoon.MakeAToonGUI import MATShuffleButton


class ServerInformationScreen(DirectFrame):
    def __init__(self, serverMenu):
        DirectFrame.__init__(self, serverMenu)

        self.serverMenu = serverMenu
