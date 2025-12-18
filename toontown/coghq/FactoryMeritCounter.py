from panda3d.core import CardMaker, NodePath, TextNode, Texture, TransparencyAttrib, VBase4
from toontown.toonbase.ToontownGlobals import getSuitFont
from direct.gui.DirectGui import DirectWaitBar, DirectFrame, DGG
from . import SuitTreasureGlobals


class FactoryMeritCounter(DirectFrame):
    def __init__(self, factory, treasureType, maxMerits, parent=aspect2d, **kw):
        DirectFrame.__init__(self, parent=parent, relief=None, **kw)
        self.factory = factory
        self.merits = 0
        self.treasureType = treasureType
        self.maxMerits = maxMerits
        self.accept('f6', self.__drainMeritBar)  # Debug

        self.filling = False
        self.barColor = SuitTreasureGlobals.TreasureColors[self.treasureType]

        self.meritBar = None
        self.meritBarImage = None
        self.ignore('stickerBookEntered')
        self.accept('stickerBookEntered', self.hide)
        self.ignore('stickerBookExited')
        self.accept('stickerBookExited', self.show)

    def load(self):
        filepath = 'phase_9/maps/sellbot-bar.png'
        tex = loader.loadTexture(filepath)
        cm = CardMaker(filepath + ' card')
        cm.setFrame(-tex.getOrigFileXSize(), tex.getOrigFileXSize(), -tex.getOrigFileYSize(), tex.getOrigFileYSize())
        self.meritBarImage = NodePath(cm.generate())
        self.meritBarImage.setTexture(tex)
        self.meritBarImage.setBin('background', 99)
        self.meritBar = DirectWaitBar(parent=self, geom=self.meritBarImage, geom_scale=(0.015, 1.0, 0.015),
                         geom_pos=(-1.65, 0.0, 0.0), relief=DGG.FLAT, scale=0.065, value=0.5, range=1, sortOrder=50,

                         frameSize=(-2.75, 2.35, -0.6, 0.6),
                         borderWidth=(0.02, 0.02),
                         frameColor=(0.5, 0.5, 0.5, 1.0), barColor=VBase4(0.85, 0.75, 0.75, 0.90),
                         text='', text_scale=0.75, text_fg=(1, 1, 1, 1), text_align=TextNode.ACenter,
                         text_pos=(0, -0.22))
        self.meritBar.setBin('background', 98)
        self.meritBar.setTransparency(TransparencyAttrib.MAlpha)
        self.__updateMeritBar(self.factory.currentMeritCount)
        self.setColorScale(1.0, 1.0, 1.0, 1.0)

    def setMeritBar(self, merits, immediate=False):
        # Method for adding or removing merits into this bar
        if immediate:
            self.merits = merits
            self.__updateMeritBar(merits)
            return

        if merits > self.merits:
            difference = merits - self.merits
        else:
            difference = -(self.merits - merits)
        self.merits = merits
        self.fillMeritBar(difference)

    def __updateMeritBar(self, merits):
        if self.meritBar is not None:
            merits = int(merits)
            self.meritBar.setProp('text', str(merits))
            self.meritBar.setProp('value', float(merits) / float(self.maxMerits))

    def __drainMeritBar(self):
        self.fillMeritBar(-self.merits, 5000)

    def __addMeritsTask(self, currentMerits, merits, goal, task=None):
        self.filling = True
        if currentMerits <= 0 and goal <= 0:
            # Looks like we want to empty the merit bar
            self.__updateMeritBar(self.merits)
            self.filling = False
            if task is not None:
                return task.done
        elif currentMerits >= goal and goal > 0:
            # We've reached the goal
            currentMerits = goal
            self.__updateMeritBar(currentMerits)
            self.filling = False
            if task is not None:
                return task.done
        else:
            currentMerits += int(round(merits))
            self.__updateMeritBar(currentMerits)
            taskMgr.doMethodLater(0.05, self.__addMeritsTask, 'addMerits', extraArgs=[currentMerits, merits, goal])

    def fillMeritBar(self, meritsToAdd, duration=300, task=None):
        # You could also use this for changing values in the merit bar
        if self.meritBar is None:
            return

        if duration >= 50:
            meritsPer = float(meritsToAdd) / (float(duration) / 200.0)
            # Smoothly fill merit bar every 0.05 seconds
            if self.filling:
                taskMgr.doMethodLater(0.05, self.fillMeritBar, 'fillMeritBar', extraArgs=[meritsToAdd, duration])
            else:
                # Get the merits that is current showing in the gui (the real merits was set before)
                currentMerits = self.merits - meritsToAdd
                self.__addMeritsTask(currentMerits, meritsPer, self.merits)
        else:
            # Instantly fill merit bar since duration is too low
            self.__updateMeritBar(meritsToAdd)
        if task is not None:
            return task.done

    def destroy(self):
        if self.meritBar:
            self.meritBar.destroy()
            self.meritBar = None
        if self.meritBarImage:
            del self.meritBarImage
        self.factory = None
        self.ignoreAll()
        DirectFrame.destroy(self)
