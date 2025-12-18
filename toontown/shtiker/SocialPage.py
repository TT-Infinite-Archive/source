from panda3d.core import TextNode, Vec4
from direct.gui.DirectGui import DirectLabel, DirectButton

from toontown.shtiker.ShtikerPage import ShtikerPage
from toontown.toonbase import TTLocalizer
from .GuildPage import GuildPage
from .GroupTrackerPage import GroupTrackerPage


class SocialPage(ShtikerPage):
    notify = directNotify.newCategory('SocialPage')

    PageGuild = 0
    PageGroupTracker = 1

    def __init__(self):
        ShtikerPage.__init__(self)

        self.defaultPage = self.PageGuild

        self.guildPageTab = None
        self.groupTrackerTab = None

        self.pageContent = None
        self.title = None
        self.currentPage = self.defaultPage

    def load(self):
        gui = loader.loadModel('phase_3.5/models/gui/fishingBook.bam')

        normalColor = (1, 1, 1, 1)
        clickColor = (0.8, 0.8, 0, 1)
        rolloverColor = (0.15, 0.82, 1.0, 1)
        diabledColor = (1.0, 0.98, 0.15, 1)

        self.title = DirectLabel(
            parent=self, relief=None, text=TTLocalizer.SocialPageTitle,
            text_scale=0.12, pos=(0, 0, 0.61))

        self.guildPageTab = DirectButton(
            parent=self, relief=None, text=TTLocalizer.GuildPageTitle,
            text_scale=0.07, text_align=TextNode.ACenter,
            text_pos=(0.245, 0, 0), image=gui.find('**/tabs/polySurface1'),
            image_pos=(0.55, 1, -0.91), image_hpr=(0, 0, -90),
            image_scale=(0.033, 0.033, 0.025), image_color=normalColor,
            image1_color=clickColor, image2_color=rolloverColor,
            image3_color=diabledColor, text_fg=Vec4(0.2, 0.1, 0, 1),
            command=self.openPage, extraArgs=[self.PageGuild],
            pos=(-0.4758, 0, 0.77))

        self.groupTrackerTab = DirectButton(
            parent=self, relief=None, text=TTLocalizer.GroupTrackerPageTitle,
            text_scale=0.07, text_align=TextNode.ACenter,
            text_pos=(0.005, 0, 0), image=gui.find('**/tabs/polySurface1'),
            image_pos=(0.55, 1, -0.91), image_hpr=(0, 0, -90),
            image_scale=(0.033, 0.033, 0.045), image_color=normalColor,
            image1_color=clickColor, image2_color=rolloverColor,
            image3_color=diabledColor, text_fg=Vec4(0.2, 0.1, 0, 1),
            command=self.openPage, extraArgs=[self.PageGroupTracker],
            pos=(0.176, 0, 0.77)
        )
        gui.removeNode()


    def unload(self):
        if self.guildPageTab is not None:
            self.guildPageTab.destroy()
            self.guildPageTab = None
        if self.groupTrackerTab is not None:
            self.groupTrackerTab.destroy()
            self.groupTrackerTab = None
        if self.pageContent is not None:
            self.pageContent.destroy()
            self.pageContent = None

        ShtikerPage.unload(self)

    def enter(self):
        ShtikerPage.enter(self)
        self.openPage()

    def exit(self):
        if self.pageContent is not None:
            self.pageContent.destroy()
            self.pageContent = None
        ShtikerPage.exit(self)

    def openPage(self, page=None):
        if page is None:
            page = self.currentPage

        if self.pageContent is not None:
            self.pageContent.destroy()
            self.pageContent = None

        if page == self.PageGuild:
            self.currentPage = self.PageGuild
            self.title['text'] = TTLocalizer.GuildPageTitle
            self.pageContent = GuildPage(self)
        elif page == self.PageGroupTracker:
            self.currentPage = self.PageGroupTracker
            self.title['text'] = TTLocalizer.GroupTrackerPageTitle
            self.pageContent = GroupTrackerPage(self)
        else:
            self.notify.warning('Tried to load page %s, but it does not exist.' % page)
            self.pageContent = None
            self.currentPage = self.defaultPage
