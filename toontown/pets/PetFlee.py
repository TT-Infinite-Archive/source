from panda3d.core import LVector3f, NodePath

from direct.showbase.PythonUtil import reduceAngle
from otp.movement.Impulse import Impulse


class PetFlee(Impulse):

    def __init__(self, chaser=None, maxDist=50.0, moveAngle=20.0):
        Impulse.__init__(self)

        self.chaser = chaser
        self.maxDist = maxDist
        self.moveAngle = moveAngle
        self.lookAtNode = NodePath('lookatNode')
        self.lookAtNode.hide()
        self.vel = None
        self.rotVel = None

    def destroy(self):
        self.lookAtNode.removeNode()
        del self.lookAtNode
        del self.chaser
        del self.vel
        del self.rotVel

    def setChaser(self, chaser):
        self.chaser = chaser

    def setMover(self, mover):
        Impulse.setMover(self, mover)

        self.lookAtNode.reparentTo(self.nodePath)
        self.vel = LVector3f(0)
        self.rotVel = LVector3f(0)

    def process(self, dt):
        me = self.nodePath
        chaser = self.chaser
        chaserPos = chaser.getPos(me)
        chaserPos.setZ(0)
        distance = LVector3f(chaserPos).length()
        self.lookAtNode.lookAt(chaser)
        relH = reduceAngle(self.lookAtNode.getH(me) + 180.0)
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
        if distance < self.maxDist and abs(relH) < self.moveAngle:
            vForward = self.mover.getFwdSpeed()
        else:
            vForward = 0
        distanceLeft = self.maxDist - distance
        if distanceLeft > 0.0 and vForward * dt > distanceLeft:
            vForward = distanceLeft / dt
        self.vel.setY(vForward)
        self.rotVel.setX(vH)
        self.mover.addShove(self.vel)
        self.mover.addRotShove(self.rotVel)
