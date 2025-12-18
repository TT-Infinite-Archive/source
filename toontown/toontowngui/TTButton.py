from panda3d.core import TextNode
from direct.gui.DirectGui import DirectButton, DGG
from toontown.toonbase.ColorGlobals import CGray, CDefault


class TTButton(DirectButton):
    def __init__(self, parent=aspect2d, text='', pos=(0.0, 0.0, 0.0), textScale=0.052, buttonScale=1, active=0, disable=False, command=None, extraArgs=None):
        DirectButton.__init__(self, parent)
        if extraArgs is None:
            extraArgs = []
        self.extraArgs = extraArgs

        if isinstance(buttonScale, (int, float)):
            buttonScale = (buttonScale, buttonScale, buttonScale)

        buttonScale = (0.7 * buttonScale[0], 1 * buttonScale[1], 1 * buttonScale[2])
        guiButton = loader.loadModel('phase_3/models/gui/quit_button')
        self.active = active
        self.command = command
        self.image = (
            guiButton.find('**/QuitBtn_UP'),
            guiButton.find('**/QuitBtn_DN'),
            guiButton.find('**/QuitBtn_RLVR')
        )
        guiButton.removeNode()
        self.button = DirectButton(
            parent=self,
            relief=None,
            image=self.image,
            image_scale=buttonScale,
            text=text,
            text_scale=textScale,
            text_pos=(0, -0.02),
            text_align=TextNode.ACenter,
            pos=pos
        )

        if command:
            self.button.bind(DGG.B1CLICK, command=self.__handleClick, extraArgs=[self.button])

        if disable:
            self.disable()

    def __handleClick(self, btn, e):
        self.command(*self.extraArgs)

    def enable(self):
        self.button['state'] = DGG.NORMAL
        self.button['image_color'] = CDefault

    def disable(self):
        self.button['state'] = DGG.DISABLED
        self.button['image_color'] = CGray

    def setActive(self, active):
        self.active = active
        if active:
            self.button['image'] = (self.image[2], self.image[2], self.image[2])
            self.button['state'] = DGG.DISABLED
        else:
            self.button['image'] = (self.image[0], self.image[1], self.image[2])
            self.button['state'] = DGG.NORMAL