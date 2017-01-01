from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.gui.DirectFrame import DirectFrame, DGG
from panda3d.core import TextNode

from toontown.toon.ClerkGagInventoryGui import ClerkGagInventoryGui
from toontown.toonbase import EventGlobals, ToontownGlobals
from toontown.toontowngui.TTArrowSelectorGroup import TTArrowSelectorGroup
from toontown.toontowngui.TTLabel import TTLabel
from toontown.toontowngui.TTArrow import TTArrow
from toontown.toontowngui.TTSeperator import TTSeperator
from toontown.util.PlacerTool3D import PlacerTool3D


class GagSelectGui(DirectFrame):
    notify = directNotify.newCategory('GagSelectGui')

    def __init__(self, toon, timeout):
        self.notify.debug('Loading...')
        DirectFrame.__init__(self, parent=aspect2d, relief=None)
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
            text='Loading...',
            text_size=TTLabel.GiantSize,
            pos=(0.0, 0.0, -0.25)
        )
        self.seperator = TTSeperator(self.mainFrame, pos=(0.0, 0.0, 0.5))
        self.trackLabel = TTLabel(self.mainFrame, text='ToonUp', text_size=TTLabel.LargeSize, pos=(0.0, 0.0, 0.23))
        self.trackLArrow = TTArrow(self.mainFrame, orientation=TTArrow.OrientationLeft, pos=(-0.25, 0.0, 0.25))
        self.trackRArrow = TTArrow(self.mainFrame, orientation=TTArrow.OrientationRight, pos=(0.25, 0.0, 0.25))
        self.trackSelector = TTArrowSelectorGroup(
            self.trackLArrow,
            self.trackRArrow,
            self.trackLabel,
            self.__handleTrackSelected,
            items=['ToonUp', 'Trap', 'Lure', 'Throw', 'Squirt', 'Sound', 'Drop']
        )
        self.gagButtons = []

    def __handleTrackSelected(self, track):
        print('Selected: %s' % track)

