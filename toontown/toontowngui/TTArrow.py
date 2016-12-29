from direct.gui.DirectButton import DirectButton, DGG
from direct.directnotify.DirectNotifyGlobal import directNotify

from toontown.toonbase.ColorGlobals import CDefault, CGray


class TTArrow(DirectButton):
    notify = directNotify.newCategory('TTArrow')
    TypeNormal = 0
    TypeShuffle = 1
    OrientationUp = 0
    OrientationDown = 1
    OrientationLeft = 2
    OrientationRight = 3

    def __init__(self, parent=aspect2d, type=0, orientation=0, **kw):
        arrow, rot, imgScale = self.__getOptions(orientation, type)

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

    def __getOptions(self, orientation, type):
        arrow = None
        # Default options
        orientationToR = {
            self.OrientationUp: 90,
            self.OrientationDown: 90,
            self.OrientationLeft: 0,
            self.OrientationRight: 0
        }
        orientationToScale = {
            self.OrientationUp: (-1.0, 1.0, 1.0),
            self.OrientationDown: (1.0, 1.0, 1.0),
            self.OrientationLeft: (-1.0, 1.0, 1.0),
            self.OrientationRight: (1.0, 1.0, 1.0)
        }
        if type == self.TypeNormal:
            gui = loader.loadModel('phase_3.5/models/gui/friendslist_gui.bam')
            arrow = (
                gui.find('**/Horiz_Arrow_UP'),
                gui.find('**/Horiz_Arrow_DN'),
                gui.find('**/Horiz_Arrow_Rllvr'),
                gui.find('**/Horiz_Arrow_UP')
            )
            gui.removeNode()
        elif type == self.TypeShuffle:
            gui = loader.loadModel('phase_3/models/gui/tt_m_gui_mat_mainGui.bam')
            arrow = (
                gui.find('**/tt_t_gui_mat_shuffleArrowUp'),
                gui.find('**/tt_t_gui_mat_shuffleArrowDown'),
                gui.find('**/tt_t_gui_mat_shuffleArrowUp'),
                gui.find('**/tt_t_gui_mat_shuffleArrowDisabled')
            )
            orientationToScale = {
                self.OrientationUp: (1.0, 1.0, 1.0),
                self.OrientationDown: (-1.0, 1.0, 1.0),
                self.OrientationLeft: (1.0, 1.0, 1.0),
                self.OrientationRight: (-1.0, 1.0, 1.0)
            }
            gui.removeNode()
        else:
            self.notify.warning('Unknown type %s' % type)
        rot = orientationToR[orientation]
        scale = orientationToScale[orientation]
        return arrow, rot, scale
