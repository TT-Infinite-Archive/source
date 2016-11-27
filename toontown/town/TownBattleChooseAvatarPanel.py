from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.gui.DirectGui import *
from direct.showbase.DirectObject import DirectObject
from toontown.toonbase import TTLocalizer, EventGlobals
from toontown.toon.InventoryGlobals import TargettedGagItem
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

    def __init__(self, battle):
        DirectObject.__init__(self)
        self.notify.debug('Initializing...')
        self.attack = None
        self.battle = battle
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

    def unload(self):
        self.notify.debug('Unloading...')
        self.frame.destroy()
        self.frame = None
        self.battle = None

    def setAttack(self, attack):
        self.notify.debug('Setting attack %s' % attack.uid)
        if not attack.isTargetted():
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
        if not self.attack.isTargetted():
            self.notify.warning('Attack un-targetable, ignoring request to updateButtons')
            return
        if self.battle is None:
            self.notify.warning('Not in battle, ignoring request to update buttons.')
            return

        enemyCount = len(self.battle.activeSuits)
        allyCount = len(self.battle.activeToons)

        if enemyCount > 0 and self.attack.targetType in (TargettedGagItem.TargetEnemy,):
            positions = self.ButtonXPositions[enemyCount]
            for index in self.EnemyButtons:
                position = positions[index]
                if position is None:
                    self.buttons[index].hide()
                else:
                    self.buttons[index].show()
                    self.buttons[index].setX(positions[index])
        elif allyCount > 0 and self.attack.targetType in (TargettedGagItem.TargetAlly,):
            positions = self.ButtonXPositions[allyCount]
            for index in self.AllyButtons:
                position = positions[index]
                if position is None:
                    self.buttons[index].hide()
                else:
                    self.buttons[index].show()
                    self.buttons[index].setX(positions[index])
        else:
            self.notify.error('Invalid number of avatars: %d' % (enemyCount + allyCount))
