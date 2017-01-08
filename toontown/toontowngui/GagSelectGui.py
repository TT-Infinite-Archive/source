from panda3d.core import TextNode
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.gui.DirectButton import DirectButton, DGG
from direct.gui.DirectFrame import DirectFrame

from toontown.data import Gag, Track
from toontown.toon.ClerkLoadoutGui import ClerkLoadoutGui
from toontown.toonbase import ToontownGlobals, ColorGlobals, EventGlobals, TTLocalizer
from toontown.toontowngui.TTGui import TTLabel, TTArrow, TTArrowSelectorGroup, TTSeperator, TTFrame, TTTooltip
from toontown.toon.LoadoutGui import GagInfoFrame
from toontown.util.ThreadedCall import ThreadedCall
from toontown.util.PlacerTool3D import PlacerTool3D


class GagSelectGui(DirectFrame):
    notify = directNotify.newCategory('GagSelectGui')
    MAX_PER_ROW = 5
    MAX_ROWS = 4
    X_START = -0.65
    X_SEP = 0.32
    Z_SEP = 0.215
    Z_START = 0.05

    def __init__(self, timeout, pos=(0.0, 0.0, 0.0)):
        self.notify.debug('Loading...')
        self.gagThread = None
        DirectFrame.__init__(self, parent=aspect2d, relief=None, pos=pos)
        self.initialiseoptions(GagSelectGui)
        self.mainFrame = TTFrame(self, pos=(-0.5, 0.0, 0.0), geom_scale=(1.7, 1, 1.7))
        self.gagInventory = ClerkLoadoutGui(base.localAvatar, (0, 0, 0.65), self.mainFrame)
        self.title = TTLabel(
            self.mainFrame,
            text='Gag Storage',
            text_size=TTLabel.GiantSize,
            text_font=ToontownGlobals.getMinnieFont(),
            pos=(0.0, 0.0, 0.35),
        )
        gui = loader.loadModel('phase_3/models/gui/dialog_box_buttons_gui')
        closeButtonImage = (gui.find('**/CloseBtn_UP'), gui.find('**/CloseBtn_DN'), gui.find('**/CloseBtn_Rllvr'))
        self.closeBtn = DirectButton(
            parent=self,
            relief=None,
            image=closeButtonImage,
            pos=(0.29, 0, 0.81),
            command=self.__handleClose
        )
        gui.removeNode()
        self.status = TTLabel(self.mainFrame, text_size=TTLabel.GiantSize, pos=(0.0, 0.0, -0.25))
        self.seperator = TTSeperator(self.mainFrame, pos=(0.0, 0.0, 0.5))
        self.filters = ['All', 'ToonUp', 'Trap', 'Lure', 'Throw', 'Squirt', 'Sound', 'Drop']
        self.trackLabel = TTLabel(self.mainFrame, text_size=TTLabel.LargeSize, pos=(0.0, 0.0, 0.23))
        self.trackLArrow = TTArrow(self.mainFrame, orientation=TTArrow.OrientationLeft, pos=(-0.25, 0.0, 0.25))
        self.trackRArrow = TTArrow(self.mainFrame, orientation=TTArrow.OrientationRight, pos=(0.25, 0.0, 0.25))
        self.trackSelector = TTArrowSelectorGroup(
            self.trackLArrow,
            self.trackRArrow,
            self.trackLabel,
            self.__handleFilterSelected,
            items=self.filters
        )
        self.gagButtons = []
        self.gagInfoFrame = GagSelectInfoFrame(self, pos=(1, 0.0, 0.45), geom_scale=(1, 1.0, 0.6))
        self.gagThread = ThreadedCall(func=self.loadGags, args=[0, self.__handleGagsLoaded])
        self.gagThread.start()
        self.accept(EventGlobals.GagSlotClick, self.__handleSlotSelected)
        self.accept(EventGlobals.GagSlotEnter, self.__handleSlotEnter)
        self.accept(EventGlobals.GAG_SELECT_GAG_ENTER, self.__handleGagEnter)
        self.accept(EventGlobals.GagSlotExit, self.__handleSlotExit)
        self.tt = None

    def destroy(self):
        if self.gagThread:
            self.gagThread.join()
            self.gagThread = None
        if self.tt:
            self.tt.destroy()
            self.tt = None
        del self.gagButtons[:]
        DirectFrame.destroy(self)

    def __handleClose(self):
        messenger.send(EventGlobals.GagSelectGuiClose)

    def __handleFilterSelected(self, filterIdx):
        self.gagThread = ThreadedCall(func=self.loadGags, args=[filterIdx, self.__handleGagsLoaded])
        self.gagThread.run()

    def __handleSlotSelected(self, slot):
        pass

    def __handleSlotEnter(self, slot):
        if self.tt:
            self.tt.destroy()
        self.tt = TTTooltip(description=TTLocalizer.GagSelectClickToUnEquip)
        self.gagInfoFrame.setGag(base.localAvatar.loadout.getGagAtSlot(slot))

    def __handleSlotExit(self, slot):
        if self.tt:
            self.tt.destroy()
            self.tt = None

    def __handleGagsLoaded(self, amount):
        self.notify.debug('Done loading %d gags.' % amount)
        if amount == 0:
            self.status['text'] = TTLocalizer.GagSelectNoGags
        else:
            self.status['text'] = ''
            for gb in self.gagButtons:
                gb.show()

    def __handleGagEnter(self, gag):
        self.gagInfoFrame.setGag(gag)

    def cleanupGagIcons(self):
        for gb in self.gagButtons:
            gb.destroy()
        del self.gagButtons[:]

    def loadGags(self, filterIdx=0, callback=None):
        self.status['text'] = TTLocalizer.lLoading
        self.cleanupGagIcons()
        gags = [gag for gag in Gag.Gags.values() if gag.uid not in Gag.AlwaysEquipped]
        if filterIdx != 0:
            # We want to filter tracks
            trackId = 0
            filterName = self.filters[filterIdx]
            for track in Track.Tracks:
                if track.name == filterName:
                    trackId = track.idn
                    break
            gags = [gag for gag in gags if gag.track == trackId]

        idx = -1
        for n in xrange(0, self.MAX_ROWS):
            for i in xrange(0, self.MAX_PER_ROW):
                idx += 1
                if len(gags) - 1 < idx:
                    break
                x = self.X_START + i * self.X_SEP
                z = self.Z_START - n * self.Z_SEP
                gag = gags[idx]
                if not base.localAvatar.inventory.gagUnlocked(gag):
                    gag = None

                gb = GagSelectGagButton(
                    parent=self.mainFrame,
                    gag=gag,
                    pos=(x, 0, z)
                )
                gb.hide()
                self.gagButtons.append(gb)
        if callback:
            callback(len(gags))


