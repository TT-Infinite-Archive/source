from direct.gui.DirectGui import DGG, DirectLabel
from direct.directnotify.DirectNotifyGlobal import directNotify

import ShtikerPage
from toontown.shtiker.OptionsTabPage import OptionsTabPage
from toontown.shtiker.CodesTabPage import CodesTabPage
from toontown.shtiker.OptionsPageGUI import OptionTab
from toontown.shtiker import OptionsPageGlobals
from toontown.toonbase import TTLocalizer


class OptionsPage(ShtikerPage.ShtikerPage):
    notify = directNotify.newCategory('OptionsPage')

    def __init__(self):
        ShtikerPage.ShtikerPage.__init__(self)

        self.optionsTabPage = None
        self.codesTabPage = None
        self.title = None
        self.optionsTab = None
        self.codesTab = None

    def load(self):
        ShtikerPage.ShtikerPage.load(self)

        self.optionsTabPage = OptionsTabPage(self)
        self.optionsTabPage.hide()
        self.codesTabPage = CodesTabPage(self)
        self.codesTabPage.hide()

        self.title = DirectLabel(
            parent=self, relief=None, text=TTLocalizer.OptionsPageTitle,
            text_scale=0.12, pos=(0, 0, 0.61))

        self.optionsTab = OptionTab(
            parent=self, tabType=1, text=TTLocalizer.OptionsPageTitle, text_scale=TTLocalizer.OPoptionsTab,
            text_pos=(0.01, 0.0, 0.0), image_pos=(0.55, 1, -0.91), pos=(-0.4, 0, 0.77),
            command=self.setMode, extraArgs=[OptionsPageGlobals.PageMode.Options])

        self.codesTab = OptionTab(
            parent=self, text=TTLocalizer.OptionsPageCodesTab, text_scale=TTLocalizer.OPoptionsTab,
            text_pos=(-0.035, 0.0, 0.0), image_pos=(0.12, 1, -0.91), pos=(0.2, 0, 0.77),
            command=self.setMode, extraArgs=[OptionsPageGlobals.PageMode.Codes])

    def enter(self):
        self.setMode(OptionsPageGlobals.PageMode.Options, updateAnyways=1)

        ShtikerPage.ShtikerPage.enter(self)

    def exit(self):
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

        if self.optionsTab is not None:
            self.optionsTab.destroy()
            self.optionsTab = None

        if self.codesTab is not None:
            self.codesTab.destroy()
            self.codesTab = None

        ShtikerPage.ShtikerPage.unload(self)

    def setMode(self, mode, updateAnyways=0):
        messenger.send('wakeup')

        if not updateAnyways:
            if self.mode == mode:
                return

        self.mode = mode

        if mode == OptionsPageGlobals.PageMode.Options:
            self.title['text'] = TTLocalizer.OptionsPageTitle
            self.optionsTab['state'] = DGG.DISABLED
            self.optionsTabPage.enter()
            self.codesTab['state'] = DGG.NORMAL
            self.codesTabPage.exit()
        elif mode == OptionsPageGlobals.PageMode.Codes:
            self.title['text'] = TTLocalizer.CdrPageTitle
            self.optionsTab['state'] = DGG.NORMAL
            self.optionsTabPage.exit()
            self.codesTab['state'] = DGG.DISABLED
            self.codesTabPage.enter()
        else:
            self.notify.warning('Invalid mode for options page %s' % mode)
