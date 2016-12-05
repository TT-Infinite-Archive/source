from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.gui.DirectGui import *
from direct.showbase.DirectObject import DirectObject
from toontown.toonbase import TTLocalizer, EventGlobals
from toontown.toon.InventoryGlobals import TargetedGagItem
from panda3d.core import Vec4


class TownBattleChooseAvatarPanel(DirectObject):
    notify = directNotify.newCategory('ChooseAvatarPanel')
    EnemyButtons = range(4)
    AllyButtons = range(4, 8)
    AllButtons = range(8)
    ButtonXPositions = (
        (0, None, None, None),
        (0.2, -0.2, None, None),
        (0.4, 0.0, -0.4, None),
        (0.6, 0.2, -0.2, -0.6)
    )

    def __init__(self):
        DirectObject.__init__(self)
        self.notify.debug('Initializing...')
        self.attack = None
        self.battle = None
        self.frame = None
        self.statusFrame = None
        self.textFrame = None
        self.backButton = None
        self.buttons = []
        self.load()
        self.hide()

    def load(self):
        self.notify.debug('Loading...')
        gui = loader.loadModel('phase_3.5/models/gui/battle_gui')
        self.frame = DirectFrame(
            relief=None,
            image=gui.find('**/BtlPick_TAB'),
            image_color=Vec4(1, 0.2, 0.2, 1)
        )
        self.statusFrame = DirectFrame(
            parent=self.frame,
            relief=None,
            image=gui.find('**/ToonBtl_Status_BG'),
            image_color=Vec4(0.5, 0.9, 0.5, 1),
            pos=(0.611, 0, 0)
        )
        self.textFrame = DirectFrame(
            parent=self.frame,
            relief=None,
            image=gui.find('**/PckMn_Select_Tab'),
            image_color=Vec4(1, 1, 0, 1),
            text=TTLocalizer.TownBattleChooseTitle,
            text_fg=Vec4(0, 0, 0, 1),
            text_pos=(0, -0.025, 0),
            text_scale=0.08,
            pos=(-0.013, 0, 0.013)
        )
        self.buttons = []
        pickButtonImage = (gui.find('**/PckMn_Arrow_Up'), gui.find('**/PckMn_Arrow_Dn'), gui.find('**/PckMn_Arrow_Rlvr'))
        backButtonImage = (gui.find('**/PckMn_BackBtn'), gui.find('**/PckMn_BackBtn_Dn'), gui.find('**/PckMn_BackBtn_Rlvr'))
        for i in xrange(8):
            # Generate buttons for each target (we have 4 targets on two sides)
            button = DirectButton(
                parent=self.frame,
                relief=None,
                image=pickButtonImage,
                command=self.__handlePick,
                extraArgs=[i]
            )
            if i >= 4:
                button.setScale(1, 1, -1)
                button.setPos(0, 0, -0.2)
            else:
                button.setScale(1, 1, 1)
                button.setPos(0, 0, 0.2)
            self.buttons.append(button)

        self.backButton = DirectButton(
            parent=self.frame,
            relief=None,
            image=backButtonImage,
            pos=(-0.647, 0, 0.006),
            scale=1.05,
            text=TTLocalizer.TownBattleChooseAvatarBack,
            text_scale=0.05,
            text_pos=(0.01, -0.012),
            text_fg=Vec4(0, 0, 0.8, 1),
            command=self.__handleBack
        )
        gui.removeNode()

    def hide(self):
        self.notify.debug('Hiding...')
        self.frame.hide()

    def show(self):
        self.notify.debug('Showing...')
        self.frame.show()
        self.updateButtons()

    def unload(self):
        self.notify.debug('Unloading...')
        if self.frame is not None:
            self.frame.destroy()
            self.frame = None
        self.battle = None

    def hidePickerButtons(self):
        for button in self.buttons:
            button.hide()

    def setAttack(self, attack):
        self.notify.debug('Setting attack %s' % attack.uid)
        if not attack.isTargeted():
            self.notify.warning('Cannot choose target for un-targeted attack')
            return
        self.attack = attack

    def setBattle(self, battle):
        self.notify.debug('Initialized battle...')
        self.battle = battle

    def __handleBack(self):
        self.notify.debug('Going back')
        messenger.send(EventGlobals.ChooserBack)

    def __handlePick(self, index):
        self.notify.debug('Targeting avatar at index %s' % index)
        if self.battle is None:
            self.notify.warning('Trying to pick target without a battle in place!')
            return
        if index in self.EnemyButtons:
            messenger.send(EventGlobals.ChooserPick, [self.battle.activeSuits[index].doId])
        elif index in self.AllyButtons:
            messenger.send(EventGlobals.ChooserPick, [self.battle.activeToons[index].doId])
        else:
            self.notify.warning('Invalid target %s' % index)

    def updateButtons(self):
        if self.battle is None or self.attack is None:
            return
        if not self.attack.isTargeted():
            self.notify.warning('Attack un-targetable, ignoring request to updateButtons')
            return

        self.hidePickerButtons()
        enemyCount = len(self.battle.activeSuits)
        allyCount = len(self.battle.activeToons)

        if enemyCount == 0 or allyCount == 0:
            self.notify.warning('Invalid number of avatars.')
            return

        if self.attack.targetType in (TargetedGagItem.TargetEnemy,):
            # Targeting enemies
            positions = self.ButtonXPositions[enemyCount - 1]
            buttons = self.EnemyButtons
        else:
            # Targeting allies
            positions = self.ButtonXPositions[allyCount - 1]
            buttons = self.AllyButtons

        for index in buttons:
            # Show or hide the buttons we need to show or hide
            position = positions[index]
            if position is None:
                self.buttons[index].hide()
            else:
                self.buttons[index].show()
                self.buttons[index].setX(positions[index])
