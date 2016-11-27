from direct.gui.DirectGui import *
from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import *
from toontown.toonbase import TTLocalizer, EventGlobals
from direct.directnotify.DirectNotifyGlobal import directNotify


class TownBattleWaitPanel(DirectObject):
    notify = directNotify.newCategory('TownBattleWaitPanel')

    def __init__(self):
        self.notify.debug('Initializing...')
        DirectObject.__init__(self)
        self.frame = None
        self.battle = None
        self.backButton = None
        self.load()
        self.hide()

    def load(self):
        self.notify.debug('Loading...')
        gui = loader.loadModel('phase_3.5/models/gui/battle_gui')
        self.frame = DirectFrame(
            relief=None, image=gui.find('**/Waiting4Others'), text_align=TextNode.ALeft, pos=(0, 0, 0), scale=0.65
        )
        backImage = (gui.find('**/PckMn_BackBtn'), gui.find('**/PckMn_BackBtn_Dn'), gui.find('**/PckMn_BackBtn_Rlvr'))
        self.backButton = DirectButton(
            parent=self.frame, relief=None, image=backImage, pos=(-0.647, 0, -0.011), scale=1.05,
            text=TTLocalizer.TownBattleWaitBack, text_scale=0.05, text_pos=(0.01, -0.012), text_fg=Vec4(0, 0, 0.8, 1),
            command=self.__handleBack
        )
        gui.removeNode()

    def hide(self):
        self.notify.debug('Hiding...')
        self.frame.hide()

    def show(self):
        self.notify.debug('Showing...')
        self.frame.show()
        self.updateText()

    def unload(self):
        self.notify.debug('Unloading...')
        self.frame.destroy()
        self.frame = None
        self.battle = None

    def setBattle(self, battle):
        self.notify.debug('Setting battle')
        self.battle = battle

    def updateText(self):
        self.notify.debug('Updating text')
        if self.battle is None:
            return

        numParticipants = len(self.battle.activeToons)
        if numParticipants > 1:
            self.frame['text'] = TTLocalizer.TownBattleWaitTitle
            self.frame['text_pos'] = (0, 0.01, 0)
            self.frame['text_scale'] = 0.1
        else:
            self.frame['text'] = TTLocalizer.TownSoloBattleWaitTitle
            self.frame['text_pos'] = (0, -0.05, 0)
            self.frame['text_scale'] = 0.13

    def __handleBack(self):
        self.notify.debug('Clicked back!')
        messenger.send(EventGlobals.WaitPanelBack)
