from panda3d.core import TextNode
from direct.gui.DirectGui import DirectLabel


class TTLabel(DirectLabel):
    TitleSize = 5
    GiantSize = 4
    LargeSize = 3
    MediumSize = 2
    NormalSize = 1
    SmallSize = 0
    Scales = {
        TitleSize: 0.12,
        GiantSize: 0.1,
        LargeSize: 0.072,
        MediumSize: 0.062,
        NormalSize: 0.052,
        SmallSize: 0.035
    }

    def __init__(self, parent=aspect2d, text_size=1, pos=(0.0, 0.0, 0.0), text_align=TextNode.ACenter, text_wordwrap=16, text='', **kw):
        scale = self.Scales.get(text_size, self.Scales[self.NormalSize])

        optiondefs = (
            ('relief', None, None),
            ('pos', pos, None),
            ('text_scale', scale, None),
            ('text_wordwrap', text_wordwrap, None),
            ('text', text, None),
            ('text_align', text_align, TextNode.ACenter)
        )

        self.defineoptions(kw, optiondefs)
        DirectLabel.__init__(self, parent)
        self.initialiseoptions(TTLabel)
