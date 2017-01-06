from panda3d.core import LVector3f
from otp.movement import Impulse

class PetLeash(Impulse.Impulse):

    def __init__(self, origin, length):
        Impulse.Impulse.__init__(self)
        self.origin = origin
        self.length = length

    def process(self, dt):
        Impulse.Impulse.process(self, dt)
        myPos = self.nodePath.getPos()
        myDist = LVector3f(myPos - self.origin.getPos()).length()
        if myDist > self.length:
            excess = myDist - self.length
            shove = LVector3f(myPos)
            shove.normalize()
            shove *= -excess
            self.mover.addShove(shove)
