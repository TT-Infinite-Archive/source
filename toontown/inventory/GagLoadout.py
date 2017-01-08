from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.showbase.DirectObject import DirectObject

from toontown.toonbase import EventGlobals
from toontown.inventory import GagLoadoutGlobals


class GagLoadout(DirectObject):
    notify = directNotify.newCategory('GagLoadout')

    def __init__(self):
        DirectObject.__init__(self)
        self._loadout = []

    def getLoadout(self):
        return self._loadout

    def isFull(self):
        return len(self._loadout) >= GagLoadoutGlobals.MAX_SLOTS

    def isEmpty(self):
        return len(self._loadout) == 0

    def setLoadout(self, loadout):
        self.notify.debug('Setting new loadout: %s' % loadout)
        self._loadout = sorted(loadout)
        messenger.send(EventGlobals.LoadoutChanged)
