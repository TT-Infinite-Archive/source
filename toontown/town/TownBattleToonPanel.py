from direct.directnotify.DirectNotifyGlobal import directNotify
from toontown.toon import LaffMeter, InventoryGlobals
from direct.gui.DirectGui import *
from toontown.toonbase import TTLocalizer
from toontown.toontowngui.TTLabel import TTLabel
from panda3d.core import Vec4


class TownBattleToonPanel(DirectFrame):
    notify = directNotify.newCategory('TownBattleToonPanel')

    def __init__(self, id):
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
        self.whichText = DirectLabel(parent=self, text='', pos=(0.1, 0, -0.08), text_scale=0.05)
        self.hide()
        gui.removeNode()

    def setLaffMeter(self, avatar):
        self.notify.debug('setLaffMeter: new avatar %s' % avatar.doId)
        if self.avatar == avatar:
            messenger.send(self.avatar.uniqueName('hpChange'), [avatar.hp, avatar.maxHp, 1])
            return
        else:
            if self.avatar:
                self.cleanupLaffMeter()
            self.avatar = avatar
            self.laffMeter = LaffMeter.LaffMeter(avatar.style, avatar.hp, avatar.maxHp)
            self.laffMeter.setAvatar(self.avatar)
            self.laffMeter.reparentTo(self)
            self.laffMeter.setPos(-0.06, 0, 0.05)
            self.laffMeter.setScale(0.045)
            self.laffMeter.start()
            self.setHealthText(avatar.hp, avatar.maxHp)
            self.hpChangeEvent = self.avatar.uniqueName('hpChange')
            self.accept(self.hpChangeEvent, self.setHealthText)

    def setHealthText(self, hp, maxHp, quietly=0):
        self.healthText['text'] = TTLocalizer.TownBattleHealthText % {'hitPoints': hp, 'maxHit': maxHp}

    def show(self):
        DirectFrame.show(self)
        if self.laffMeter:
            self.laffMeter.start()

    def hide(self):
        DirectFrame.hide(self)
        if self.laffMeter:
            self.laffMeter.stop()

    def updateLaffMeter(self, hp):
        if self.laffMeter:
            self.laffMeter.adjustFace(hp, self.avatar.maxHp)
        self.setHealthText(hp, self.avatar.maxHp)

    def setGagImage(self, image):
        self.gagImage = image.instanceUnderNode(self.gagNode, 'gag')
        self.gagImage.setScale(0.8)
        self.gagImage.setPos(0, 0, 0.02)

    def unsetGagImage(self):
        if self.gagImage is None:
            return
        self.gagImage.removeNode()
        self.gagImage = None

    def setValues(self, index, attackId, numTargets=None, targetIndex=None, localNum=None):
        self.notify.debug('setValues(%s, %s, %s, %s, %s)' % (index, attackId, numTargets, targetIndex, localNum))
        self.undecidedText.hide()
        self.sosText.hide()
        self.fireText.hide()
        self.gagNode.hide()
        self.whichText.hide()
        self.passNode.hide()
        self.unsetGagImage()
        gag = InventoryGlobals.Gags.get(attackId)
        if gag is None:
            self.undecidedText.show()
        elif gag.uid == 0:
            # This is not an attack
            self.undecidedText.show()
        else:
            self.undecidedText.hide()
            self.gagNode.show()
            self.setGagImage(gag.getDisplayObject().getButtonIcon())
            if numTargets is not None and targetIndex is not None and localNum is not None:
                self.whichText.show()
                self.whichText['text'] = self.determineWhichText(numTargets, targetIndex, index)

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
        self.cleanupLaffMeter()
        if self.gagImage is not None:
            self.gagImage.removeNode()
            self.gagImage = None
        self.gagNode.removeNode()
        self.gagNode = None
        DirectFrame.destroy(self)

    def cleanupLaffMeter(self):
        self.notify.debug('Cleaning up laffmeter!')
        self.ignore(self.hpChangeEvent)
        if self.laffMeter:
            self.laffMeter.destroy()
            self.laffMeter = None
