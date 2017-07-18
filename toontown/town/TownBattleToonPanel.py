from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.gui.DirectGui import DirectFrame
from panda3d.core import Vec4

from toontown.data.GagDefs import Gags
from toontown.data.Gag import Gag
from toontown.toon import LaffMeter
from toontown.toonbase import TTLocalizer
from toontown.toontowngui.TTLabel import TTLabel


class TownBattleToonPanel(DirectFrame):
    notify = directNotify.newCategory('TownBattleToonPanel')

    def __init__(self, idx):
        self.notify.debug('Initialized.... %s' % idx)
        gui = loader.loadModel('phase_3.5/models/gui/battle_gui')
        DirectFrame.__init__(self, relief=None, image=gui.find('**/ToonBtl_Status_BG'), image_color=Vec4(0.5, 0.9, 0.5, 0.7))
        self.setScale(0.8)
        self.initialiseoptions(TownBattleToonPanel)
        self.avatar = None
        self.undecidedText = TTLabel(self, TTLabel.GiantSize, (0.1, 0, 0.015), text=TTLocalizer.TownBattleUndecided)
        self.healthText = TTLabel(self, TTLabel.NormalSize, (-0.06, 0, -0.075))
        self.hpChangeEvent = None
        passGui = gui.find('**/tt_t_gui_bat_pass')
        passGui.detachNode()
        self.passNode = self.attachNewNode('pass')
        self.passNode.setPos(0.1, 0, 0.05)
        passGui.setScale(0.2)
        passGui.reparentTo(self.passNode)
        self.passNode.hide()
        self.laffMeter = None
        self.index = idx
        self.battle = None
        self.hide()
        gui.removeNode()

    def show(self):
        DirectFrame.show(self)
        if self.laffMeter:
            self.laffMeter.start()

    def hide(self):
        DirectFrame.hide(self)
        if self.laffMeter:
            self.laffMeter.stop()

    def cleanup(self):
        self.ignoreAll()
        self.unsetLaffMeter()
        self.battle = None
        DirectFrame.destroy(self)

    def setAvatar(self, avatar):
        if self.avatar == avatar:
            # We already set this avatar
            return
        self.notify.debug('%s Setting my avatar to %s' % (self.index, avatar.doId))
        if self.avatar:
            # We have a different avatar, remove old stuff
            self.unsetAvatar()
        self.avatar = avatar
        self.hpChangeEvent = self.avatar.uniqueName('hpChange')
        self.accept(self.hpChangeEvent, self.setHealthText)
        self.setHealthText(self.avatar.hp, self.avatar.maxHp)
        self.setLaffMeter()

    def unsetAvatar(self):
        self.unsetLaffMeter()
        self.avatar = None

    def setBattle(self, battle):
        self.notify.debug('Setting battle...')
        self.battle = battle

    def setHealthText(self, hp, maxHp, quietly=0):
        self.healthText['text'] = TTLocalizer.TownBattleHealthText % {'hitPoints': hp, 'maxHit': maxHp}

    def setLaffMeter(self):
        if self.laffMeter:
            self.unsetLaffMeter()
        self.notify.debug('Creating a new laff meter')

        self.laffMeter = LaffMeter.LaffMeter(
            self.avatar.style,
            self.avatar.hp,
            self.avatar.maxHp
        )
        self.laffMeter.setAvatar(self.avatar)
        self.laffMeter.reparentTo(self)
        self.laffMeter.setPos(-0.06, 0, 0.05)
        self.laffMeter.setScale(0.045)
        self.laffMeter.start()

    def unsetLaffMeter(self):
        self.notify.debug('Removing laff meter')
        self.ignore(self.hpChangeEvent)
        if self.laffMeter:
            self.laffMeter.destroy()
            self.laffMeter = None

    def updateLaffMeter(self):
        self.notify.debug('Updating laff meter')
        self.laffMeter.adjustFace(self.avatar.hp, self.avatar.maxHp)

    def hideAll(self):
        self.undecidedText.hide()
        self.passNode.hide()

    def updateAttack(self):
        self.notify.debug('Updating attack state')
        if self.avatar is None:
            return
        # First hide existing icons
        self.hideAll()
        if self.avatar.doId in self.battle.toonsThatAttacked:
            self.passNode.show()
        else:
            self.undecidedText.show()
