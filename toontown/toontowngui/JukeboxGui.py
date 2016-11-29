from panda3d.core import Vec4
from direct.gui.DirectGui import DirectFrame, DirectScrolledList, DirectLabel, DirectButton
from toontown.toonbase import ToontownGlobals, TTLocalizer


class JukeboxGui(DirectFrame):
    def __init__(self, parent=aspect2d, pos=(0.0, 0.0, 0.0), scale=0.8):
        DirectFrame.__init__(self, parent, pos=pos, scale=scale)

        gui = loader.loadModel('phase_13/models/parties/jukeboxGUI')
        self.queueItems = []
        self.mainFrame = DirectFrame(
            parent=self,
            relief=None
        )
        incButtonImage = (
            gui.find('**/ButtonDown_up'),
            gui.find('**/ButtonDown_down'),
            gui.find('**/ButtonDown_rollover')
        )
        decButtonImage = (
            gui.find('**/ButtonUp_up'),
            gui.find('**/ButtonUp_down'),
            gui.find('**/ButtonUp_rollover')
        )
        self.songSelectorFrame = DirectFrame(
            parent=self.mainFrame,
            relief=None,
            image=gui.find('**/songTitle_background')
        )
        self.queue = DirectScrolledList(
            parent=self.mainFrame,
            relief=None,
            incButton_image=incButtonImage,
            incButton_relief=None,
            incButton_image3_color=Vec4(0.6, 0.6, 0.6, 0.6),
            decButton_image=decButtonImage,
            decButton_relief=None,
            decButton_image3_color=Vec4(0.6, 0.6, 0.6, 0.6),
            image=gui.find('**/queue_background'),
            itemFrame_relief=None,
            itemFrame_pos=(0.0, 0.0, 0.0),
            itemFrame_scale=0.07,
            numItemsVisible=9,
            items=self.queueItems
        )
        self.queueLabel = DirectLabel(
            parent=self.queue,
            relief=None,
            text='Queue',
            text_shadow=(0.0, 0.0, 0.0, 1.0),
            text_fg=(0.5, 1.0, 1.0, 1.0),
            pos=(0.0, 0.0, 0.0),
            scale=0.12
        )
        gui.removeNode()
        gui = loader.loadModel('phase_3/models/gui/tt_m_gui_mat_mainGui.bam')
        image = (
            gui.find('**/tt_t_gui_mat_shuffleArrowUp'),
            gui.find('**/tt_t_gui_mat_shuffleArrowDown'),
            gui.find('**/tt_t_gui_mat_shuffleArrowUp'),
            gui.find('**/tt_t_gui_mat_shuffleArrowDisabled')
        )
        self.leftArrow = DirectButton(
            self.songSelectorFrame,
            relief=None,
            image=image,
            image_scale=(0.6, 0.6, 0.6),
            image1_scale=(0.7, 0.7, 0.7),
            image2_scale=(0.7, 0.7, 0.7),
            pos=(-0.3, 0.0, 0.0),
            command=self.__handleLeftClicked
        )
        self.rightArrow = DirectButton(
            self.songSelectorFrame,
            relief=None,
            image=image,
            image_scale=(-0.6, 0.6, 0.6),
            image1_scale=(-0.7, 0.7, 0.7),
            image2_scale=(-0.7, 0.7, 0.7),
            pos=(0.3, 0.0, 0.0),
            command=self.__handleRightClicked
        )
        gui.removeNode()

    def __handleLeftClicked(self):
        pass

    def __handleRightClicked(self):
        pass
