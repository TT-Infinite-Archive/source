from direct.distributed.DistributedObjectGlobalUD import DistributedObjectGlobalUD
from toontown.suit.MegaInvasionGlobals import *
from datetime import datetime
from toontown.parties.ToontownTimeZone import ToontownTimeZone

PARSE_INTERVAL = 60


class MegaInvasionManagerUD(DistributedObjectGlobalUD):
    notify = directNotify.newCategory('MegaInvasionManagerUD')

    def announceGenerate(self):
        DistributedObjectGlobalUD.announceGenerate(self)
        taskMgr.doMethodLater(10, self.parseInvasions, self.uniqueName('parseInvasions'))
        self.calledInvasion = None

    def parseInvasions(self, task):
        for invasion in invasions:
            if self.calledInvasion is not None:
                continue

            index = invasions.index(invasion)
            if index == self.calledInvasion:
                continue

            start = parseInvasionTime(invasion[START_TIME])
            end = parseInvasionTime(invasion[END_TIME])
            now = datetime.now(tz=ToontownTimeZone())
            if start < now < end:
                taskMgr.remove(self.uniqueName('endInvasion'))
                self.calledInvasion = index
                self.callInvasion(index)
                timeLeft = end - now
                taskMgr.doMethodLater(timeLeft.total_seconds(), self.endInvasion, self.uniqueName('endInvasion'),
                    extraArgs=[index], appendTask=False)

        taskMgr.doMethodLater(PARSE_INTERVAL, self.parseInvasions, self.uniqueName('parseInvasions'))

    def callInvasion(self, index):
        self.sendUpdate('callInvasion', [index])

    def endInvasion(self, index):
        self.calledInvasion = None
        self.sendUpdate('endInvasion', [index])

    def hello(self):
        if self.calledInvasion is not None:
            self.sendUpdateToChannel(self.air.getAvatarIdFromSender(), 'callInvasion', [self.calledInvasion])
