from panda3d.core import Vec4, TextNode
from direct.gui.DirectGui import DirectFrame, DirectScrolledList, DirectLabel, DirectButton, DGG
from toontown.toonbase import TTLocalizer
from toontown.safezone import JukeboxGlobals
from toontown.toontowngui.TTLabel import TTLabel


class JukeboxGui(DirectFrame):
    def __init__(self, jukebox, parent=aspect2d, pos=(0.0, 0.0, 0.0), scale=1.0):
        DirectFrame.__init__(self, parent, pos=pos, scale=scale)
        self.jukebox = jukebox
        self.songId = 0
        self.pickerSongId = 1

        gui = loader.loadModel('phase_13/models/parties/jukeboxGUI')
        self.queueItems = []
        self.mainFrame = DirectFrame(
            parent=self,
            relief=None
        )
        self.songSelectorFrame = DirectFrame(
            parent=self.mainFrame,
            relief=None,
            image=gui.find('**/songTitle_background'),
            image_scale=(0.5, 1.0, 1.0),
            pos=(-0.75, 0.0, -0.8)
        )
        self.currentPlayingFrame = DirectFrame(
            parent=self.mainFrame,
            relief=None,
            image=gui.find('**/songTitle_background'),
            image_scale=(0.75, 1.0, 1.0),
            pos=(-0.75, 0.0, -0.25)
        )
        self.currentPlayingLabel = DirectLabel(
            parent=self.currentPlayingFrame,
            relief=None,
            text=TTLocalizer.JukeboxCurrentlyPlayingTitle,
            text_shadow=(0.0, 0.0, 0.0, 1.0),
            text_fg=(0.5, 1.0, 1.0, 1.0),
            pos=(0.05, 0.0, 0.7),
            scale=0.12
        )
        self.songSelectorLabel = DirectLabel(
            parent=self.songSelectorFrame,
            relief=None,
            text=TTLocalizer.JukeboxSongSelectorTitle,
            text_shadow=(0.0, 0.0, 0.0, 1.0),
            text_fg=(0.5, 1.0, 1.0, 1.0),
            pos=(0.05, 0.0, 0.7),
            scale=0.12
        )
        self.currentPlayingDisplay = TTLabel(
            parent=self.currentPlayingFrame,
            text_size=TTLabel.LargeSize,
            text='',
            pos=(0.0, 0.0, 0.475)
        )
        self.songSelectorDisplay = TTLabel(
            parent=self.songSelectorFrame,
            text_size=TTLabel.LargeSize,
            text='',
            pos=(0.0, 0.0, 0.475)
        )
        self.queue = DirectScrolledList(
            parent=self.mainFrame,
            relief=None,
            pos=(0.2, 0.0, 0.3),
            incButton_image=(
                gui.find('**/queueButtonDown_up'),
                gui.find('**/queueButtonDown_down'),
                gui.find('**/queueButtonDown_rollover')
            ),
            incButton_relief=None,
            incButton_image3_color=Vec4(0.6, 0.6, 0.6, 0.6),
            decButton_image=(
                gui.find('**/queueButtonUp_up'),
                gui.find('**/queueButtonUp_down'),
                gui.find('**/queueButtonUp_rollover')
            ),
            decButton_relief=None,
            decButton_image3_color=Vec4(0.6, 0.6, 0.6, 0.6),
            image=gui.find('**/queue_background'),
            itemFrame_relief=None,
            itemFrame_pos=(0.35, 0.0, -0.025),
            numItemsVisible=9,
            forceHeight=0.075,
            items=self.queueItems
        )
        self.queueLabel = DirectLabel(
            parent=self.queue,
            relief=None,
            text=TTLocalizer.JukeboxQueueTitle,
            text_shadow=(0.0, 0.0, 0.0, 1.0),
            text_fg=(0.2, 1.0, 1.0, 1.0),
            pos=(0.7, 0.0, 0.2),
            scale=0.12
        )
        self.addSongButton = DirectButton(
            parent=self.mainFrame,
            relief=None,
            image=(
                gui.find('**/addSongButton_up'),
                gui.find('**/addSongButton_down'),
                gui.find('**/addSongButton_rollover')
            ),
            image_scale=0.5,
            pos=(0.2, 0.0, -0.1),
            command=self.__handleAddSongButton
        )
        self.addSongLabel = TTLabel(
            parent=self.addSongButton,
            text=TTLocalizer.JukeboxAddSong,
            text_size=TTLabel.NormalSize,
            pos=(0, 0, -0.175)
        )
        self.closeButton = DirectButton(
            parent=self.mainFrame,
            relief=None,
            image=(
                gui.find('**/can_cancelButton_up'),
                gui.find('**/can_cancelButton_down'),
                gui.find('**/can_cancelButton_rollover')
            ),
            pos=(-0.05, 0.0, -0.3),
            command=self.__handleCloseButton
        )
        gui.removeNode()
        gui = loader.loadModel('phase_3/models/gui/tt_m_gui_mat_mainGui')
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
            image_scale=(0.8, 0.8, 0.8),
            image1_scale=(0.9, 0.9, 0.9),
            image2_scale=(0.9, 0.9, 0.9),
            pos=(-0.65, 0.0, 0.5),
            command=self.__handleLeftClicked
        )
        self.rightArrow = DirectButton(
            self.songSelectorFrame,
            relief=None,
            image=image,
            image_scale=(-0.8, 0.8, 0.8),
            image1_scale=(-0.9, 0.9, 0.9),
            image2_scale=(-0.9, 0.9, 0.9),
            pos=(0.65, 0.0, 0.5),
            command=self.__handleRightClicked
        )
        gui.removeNode()
        self.updateArrows()
        self.updateSelectorText()

    def setSongId(self, songId):
        self.songId = songId
        self.updateCurrentSongText()

    def updateQueue(self, queue):
        self.emptyQueue()
        for songId in queue:
            ttsong = JukeboxGlobals.Songs.get(songId)
            if ttsong is None:
                text = 'Error'
            else:
                text = ttsong.name
            self.queueItems.append(TTLabel(text=text, text_align=TextNode.ALeft))
        self.updateQueueList()

    def emptyQueue(self):
        for queueItem in self.queueItems:
            queueItem.destroy()
        del self.queueItems[:]

    def updateQueueList(self):
        if self.queueItems is None:
            return

        # Clear the Queue
        self.queue.removeAllItems()

        # Re-Populate the queue list
        for queueItem in self.queueItems:
            self.queue.addItem(queueItem, refresh=0)

        self.queue.refresh()

    def updateCurrentSongText(self):
        ttsong = JukeboxGlobals.Songs.get(self.songId)
        if ttsong is None:
            text = 'Nothing'
        else:
            text = ttsong.name
        self.currentPlayingDisplay['text'] = text

    def updateArrows(self):
        if self.pickerSongId == 1:
            self.leftArrow['state'] = DGG.DISABLED
        else:
            self.leftArrow['state'] = DGG.NORMAL
        if self.pickerSongId == list(JukeboxGlobals.Songs.keys())[-1]:
            self.rightArrow['state'] = DGG.DISABLED
        else:
            self.rightArrow['state'] = DGG.NORMAL

    def updateSelectorText(self):
        ttsong = JukeboxGlobals.Songs.get(self.pickerSongId)
        if ttsong is None:
            text = 'Error'
        else:
            text = ttsong.name
        self.songSelectorDisplay['text'] = text

    def __handleLeftClicked(self):
        if self.pickerSongId == 1:
            return
        self.pickerSongId -= 1
        self.updateSelectorText()
        self.updateArrows()

    def __handleRightClicked(self):
        if self.pickerSongId == list(JukeboxGlobals.Songs.keys())[-1]:
            return
        self.pickerSongId += 1
        self.updateSelectorText()
        self.updateArrows()

    def __handleAddSongButton(self):
        self.jukebox.d_requestPlaySong(self.pickerSongId)

    def __handleCloseButton(self):
        self.jukebox.exitGui()
