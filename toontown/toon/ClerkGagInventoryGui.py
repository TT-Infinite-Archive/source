from direct.directnotify.DirectNotifyGlobal import directNotify
from toontown.toon.GagInventoryGui import GagInventoryGui


class ClerkGagInventoryGui(GagInventoryGui):
    notify = directNotify.newCategory('GagInventoryGui')

    def __init__(self, toon, pos, parent=aspect2d):
        GagInventoryGui.__init__(self, toon, pos, parent)
        self.mainFrame['geom'] = None
