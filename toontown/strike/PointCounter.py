from panda3d.core import NodePath, Vec3, TextNode

from toontown.toon import ToonDNA
from toontown.toon.ToonHead import ToonHead

from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectFrame import DirectFrame


class PointLabel:
    LABEL_POSITIONS = [
        (0, 0, 0),
        (-0.3, 0, 1.5),
        (-0.3, 0, 2.8),
        (-0.3, 0, 4.1),
    ]

    FONT = 'phase_3/models/fonts/ImpressBT.ttf'

    def __init__(self, counter, avId, index):
        self.counter = counter
        self.avId = avId
        self.index = index

        self.frame = None
        self.points = None
        self.name = None

    def initialize(self):
        self.frame = DirectFrame(parent=self.counter, frameSize=(-1.0, 1.0, -1.0, 1.0),
                                 pos=self.LABEL_POSITIONS[self.index], scale=1 if self.index == 0 else 0.6, relief=None)

        av = base.cr.doId2do[self.avId]
        color = ToonDNA.allColorsList[av.style.headColor]

        head = self.generateToonHead(av.style)
        scale = self.frame.attachNewNode('scale')
        head.reparentTo(scale)
        head.setH(-150)

        bMin, bMax = head.getTightBounds()
        center = (bMin + bMax) / 2.0
        head.setPos(-center[0], 2, -center[2])
        corner = Vec3(bMax - center)
        scale.setScale(1.0 / max(corner[0], corner[1], corner[2]))

        self.points = OnscreenText(parent=self.frame, font=loader.loadFont(self.FONT), text='', scale=0.8,
                                  pos=(0.95, 0.1, 0), align=TextNode.ALeft, fg=color, shadow=(0.1, 0.1, 0.1, 1))

        self.name = OnscreenText(parent=self.frame, font=loader.loadFont(self.FONT), text=av.name, scale=0.8,
                                  pos=(0.95, -0.6, 0), align=TextNode.ALeft, fg=color, shadow=(0.1, 0.1, 0.1, 1))

    def generateToonHead(self, style):
        head = ToonHead()
        head.setupHead(style, forGui=True)
        head.setDepthTest(True)
        head.setDepthWrite(True)
        head.setH(180)
        return head

    def updatePoints(self, points):
        self.points['text'] = str(points)


class PointCounter(NodePath):
    def __init__(self, strike):
        NodePath.__init__(self, 'point-counter')

        self.strike = strike
        self.pointLabels = {}

    def initialize(self):
        self.reparentTo(base.a2dBottomLeft)
        self.setScale(0.1)
        self.setPos(0.13, 0, 0.38)

        self.createLabel(self.strike.localParticipant, 0)
        for i, p in enumerate(self.strike.participants):
            self.createLabel(p, i+1)

    def createLabel(self, participant, index):
        label = PointLabel(self, participant.avId, index)
        label.initialize()
        label.updatePoints(participant.points)
        self.pointLabels[participant.avId] = label
