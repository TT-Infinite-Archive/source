from panda3d.core import NodePath
from direct.showbase.PythonUtil import randFloat, normalDistrib

from toontown.pets.PetChase import PetChase


class PetWander(PetChase):
    def __init__(self, minDist=5.0, moveAngle=20.0):
        self.movingTarget = hidden.attachNewNode('petWanderTarget')

        PetChase.__init__(self, self.movingTarget, minDist, moveAngle)

        self.targetMoveCountdown = 0
        self.collEvent = None
        self.gotCollision = False

    def __ignoreCollisions(self):
        if self.collEvent is not None:
            self.ignore(self.collEvent)
            self.collEvent = None

    def setMover(self, mover):
        PetChase.setMover(self, mover)

        self.mover = mover
        self.__ignoreCollisions()
        self.collEvent = mover.getCollisionEventName()
        self.accept(self.collEvent, self._handleCollision)

    def clearMover(self):
        PetChase.clearMover(self)

        self.__ignoreCollisions()

    def _handleCollision(self, collEntry):
        self.gotCollision = True
        if self.target.isEmpty():
            self.gotCollision = False
            return
        self.target.setPos(self.getNodePath().getPos())
        self.targetMoveCountdown *= 0.5

    def destroy(self):
        self.__ignoreCollisions()
        if hasattr(self, 'movingTarget'):
            self.movingTarget.removeNode()
            del self.movingTarget

    def process(self, dt):
        self.targetMoveCountdown -= dt
        if self.targetMoveCountdown <= 0.0:
            distance = normalDistrib(3.0, 30.0)
            heading = normalDistrib(-(90 + 45), 90 + 45)
            if self.gotCollision:
                self.gotCollision = False
                heading += 180
            target = self.getTarget()
            if target.isEmpty():
                return
            target.setPos(self.getNodePath().getPos())
            target.setH(target, heading)
            target.setY(target, distance)
            duration = distance / self.mover.getFwdSpeed()
            self.targetMoveCountdown = duration * randFloat(1.2, 3.0)

        PetChase.process(self, dt)
