from direct.gui.DirectGui import *
from direct.directnotify.DirectNotifyGlobal import directNotify
from toontown.util import TTCardMaker
from toontown.toon.GagInventoryGui import GagInventoryGui
from toontown.toonbase import EventGlobals, ToontownGlobals


class GagSelectGui(DirectFrame):
    notify = directNotify.newCategory('GagSelectGui')

    def __init__(self, toon):
        self.notify.debug('Loading...')
        DirectFrame.__init__(self, parent=aspect2d, relief=None)
        self.initialiseoptions(GagSelectGui)
        self.gagInventory = GagInventoryGui(base.localAvatar, (0, 0, 0))
        self.gagCacheFrame = DirectFrame(
            self,
            relief=None,
            pos=(0.0, 0.0, 0.0),
            geom=DGG.getDefaultDialogGeom(),
            geom_scale=(1.65, 1, 0.4),
            geom_color=ToontownGlobals.GlobalDialogColor
        )
