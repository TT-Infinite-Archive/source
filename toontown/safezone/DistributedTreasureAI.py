from direct.distributed.DistributedObjectAI import DistributedObjectAI

# TODO TTI: valentines day treasure
class DistributedTreasureAI(DistributedObjectAI):

    def __init__(self, air, treasurePlanner, treasureType, x, y, z):
        DistributedObjectAI.__init__(self, air)
        self.treasurePlanner = treasurePlanner
        self.treasureType = treasureType
        self.pos = (x, y, z)

    def requestGrab(self):
        # This is the handler that gets called when a localToon tries to grab
        # a DistributedTreasure
        avId = self.air.getAvatarIdFromSender()
        self.treasurePlanner.grabAttempt(avId, self.getDoId())

    def d_setGrab(self, avId):
        # This is how the treasurePlanner tells everyone that this treasure
        # has been grabbed.
        self.sendUpdate("setGrab", [avId])

    def d_setReject(self):
        # This is how the treasurePlanner tells everyone that this treasure
        # has been attempted for, but rejected.
        self.sendUpdate("setReject", [])

    def getTreasureType(self):
        return self.treasureType

    def getPosition(self):
        # This is needed because setPosition is a required field.
        return self.pos

    def setPosition(self, x, y, z):
        self.pos = (x, y, z)

    def b_setPosition(self, x, y, z):
        self.setPosition(x, y, z)
        self.d_setPosition(x, y, z)

    def d_setPosition(self, x, y, z):
        # This is how the treasurePlanner tells everyone that this treasure
        # has been attempted for, but rejected.
        self.sendUpdate("setPosition", [x, y, z])