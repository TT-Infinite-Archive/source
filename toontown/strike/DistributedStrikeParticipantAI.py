from direct.distributed.DistributedObjectAI import DistributedObjectAI

from pandac.PandaModules import CollisionSphere, CollisionNode, NodePath


class DistributedStrikeParticipantAI(DistributedObjectAI):
    def __init__(self, air, strike, avId):
        DistributedObjectAI.__init__(self, air)

        self.strike = strike
        self.node = None
        self.flock = None
        self.activeSpheres = ['spawn1', 'spawn2']

        self.avId = avId
        self.points = 500
        self.hp = 30
        self.maxHp = 30

    def registerFlock(self, node, flock):
        self.node = node
        self.flock = flock

        cs = CollisionSphere(0, 0, 0, 2)
        cnp = self.node.attachNewNode(CollisionNode('cnode'))
        cnp.node().addSolid(cs)

    def setPosition(self, x, y):
        avId = self.air.getAvatarIdFromSender()
        if avId != self.avId:
            return

        self.node.setX(x)
        self.node.setY(y)

    def enterSpawnSphere(self, name):
        avId = self.air.getAvatarIdFromSender()
        if avId != self.avId:
            return

        if name in self.activeSpheres:
            self.activeSpheres.remove(name)
            self.activeSpheres.insert(0, name)
            return

        self.activeSpheres.insert(0, name)
        if len(self.activeSpheres) == 3:
            self.activeSpheres.pop()

    def getAvId(self):
        return self.avId

    def getPoints(self):
        return self.points

    def getHp(self):
        return self.hp

    def getMaxHp(self):
        return self.maxHp
