from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.gui.DirectFrame import DirectFrame, DGG
from direct.gui.DirectButton import DirectButton
from panda3d.core import TextNode

from toontown.toon.ClerkGagInventoryGui import ClerkGagInventoryGui
from toontown.toon import InventoryGlobals
from toontown.toonbase import EventGlobals, ToontownGlobals
from toontown.toontowngui.TTArrowSelectorGroup import TTArrowSelectorGroup
from toontown.toontowngui.TTLabel import TTLabel
from toontown.toontowngui.TTArrow import TTArrow
from toontown.toontowngui.TTSeperator import TTSeperator
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

    def __init__(self, toon, timeout, pos=(0.0, 0.0, 0.0)):
        self.notify.debug('Loading...')
        self.gagThread = None
        DirectFrame.__init__(self, parent=aspect2d, relief=None, pos=pos)
        self.initialiseoptions(GagSelectGui)
        self.mainFrame = DirectFrame(
            self,
            relief=None,
            pos=(0.0, 0.0, 0.0),
            geom=DGG.getDefaultDialogGeom(),
            geom_scale=(1.7, 1, 1.7),
            geom_color=ToontownGlobals.GlobalDialogColor
        )
        self.gagInventory = ClerkGagInventoryGui(base.localAvatar, (0, 0, 0.65), self.mainFrame)
        self.title = TTLabel(
            self.mainFrame,
            text='Gag Cache',
            text_size=TTLabel.GiantSize,
            text_font=ToontownGlobals.getMinnieFont(),
            pos=(0.0, 0.0, 0.35),
        )
        self.status = TTLabel(
            self.mainFrame,
            text_size=TTLabel.GiantSize,
            pos=(0.0, 0.0, -0.25)
        )
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
        self.gagThread = ThreadedCall(func=self.loadGags, args=[0, self.__handleGagsLoaded])
        self.gagThread.start()

    def destroy(self):
        del self.gagButtons[:]
        DirectFrame.destroy(self)

    def __handleFilterSelected(self, filterIdx):
        print('Selected: %s' % self.filters[filterIdx])
        #self.loadGags(filterIdx)

    def __handleGagSelected(self, gag):
        print('Selected: %s' % gag)
        pass

    def __handleGagsLoaded(self):
        self.status['text'] = ''
        for gb in self.gagButtons:
            gb.show()

    def cleanupGagIcons(self):
        for gb in self.gagButtons:
            gb.destroy()
        del self.gagButtons[:]

    def loadGags(self, filterIdx=0, callback=None):
        self.status['text'] = 'Loading...'
        self.cleanupGagIcons()
        gags = [gag for gag in InventoryGlobals.Gags.values() if gag.uid not in InventoryGlobals.AlwaysEquipped]
        if filterIdx != 0:
            # We want to filter tracks
            trackId = 0
            filterName = self.filters[filterIdx]
            for track in InventoryGlobals.Tracks:
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
                gb = DirectButton(
                    parent=self.mainFrame,
                    relief=None,
                    pos=(x, 0, z),
                    geom=gag.displayObject.icon,
                    command=self.__handleGagSelected,
                    extraArgs=[gag]
                )
                gb.hide()
                self.gagButtons.append(gb)
        if callback:
            callback()
