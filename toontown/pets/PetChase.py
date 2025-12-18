from panda3d.core import LVector3, LVector3f, NodePath
from direct.showbase.PythonUtil import reduceAngle
from otp.movement.Impulse import Impulse
import math


class PetChase(Impulse):
    def __init__(self, target=None, minDist=None, moveAngle=None):
        Impulse.__init__(self)

        self.target = target
        if minDist is None:
            minDist = 5.0
        self.minDist = minDist
        if moveAngle is None:
            moveAngle = 20.0
        self.moveAngle = moveAngle
        self.lookAtNode = NodePath('lookatNode')
        self.vel = None
        self.rotVel = None

    def setTarget(self, target):
        self.target = target

    def getTarget(self):
        return self.target

    def destroy(self):
        del self.target
        del self.vel
        del self.rotVel

    def setMover(self, mover):
        Impulse.setMover(self, mover)

        self.lookAtNode.reparentTo(self.nodePath)
        self.vel = LVector3f(0)
        self.rotVel = LVector3f(0)

    def process(self, dt):
        me = self.nodePath
        target = self.target
        if target.isEmpty() or me.isEmpty():
            return
        targetPos = target.getPos(me)
        x = targetPos[0]
        y = targetPos[1]
        distance = math.sqrt(x * x + y * y)
        self.lookAtNode.lookAt(target)
        relH = reduceAngle(self.lookAtNode.getH(me))
        epsilon = 0.005
        rotSpeed = self.mover.getRotSpeed()
        if relH < -epsilon:
            vH = -rotSpeed
        elif relH > epsilon:
            vH = rotSpeed
        else:
            vH = 0
        if abs(vH * dt) > abs(relH):
            vH = relH / dt
        if distance > self.minDist and abs(relH) < self.moveAngle:
            vForward = self.mover.getFwdSpeed()
        else:
            vForward = 0
        distanceLeft = distance - self.minDist
        if distance > self.minDist and vForward * dt > distanceLeft:
            vForward = distanceLeft / dt
        if vForward:
            self.vel.setY(vForward)
            self.mover.addShove(self.vel)
        if vH:
            self.rotVel.setX(vH)
            self.mover.addRotShove(self.rotVel)

    def setMinDist(self, minDist):
        self.minDist = minDist