class GagSelectInfoFrame(GagInfoFrame):
    def __init__(self, parent, pos=(0.0, 0.0, 0.0), scale=(1, 1, 1), geom_scale=(0.9, 0.5, 0.5)):
        GagInfoFrame.__init__(self, parent, pos, scale, geom_scale)
        self.gagTitle.setPos(0, 0, 0.2)
        self.gagDescription.setPos(-0.12, 0.0, 0.06)
        self.gagIcon.setPos(-0.29, 0, 0.04)
        self.status = TTLabel(self.mainFrame, text=TTLocalizer.GagSelectNoGagInfo, pos=(0, 0, 0.05))
        self.show()

    def setGag(self, gag):
        if gag is None:
            return
        GagInfoFrame.setGag(self, gag)
        self.status['text'] = ''

    def unsetGag(self):
        self.setTitle('')
        self.setDescription('')
        self.setIcon(None)
        self.setStatus(TTLocalizer.GagSelectNoGagInfo)

    def setStatus(self, status):
        self.status['text'] = status


class GagSelectGagButton(DirectButton):
    def __init__(self, parent=aspect2d, gag=None, **kw):
        self.gag = gag
        self.tt = None
        self.equipped = False
        self.unlocked = False
        if gag is None:
            text = '?'
        else:
            text = ''
        optiondefs = (
            ('relief', None, None),
        )

        self.defineoptions(kw, optiondefs)
        DirectButton.__init__(self, parent)
        self.initialiseoptions(GagSelectGagButton)
        self['text'] = text
        self['text_pos'] = (0.0, -0.035, 0.0)
        self['text_font'] = ToontownGlobals.getFancyFont()
        self['text_scale'] = 0.12
        self.gbi = None

        self.eLabel = TTLabel(
            parent=self,
            text='E',
            pos=(-0.1, 0.0, 0.05)
        )
        if gag:
            glow = gag.glow
            glow.reparentTo(self)

        self.gbi = DirectButton(
            parent=self,
            relief=None,
            image=None if gag is None else gag.icon,
            state=(DGG.NORMAL if gag is not None else DGG.DISABLED),
            command=self.__handleGagSelected
        )
        self.gbi.bind(DGG.WITHIN, self.__handleEnterGag, extraArgs=[gag])
        self.gbi.bind(DGG.WITHOUT, self.__handleExitGag, extraArgs=[gag])
        self.setEquipped(base.localAvatar.loadout.isEquipped(self.gag))
        self.setUnlocked(base.localAvatar.inventory.gagUnlocked(self.gag))
        self.accept(EventGlobals.LoadoutChanged, self.__handleLoadoutChanged)
        self.accept(EventGlobals.InventoryChanged, self.__handleInventoryChanged)

    def setEquipped(self, flag):
        self.equipped = flag
        if flag:
            self.eLabel.show()
            if self.tt:
                self.tt.description['text'] = TTLocalizer.GagSelectEquipped
        else:
            if self.tt:
                self.tt.description['text'] = TTLocalizer.GagSelectClickToEquip
            self.eLabel.hide()

    def setUnlocked(self, flag):
        self.unlocked = flag
        if flag:
            self.gbi.show()
        else:
            self.gbi.hide()

    def __handleLoadoutChanged(self):
        if base.localAvatar.loadout.isEquipped(self.gag):
            pass

    def __handleInventoryChanged(self):
        pass

    def __handleGagSelected(self):
        messenger.send(EventGlobals.EQUIP_GAG, [self.gag])

    def __handleEnterGag(self, gag, e=None):
        messenger.send(EventGlobals.GAG_SELECT_GAG_ENTER, [self.gag])
        if self.tt:
            self.tt.destroy()
        if self.equipped:
            description = TTLocalizer.GagSelectEquipped
        else:
            description = TTLocalizer.GagSelectClickToEquip

        self.tt = TTTooltip(description=description)

    def __handleExitGag(self, gag, e=None):
        messenger.send(EventGlobals.GAG_SELECT_GAG_EXIT, [self.gag])
        if self.tt:
            self.tt.destroy()
            self.tt = None