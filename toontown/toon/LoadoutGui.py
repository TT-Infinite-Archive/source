from panda3d.core import TextNode
from direct.gui.DirectGui import *
from toontown.util import TTCardMaker
from toontown.toonbase import EventGlobals, ToontownGlobals, ColorGlobals
from toontown.toontowngui import TTLabel


class LoadoutGui(DirectFrame):
    MaxSlots = 6
    SlotPositions = (
        (-0.65, 0.0, 0.0),
        (-0.4, 0.0, 0.0),
        (-0.15, 0.0, 0.0),
        (0.15, 0.0, 0.0),
        (0.4, 0.0, 0.0),
        (0.65, 0.0, 0.0),
    )
    notify = directNotify.newCategory('GagInventoryGui')

    def __init__(self, toon, pos, parent=aspect2d):
        self.notify.debug('Loading...')
        DirectFrame.__init__(self, parent=parent, relief=None, pos=pos)
        self.initialiseoptions(LoadoutGui)
        self.mainFrame = DirectFrame(
            self,
            relief=None,
            geom=DGG.getDefaultDialogGeom(),
            geom_scale=(1.65, 1, 0.4),
            geom_color=ToontownGlobals.GlobalDialogColor
        )
        self.gagSlots = []
        self.toon = toon
        self.load()
        self.gagInfoFrame = None
        self.accept(EventGlobals.LoadoutChanged, self.load)
        self.acceptOnscreenHooks()
        self.onscreen = False

    def destroy(self):
        self.notify.debug('Destroying...')
        self.unload()
        self.ignore(EventGlobals.LoadoutChanged)
        self.ignoreOnscreenHooks()
        DirectFrame.destroy(self)

    def load(self):
        self.notify.debug('Loading...')
        self.unload()
        loadout = self.toon.loadout.getLoadout()
        for index in xrange(0, self.MaxSlots):
            gag = None
            if index < len(loadout):
                gag = loadout[index]

            gagSlotGui = LoadoutSlotGui(
                self.mainFrame,
                gag,
                index,
                pos=self.SlotPositions[index],
                clickCommand=self.__handleSelection,
                enterCommand=self.__handleEnterGagSlot,
                exitCommand=self.__handleExitGagSlot
            )
            self.gagSlots.append(gagSlotGui)

    def unload(self):
        for gagSlot in self.gagSlots:
            gagSlot.destroy()
        del self.gagSlots[:]

    def acceptOnscreenHooks(self):
        self.accept(ToontownGlobals.InventoryHotkeyOn, self.showOnscreen)
        self.accept(ToontownGlobals.InventoryHotkeyOff, self.hideOnscreen)

    def ignoreOnscreenHooks(self):
        self.ignore(ToontownGlobals.InventoryHotkeyOn)
        self.ignore(ToontownGlobals.InventoryHotkeyOff)

    def showOnscreen(self):
        self.onscreen = True
        self.show()
        self.reparentTo(aspect2d)
        if self.gagInfoFrame is not None:
            self.gagInfoFrame.destroy()
        self.gagInfoFrame = GagInfoFrame(parent=self, pos=(-0.39, 0, -0.35))
        self.accept(EventGlobals.GagSlotEnter, self.updateGagInfo)
        self.accept(EventGlobals.GagSlotExit, self.clearGagInfo)

    def hideOnscreen(self):
        self.onscreen = False
        self.ignore(EventGlobals.GagSlotEnter)
        self.ignore(EventGlobals.GagSlotExit)
        if self.gagInfoFrame:
            self.gagInfoFrame.destroy()
            self.gagInfoFrame = None
        self.hide()
        self.reparentTo(hidden)

    def updateGagInfo(self, slot):
        gag = base.localAvatar.loadout.getGagAtSlot(slot)
        self.gagInfoFrame.setGag(gag)

    def clearGagInfo(self, slot):
        self.gagInfoFrame.unsetGag()

    def __handleSelection(self, slotIndex):
        self.notify.debug('Selected gag at slot %d' % slotIndex)
        messenger.send(EventGlobals.GagSlotClick, [slotIndex])

    def __handleEnterGagSlot(self, slotIndex):
        messenger.send(EventGlobals.GagSlotEnter, [slotIndex])

    def __handleExitGagSlot(self, slotIndex):
        messenger.send(EventGlobals.GagSlotExit, [slotIndex])


