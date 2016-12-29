from direct.gui.DirectButton import DirectButton, DGG
from direct.directnotify.DirectNotifyGlobal import directNotify

from toontown.toonbase.ColorGlobals import CDefault, CGray


class TTArrow(DirectButton):
    notify = directNotify.newCategory('TTArrow')
    OrientationUp = 0
    OrientationDown = 1
    OrientationLeft = 2
    OrientationRight = 3
    OrientationToR = {
        OrientationUp: 90,
        OrientationDown: 90,
        OrientationLeft: 0,
        OrientationRight: 0
    }
    OrientationToScale = {
        OrientationUp: (-1.0, 1.0, 1.0),
        OrientationDown: (1.0, 1.0, 1.0),
        OrientationLeft: (-1.0, 1.0, 1.0),
        OrientationRight: (1.0, 1.0, 1.0)
    }

    def __init__(self, parent=aspect2d, orientation=0, **kw):
        arrow = self.__getImage()
        rot = self.OrientationToR[orientation]
        imgScale = self.OrientationToScale[orientation]

        optiondefs = (
            ('image', arrow, None),
            ('image_scale', imgScale, (1, 1, 1)),
            ('relief', None, None),
        )

        self.defineoptions(kw, optiondefs)
        DirectButton.__init__(self, parent)
        self.initialiseoptions(TTArrow)

        # Set orientation rot
        self.setR(rot)

    def enable(self):
        self['state'] = DGG.NORMAL
        self['image_color'] = CDefault

    def disable(self):
        self['state'] = DGG.DISABLED
        self['image_color'] = CGray

    def __getImage(self):
        gui = loader.loadModel('phase_3.5/models/gui/friendslist_gui.bam')
        arrow = (
            gui.find('**/Horiz_Arrow_UP'),
            gui.find('**/Horiz_Arrow_DN'),
            gui.find('**/Horiz_Arrow_Rllvr'),
            gui.find('**/Horiz_Arrow_UP')
        )
        gui.removeNode()
        return arrow


class TTShuffleArrow(TTArrow):
    OrientationToScale = {
        TTArrow.OrientationUp: (1.0, 1.0, 1.0),
        TTArrow.OrientationDown: (-1.0, 1.0, 1.0),
        TTArrow.OrientationLeft: (1.0, 1.0, 1.0),
        TTArrow.OrientationRight: (-1.0, 1.0, 1.0)
    }

    def __getImage(self):
        gui = loader.loadModel('phase_3/models/gui/tt_m_gui_mat_mainGui.bam')
        arrow = (
            gui.find('**/tt_t_gui_mat_shuffleArrowUp'),
            gui.find('**/tt_t_gui_mat_shuffleArrowDown'),
            gui.find('**/tt_t_gui_mat_shuffleArrowUp'),
            gui.find('**/tt_t_gui_mat_shuffleArrowDisabled')
        )
        gui.removeNode()
        return arrow
