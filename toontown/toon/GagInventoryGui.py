from direct.gui.DirectGui import *
from direct.directnotify import DirectNotifyGlobal
from toontown.util import TTCardMaker
from toontown.toonbase import EventGlobals, ToontownGlobals


class GagInventoryGui(DirectFrame):
    MaxSlots = 6
    SlotPositions = (
        (-0.65, 0.0, 0.0),
        (-0.4, 0.0, 0.0),
        (-0.15, 0.0, 0.0),
        (0.15, 0.0, 0.0),
        (0.4, 0.0, 0.0),
        (0.65, 0.0, 0.0),
    )
    notify = DirectNotifyGlobal.directNotify.newCategory('GagInventoryGui')

    def __init__(self, toon):
        self.notify.debug('Loading...')
        DirectFrame.__init__(self, parent=aspect2d, relief=None)
        self.initialiseoptions(GagInventoryGui)
        self.mainFrame = DirectFrame(
            self,
            relief=None,
            pos=(0.0, 0.0, 0.25),
            geom=DGG.getDefaultDialogGeom(),
            geom_scale=(1.65, 1, 0.4),
            geom_color=ToontownGlobals.GlobalDialogColor
        )
        self.gagSlots = []
        self.toon = toon
        self.loadEquippedGags()
        self.accept(EventGlobals.GagsChanged, self.loadEquippedGags)

    def loadEquippedGags(self):
        self.notify.debug('Loading Equipped Gags...')
        self.unloadEquippedGags()
        eqItems = self.toon.inventory.getEquippedItems()
        for index in xrange(0, self.MaxSlots):
            if index < len(eqItems):
                gagSlot = eqItems[index]
                gagObj = gagSlot.gag
            else:
                gagObj = None

            gagSlotGui = GagInventorySlot(
                self.mainFrame,
                gagObj,
                index,
                pos=self.SlotPositions[index],
                clickCommand=self.__handleSelection,
                enterCommand=self.__handleEnterGagSlot,
                exitCommand=self.__handleExitGagSlot
            )
            self.gagSlots.append(gagSlotGui)

    def show(self):
        self.notify.debug('Showing...')
        DirectFrame.show(self)

    def hide(self):
        self.notify.debug('Hiding...')
        DirectFrame.hide(self)

    def unloadEquippedGags(self):
        for gagSlot in self.gagSlots:
            gagSlot.destroy()
        self.gagSlots[:] = []

    def destroy(self):
        self.notify.debug('Destroying...')
        self.unloadEquippedGags()
        self.ignore(EventGlobals.GagsChanged)
        DirectFrame.destroy(self)

    def __handleSelection(self, slotIndex):
        messenger.send(EventGlobals.GagInventorySelection, [slotIndex])

    def __handleEnterGagSlot(self, slotIndex):
        messenger.send(EventGlobals.GagSlotEnter, [slotIndex])

    def __handleExitGagSlot(self, slotIndex):
        messenger.send(EventGlobals.GagSlotExit, [slotIndex])


class GagInventorySlot(DirectButton):
    StateEmpty = 0
    StateNormal = 1

    def __init__(self, parent, gagItem, index, pos=(0, 0, 0), color=(1, 1, 1, 1), clickCommand=None, enterCommand=None, exitCommand=None):
        self.parent = parent
        self.gagItem = gagItem
        if self.gagItem is not None:
            self.gdObj = gagItem.getDisplayObject()
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
            self.icon = self.gdObj.getButtonIcon()
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
        self.parent = None
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

