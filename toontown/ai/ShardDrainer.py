"""
Closing a district down without dropping the Toons standing in it.
"""
import time

from panda3d.core import ConfigVariableInt

from direct.directnotify import DirectNotifyGlobal
from direct.distributed.MsgTypes import CLIENTAGENT_EJECT
from direct.distributed.PyDatagram import PyDatagram
from direct.showbase.DirectObject import DirectObject

BOOT_DISTRICT_RESET = 153


class ShardDrainer(DirectObject):
    notify = DirectNotifyGlobal.directNotify.newCategory('ShardDrainer')

    POLL_TASK = 'ShardDrainer-poll'

    def __init__(self, air):
        self.air = air
        self.draining = False
        self.deadline = 0

    def isDraining(self):
        return self.draining

    def start(self, reason='Requested.'):
        """
        Closes the district off. Returns None, or why it would not start.
        """
        if self.draining:
            return 'This district is already draining.'

        district = getattr(self.air, 'distributedDistrict', None)

        if district is None:
            return 'This district is still starting up.'

        grace = ConfigVariableInt('drain-grace-seconds', 180).getValue()

        self.draining = True
        self.deadline = time.time() + grace

        self.notify.info('Draining: %s Grace period is %ds.' % (reason, grace))

        district.b_setAvailable(0)
        district.b_setDraining(1)

        interval = ConfigVariableInt('drain-poll-seconds', 5).getValue()
        taskMgr.doMethodLater(interval, self.__poll, self.POLL_TASK)

        return None

    def __poll(self, task):
        remaining = self.air.playerToons()

        if not remaining:
            self.notify.info('Everyone has moved off. Shutting down.')
            self.__finish()
            return task.done

        if time.time() >= self.deadline:
            self.notify.info('Grace period is up with %d Toon(s) left; '
                             'they are being sent back to the district list.'
                             % len(remaining))
            for av in remaining:
                self.__eject(av)

            self.__finish()
            return task.done

        return task.again

    def __eject(self, av):
        datagram = PyDatagram()
        datagram.addServerHeader(
            av.GetPuppetConnectionChannel(av.doId),
            self.air.ourChannel, CLIENTAGENT_EJECT)
        datagram.addUint16(BOOT_DISTRICT_RESET)
        datagram.addString('This district is closing for an update.')
        self.air.send(datagram)

    def __finish(self):
        self.air.statusReporter.update({'available': False, 'draining': False})
        self.air.statusReporter.flush()
        self.air.statusReporter.stop()

        taskMgr.stop()
