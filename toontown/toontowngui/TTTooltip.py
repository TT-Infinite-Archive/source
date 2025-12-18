from direct.gui.DirectButton import DirectFrame, DGG
from direct.gui.DirectLabel import DirectLabel


class TTTooltip(DirectFrame):
    notify = directNotify.newCategory('TTTooltip')

    def __init__(self, parent=aspect2d, description='nondescript', **kw):
        optiondefs = (
            ('relief', None, None),
        )

        self.defineoptions(kw, optiondefs)
        DirectFrame.__init__(self, parent)
        self.initialiseoptions(TTTooltip)

        self.description = DirectLabel(
            parent=self,
            relief=None,
            text=description,
            text_wordwrap=16,
            text_scale=(0.05)
        )
        bounds = [bound for bound in self.description.getBounds()]
        height = self.description.getHeight()
        descOverItemZAdjust = height - self.getHeight() / 2.0
        descZPos = self.getPos(aspect2d)[2] - height
        if descZPos < -1.0:
            self.description.setZ(descOverItemZAdjust)
        descWidth = self.description.getWidth()
        geom = loader.loadModel('phase_4/models/parties/tt_m_gui_sbk_calendar_popUp_bg')
        self.description['geom'] = geom
        self.description['geom_scale'] = (descWidth * 1.1, 1, height * 1.1)
        descGeomZ = (bounds[2] - bounds[3]) / 2.0
        descGeomZ += bounds[3] * 1.1
        self.description['geom_pos'] = (0, 0, descGeomZ)
        geom.removeNode()
        taskMgr.add(self.mouseMoverTask, self.uniqueName('mouseMoverTask'))
        self.setBin('gui-popup', 0)

    def destroy(self):
        taskMgr.remove(self.uniqueName('mouseMoverTask'))
        DirectFrame.destroy(self)

    def mouseMoverTask(self, task):
        if base.mouseWatcherNode.hasMouse():
            mpos = base.mouseWatcherNode.getMouse()
            offPos = (self.description.getBounds()[0], 0.0, self.getHeight() * 2)
            newPos = (mpos[0] - offPos[0]/2 * 1.35, 0, mpos[1] - offPos[2] * 1.35)

            self.setPos(render2d, newPos)
        return task.cont