from panda3d.core import TextNode, Vec4
from direct.directnotify import DirectNotifyGlobal
from direct.gui.DirectGui import *
from toontown.toonbase import TTLocalizer, EventGlobals
from toontown.fishing import FishPicker
from toontown.fishing import FishBrowser
from toontown.fishing import FishGlobals
from toontown.shtiker import ShtikerPage
FishPage_Tank = 0
FishPage_Collection = 1


class FishPage(ShtikerPage.ShtikerPage):
    notify = DirectNotifyGlobal.directNotify.newCategory('FishPage')

    def __init__(self):
        ShtikerPage.ShtikerPage.__init__(self)
        self.avatar = None
        self.mode = FishPage_Tank

    def enter(self):
        if not hasattr(self, 'title'):
            self.load()
        self.setMode(self.mode, 1)
        self.accept(localAvatar.uniqueName('fishTankChange'), self.updatePage)
        ShtikerPage.ShtikerPage.enter(self)

    def exit(self):
        if hasattr(self, 'picker'):
            self.picker.hide()
        if hasattr(self, 'browser'):
            self.browser.hide()
        self.ignore(localAvatar.uniqueName('fishTankChange'))
        ShtikerPage.ShtikerPage.exit(self)

    def setAvatar(self, av):
        self.avatar = av

    def getAvatar(self):
        return self.avatar

    def load(self):
        ShtikerPage.ShtikerPage.load(self)
        gui = loader.loadModel('phase_3.5/models/gui/fishingBook')
        rodFrame = gui.find('**/bucket/fram1')
        rodFrame.removeNode()
        self.title = DirectLabel(parent=self, relief=None, text='', text_scale=0.1, pos=(0, 0, 0.65))
        normalColor = (1, 1, 1, 1)
        clickColor = (0.8, 0.8, 0, 1)
        rolloverColor = (0.15, 0.82, 1.0, 1)
        diabledColor = (1.0, 0.98, 0.15, 1)
        self.tankTab = DirectButton(parent=self, relief=None, text=TTLocalizer.FishPageTankTab, text_scale=TTLocalizer.FPtankTab, text_align=TextNode.ALeft, image=gui.find('**/tabs/polySurface1'), image_pos=(0.55, 1, -0.91), image_hpr=(0, 0, -90), image_scale=(0.033, 0.033, 0.035), image_color=normalColor, image1_color=clickColor, image2_color=rolloverColor, image3_color=diabledColor, text_fg=Vec4(0.2, 0.1, 0, 1), command=self.setMode, extraArgs=[FishPage_Tank], pos=(0.92, 0, 0.55))
        self.collectionTab = DirectButton(parent=self, relief=None, text=TTLocalizer.FishPageCollectionTab, text_scale=TTLocalizer.FPcollectionTab, text_align=TextNode.ALeft, image=gui.find('**/tabs/polySurface2'), image_pos=(0.12, 1, -0.91), image_hpr=(0, 0, -90), image_scale=(0.033, 0.033, 0.035), image_color=normalColor, image1_color=clickColor, image2_color=rolloverColor, image3_color=diabledColor, text_fg=Vec4(0.2, 0.1, 0, 1), command=self.setMode, extraArgs=[FishPage_Collection], pos=(0.92, 0, 0.1))
        self.tankTab.setPos(-0.4, 0, 0.775)
        self.collectionTab.setPos(0.15, 0, 0.775)

    def createFishPicker(self):
        if not hasattr(self, 'picker'):
            self.picker = FishPicker.FishPicker(self)
            self.picker.setPos(-0.555, 0, 0.1)
            self.picker.setScale(0.95)
            self.rod = DirectLabel(parent=self.picker, relief=None, text='', text_align=TextNode.ALeft, text_scale=0.06, pos=(0.9, 0, -0.65))

    def createFishBrowser(self):
        if not hasattr(self, 'browser'):
            self.browser = FishBrowser.FishBrowser(self)
            self.browser.setScale(1.1)
            self.collectedTotal = DirectLabel(parent=self.browser, relief=None, text='', text_scale=0.06, pos=(0, 0, -0.61))

    def setMode(self, mode, updateAnyways = 0):
        messenger.send(EventGlobals.WakeUp)
        if not updateAnyways:
            if self.mode == mode:
                return
            else:
                self.mode = mode
        self.show()
        if mode == FishPage_Tank:
            self.title['text'] = TTLocalizer.FishPageTitleTank
            if not hasattr(self, 'picker'):
                self.createFishPicker()
            self.picker.show()
            if hasattr(self, 'browser'):
                self.browser.hide()
            self.tankTab['state'] = DGG.DISABLED
            self.collectionTab['state'] = DGG.NORMAL
        elif mode == FishPage_Collection:
            self.title['text'] = TTLocalizer.FishPageTitleCollection
            if hasattr(self, 'picker'):
                self.picker.hide()
            if not hasattr(self, 'browser'):
                self.createFishBrowser()
            self.browser.show()
            self.tankTab['state'] = DGG.NORMAL
            self.collectionTab['state'] = DGG.DISABLED
        self.updatePage()

    def unload(self):
        self.avatar = None
        self.tankTab.destroy()
        self.collectionTab.destroy()
        ShtikerPage.ShtikerPage.unload(self)

    def updatePage(self):
        if hasattr(self, 'collectedTotal'):
            self.collectedTotal['text'] = TTLocalizer.FishPageCollectedTotal % (len(base.localAvatar.fishCollection), FishGlobals.getTotalNumFish())
        if hasattr(self, 'rod'):
            rod = base.localAvatar.getFishingRod()
            rodName = TTLocalizer.FishingRodNameDict[rod]
            rodWeightRange = FishGlobals.getRodWeightRange(rod)
            self.rod['text'] = TTLocalizer.FishPageRodInfo % (rodName, rodWeightRange[0], rodWeightRange[1])
        if self.mode == FishPage_Tank:
            if hasattr(self, 'picker'):
                newTankFish = base.localAvatar.fishTank.getFish()
                self.picker.update(newTankFish)
        elif self.mode == FishPage_Collection:
            if hasattr(self, 'browser'):
                self.browser.update()

    def destroy(self):
        self.notify.debug('destroy')
        DirectFrame.destroy(self)
