from direct.gui.DirectGui import DirectFrame, DGG
from toontown.toonbase import ToontownGlobals


class TTFrame(DirectFrame):
    def __init__(self, parent=aspect2d, **kw):
        optiondefs = (
            ('relief', None, None),
            ('geom', DGG.getDefaultDialogGeom(), None),
            ('geom_color', ToontownGlobals.GlobalDialogColor, (1.0, 1.0, 1.0, 1.0))
        )

        self.defineoptions(kw, optiondefs)
        DirectFrame.__init__(self, parent)
        self.initialiseoptions(TTFrame)

