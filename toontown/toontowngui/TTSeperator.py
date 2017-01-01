from direct.gui.DirectGui import DirectFrame, DGG
from toontown.toonbase.ColorGlobals import CBlack


class TTSeperator(DirectFrame):
    def __init__(self, parent=aspect2d, width=0.002, length=0.8, pos=(0.0, 0.0, 0.0)):
        frameSize = (-length, length, -width, width)
        DirectFrame.__init__(self, parent, relief=None, pos=pos)
        self.mainFrame = DirectFrame(self, relief=DGG.FLAT, frameSize=frameSize, frameColor=CBlack)
