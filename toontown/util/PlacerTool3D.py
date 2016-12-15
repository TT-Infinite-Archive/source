from panda3d.core import TextNode
from direct.gui.DirectGui import DirectFrame, DGG, DirectButton

from toontown.toonbase import ToontownGlobals
from toontown.toontowngui import TTLabel
from toontown.util import PlacerTool


class PlacerTool3D(DirectFrame):
    def __init__(self, target, increment=0.05, parent=aspect2d, pos=(0.0, 0.0, 0.0)):
        DirectFrame.__init__(self, parent)
        self.target = target
        self.increment = increment
        self.mainFrame = DirectFrame(
            parent=self,
            relief=None,
            geom=DGG.getDefaultDialogGeom(),
            geom_color=ToontownGlobals.GlobalDialogColor,
            geom_scale=(0.75, 0.45, 0.45),
            pos=pos,
        )
        # Arrow gui (preload)
        gui = loader.loadModel('phase_3/models/gui/tt_m_gui_mat_mainGui.bam')
        # Target values
        scale = self.target.getScale()
        self.mainFrame.setBin('gui-popup', 0)
        # Pos
        pos = self.target.getPos()
        self.posLabel = TTLabel.TTLabel(
            self.mainFrame, text='Position: ', pos=(-0.35, 0.0, 0.105), text_align=TextNode.ALeft)
        self.xPosSpinner = PlacerToolSpinner(
            self.mainFrame, value=pos[0], pos=(-0.08, 0.0, 0.1), increment=increment, callback=self.handleXChange)
        self.yPosSpinner = PlacerToolSpinner(
            self.mainFrame, value=pos[1], pos=(0.06, 0.0, 0.1), increment=increment, callback=self.handleYChange)
        self.zPosSpinner = PlacerToolSpinner(
            self.mainFrame, value=pos[2], pos=(0.2, 0.0, 0.1), increment=increment, callback=self.handleZChange)
        # hpr
        hpr = self.target.getHpr()
        self.hprLabel = TTLabel.TTLabel(
            self.mainFrame, text='HPR: ', pos=(-0.35, 0.0, -0.105), text_align=TextNode.ALeft)
        self.hSpinner = PlacerToolSpinner(
            self.mainFrame, value=hpr[0], pos=(-0.08, 0.0, -0.11), increment=5, callback=self.handleHChange)
        self.pSpinner = PlacerToolSpinner(
            self.mainFrame, value=hpr[1], pos=(0.06, 0.0, -0.11), increment=5, callback=self.handlePChange)
        self.rSpinner = PlacerToolSpinner(
            self.mainFrame, value=hpr[2], pos=(0.2, 0.0, -0.11), increment=5, callback=self.handleRChange)

        gui.removeNode()
        gui = loader.loadModel('phase_3/models/gui/tt_m_gui_mat_nameShop')
        thumb = gui.find('**/tt_t_gui_mat_namePanelCircle')
        self.dragButton = DirectButton(
            self.mainFrame,
            relief=None,
            image=thumb,
            image_scale=(0.5, 0.5, 0.5),
            pos=(0.325, 0.0, 0.175)
        )
        self.dragButton.bind(DGG.B1PRESS, self.onPress)

    def handleXChange(self, value):
        self.changeTargetPos(0, value)

    def handleYChange(self, value):
        self.changeTargetPos(1, value)

    def handleZChange(self, value):
        self.changeTargetPos(2, value)

    def handleHChange(self, value):
        self.changeTargetHpr(0, value)

    def handlePChange(self, value):
        self.changeTargetHpr(1, value)

    def handleRChange(self, value):
        self.changeTargetHpr(2, value)

    def changeTargetPos(self, index, value):
        pos = self.target.getPos()
        pos[index] = value
        self.target.setPos(pos)

    def changeTargetHpr(self, index, value):
        hpr = self.target.getHpr()
        hpr[index] = value
        self.target.setHpr(hpr)

    def onPress(self, e=None):
        self.accept('mouse1-up', self.onRelease)
        taskMgr.add(self.mouseMoverTask, '%s-mouseMoverTask' % self.id)

    def onRelease(self, e=None):
        self.ignore('mouse1-up')
        taskMgr.remove('%s-mouseMoverTask' % self.id)

    def mouseMoverTask(self, task):
        if base.mouseWatcherNode.hasMouse():
            mpos = base.mouseWatcherNode.getMouse()
            self.setPos(render2d, mpos[0] - 0.18, 0, mpos[1] - 0.175)
        return task.cont


class PlacerToolSpinner(DirectFrame):
    def __init__(self, parent=render2d, pos=(0.0, 0.0, 0.0), scale=1.0, precision=2, value=0, callback=None, increment=0.01):
        DirectFrame.__init__(self, parent, pos=pos, scale=1.0)
        self.precision = precision
        self.increment = increment
        self.value = value
        self.callback = callback

        self.display = TTLabel.TTLabel(self, pos=(0.0, 0.0, 0.0))
        gui = loader.loadModel('phase_3/models/gui/tt_m_gui_mat_mainGui.bam')
        image = (
            gui.find('**/tt_t_gui_mat_shuffleArrowUp'),
            gui.find('**/tt_t_gui_mat_shuffleArrowDown'),
            gui.find('**/tt_t_gui_mat_shuffleArrowUp'),
            gui.find('**/tt_t_gui_mat_shuffleArrowDisabled')
        )
        self.upArrow = DirectButton(self,
            relief=None,
            image=image,
            image_scale=(0.6, 0.6, 0.6),
            image1_scale=(0.7, 0.7, 0.7),
            image2_scale=(0.7, 0.7, 0.7),
            pos=(0.0, 0.0, 0.08),
            command=self.__handleUpClicked
        )
        self.upArrow.setR(90)
        self.downArrow = DirectButton(
            self,
            relief=None,
            image=image,
            image_scale=(0.6, 0.6, 0.6),
            image1_scale=(0.7, 0.7, 0.7),
            image2_scale=(0.7, 0.7, 0.7),
            pos=(0.0, 0.0, -0.05),
            command=self.__handleDownClicked
        )
        self.downArrow.setR(-90)
        self.setValue(value)

    def setValue(self, value):
        self.value = value
        self.display['text'] = format(self.value, '.%df' % self.precision)

    def __handleUpClicked(self):
        self.value += self.increment
        self.setValue(self.value)
        if self.callback:
            self.callback(self.value)

    def __handleDownClicked(self):
        self.value -= self.increment
        self.setValue(self.value)
        if self.callback:
            self.callback(self.value)