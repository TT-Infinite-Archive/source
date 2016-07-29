from pandac.PandaModules import *

from otp.movement.Impulse import Impulse
from otp.otpbase import OTPGlobals


class PetCollider(Impulse):
    def __init__(self, petRadius, collTrav):
        Impulse.__init__(self)

        self.petRadius = petRadius
        self.collTrav = collTrav
        self.vel = None
        self.rotVel = None
        self.vH = 0
        self.fwdCLine = CollisionSegment(0.0, 0.0, 0.0, 0.0, 1.0, 0.0)
        self.leftCLine = CollisionSegment(0.0, 0.0, 0.0, -1.0, 1.0, 0.0)
        self.rightCLine = CollisionSegment(0.0, 0.0, 0.0, 1.0, 1.0, 0.0)
        self.calcCollLines()
        cLineNode = CollisionNode('cLineNode')
        cLineNode.addSolid(self.fwdCLine)
        cLineNode.addSolid(self.leftCLine)
        cLineNode.addSolid(self.rightCLine)
        cLineNode.setFromCollideMask(OTPGlobals.WallBitmask)
        cLineNode.setIntoCollideMask(BitMask32.allOff())
        self.cLineNodePath = hidden.attachNewNode(cLineNode)
        self.cHandler = CollisionHandlerEvent()
        self.cHandler.addInPattern(self._getCollisionEvent())
        self.cHandler.addAgainPattern(self._getCollisionEvent())
        self.collTrav.addCollider(self.cLineNodePath, self.cHandler)

        self.accept(self._getCollisionEvent(), self.handleCollision)

    def setMover(self, mover):
        Impulse.setMover(self, mover)

        self.cLineNodePath.reparentTo(self.nodePath)
        self.vel = LVector3f(0)
        self.rotVel = LVector3f(0)

    def destroy(self):
        self.ignore(self._getCollisionEvent())
        self.collTrav.removeCollider(self.cLineNodePath)
        del self.cHandler
        del self.collTrav
        self.cLineNodePath.removeNode()
        del self.cLineNodePath
        del self.vel

    def calcCollLines(self):
        self.fwdCLine.setPointB(Point3(0, self.mover.getFwdSpeed(), 0))
        self.leftCLine.setPointB(Point3(-self.petRadius, self.petRadius, 0))
        self.rightCLine.setPointB(Point3(self.petRadius, self.petRadius, 0))

    def _getCollisionEvent(self):
        return 'petFeeler-%s' % id(self)

    def handleCollision(self, collEntry):
        cPoint = collEntry.getSurfacePoint(self.cLineNodePath)
        cNormal = collEntry.getSurfaceNormal(self.cLineNodePath)
        messenger.send(self.mover.getCollisionEventName(), [cPoint, cNormal])
