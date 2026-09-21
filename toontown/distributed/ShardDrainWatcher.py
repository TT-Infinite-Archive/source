"""
Moving the local Toon off a district that is closing.
"""
from panda3d.core import ConfigVariableInt

from direct.directnotify import DirectNotifyGlobal
from direct.showbase.DirectObject import DirectObject

from toontown.hood import ZoneUtil
from toontown.toonbase import TTLocalizer


class ShardDrainWatcher(DirectObject):
    notify = DirectNotifyGlobal.directNotify.newCategory('ShardDrainWatcher')

    POLL_TASK = 'ShardDrainWatcher-poll'

    def __init__(self, cr):
        self.cr = cr
        self.watching = False

        self.accept('shardDrainingChanged', self.handleDrainingChanged)

        self.accept('shardInfoUpdated', self.check)

    def delete(self):
        self.stop()
        self.ignoreAll()

    def ourDistrict(self):
        avatar = getattr(base, 'localAvatar', None)

        if avatar is None:
            return None

        return self.cr.activeDistrictMap.get(avatar.defaultShard)

    def handleDrainingChanged(self, doId, draining):
        district = self.ourDistrict()

        if district is None or district.doId != doId:
            return

        if draining:
            self.start()
        else:
            self.stop()

    def check(self):
        district = self.ourDistrict()

        if district is not None and district.draining:
            self.start()

    def start(self):
        if self.watching:
            return

        self.watching = True

        self.notify.info('%s is draining; looking for a way out.'
                         % self.cr.getShardName(base.localAvatar.defaultShard))

        base.localAvatar.setSystemMessage(0, TTLocalizer.ShardDrainingNotice)

        interval = ConfigVariableInt('drain-relocate-poll-seconds', 10).getValue()
        taskMgr.doMethodLater(interval, self.__poll, self.POLL_TASK)

    def stop(self):
        taskMgr.remove(self.POLL_TASK)
        self.watching = False

    def canMove(self):
        avatar = getattr(base, 'localAvatar', None)

        if avatar is None:
            return False

        if not avatar.getTeleportAvailable():
            return False

        if avatar.hasActiveBoardingGroup():
            return False

        return self.place() is not None

    def place(self):
        playGame = getattr(self.cr, 'playGame', None)

        if playGame is None:
            return None

        return playGame.getPlace()

    def __poll(self, task):
        district = self.ourDistrict()

        if district is None or not district.draining:
            self.stop()
            return task.done

        if not self.canMove():
            return task.again

        target = self.cr.getStartingDistrict()

        if target is None or target.doId == district.doId:
            # Nowhere better to be. Try again because one may come back up
            return task.again

        self.notify.info('Moving to %s.' % target.name)

        base.localAvatar.setSystemMessage(
            0, TTLocalizer.ShardDrainingMoving % target.name)

        hoodId = ZoneUtil.getCanonicalHoodId(base.localAvatar.lastHood)
        self.place().requestTeleport(hoodId, hoodId, target.doId, -1)

        self.stop()
        return task.done
