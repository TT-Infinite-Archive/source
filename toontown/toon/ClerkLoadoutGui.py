from direct.directnotify.DirectNotifyGlobal import directNotify
from toontown.toon.LoadoutGui import LoadoutGui


class ClerkLoadoutGui(LoadoutGui):
    notify = directNotify.newCategory('GagInventoryGui')

    def __init__(self, toon, pos, parent=aspect2d):
        LoadoutGui.__init__(self, toon, pos, parent)
        self.mainFrame['geom'] = None
