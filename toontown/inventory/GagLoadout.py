from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.showbase.DirectObject import DirectObject

from toontown.toonbase import EventGlobals
from toontown.inventory import GagLoadoutGlobals
from toontown.data.Gag import Gags


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

    def isEquipped(self, gag):
        return gag in self._loadout

    def setLoadout(self, loadout):
        self.notify.debug('Setting new loadout: %s' % loadout)
        # Convert the loadout of gag ids to gag objects
        self._loadout = [Gags[gagId] for gagId in loadout]
        messenger.send(EventGlobals.LoadoutChanged)

    def getGagAtSlot(self, slot):
        return self._loadout[slot]
