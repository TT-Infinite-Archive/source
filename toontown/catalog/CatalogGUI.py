from direct.gui.DirectGui import DirectButton
from toontown.toonbase.TTLocalizer import CatalogNew, CatalogBackorder, CatalogLoyalty
from toontown.toonbase.ToontownGlobals import getSignFont

preloaded = {}


def loadModels():
    if not preloaded:
        gui = loader.loadModel('phase_5.5/models/gui/catalog_gui')
        preloaded['newDown'] = gui.find('**/new1')
        preloaded['newUp'] = gui.find('**/new2')
        preloaded['backDown'] = gui.find('**/previous2')
        preloaded['backUp'] = gui.find('**/previous1')
        preloaded['giftToggleUp'] = gui.find('**/giftButtonUp')
        preloaded['giftToggleDown'] = gui.find('**/giftButtonDown')
        preloaded['giftFriends'] = gui.find('**/gift_names')
        gui.removeNode()
        del gui

    TabImage = {
        NEW: (preloaded['newDown'], preloaded['newDown'], preloaded['newDown'], preloaded['newUp']),
        BACKORDER: (preloaded['backDown'], preloaded['backDown'], preloaded['backDown'], preloaded['backUp']),
        LOYALTY: (preloaded['newDown'], preloaded['newDown'], preloaded['newDown'], preloaded['newUp']),
        EMBLEM: (preloaded['backDown'], preloaded['backDown'], preloaded['backDown'], preloaded['backUp']),
    }


NEW = 0
BACKORDER = 1
LOYALTY = 2
EMBLEM = 3

TabText = {
    NEW: CatalogNew,
    BACKORDER: CatalogBackorder,
    LOYALTY: CatalogLoyalty,
}

TabImage = {
}

TabTextFG = {
    NEW: ((0.353, 0.627, 0.627, 1.0), (0.353, 0.427, 0.427, 1.0)),
    BACKORDER: ((0.392, 0.549, 0.627, 1.0), (0.392, 0.349, 0.427, 1.0)),
    LOYALTY: ((0.353, 0.627, 0.627, 1.0), (0.353, 0.427, 0.427, 1.0)),
    EMBLEM: ((0.353, 0.627, 0.627, 1.0), (0.353, 0.427, 0.427, 1.0)),
}

TabFrameSize = {
    NEW: (-0.2, 0.25, 0.45, 1.2),
    BACKORDER: (-0.2, 0.25, -0.2, 0.4),
    LOYALTY: (-0.2, 0.25, -0.85, -0.3),
    EMBLEM: (-0.2, 0.25, -2.0, -1.45),
}

TabTextScale = {
    NEW: 0.08,
    BACKORDER: 0.065,
    LOYALTY: 0.065,
    EMBLEM: 0.065,
}

TabImagePos = {
    NEW: (0.0, 0.0, 0.4),
    BACKORDER: (0.0, 0.0, 0.4),
    LOYALTY: (0.0, 0.0, -1.0),
    EMBLEM: (0.0, 0.0, -1.5),
}


class CatalogTabButton(DirectButton):
    def __init__(self, category=NEW, **kw):
        loadModels()
        self.category = category

        optiondefs = (
            ('image', TabImage[category], None),
            ('pressEffect', 0, None),
            ('image_pos', TabImagePos[category], None),
            ('image_scale', (1.0, 1.0, 0.75), None),
            ('relief', None, None),
            ('text', TabText[category], None),
            ('text_font', getSignFont(), None),
            ('text_scale', TabTextScale[category], None),
            ('text_fg', TabTextFG[category][0], None),
            ('text_fg2', TabTextFG[category][1], None),
        )

        self.defineoptions(kw, optiondefs)
        DirectButton.__init__(self, kw['parent'])
        self.initialiseoptions(CatalogTabButton)

    def toggleDisabled(self, disable):
        if disable:
            self.setProp('image', TabImage[self.category][0])
            self.disabled = False
        else:
            self.setProp('image', TabImage[self.category])
            self.disabled = True
