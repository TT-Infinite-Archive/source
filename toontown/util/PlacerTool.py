from direct.gui.DirectGui import DirectFrame, DGG, DirectButton

from toontown.toonbase import ToontownGlobals
from toontown.toontowngui import TTLabel


class PlacerTool(DirectFrame):
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
        self.mainFrame.setBin('gui-popup', 0)
        self.posDisplay = TTLabel.TTLabel(parent=self.mainFrame, text=str(self.target.getPos()))

        gui = loader.loadModel('phase_3/models/gui/tt_m_gui_mat_mainGui.bam')
        image = (
            gui.find('**/tt_t_gui_mat_shuffleArrowUp'),
            gui.find('**/tt_t_gui_mat_shuffleArrowDown'),
            gui.find('**/tt_t_gui_mat_shuffleArrowUp'),
            gui.find('**/tt_t_gui_mat_shuffleArrowDisabled')
        )
        self.leftArrow = DirectButton(
            self.mainFrame,
            relief=None,
            image=image,
            image_scale=(0.6, 0.6, 0.6),
            image1_scale=(0.7, 0.7, 0.7),
            image2_scale=(0.7, 0.7, 0.7),
            pos=(-0.3, 0.0, 0.0),
            command=self.__handleLeftClicked
        )
        self.rightArrow = DirectButton(
            self.mainFrame,
            relief=None,
            image=image,
            image_scale=(-0.6, 0.6, 0.6),
            image1_scale=(-0.7, 0.7, 0.7),
            image2_scale=(-0.7, 0.7, 0.7),
            pos=(0.3, 0.0, 0.0),
            command=self.__handleRightClicked
        )
        self.upArrow = DirectButton(
            self.mainFrame,
            relief=None,
            image=image,
            image_scale=(0.6, 0.6, 0.6),
            image1_scale=(0.7, 0.7, 0.7),
            image2_scale=(0.7, 0.7, 0.7),
            pos=(0.0, 0.0, 0.15),
            command=self.__handleUpClicked
        )
        self.upArrow.setR(90)
        self.downArrow = DirectButton(
            self.mainFrame,
            relief=None,
            image=image,
            image_scale=(0.6, 0.6, 0.6),
            image1_scale=(0.7, 0.7, 0.7),
            image2_scale=(0.7, 0.7, 0.7),
            pos=(0.0, 0.0, -0.15),
            command=self.__handleDownClicked
        )
        self.downArrow.setR(-90)
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

    def __handleLeftClicked(self):
        pos = self.target.getPos()
        pos[0] -= self.increment
        self.target.setPos(pos)
        self.posDisplay['text'] = str(pos)

    def __handleRightClicked(self):
        pos = self.target.getPos()
        pos[0] += self.increment
        self.target.setPos(pos)
        self.posDisplay['text'] = str(pos)

    def __handleUpClicked(self):
        pos = self.target.getPos()
        pos[2] += self.increment
        self.target.setPos(pos)
        self.posDisplay['text'] = str(pos)

    def __handleDownClicked(self):
        pos = self.target.getPos()
        pos[2] -= self.increment
        self.target.setPos(pos)
        self.posDisplay['text'] = str(pos)

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
