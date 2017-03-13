from direct.distributed.DistributedObject import DistributedObject


class DistributedStrikeParticipant(DistributedObject):
    def __init__(self, cr):
        DistributedObject.__init__(self, cr)

        self.strike = None
        self.avId = None
        self.points = None

        self.hp = None
        self.maxHp = None

    def setStrike(self, strike):
        self.strike = strike

    def setAvId(self, avId):
        self.avId = avId

    def setPoints(self, points):
        self.points = points

    def setHp(self, hp):
        self.hp = hp

    def setMaxHp(self, maxHp):
        self.maxHp = maxHp

    def isOurs(self):
        return self.avId == base.localAvatar.doId

    def announceGenerate(self):
        if self.isOurs():
            taskMgr.add(self.__broadcastPosition, 'broadcast-position-%s' % id(self))

    def __broadcastPosition(self, task):
        pos = base.localAvatar.getPos()
        self.sendUpdate('setPosition', [pos[0], pos[1]])
        return task.cont
