import ShtikerPage
from toontown.toonbase import TTLocalizer
from toontown.toontowngui.TTLabel import TTLabel
from toontown.shtiker.CogMenu import CogMenu
from toontown.toontowngui.JarGui import JarGui


class InventoryPage(ShtikerPage.ShtikerPage):

    def __init__(self):
        ShtikerPage.ShtikerPage.__init__(self)
        self.title = None
        self.moneyDisplay = None
        self.cogMenu = None

    def load(self):
        ShtikerPage.ShtikerPage.load(self)
        self.title = TTLabel(
            parent=self,
            text=TTLocalizer.InventoryPageTitle,
            text_size=TTLabel.TitleSize,
            pos=(0, 0, 0.62)
        )
        self.moneyDisplay = JarGui(parent=self, pos=(0.6, 0.0, -0.4))
        self.cogMenu = CogMenu()
        self.cogMenu.reparentTo(self)
        self.cogMenu.setX(-0.165)
        self.cogMenu.setZ(0.63)
        self.cogMenu.setScale(0.82)
        self.cogMenu.hide()

    def unload(self):
        if self.title:
            self.title.destroy()
            self.title = None
        if self.moneyDisplay:
            self.moneyDisplay.destroy()
            self.moneyDisplay = None
        if self.cogMenu:
            self.cogMenu.cleanup()
            self.cogMenu = None
        ShtikerPage.ShtikerPage.unload(self)

    def enter(self):
        ShtikerPage.ShtikerPage.enter(self)
        base.localAvatar.gagPanel.show()
        base.localAvatar.gagPanel.reparentTo(self)
        base.localAvatar.gagPanel.ignoreOnscreenHooks()
        self.moneyDisplay.update()
        self.moneyDisplay.listen()

    def exit(self):
        self.moneyDisplay.unlisten()
        self.makePageWhite(None)
        base.localAvatar.gagPanel.hide()
        base.localAvatar.gagPanel.reparentTo(hidden)
        base.localAvatar.gagPanel.acceptOnscreenHooks()
        ShtikerPage.ShtikerPage.exit(self)
