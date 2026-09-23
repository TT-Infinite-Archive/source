from direct.gui.DirectGui import DirectLabel
from direct.directnotify.DirectNotifyGlobal import directNotify

from . import ShtikerPage
from toontown.shtiker.OptionsTabPage import OptionsTabPage
from toontown.shtiker.CodesTabPage import CodesTabPage
from toontown.shtiker.OptionsPageGlobals import ECategory
from toontown.shtiker import OptionsPageGlobals
from toontown.toonbase import TTLocalizer
from toontown.toontowngui.TTTabBar import TTTabBar


class OptionsPage(ShtikerPage.ShtikerPage):
    notify = directNotify.newCategory('OptionsPage')

    TabsZ = 0.77

    Titles = {
        ECategory.VIDEO: TTLocalizer.OptionsPageVideo,
        ECategory.SOUND: TTLocalizer.OptionsPageSound,
        ECategory.GAMEPLAY: TTLocalizer.OptionsPageGameplay,
        ECategory.SOCIAL: TTLocalizer.OptionsPageSocial,
        ECategory.CODES: TTLocalizer.CdrPageTitle
    }

    def __init__(self):
        ShtikerPage.ShtikerPage.__init__(self)

        self.mode = None
        self.optionsTabPage = None
        self.codesTabPage = None
        self.title = None
        self.tabBar = None

    def load(self):
        ShtikerPage.ShtikerPage.load(self)

        self.optionsTabPage = OptionsTabPage(self, wantTabs = False)
        self.optionsTabPage.hide()
        self.codesTabPage = CodesTabPage(self)
        self.codesTabPage.hide()

        self.title = DirectLabel(
            parent=self, relief=None, text=TTLocalizer.OptionsPageTitle,
            text_scale=0.12, pos=(0, 0, 0.61))

        self.tabBar = TTTabBar(
            self,
            tabs=OptionsPageGlobals.Categories + ((ECategory.CODES, TTLocalizer.OptionsPageCodesTab),),
            pos=(0, 0, self.TabsZ),
            command=self.setMode)

    def enter(self):
        self.setMode(ECategory.VIDEO, updateAnyways=1)

        ShtikerPage.ShtikerPage.enter(self)

    def exit(self):
        self.mode = None
        self.optionsTabPage.exit()
        self.codesTabPage.exit()

        ShtikerPage.ShtikerPage.exit(self)

    def unload(self):
        if self.optionsTabPage is not None:
            self.optionsTabPage.unload()
            self.optionsTabPage = None

        if self.codesTabPage is not None:
            self.codesTabPage.unload()
            self.codesTabPage = None

        if self.title is not None:
            self.title.destroy()
            self.title = None

        if self.tabBar is not None:
            self.tabBar.destroy()
            self.tabBar = None

        ShtikerPage.ShtikerPage.unload(self)

    def setMode(self, mode, updateAnyways=0):
        messenger.send('wakeup')

        if not updateAnyways:
            if self.mode == mode:
                return

        previous = self.mode
        self.mode = mode
        self.title['text'] = self.Titles[mode]
        self.tabBar.setActive(mode)

        if mode == ECategory.CODES:
            if previous is not None:
                self.optionsTabPage.exit()
            self.codesTabPage.enter()
        else:
            if previous == ECategory.CODES:
                self.codesTabPage.exit()
            if previous is None or previous == ECategory.CODES:
                self.optionsTabPage.enter()
            self.optionsTabPage.setOptionsState(mode)
