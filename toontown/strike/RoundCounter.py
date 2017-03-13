from panda3d.core import NodePath, TextNode, Vec4

from direct.interval.IntervalGlobal import *


class RoundCounter(NodePath):
    FONT = 'phase_3/models/fonts/vtRemingtonPortable.ttf'
    ROUND_END_SFX = 'phase_4/audio/corpstrike/ost_round_end.ogg'
    ROUND_START_SFX = 'phase_4/audio/corpstrike/ost_round_start.ogg'

    def __init__(self):
        NodePath.__init__(self, 'round-counter')

        self.round = None

    def initialize(self):
        self.reparentTo(base.a2dBottomLeft)
        self.setPos(0.055, 0, 0.06)

    def generateRoundText(self, round):
        tn = TextNode('round-text')
        tn.setText(str(round))
        tn.setFont(loader.loadFont(self.FONT))
        tn.setTextColor(0.15, 0.15, 0.15, 1.0)
        tn.setShadow(0.05, 0.05)
        tn.setShadowColor(0.3, 0.3, 0.3, 1)
        return tn

    def removeRoundText(self):
        self.find('**/*round-text').removeNode()

    def attachRoundText(self, text):
        node = self.attachNewNode(text)
        node.setName('round-text')
        node.setScale(0.3)

    def transitionRound(self, round):
        newText = self.generateRoundText(round)

        if self.round is not None:
            roundEnd = Sequence(
                Parallel(
                    Sequence(
                        Func(self.setTransparency, 1),
                        LerpColorScaleInterval(self, 3, Vec4(1, 1, 1, 0), startColorScale=Vec4(1, 1, 1, 1)),
                        Func(self.clearColorScale),
                        Func(self.clearTransparency),
                        Func(self.hide)
                    ),
                    Func(base.playSfx, loader.loadSfx(self.ROUND_END_SFX), volume=0.25),
                ),
                Func(self.removeRoundText),
                Wait(5)
            )
        else:
            roundEnd = Sequence()

        roundStart = Parallel(
            Sequence(
                Func(self.attachRoundText, newText),
                Sequence(
                    Func(self.show),
                    Func(self.setTransparency, 1),
                    LerpColorScaleInterval(self, 4, Vec4(1, 1, 1, 1), startColorScale=Vec4(1, 1, 1, 0)),
                    Func(self.clearColorScale),
                    Func(self.clearTransparency)
                 ),
            ),
            Func(base.playSfx, loader.loadSfx(self.ROUND_START_SFX), volume=0.25),
        )

        Sequence(
            roundEnd,
            roundStart,
        ).start()

        self.round = round
