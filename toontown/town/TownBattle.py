from toontown.toonbase.ToontownBattleGlobals import *
from direct.fsm import StateData
from direct.fsm import ClassicFSM, State
import TownBattleWaitPanel
import TownBattleChooseAvatarPanel
import TownBattleToonPanel
from toontown.toontowngui import TTDialog
from direct.directnotify.DirectNotifyGlobal import directNotify
from toontown.toonbase import ToontownTimer, EventGlobals
from toontown.toonbase import TTLocalizer
from toontown.toon import InventoryGlobals


class TownBattle(StateData.StateData):
    notify = directNotify.newCategory('TownBattle')
    evenPos = (0.75, 0.25, -0.25, -0.75)
    oddPos = (0.5, 0, -0.5)

    def __init__(self, doneEvent):
        StateData.StateData.__init__(self, doneEvent)
        self.numCogs = 1
        self.creditLevel = None
        self.luredIndices = []
        self.trappedIndices = []
        self.numToons = 1
        self.toons = []
        self.localNum = 0
        self.time = 0
        self.bldg = 0
        self.track = -1
        self.level = -1
        self.target = 0
        self.battle = None
        self.toonAttacks = [
            (-1, 0, 0),
            (-1, 0, 0),
            (-1, 0, 0),
            (-1, 0, 0)
        ]
        self.fsm = ClassicFSM.ClassicFSM('TownBattle', [
            State.State('Off', self.enterOff, self.exitOff, ['Attack']),
            State.State('Attack', self.enterAttack, self.exitAttack, ['ChooseTarget', 'AttackWait']),
            State.State('ChooseTarget', self.enterChooseTarget, self.exitChooseTarget, ['AttackWait', 'Attack']),
            State.State('AttackWait', self.enterAttackWait, self.exitAttackWait, ['ChooseTarget', 'Attack']),
        ], 'Off', 'Off')
        self.waitPanel = TownBattleWaitPanel.TownBattleWaitPanel()
        self.choosePanel = TownBattleChooseAvatarPanel.TownBattleChooseAvatarPanel()
        self.toonPanels = (
            TownBattleToonPanel.TownBattleToonPanel(0),
            TownBattleToonPanel.TownBattleToonPanel(1),
            TownBattleToonPanel.TownBattleToonPanel(2),
            TownBattleToonPanel.TownBattleToonPanel(3)
        )
        self.timer = ToontownTimer.ToontownTimer()
        self.timer.posInTopRightCorner()
        self.timer.setScale(0.4)
        self.timer.hide()

    def cleanup(self):
        self.unload()
        del self.fsm
        self.choosePanel.unload()
        del self.waitPanel
        for toonPanel in self.toonPanels:
            toonPanel.cleanup()

        del self.toonPanels
        self.timer.destroy()
        del self.timer
        del self.toons

    def enter(self, event, parentFSMState, bldg=0, creditMultiplier=1, tutorialFlag=0):
        self.parentFSMState = parentFSMState
        self.parentFSMState.addChild(self.fsm)
        if not self.isLoaded:
            self.load()
        self.battleEvent = event
        self.fsm.enterInitialState()
        base.localAvatar.laffMeter.start()
        self.numToons = 1
        self.numCogs = 1
        self.toons = [base.localAvatar.doId]
        self.toonPanels[0].setLaffMeter(base.localAvatar)
        self.bldg = bldg
        self.creditLevel = None
        self.creditMultiplier = creditMultiplier
        self.tutorialFlag = tutorialFlag

    def exit(self):
        base.localAvatar.laffMeter.stop()
        self.parentFSMState.removeChild(self.fsm)
        del self.parentFSMState

    def unload(self):
        StateData.StateData.unload(self)
        self.waitPanel.unload()
        self.choosePanel.unload()

    def setState(self, state):
        if hasattr(self, 'fsm'):
            self.fsm.request(state)

    def updateTimer(self, time):
        self.time = time
        self.timer.setTime(time)

    def setBattle(self, battle):
        self.battle = battle
        self.choosePanel.setBattle(battle)
        self.waitPanel.setBattle(battle)

    def adjustCogsAndToons(self, activeSuits, luredSuits, activeToons):
        pass

    def __enterPanels(self, num, localNum):
        self.notify.debug('enterPanels() num: %d localNum: %d' % (num, localNum))
        for toonPanel in self.toonPanels:
            toonPanel.hide()
            toonPanel.setPos(0, 0, -0.9)

        if num == 1:
            self.toonPanels[0].setX(self.oddPos[1])
            self.toonPanels[0].show()
        elif num == 2:
            self.toonPanels[0].setX(self.evenPos[1])
            self.toonPanels[0].show()
            self.toonPanels[1].setX(self.evenPos[2])
            self.toonPanels[1].show()
        elif num == 3:
            self.toonPanels[0].setX(self.oddPos[0])
            self.toonPanels[0].show()
            self.toonPanels[1].setX(self.oddPos[1])
            self.toonPanels[1].show()
            self.toonPanels[2].setX(self.oddPos[2])
            self.toonPanels[2].show()
        elif num == 4:
            self.toonPanels[0].setX(self.evenPos[0])
            self.toonPanels[0].show()
            self.toonPanels[1].setX(self.evenPos[1])
            self.toonPanels[1].show()
            self.toonPanels[2].setX(self.evenPos[2])
            self.toonPanels[2].show()
            self.toonPanels[3].setX(self.evenPos[3])
            self.toonPanels[3].show()
        else:
            self.notify.error('Bad number of toons: %s' % num)

    def updateChosenAttacks(self, toonIndices, attackIds, targets):
        self.notify.debug('updateChosenAttacks(%s, %s, %s)' % (toonIndices, attackIds, targets))
        for i in xrange(4):
            if toonIndices[i] == -1:
                # Toon is missing, continue
                continue
            else:
                numTargets = 0
                target = -2
                gag = InventoryGlobals.Gags.get(attackIds[i], None)
                if gag is not None and gag.targetsAlly():
                    numTargets = self.numToons
                    if gag.targetCount != 4:
                        target = targets[i]
                elif gag is not None and gag.targetsEnemy():
                    numTargets = self.numCogs
                    if gag.targetCount == 4:
                        target = -1
                    else:
                        target = targets[i]
                self.toonPanels[toonIndices[i]].setValues(toonIndices[i], attackIds[i], numTargets, target, self.localNum)

    def updateLaffMeter(self, toonNum, hp):
        self.toonPanels[toonNum].updateLaffMeter(hp)

    def enterOff(self):
        if self.isLoaded:
            for toonPanel in self.toonPanels:
                toonPanel.hide()

        self.toonAttacks = [
            (-1, 0, 0),
            (-1, 0, 0),
            (-1, 0, 0),
            (-1, 0, 0)
        ]
        self.target = 0
        if hasattr(self, 'timer'):
            self.timer.hide()

    def exitOff(self):
        if self.isLoaded:
            self.__enterPanels(self.numToons, self.localNum)
        self.timer.show()

    def enterAttack(self):
        self.notify.debug('Enter Attack')
        base.localAvatar.gagPanel.show()
        self.accept(EventGlobals.GagInventorySelection, self.__handleGagSelected)

    def exitAttack(self):
        self.notify.debug('Exit Attack')
        base.localAvatar.gagPanel.hide()
        self.ignore(EventGlobals.GagInventorySelection)

    def __handleGagSelected(self, slotIndex):
        gag = base.localAvatar.inventory.getGagAtSlot(slotIndex)
        if gag is None:
            return
        self.__handleAttackSelected(gag.uid)

    def __handleAttackSelected(self, attackId):
        self.notify.debug('attackSelected: %s' % attackId)
        self.attackId = attackId
        self.toonPanels[self.localNum].setValues(self.localNum, attackId)
        gag = InventoryGlobals.Gags.get(attackId)
        if gag is not None and gag.isTargeted():
            self.fsm.request('ChooseTarget')
        else:
            self.fsm.request('AttackWait')
            response = {
                'mode': 'Attack',
                'attackId': self.attackId,
                'target': 0
            }
            messenger.send(self.battleEvent, [response])

    def enterChooseTarget(self):
        if self.choosePanel is None:
            return
        self.choosePanel.setAttack(InventoryGlobals.Gags.get(self.attackId))
        self.accept(EventGlobals.ChooserPick, self.__handleChoosePanelPick)
        self.accept(EventGlobals.ChooserBack, self.__handleChoosePanelBack)
        self.choosePanel.show()

    def exitChooseTarget(self):
        self.ignore(EventGlobals.ChooserBack)
        self.ignore(EventGlobals.ChooserPick)
        self.choosePanel.hide()

    def __handleChoosePanelPick(self, targetId):
        self.target = targetId
        self.fsm.request('AttackWait')
        response = {
            'mode': 'Attack',
            'attackId': self.attackId,
            'target': self.target
        }
        messenger.send(self.battleEvent, [response])

    def __handleChoosePanelBack(self):
        self.fsm.request('Attack')
        response = {
            'mode': 'UnAttack'
        }
        localIndex = self.battle.activeToons.index(base.localAvatar)
        self.toonPanels[localIndex].setValues(localIndex, None)
        messenger.send(self.battleEvent, [response])

    def enterAttackWait(self):
        self.waitPanel.show()
        self.accept(EventGlobals.WaitPanelBack, self.__handleAttackWaitBack)

    def exitAttackWait(self):
        self.ignore(EventGlobals.WaitPanelBack)
        self.waitPanel.hide()

    def __handleAttackWaitBack(self):
        gag = InventoryGlobals.Gags.get(self.attackId)
        if gag and gag.isTargeted():
            self.fsm.request('ChooseTarget')
        else:
            self.fsm.request('Attack')

        response = {
            'mode': 'UnAttack'
        }
        messenger.send(self.battleEvent, [response])