from direct.gui.DirectGui import DirectFrame, OnscreenText, DirectButton, DGG
from panda3d.core import TextNode, NodePath, CardMaker, TransparencyAttrib
from toontown.toonbase import ToontownGlobals, TTLocalizer


class ConfirmDialog(DirectFrame):
    def __init__(self, parent=aspect2d, text=TTLocalizer.AreYouSure, buttonTexts=(TTLocalizer.lYes, TTLocalizer.lCancel), color=(1.0, 1.0, 1.0, 0.95), scale=(1.0, 1.0, 1.0), commands=(None, None)):
        self.parent = parent
        self.text = text
        self.buttonTexts = buttonTexts
        self.commands = commands

        DirectFrame.__init__(self, parent=self.parent, relief=None)

        filepath = 'phase_3/maps/curved-gui-square.png'
        tex = loader.loadTexture(filepath)
        cm = CardMaker(filepath + ' card')
        cm.setFrame(-tex.getOrigFileXSize(), tex.getOrigFileXSize(), -tex.getOrigFileYSize(), tex.getOrigFileYSize())

        buttonModels = preloader.getModel('phase_3.5/models/gui/inventory_gui')
        upButton = buttonModels.find('**/InventoryButtonUp')
        downButton = buttonModels.find('**/InventoryButtonDown')
        rolloverButton = buttonModels.find('**/InventoryButtonRollover')

        background = NodePath(cm.generate())
        background.setTexture(tex)
        background.setTransparency(TransparencyAttrib.MAlpha)

        self.mainFrame = DirectFrame(
            self.parent,
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
        self.parent = None

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


