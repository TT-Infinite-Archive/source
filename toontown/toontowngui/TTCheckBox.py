from direct.gui.DirectGui import DirectButton, DGG
from toontown.toonbase.ColorGlobals import CDefault, CGray


class TTCheckBox(DirectButton):
    def __init__(self, parent=aspect2d, pos=(0, 0, 0), checked=False, disable=False, command=None):
        DirectButton.__init__(self, parent, relief=None)
        hostingGui = preloader.getModel('phase_4/models/parties/schtickerbookHostingGUI')
        self._parent = parent
        self.checkedImage = hostingGui.find('**/checked_button')
        self.uncheckedImage = hostingGui.find('**/unchecked_button')
        self.checked = checked
        self.command = command

        if checked:
            image = (self.checkedImage, self.checkedImage, self.checkedImage)
        else:
            image = (self.uncheckedImage, self.uncheckedImage, self.uncheckedImage)

        self.checkButton = DirectButton(
            self,
            relief=None,
            pos=pos,
            image=image,
        )

        self.checkButton.bind(DGG.B1CLICK, self.__handleClick, extraArgs=[self.checkButton])
        self.checkButton.bind(DGG.WITHIN, self.__handleEnter, extraArgs=[self.checkButton])
        self.checkButton.bind(DGG.WITHOUT, self.__handleExit, extraArgs=[self.checkButton])

        if disable:
            self.disable()

    def enable(self):
        self.checkButton['state'] = DGG.NORMAL
        self.checkButton['image_color'] = CDefault

    def disable(self):
        self.checkButton['state'] = DGG.DISABLED
        self.checkButton['image_color'] = CGray

    def setChecked(self, checked):
        self.checked = checked
        if checked:
            self.checkButton['image'] = (self.checkedImage, self.checkedImage, self.checkedImage)
            self.checkButton.setImage()
        else:
            self.checkButton['image'] = (self.uncheckedImage, self.uncheckedImage, self.uncheckedImage)
            self.checkButton.setImage()

    def __handleClick(self, button, e):
        self.setChecked(not self.checked)

        if self.command:
            self.command()

    def __handleEnter(self, button, e):
        button['image_scale'] = 1.1
        button['image_color'] = (1, 1, 0.2, 1.0)

    def __handleExit(self, button, e):
        button['image_scale'] = 1.0
        button['image_color'] = (1, 1, 1.0, 1.0)
