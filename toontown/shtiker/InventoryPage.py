import ShtikerPage
from toontown.toonbase import ToontownBattleGlobals
from direct.gui.DirectGui import *
from pandac.PandaModules import *
from toontown.toonbase import ToontownGlobals, EventGlobals, ColorGlobals
from toontown.toonbase import TTLocalizer
from toontown.toontowngui import TTLabel
from toontown.shtiker.CogMenu import CogMenu
from toontown.toontowngui.JarGui import JarGui
from toontown.util.PlacerTool3D import PlacerTool3D


class InventoryPage(ShtikerPage.ShtikerPage):

    def __init__(self):
        ShtikerPage.ShtikerPage.__init__(self)
        self.currentTrackInfo = None
        self.onscreen = 0
        self.lastInventoryTime = globalClock.getRealTime()

    def load(self):
        ShtikerPage.ShtikerPage.load(self)
        self.title = DirectLabel(
            parent=self,
            relief=None,
            text=TTLocalizer.InventoryPageTitle,
            text_scale=0.12,
            textMayChange=1,
            pos=(0, 0, 0.62)
        )

        self.gagInfoFrame = GagInfoFrame(parent=self, pos=(-0.39, 0, -0.35))
        self.moneyDisplay = JarGui(parent=self, pos=(0.6, 0.0, -0.4))
        self.cogMenu = CogMenu()
        self.cogMenu.reparentTo(self)
        self.cogMenu.setX(-0.165)
        self.cogMenu.setZ(0.63)
        self.cogMenu.setScale(0.82)
        self.cogMenu.hide()

    def unload(self):
        del self.title
        self.cogMenu.cleanup()
        del self.cogMenu
        ShtikerPage.ShtikerPage.unload(self)

    def enter(self):
        ShtikerPage.ShtikerPage.enter(self)
        base.localAvatar.gagPanel.show()
        base.localAvatar.gagPanel.reparentTo(self)
        self.moneyDisplay.update()
        self.moneyDisplay.listen()
        self.accept(EventGlobals.GagSlotEnter, self.updateGagInfo)
        self.accept(EventGlobals.GagSlotExit, self.clearGagInfo)
        self.accept('enterBookDelete', self.enterDeleteMode)
        self.accept('exitBookDelete', self.exitDeleteMode)

    def exit(self):
        ShtikerPage.ShtikerPage.exit(self)
        self.clearTrackInfo(self.currentTrackInfo)
        self.ignore(EventGlobals.GagSlotEnter)
        self.ignore(EventGlobals.GagSlotExit)
        self.ignore('enterBookDelete')
        self.ignore('exitBookDelete')
        self.moneyDisplay.unlisten()
        self.makePageWhite(None)
        base.localAvatar.gagPanel.hide()
        base.localAvatar.gagPanel.reparentTo(hidden)
        self.exitDeleteMode()

    def enterDeleteMode(self):
        self.title['text'] = TTLocalizer.InventoryPageDeleteTitle
        self.title['text_fg'] = (0, 0, 0, 1)
        self.book['image_color'] = Vec4(1, 1, 0, 1)

    def exitDeleteMode(self):
        self.title['text'] = TTLocalizer.InventoryPageTitle
        self.title['text_fg'] = (0, 0, 0, 1)
        self.book['image_color'] = Vec4(1, 1, 1, 1)

    def updateTrackInfo(self, trackIndex):
        self.currentTrackInfo = trackIndex
        trackName = TextEncoder.upper(ToontownBattleGlobals.Tracks[trackIndex])
        if base.localAvatar.hasTrackAccess(trackIndex):
            curExp, nextExp = base.localAvatar.inventory.getCurAndNextExpValues(trackIndex)
            trackText = '%s / %s' % (curExp, nextExp)
            self.trackProgress['range'] = nextExp
            self.trackProgress['value'] = curExp
            if curExp >= ToontownBattleGlobals.regMaxSkill:
                str = TTLocalizer.InventoryPageTrackFull % trackName
                trackText = TTLocalizer.InventoryUberTrackExp % {'nextExp': ToontownBattleGlobals.MaxSkill - curExp}
                self.trackProgress['range'] = ToontownBattleGlobals.UberSkill
                uberCurrExp = curExp - ToontownBattleGlobals.regMaxSkill
                self.trackProgress['value'] = uberCurrExp
            else:
                morePoints = nextExp - curExp
                if morePoints == 1:
                    str = TTLocalizer.InventoryPageSinglePoint % {'trackName': trackName,
                     'numPoints': morePoints}
                else:
                    str = TTLocalizer.InventoryPagePluralPoints % {'trackName': trackName,
                     'numPoints': morePoints}
            self.trackInfo['text'] = str
            self.trackProgress['text'] = trackText
            self.trackProgress['frameColor'] = (ToontownBattleGlobals.TrackColors[trackIndex][0] * 0.6,
             ToontownBattleGlobals.TrackColors[trackIndex][1] * 0.6,
             ToontownBattleGlobals.TrackColors[trackIndex][2] * 0.6,
             1)
            self.trackProgress['barColor'] = (ToontownBattleGlobals.TrackColors[trackIndex][0],
             ToontownBattleGlobals.TrackColors[trackIndex][1],
             ToontownBattleGlobals.TrackColors[trackIndex][2],
             1)
            self.trackProgress.show()
        else:
            str = TTLocalizer.InventoryPageNoAccess % trackName
            self.trackInfo['text'] = str
            self.trackProgress.hide()

    def clearTrackInfo(self, trackIndex):
        if self.currentTrackInfo == trackIndex:
            self.trackInfo['text'] = ''
            self.trackProgress.hide()
            self.currentTrackInfo = None
        return

    def acceptOnscreenHooks(self):
        self.accept(ToontownGlobals.InventoryHotkeyOn, self.showInventoryOnscreen)
        self.accept(ToontownGlobals.InventoryHotkeyOff, self.hideInventoryOnscreen)
        self.accept(EventGlobals.SHOW_BATTLE_INVENTORY, self.showInventoryBattle)
        self.accept(EventGlobals.HIDE_BATTLE_INVENTORY, self.hideInventoryBattle)

    def ignoreOnscreenHooks(self):
        self.ignore(ToontownGlobals.InventoryHotkeyOn)
        self.ignore(ToontownGlobals.InventoryHotkeyOff)

    def updateGagInfo(self, slot):
        gag = base.localAvatar.inventory.getGagAtSlot(slot)
        self.gagInfoFrame.setGag(gag)

    def clearGagInfo(self, slot):
        self.gagInfoFrame.unsetGag()

    def showInventoryBattle(self):
        base.localAvatar.gagPanel.show()
        base.localAvatar.gagPanel.reparentTo(self)
        self.accept(EventGlobals.GagSlotEnter, self.updateGagInfo)
        self.accept(EventGlobals.GagSlotExit, self.clearGagInfo)
        self.clearGagInfo(None)
        self.reparentTo(aspect2d)
        self.moneyDisplay.hide()
        self.title.hide()
        self.show()

    def hideInventoryBattle(self):
        base.localAvatar.gagPanel.hide()
        base.localAvatar.gagPanel.reparentTo(hidden)
        self.ignore(EventGlobals.GagSlotEnter)
        self.ignore(EventGlobals.GagSlotExit)
        self.clearGagInfo(None)
        self.reparentTo(self.book)
        self.moneyDisplay.show()
        self.title.show()
        self.hide()

    def showInventoryOnscreen(self):
        messenger.send('wakeup')
        timedif = globalClock.getRealTime() - self.lastInventoryTime
        if timedif < 0.7:
            return
        self.lastInventoryTime = globalClock.getRealTime()
        if self.onscreen or base.localAvatar.questPage.onscreen:
            return
        self.onscreen = 1
        base.localAvatar.gagPanel.show()
        base.localAvatar.gagPanel.reparentTo(self)
        self.moneyDisplay.update()
        self.moneyDisplay.listen()
        self.accept(EventGlobals.GagSlotEnter, self.updateGagInfo)
        self.accept(EventGlobals.GagSlotExit, self.clearGagInfo)
        self.cogMenu.update()
        self.reparentTo(aspect2d)
        self.cogMenu.show()
        self.title.hide()
        self.show()

    def hideInventoryOnscreen(self):
        if not self.onscreen:
            return
        self.onscreen = 0
        self.ignore(EventGlobals.GagSlotEnter)
        self.ignore(EventGlobals.GagSlotExit)
        self.ignore(localAvatar.uniqueName('moneyChange'))
        base.localAvatar.gagPanel.hide()
        base.localAvatar.gagPanel.reparentTo(hidden)
        self.reparentTo(self.book)
        self.cogMenu.hide()
        self.title.show()
        self.hide()


