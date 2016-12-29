from direct.gui.DirectGui import *
from direct.directnotify.DirectNotifyGlobal import directNotify
from toontown.toon.ClerkGagInventoryGui import ClerkGagInventoryGui
from toontown.toonbase import EventGlobals, ToontownGlobals
from toontown.util.PlacerTool3D import PlacerTool3D
from toontown.toontowngui.TTLabel import TTLabel
from toontown.toontowngui.TTSeperator import TTSeperator


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

