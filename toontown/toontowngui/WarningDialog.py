from direct.gui.DirectGui import DirectFrame, OnscreenText, DirectButton, DGG
from panda3d.core import TextNode, NodePath, CardMaker, TransparencyAttrib
from toontown.toonbase import ToontownGlobals, TTLocalizer
from toontown.util import TTCardMaker


class WarningDialog(DirectFrame):
    def __init__(self, parent, text, button_text=TTLocalizer.lOK, color=(1.0, 1.0, 1.0, 1.0), scale=(1.0, 1.0, 1.0), command=None):
        self.parent = parent
        self.text = text
        self.button_text = button_text
        self.command = command

        DirectFrame.__init__(self, parent=self.parent, relief=None)

        background = TTCardMaker.makeCard('phase_3/maps/curved-gui-square.png')

        buttonModels = preloader.getModel('phase_3.5/models/gui/inventory_gui')
        upButton = buttonModels.find('**/InventoryButtonUp')
        downButton = buttonModels.find('**/InventoryButtonDown')
        rolloverButton = buttonModels.find('**/InventoryButtonRollover')

        self.mainFrame = DirectFrame(
            self.parent,
            relief=None,
            scale=scale,
            image=background,
            image_color=color,
            image_scale=(0.0004, 1, 0.00025)
        )
        self.button = DirectButton(
            self.mainFrame,
            relief=None,
            pos=(0.0, 0.0, -0.15),
            text=button_text,
            text_scale=0.05,
            text_pos=(0.0, -0.015, 0.0),
            text_font=ToontownGlobals.getInterfaceFont(),
            image=(upButton, downButton, rolloverButton),
            image_color=(0, 0.35, 1, 1),
            image_scale=(1, 1, 1),
            command=self.handleClick
        )
        self.message = OnscreenText(
            parent=self.mainFrame,
            text=self.text,
            scale=0.05,
            wordwrap=11,
            font=ToontownGlobals.getInterfaceFont(),
            align=TextNode.ACenter,
            pos=(0.0, 0.1, 0.0)
        )
        self.button.bind(DGG.WITHIN, self.__handleEnter)
        self.button.bind(DGG.WITHOUT, self.__handleExit)
        background.removeNode()

    def destroy(self):
        self.parent = None
        self.mainFrame.destroy()
        DirectFrame.destroy(self)

    def handleClick(self):
        if self.command is not None:
            self.command()
        self.destroy()

    def __handleEnter(self, e):
        self.button['image_color'] = (1, 1, 0.2, 1.0)

    def __handleExit(self, e):
        self.button['image_color'] = (0, 0.35, 1, 1.0)