class GagInfoFrame(DirectFrame):
    def __init__(self, parent, pos=(0.0, 0.0, 0.0), scale=(1, 1, 1)):
        DirectFrame.__init__(
            self,
            parent,
            relief=None,
            pos=pos,
            scale=scale
        )
        self.mainFrame = DirectFrame(
            parent=self,
            relief=None,
            geom=DGG.getDefaultDialogGeom(),
            geom_color=ToontownGlobals.GlobalDialogColor,
            geom_scale=(0.9, 0.5, 0.5)
        )
        self.gagTitle = TTLabel.TTLabel(
            parent=self.mainFrame,
            text_size=TTLabel.TTLabel.MediumSize,
            pos=(0.0, 0.0, 0.15),
            text='',
            text_align=TextNode.ACenter,
            text_fg=ColorGlobals.CDarkGray
        )
        self.gagDescription = TTLabel.TTLabel(
            parent=self.mainFrame,
            pos=(-0.12, 0.0, 0.03),
            text='',
            text_align=TextNode.ALeft,
            text_wordwrap=10
        )
        self.gagIcon = DirectButton(
            parent=self.mainFrame,
            relief=None,
            pos=(-0.29, 0, 0),
            suppressMouse=True,
            state=DGG.DISABLED
        )
        self.hide()

    def destroy(self):
        self.gagTitle.destroy()
        self.gagDescription.destroy()
        self.mainFrame.destroy()
        DirectFrame.destroy(self)

    def setGag(self, gag):
        self.show()
        self.setTitle(gag.name)
        self.setTitleColor(gag.getRarityColor())
        self.setDescription(gag.getDescription())
        self.setIcon(gag.getDisplayObject().getButtonIcon())

    def unsetGag(self):
        self.hide()
        self.setTitle('')
        self.setDescription('')
        self.setIcon(None)

    def setTitle(self, title):
        self.gagTitle['text'] = title

    def setDescription(self, desc):
        self.gagDescription['text'] = desc

    def setIcon(self, icon):
        self.gagIcon['image'] = icon

    def setTitleColor(self, color):
        self.gagTitle['text_fg'] = color