class LoadoutSlotGui(DirectButton):
    StateEmpty = 0
    StateNormal = 1

    def __init__(self, parent, gagItem, index, pos=(0, 0, 0), color=(1, 1, 1, 1), clickCommand=None, enterCommand=None, exitCommand=None):
        self.gagItem = gagItem
        if self.gagItem is not None:
            self.gdObj = gagItem.displayObject
        else:
            self.gdObj = None
        self.index = index
        self.pos = pos
        self.clickCommand = clickCommand
        self.enterCommand = enterCommand
        self.exitCommand = exitCommand
        self.color = color
        self.isEmpty = False

        DirectButton.__init__(self, parent, relief=None, pos=pos)
        background = TTCardMaker.makeCard('phase_3/maps/gui-circle.png')

        self.mainButton = DirectButton(
            self,
            relief=None,
            image=background,
            image_color=color,
            image_scale=(0.0025, 1, 0.0025),
            command=self.__handleClick
        )
        self.mainButton.bind(DGG.WITHIN, self.__handleEnter)
        self.mainButton.bind(DGG.WITHOUT, self.__handleExit)

        if self.gdObj is not None:
            self.icon = self.gdObj.button
            if self.icon is not None:
                pos = self.icon.getPos()
                self.icon.reparentTo(self.mainButton)
                self.icon.setPos(pos)
            else:
                self.isEmpty = True
        else:
            self.isEmpty = True

        self.updateButtonState()

    def destroy(self):
        if self.mainButton is not None:
            self.mainButton.destroy()
            self.mainButton = None
        DirectButton.destroy(self)

    def setButtonState(self, state):
        if state == self.StateEmpty:
            self.mainButton['state'] = DGG.DISABLED
        elif state == self.StateNormal:
            self.mainButton['state'] = DGG.NORMAL
            self.mainButton['clickSound'] = DGG.getDefaultClickSound()
            self.mainButton['rolloverSound'] = DGG.getDefaultRolloverSound()
            self.mainButton.setClickSound()
            self.mainButton.setRolloverSound()
            self.mainButton.bind(DGG.WITHIN, self.__handleEnter)
            self.mainButton.bind(DGG.WITHOUT, self.__handleExit)
            if self.icon is not None:
                color = self.icon.getColorScale()
                self.icon.setColorScale(color[0], color[1], color[2], 1.0)

    def updateButtonState(self):
        if self.isEmpty:
            self.setButtonState(self.StateEmpty)
        else:
            self.setButtonState(self.StateNormal)

    def __handleClick(self, e=None):
        if self.clickCommand is not None:
            self.clickCommand(self.index)

    def __handleEnter(self, e=None):
        _, _, _, alpha = self.mainButton['image_color']
        self.mainButton['image_color'] = (0.2, 1, 0.75, alpha)
        if self.enterCommand is not None:
            self.enterCommand(self.index)

    def __handleExit(self, e):
        _, _, _, alpha = self.mainButton['image_color']
        self.mainButton['image_color'] = (1, 1, 1, alpha)
        if self.exitCommand is not None:
            self.exitCommand(self.index)

    def doNothing(self, e):
        pass


class GagInfoFrame(DirectFrame):
    def __init__(self, parent, pos=(0.0, 0.0, 0.0), scale=(1, 1, 1), geom_scale=(0.9, 0.5, 0.5)):
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
            geom_scale=geom_scale
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
        self.setTitleColor(gag.rarityColor)
        self.setDescription(gag.description)
        self.setIcon(gag.displayObject.button)

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
