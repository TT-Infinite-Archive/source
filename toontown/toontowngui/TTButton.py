from direct.gui.DirectGui import DirectButton, DGG
from panda3d.core import TextNode


class TTButton(DirectButton):
    def __init__(self, parent=aspect2d, text='', pos=(0.0, 0.0, 0.0), scale=1, active=0, command=None, extraArgs=None):
        DirectButton.__init__(self, parent)
        if extraArgs is None:
            extraArgs = []
        self.extraArgs = extraArgs

        if isinstance(scale, (int, long)):
            scale = (scale, scale, scale)

        scale = (0.7 * scale[0], 1 * scale[1], 1 * scale[2])
        guiButton = loader.loadModel('phase_3/models/gui/quit_button')
        self.active = active
        self.command = command
        self.image = (
            guiButton.find('**/QuitBtn_UP'),
            guiButton.find('**/QuitBtn_DN'),
            guiButton.find('**/QuitBtn_RLVR')
        )
        self.button = DirectButton(
            parent=self,
            relief=None,
            image=self.image,
            image_scale=scale,
            text=text,
            text_scale=0.052,
            text_pos=(0, -0.02),
            text_align=TextNode.ACenter,
            pos=pos
        )

        if command:
            self.button.bind(DGG.B1CLICK, command=self.__handleClick, extraArgs=[self.button])

        guiButton.removeNode()

    def __handleClick(self, btn, e):
        self.command(*self.extraArgs)

    def setActive(self, active):
        self.active = active
        if active:
            self.button['image'] = (self.image[2], self.image[2], self.image[2])
            self.button['state'] = DGG.DISABLED
        else:
            self.button['image'] = (self.image[0], self.image[1], self.image[2])
            self.button['state'] = DGG.NORMAL