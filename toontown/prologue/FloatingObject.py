from pandac.PandaModules import *
from direct.interval.IntervalGlobal import *


class FloatingObject(NodePath):
    def __init__(self, parent):
        NodePath.__init__(self, 'floating-%s' % parent.getNumChildren())
        self.reparentTo(parent)

        self.animation = None

    def setup(self, animationIntensity):
        pos = self.getPos()
        self.animation = Sequence(
            LerpPosInterval(
                self,
                duration=8,
                pos=pos + Point3(0, 0, animationIntensity),
                blendType='easeInOut'
            ),
            LerpPosInterval(
                self,
                duration=8,
                pos=pos,
                blendType='easeInOut'
            )
        )
        self.animation.loop()

    def destroy(self):
        self.removeNode()

        if self.animation is not None:
            self.animation.finish()
            self.animation = None
