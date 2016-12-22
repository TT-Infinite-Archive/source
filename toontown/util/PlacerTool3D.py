from panda3d.core import TextNode
from direct.gui.DirectGui import DirectFrame, DGG, DirectButton

from toontown.toonbase import ToontownGlobals
from toontown.toontowngui import TTLabel
from toontown.util import PlacerTool


class PlacerTool3D(DirectFrame):
    ORIGINAL_SCALE = (0.85, 1.0, 0.85)
    MINIMIZED_SCALE = (0.85, 1.0, 0.15)
    ORIG_DRAG_BUTTON_POS = (0.37, 0.0, 0.37)
    MINI_DRAG_BUTTON_POS = (0.37, 0.0, 0.03)
    ORIG_MINI_BUTTON_POS = (0.29, 0.0, 0.37)
    MINI_MINI_BUTTON_POS = (0.29, 0.0, 0.03)
    ORIG_NAME_POS = (-0.39, 0.0, 0.27)
    MINI_NAME_POS = (-0.39, 0.0, 0.0)

    def __init__(self, target, increment=0.05, parent=aspect2d, pos=(0.0, 0.0, 0.0)):
        DirectFrame.__init__(self, parent)
        self.target = target
        self.increment = increment
        self.minimized = False
        self.mainFrame = DirectFrame(
            parent=self,
            relief=None,
            geom=DGG.getDefaultDialogGeom(),
            geom_color=ToontownGlobals.GlobalDialogColor,
            geom_scale=self.ORIGINAL_SCALE,
            pos=pos,
        )
        # Arrow gui (preload)
        gui = loader.loadModel('phase_3/models/gui/tt_m_gui_mat_mainGui.bam')
        # Set Bins
        self.mainFrame.setBin('gui-popup', 0)
        # Name
        name = self.target.getName()
        self.nameLabel = TTLabel.TTLabel(
            self.mainFrame, text='Target: %s' % name, pos=(-0.39, 0.0, 0.27), text_align=TextNode.ALeft, text_wordwrap=13)
        # Pos
        pos = self.target.getPos()
        self.posLabel = TTLabel.TTLabel(
            self.mainFrame, text='Position: ', pos=(-0.39, 0.0, 0.055), text_align=TextNode.ALeft)
        self.xPosSpinner = PlacerToolSpinner(
            self.mainFrame, value=pos[0], pos=(-0.085, 0.0, 0.06), increment=increment, callback=self.handleXChange)
        self.yPosSpinner = PlacerToolSpinner(
            self.mainFrame, value=pos[1], pos=(0.1, 0.0, 0.06), increment=increment, callback=self.handleYChange)
        self.zPosSpinner = PlacerToolSpinner(
            self.mainFrame, value=pos[2], pos=(0.28, 0.0, 0.06), increment=increment, callback=self.handleZChange)
        # hpr
        hpr = self.target.getHpr()
        self.hprLabel = TTLabel.TTLabel(
            self.mainFrame, text='HPR: ', pos=(-0.39, 0.0, -0.19), text_align=TextNode.ALeft)
        self.hSpinner = PlacerToolSpinner(
            self.mainFrame, value=hpr[0], pos=(-0.085, 0.0, -0.195), increment=5, callback=self.handleHChange)
        self.pSpinner = PlacerToolSpinner(
            self.mainFrame, value=hpr[1], pos=(0.1, 0.0, -0.195), increment=5, callback=self.handlePChange)
        self.rSpinner = PlacerToolSpinner(
            self.mainFrame, value=hpr[2], pos=(0.28, 0.0, -0.195), increment=5, callback=self.handleRChange)
        # scale
        scale = [self.target.getScale()[0], self.target.getScale()[1], self.target.getScale()[2]]
        self.scaleLabel = TTLabel.TTLabel(
            self.mainFrame, text='Scale: %s' % scale, pos=(-0.39, 0.0, -0.35), text_align=TextNode.ALeft)

        gui.removeNode()
        gui = loader.loadModel('phase_3/models/gui/tt_m_gui_mat_nameShop')
        thumb = gui.find('**/tt_t_gui_mat_namePanelCircle')
        self.dragButton = DirectButton(
            self.mainFrame,
            relief=None,
            image=thumb,
            image_scale=(0.5, 0.5, 0.5),
            pos=(0.37, 0.0, 0.37)
        )
        self.minimizeButton = DirectButton(
            self.mainFrame,
            relief=None,
            image=thumb,
            image_scale=(0.5, 0.5, 0.5),
            image_color=(0.0, 0.0, 0.65, 1.0),
            pos=(0.29, 0.0, 0.37),
            command=self.toggleMinimize,
            extraArgs=[]
        )
        self.dragButton.bind(DGG.B1PRESS, self.onPress)
        PlacerTool.PlacerTool(self.xPosSpinner, increment=0.005)
        PlacerTool.PlacerTool(self.yPosSpinner, increment=0.005)
        PlacerTool.PlacerTool(self.zPosSpinner, increment=0.005)

    def destroy(self):
        self.target = None
        DirectFrame.destroy(self)

    def setTarget(self, target):
        self.target = target
        name = self.target.getName()
        scale = [self.target.getScale()[0], self.target.getScale()[1], self.target.getScale()[2]]
        x, y, z = self.target.getPos()
        h, p, r = self.target.getHpr()
        self.nameLabel['text'] = 'Target: %s' % name
        self.scaleLabel['text'] = 'Scale: %s' % scale
        self.xPosSpinner.setValue(x)
        self.yPosSpinner.setValue(y)
        self.zPosSpinner.setValue(z)
        self.hSpinner.setValue(h)
        self.pSpinner.setValue(p)
        self.rSpinner.setValue(r)

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

    def toggleMinimize(self):
        if self.minimized:
            self.maximize()
        else:
            self.minimize()

    def minimize(self):
        self.minimized = True
        self.mainFrame['geom_scale'] = self.MINIMIZED_SCALE
        self.nameLabel.setPos(self.MINI_NAME_POS)
        self.dragButton.setPos(self.MINI_DRAG_BUTTON_POS)
        self.minimizeButton.setPos(self.MINI_MINI_BUTTON_POS)
        self.posLabel.hide()
        self.xPosSpinner.hide()
        self.yPosSpinner.hide()
        self.zPosSpinner.hide()
        self.hprLabel.hide()
        self.hSpinner.hide()
        self.pSpinner.hide()
        self.rSpinner.hide()
        self.scaleLabel.hide()
        self.setPos(0, 0, 0)

    def maximize(self):
        self.minimized = False
        self.mainFrame['geom_scale'] = self.ORIGINAL_SCALE
        self.nameLabel.setPos(self.ORIG_NAME_POS)
        self.dragButton.setPos(self.ORIG_DRAG_BUTTON_POS)
        self.minimizeButton.setPos(self.ORIG_MINI_BUTTON_POS)
        self.posLabel.show()
        self.xPosSpinner.show()
        self.yPosSpinner.show()
        self.zPosSpinner.show()
        self.hprLabel.show()
        self.hSpinner.show()
        self.pSpinner.show()
        self.rSpinner.show()
        self.scaleLabel.show()
        self.setPos(0, 0, 0)

    def onPress(self, e=None):
        self.accept('mouse1-up', self.onRelease)
        taskMgr.add(self.mouseMoverTask, '%s-mouseMoverTask' % self.id)

    def onRelease(self, e=None):
        self.ignore('mouse1-up')
        taskMgr.remove('%s-mouseMoverTask' % self.id)

    def mouseMoverTask(self, task):
        if base.mouseWatcherNode.hasMouse():
            mpos = base.mouseWatcherNode.getMouse()
            buttonPos = self.dragButton.getPos()
            newPos = (mpos[0] - buttonPos[0]/2 - 0.02, 0, mpos[1] - buttonPos[2])
            self.setPos(render2d, newPos)
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