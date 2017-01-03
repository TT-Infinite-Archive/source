from panda3d.core import TextNode
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.gui.DirectButton import DirectButton, DGG
from direct.gui.DirectFrame import DirectFrame

from toontown.data import Gag, Track
from toontown.toon.ClerkGagInventoryGui import ClerkGagInventoryGui
from toontown.toonbase import ToontownGlobals, ColorGlobals
from toontown.toontowngui.TTGui import TTLabel, TTArrow, TTArrowSelectorGroup, TTSeperator, TTFrame
from toontown.shtiker.InventoryPage import GagInfoFrame
from toontown.util.PlacerTool3D import PlacerTool3D
from toontown.util.ThreadedCall import ThreadedCall


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
        self.mainFrame = TTFrame(self, pos=(-0.5, 0.0, 0.0), geom_scale=(1.7, 1, 1.7))
        self.gagInventory = ClerkGagInventoryGui(base.localAvatar, (0, 0, 0.65), self.mainFrame)
        self.title = TTLabel(
            self.mainFrame,
            text='Gag Storage',
            text_size=TTLabel.GiantSize,
            text_font=ToontownGlobals.getMinnieFont(),
            pos=(0.0, 0.0, 0.35),
        )
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
        PlacerTool3D(self.gagInfoFrame, increment=0.01)
        self.gagThread = ThreadedCall(func=self.loadGags, args=[0, self.__handleGagsLoaded])
        self.gagThread.start()

    def destroy(self):
        if self.gagThread:
            self.gagThread.join()
            self.gagThread = None
        del self.gagButtons[:]
        DirectFrame.destroy(self)

    def __handleFilterSelected(self, filterIdx):
        print('Selected: %s' % self.filters[filterIdx])
        self.gagThread = ThreadedCall(func=self.loadGags, args=[filterIdx, self.__handleGagsLoaded])
        self.gagThread.start()

    def __handleGagSelected(self, gag):
        print('Selected: %s' % gag)
        pass

    def __handleGagsLoaded(self, amount):
        if amount == 0:
            self.status['text'] = '???'
        else:
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
                text = ''
                state = DGG.NORMAL
                if gag.uid not in [slot.gag.uid for slot in base.localAvatar.inventory.items]:
                    text = '?'
                    gag = None
                    state = DGG.DISABLED

                gb = DirectButton(
                    parent=self.mainFrame,
                    relief=None,
                    pos=(x, 0, z),
                    text=text,
                    text_scale=0.12,
                    text_font=ToontownGlobals.getFancyFont(),
                    text_pos=(0.0, -0.045, 0.0)
                )
                if gag is not None:
                    glow = gag.glow
                    glow.reparentTo(gb)
                    gbi = DirectButton(
                        parent=gb,
                        relief=None,
                        image=gag.icon,
                        state=state,
                        command=self.__handleGagSelected,
                        extraArgs=[gag]
                    )
                    gbi.bind(DGG.WITHIN, self.__handleEnterGag, extraArgs=[gag])
                gb.hide()
                self.gagButtons.append(gb)
        if callback:
            callback(len(gags))

    def __handleEnterGag(self, gag, e=None):
        self.gagInfoFrame.setGag(gag)


class GagSelectInfoFrame(GagInfoFrame):
    def __init__(self, parent, pos=(0.0, 0.0, 0.0), scale=(1, 1, 1), geom_scale=(0.9, 0.5, 0.5)):
        GagInfoFrame.__init__(self, parent, pos, scale, geom_scale)
        self.gagTitle.setPos(0, 0, 0.2)
        self.gagDescription.setPos(-0.12, 0.0, 0.06)
        self.gagIcon.setPos(-0.29, 0, 0.04)
        self.status = TTLabel(self.mainFrame, text='Hover over a gag to view information about it!', pos=(0, 0, 0.05))
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
        self.setStatus('Hover over a gag to view information about it!')

    def setStatus(self, status):
        self.status['text'] = status