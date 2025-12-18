from panda3d.core import CardMaker, TextNode
from direct.gui.DirectGui import DirectFrame, OnscreenText, DirectButton, DGG
from toontown.toonbase import ToontownGlobals, TTLocalizer
from toontown.util import TTCardMaker


class ConfirmDialog(DirectFrame):
    def __init__(self, parent=aspect2d, text=TTLocalizer.AreYouSure, buttonTexts=(TTLocalizer.lYes, TTLocalizer.lCancel), color=(1.0, 1.0, 1.0, 0.95), scale=(1.0, 1.0, 1.0), commands=(None, None)):
        self._parent = parent
        self.text = text
        self.buttonTexts = buttonTexts
        self.commands = commands

        DirectFrame.__init__(self, parent=self._parent, relief=None)

        buttonModels = preloader.getModel('phase_3.5/models/gui/inventory_gui')
        upButton = buttonModels.find('**/InventoryButtonUp')
        downButton = buttonModels.find('**/InventoryButtonDown')
        rolloverButton = buttonModels.find('**/InventoryButtonRollover')

        background = TTCardMaker.makeCard('phase_3/maps/curved-gui-square.png')

        self.mainFrame = DirectFrame(
            self._parent,
            relief=None,
            scale=scale,
            image=background,
            image_color=color,
            image_scale=(0.0004, 1, 0.00025)
        )
        self.okButton = DirectButton(
            self.mainFrame,
            relief=None,
            pos=(-0.15, 0.0, -0.15),
            text=buttonTexts[0],
            text_scale=0.05,
            text_pos=(0.0, -0.015, 0.0),
            text_font=ToontownGlobals.getInterfaceFont(),
            image=(upButton, downButton, rolloverButton),
            image_color=(0, 0.35, 1, 1),
            image_scale=(1, 1, 1),
        )
        self.cancelButton = DirectButton(
            self.mainFrame,
            relief=None,
            pos=(0.15, 0.0, -0.15),
            text=buttonTexts[1],
            text_scale=0.05,
            text_pos=(0.0, -0.015, 0.0),
            text_font=ToontownGlobals.getInterfaceFont(),
            image=(upButton, downButton, rolloverButton),
            image_color=(0, 0.35, 1, 1),
            image_scale=(1, 1, 1),
        )

        self.okButton.bind(DGG.B1CLICK, self.__handleClick, extraArgs=[self.okButton])
        self.okButton.bind(DGG.WITHIN, self.__handleEnter, extraArgs=[self.okButton])
        self.okButton.bind(DGG.WITHOUT, self.__handleExit, extraArgs=[self.okButton])

        self.cancelButton.bind(DGG.B1CLICK, self.__handleClick, extraArgs=[self.cancelButton])
        self.cancelButton.bind(DGG.WITHIN, self.__handleEnter, extraArgs=[self.cancelButton])
        self.cancelButton.bind(DGG.WITHOUT, self.__handleExit, extraArgs=[self.cancelButton])

        self.message = OnscreenText(parent=self.mainFrame, text=self.text, scale=0.05, wordwrap=11, align=TextNode.ACenter, pos=(0.0, 0.1, 0.0), font=ToontownGlobals.getInterfaceFont())

        background.removeNode()

    def destroy(self):
        self._parent = None

        self.mainFrame.destroy()
        DirectFrame.destroy(self)

    def __handleClick(self, button, e):
        if self.commands[0] is not None and button == self.okButton:
            self.commands[0]()
        elif self.commands[1] is not None and button == self.cancelButton:
            self.commands[1]()
        self.destroy()

    def __handleEnter(self, button, e):
        button['image_color'] = (1, 1, 0.2, 1.0)

    def __handleExit(self, button, e):
        button['image_color'] = (0, 0.35, 1, 1.0)


