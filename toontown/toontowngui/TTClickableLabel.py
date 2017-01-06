from direct.gui.DirectGui import DirectButton, DGG
from toontown.toonbase.ColorGlobals import CBlack, CGray, CLime, COrange


class TTClickableLabel(DirectButton):
    def __init__(self, parent=aspect2d, pos=(0, 0, 0), scale=1.0, text='', active=False, command=None, extraArgs=None):
        DirectButton.__init__(self, parent, relief=None)
        self.parent = parent
        self.pos = pos
        self.text = text
        self.command = command
        self.color = CBlack
        self.active = active

        if extraArgs is None:
            self.extraArgs = []
        else:
            self.extraArgs = extraArgs

        self.mainButton = DirectButton(
            self,
            relief=None,
            text=text,
            text_scale=0.07,
            text_fg=self.color,
            pos=pos,
            scale=scale
        )

        self.mainButton.bind(DGG.B1CLICK, self.__handleClick, extraArgs=[self.mainButton])
        self.mainButton.bind(DGG.WITHIN, self.__handleEnter, extraArgs=[self.mainButton])
        self.mainButton.bind(DGG.WITHOUT, self.__handleExit, extraArgs=[self.mainButton])

        if active:
            self.setActive(1)

    def setActive(self, active):
        if self.active == active:
            return
        if active:
            self.color = COrange
            self.mainButton['text_fg'] = COrange
        else:
            self.color = CBlack
            self.mainButton['text_fg'] = CBlack
        self.active = active

    def enable(self):
        self.mainButton['state'] = DGG.NORMAL
        self.mainButton['text_fg'] = self.color

    def disable(self):
        self.mainButton['state'] = DGG.DISABLED
        self.mainButton['text_fg'] = CGray

    def __handleClick(self, button, e):
        self.setActive(1)

        if self.command:
            self.command(*self.extraArgs)

    def __handleEnter(self, button, e):
        button['text_scale'] = 0.08
        button['text_fg'] = CLime

    def __handleExit(self, button, e):
        button['text_scale'] = 0.07
        button['text_fg'] = self.color



