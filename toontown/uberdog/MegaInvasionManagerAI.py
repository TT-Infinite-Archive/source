from direct.distributed.DistributedObjectGlobalAI import DistributedObjectGlobalAI
from toontown.suit.MegaInvasionGlobals import *
from toontown.suit.SuitInvasionGlobals import *

import random
from time import time


class MegaInvasionManagerAI(DistributedObjectGlobalAI):
    notify = directNotify.newCategory('MegaInvasionManagerAI')

    def announceGenerate(self):
        DistributedObjectGlobalAI.announceGenerate(self)
        self.air.netMessenger.accept('shardStatus', self, self.handleShardStatus)
        self.recallInvasion = False
        self.waitingOnStatus = False
        self.index = None
        self.currentTask = ''
        self.sendHello()

    def sendHello(self):
        self.sendUpdate('hello', [])

    def callInvasion(self, index):
        if self.air.distributedDistrict.name in safeShards:
            return

        self.index = index
        invasion = invasions[index]

        if self.currentTask is not None:
            taskMgr.remove(self.currentTask)
            self.currentTask = ''

        if self.air.suitInvasionManager.invading is True:
            self.waitingOnStatus = True
            return

        if datetime.now(tz=ToontownTimeZone()) > parseInvasionTime(invasion[END_TIME]):
            self.recallInvasion = False
            self.index = None
            self.waitingOnStatus = False
            taskMgr.remove(self.uniqueName('recallInvasion-%d' % index))
            return

        suitDept, suitIndex, amount = invasion[SUIT_DEPT], invasion[SUIT_INDEX], invasion[SUIT_AMOUNT]

        random.seed(time() + self.air.ourChannel)

        if suitDept == RANDOM:
            suitDept = random.choice(range(0, 4))

        if suitIndex == RANDOM:
            suitIndex = random.choice(range(0, 8))

        if amount == RANDOM:
            amount = int(random.random() * 10000) + 1000

        flagChance = invasion[FLAG_CHANCE]

        if random.random() < flagChance:
            flags = random.choice([IFSkelecog, IFV2, IFWaiter])
        else:
            flags = 0

        self.air.suitInvasionManager.startInvasion(suitDeptIndex=suitDept,
                                                   suitTypeIndex=suitIndex,
                                                   flags=flags,
                                                   invasionType=INVASION_TYPE_MEGA,
                                                   amount=amount)

        holidayId = invasion[HOLIDAY_ID]

        if holidayId is not None and not self.air.holidayManager.isHolidayRunning(holidayId):
            self.air.holidayManager.appendHoliday(holidayId)
            self.air.holidayManager.startHoliday(holidayId)

        if invasion[REOCCURING]:
            self.recallInvasion = True
            self.currentTask = self.uniqueName('recallInvasion-%d' % self.index)

    def endInvasion(self, index):
        self.recallInvasion = False
        self.index = None
        self.waitingOnStatus = False
        taskMgr.remove(self.uniqueName('recallInvasion-%d' % index))
        self.air.suitInvasionManager.stopInvasion()

    def handleShardStatus(self, channel, status):
        if self.index is None:
            return

        if channel != self.air.ourChannel:
            return

        if status.get('invasion') is None and self.waitingOnStatus:
            self.waitingOnStatus = False
            self.callInvasion(self.index)
            return

        if status.get('invasion') is None and self.recallInvasion:
            random.seed(time() + self.air.ourChannel)
            delay = random.randint(5, 1800)
            self.currentTask = self.uniqueName('recallInvasion-%d' % self.index)
            if self.currentTask is not None:
                taskMgr.doMethodLater(delay, self.callInvasion, self.currentTask, extraArgs=[self.index], appendTask=False)
                return
