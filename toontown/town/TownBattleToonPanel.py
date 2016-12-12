from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.gui.DirectGui import DirectFrame
from panda3d.core import Vec4

from toontown.toon import LaffMeter, InventoryGlobals
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
        self.sosText = TTLabel(self, TTLabel.MediumSize, (0.1, 0, 0.015), text=TTLocalizer.TownBattleToonSOS)
        self.fireText = TTLabel(self, TTLabel.MediumSize, (0.1, 0, 0.015), text=TTLocalizer.TownBattleToonFire)
        self.undecidedText = TTLabel(self, TTLabel.GiantSize, (0.1, 0, 0.015), text=TTLocalizer.TownBattleUndecided)
        self.healthText = TTLabel(self, TTLabel.NormalSize, (-0.06, 0, -0.075))
        self.sosText.hide()
        self.fireText.hide()
        self.hpChangeEvent = None
        self.gagNode = self.attachNewNode('gag')
        self.gagNode.setPos(0.1, 0, 0.03)
        self.gagImage = None
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
        self.whichText = TTLabel(self, pos=(0.1, 0, -0.08))
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
        self.notify.debug('Cleaning up laffmeter!')
        self.ignore(self.hpChangeEvent)
        if self.laffMeter:
            self.laffMeter.destroy()
            self.laffMeter = None

    def updateLaffMeter(self):
        self.laffMeter.adjustFace(self.avatar.hp, self.avatar.maxHp)

    def setGagImage(self, image):
        if self.gagImage:
            self.unsetGagImage()
        self.gagImage = image.instanceUnderNode(self.gagNode, 'gag')
        self.gagImage.setScale(0.8)
        self.gagImage.setPos(0, 0, 0.02)

    def unsetGagImage(self):
        if self.gagImage is None:
            return
        self.gagImage.removeNode()
        self.gagImage = None

    def hideAllImages(self):
        self.undecidedText.hide()
        self.sosText.hide()
        self.fireText.hide()
        self.gagNode.hide()
        self.whichText.hide()
        self.passNode.hide()
        self.unsetGagImage()

    def updateAttack(self):
        if self.avatar is None:
            return
        toonAttack = self.battle.toonAttacks.get(self.avatar.doId)
        self.hideAllImages()
        if toonAttack is None:
            # This gag means no attack
            self.notify.debug('Showing that toon at index %s has no attack yet.' % self.index)
            self.undecidedText.show()
            return
        self.notify.debug('Showing that toon at index %s attacks with %d.' % (self.index, toonAttack.attackId))
        attackId = toonAttack.attackId
        gag = InventoryGlobals.Gags.get(attackId)
        if attackId == 0:
            # This gag means no gag
            self.undecidedText.show()
        elif gag is None:
            # ???
            self.undecidedText.show()
        else:
            self.setGagImage(gag.getDisplayObject().getButtonIcon())
            self.gagNode.show()
            attacker = self.battle.findToon(toonAttack.attackerId)
            if attacker is None:
                self.notify.warning('Failed to set attack attacker %d not in this battle.' % toonAttack.attackerId)
                return
            attackerIndex = self.battle.activeToons.index(attacker)
            if not gag.isTargeted():
                return
            elif gag.targetsAlly():
                numTargets = len(self.battle.activeToons)
                if gag.targetCount == 4:
                    # Everyone except me
                    targetIndex = -2
                else:
                    target = base.cr.doId2do.get(toonAttack.targetId)
                    if target is not None and target.doId in self.battle.activeToons:
                        target = self.battle.findToon(toonAttack.targetId)
                        if target is None:
                            self.notify.warning('Failed to target toon %d not in this battle.' % toonAttack.targetId)
                            return
                        targetIndex = self.battle.activeToons.index(target)
                    else:
                        # Don't know what to do?
                        targetIndex = -2
            elif gag.targetsEnemy():
                numTargets = len(self.battle.activeSuits)
                if gag.targetCount == 4:
                    # All enemies
                    targetIndex = -1
                else:
                    target = self.battle.findSuit(toonAttack.targetId)
                    if target is None:
                        self.notify.warning('Failed to target suit %d not in this battle.' % toonAttack.targetId)
                        return
                    targetIndex = self.battle.activeSuits.index(target)
            else:
                self.notify.warning('Failed to set attack')
                return

            self.whichText['text'] = self.determineWhichText(numTargets, targetIndex, attackerIndex)
            self.whichText.show()

    def determineWhichText(self, numTargets, targetIndex, index):
        returnStr = ''
        targetList = range(numTargets)
        targetList.reverse()
        for i in targetList:
            if targetIndex == -1:
                # Everyone
                returnStr += 'X'
            elif targetIndex == -2:
                # Everyone except me
                if i == index:
                    returnStr += '-'
                else:
                    returnStr += 'X'
            elif targetIndex in xrange(0, 4):
                # Specific targets
                if i == targetIndex:
                    returnStr += 'X'
                else:
                    returnStr += '-'
            else:
                self.notify.error('Bad target index: %s' % targetIndex)

        return returnStr

    def cleanup(self):
        self.ignoreAll()
        self.unsetLaffMeter()
        if self.gagImage is not None:
            self.gagImage.removeNode()
            self.gagImage = None
        self.gagNode.removeNode()
        self.gagNode = None
        self.battle = None
        DirectFrame.destroy(self)
