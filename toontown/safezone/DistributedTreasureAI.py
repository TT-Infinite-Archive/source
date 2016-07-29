from direct.distributed.DistributedObjectAI import DistributedObjectAI


class DistributedTreasureAI(DistributedObjectAI):
    def __init__(self, air, treasurePlanner, treasureType, x, y, z):
        DistributedObjectAI.__init__(self, air)

        self.treasurePlanner = treasurePlanner
        self.treasureType = treasureType
        self.pos = (x, y, z)

    def requestGrab(self, avId=None):
        if avId is None:
            avId = self.air.getAvatarIdFromSender()
        self.treasurePlanner.grabAttempt(avId, self.getDoId())

    def validAvatar(self, av):
        return True

    def getTreasureType(self):
        return self.treasureType

    def d_setGrab(self, avId):
        self.sendUpdate('setGrab', [avId])

    def d_setReject(self):
        self.sendUpdate('setReject', [])

    def getPosition(self):
        return self.pos

    def setPosition(self, x, y, z):
        self.pos = (x, y, z)

    def b_setPosition(self, x, y, z):
        self.setPosition(x, y, z)
        self.d_setPosition(x, y, z)

    def d_setPosition(self, x, y, z):
        self.sendUpdate('setPosition', [x, y, z])
