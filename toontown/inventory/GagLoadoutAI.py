from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.showbase.DirectObject import DirectObject

from toontown.inventory import GagLoadoutGlobals


class GagLoadoutAI(DirectObject):
    notify = directNotify.newCategory('GagLoadoutAI')

    def __init__(self):
        DirectObject.__init__(self)
        self._loadout = []

    def setLoadout(self, loadout):
        self._loadout = sorted(loadout)
        self.notify.debug('Setting loadout %s' % self._loadout)

    def equipGag(self, gagId):
        if self.isFull() or self.isEquipped(gagId):
            return False
        self._loadout.append(gagId)
        self._loadout.sort()
        return True

    def removeGag(self, gagId):
        if self.isEmpty() or not self.isEquipped(gagId):
            return False
        self._loadout.remove(gagId)
        return True

    def isFull(self):
        return len(self._loadout) >= GagLoadoutGlobals.MAX_SLOTS

    def isEquipped(self, gagId):
        return gagId in self._loadout

    def isEmpty(self):
        return len(self._loadout) == 0

    def toList(self):
        return self._loadout
