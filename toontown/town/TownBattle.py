from toontown.toonbase.ToontownBattleGlobals import *
from direct.fsm import StateData
from direct.fsm import ClassicFSM, State
import TownBattleWaitPanel
import TownBattleChooseAvatarPanel
import TownBattleSOSPanel
import TownBattleSOSPetSearchPanel
import TownBattleSOSPetInfoPanel
import TownBattleToonPanel
from toontown.toontowngui import TTDialog
from direct.directnotify import DirectNotifyGlobal
from toontown.battle import BattleBase
from toontown.toonbase import ToontownTimer, EventGlobals
from toontown.toonbase import TTLocalizer
from toontown.pets import PetConstants
from direct.gui.DirectGui import DGG
from toontown.battle import FireCogPanel
from toontown.toon import InventoryGlobals


class TownBattle(StateData.StateData):
    notify = DirectNotifyGlobal.directNotify.newCategory('TownBattle')
    evenPos = (
        0.75,
        0.25,
        -0.25,
        -0.75
    )
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
            State.State('Attack', self.enterAttack, self.exitAttack, ['ChooseTarget', 'AttackWait', 'Run', 'Fire', 'SOS']),
            State.State('ChooseTarget', self.enterChooseTarget, self.exitChooseTarget, ['AttackWait', 'Attack']),
            State.State('AttackWait', self.enterAttackWait, self.exitAttackWait, ['ChooseTarget', 'Attack']),
            State.State('Run', self.enterRun, self.exitRun, ['Attack']),
            State.State('SOS', self.enterSOS, self.exitSOS, ['Attack', 'AttackWait', 'SOSPetSearch', 'SOSPetInfo']),
            State.State('SOSPetSearch', self.enterSOSPetSearch, self.exitSOSPetSearch, ['SOS', 'SOSPetInfo']),
            State.State('SOSPetInfo', self.enterSOSPetInfo, self.exitSOSPetInfo, ['SOS', 'AttackWait']),
            State.State('Fire', self.enterFire, self.exitFire, ['Attack', 'AttackWait'])
        ], 'Off', 'Off')
        self.runPanel = TTDialog.TTDialog(
            dialogName='TownBattleRunPanel',
            text=TTLocalizer.TownBattleRun,
            style=TTDialog.TwoChoice,
            command=self.__handleRunPanelDone
        )
        self.runPanel.hide()
        self.waitPanel = TownBattleWaitPanel.TownBattleWaitPanel()
        self.choosePanel = TownBattleChooseAvatarPanel.TownBattleChooseAvatarPanel()
        self.SOSPanelDoneEvent = 'SOS-panel-done'
        self.SOSPanel = TownBattleSOSPanel.TownBattleSOSPanel(self.SOSPanelDoneEvent)
        self.SOSPetSearchPanelDoneEvent = 'SOSPetSearch-panel-done'
        self.SOSPetSearchPanel = TownBattleSOSPetSearchPanel.TownBattleSOSPetSearchPanel(self.SOSPetSearchPanelDoneEvent)
        self.SOSPetInfoPanelDoneEvent = 'SOSPetInfo-panel-done'
        self.SOSPetInfoPanel = TownBattleSOSPetInfoPanel.TownBattleSOSPetInfoPanel(self.SOSPetInfoPanelDoneEvent)
        self.fireCogPanelDoneEvent = 'fire-cog-panel-done'
        self.FireCogPanel = FireCogPanel.FireCogPanel(self.fireCogPanelDoneEvent)
        self.cogFireCosts = [None, None, None, None]
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
        self.runPanel.cleanup()
        self.choosePanel.unload()
        del self.runPanel
        del self.waitPanel
        del self.SOSPanel
        del self.FireCogPanel
        del self.SOSPetSearchPanel
        del self.SOSPetInfoPanel
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
        self.SOSPanel.bldg = bldg

    def exit(self):
        base.localAvatar.laffMeter.stop()
        self.parentFSMState.removeChild(self.fsm)
        del self.parentFSMState

    def load(self):
        if self.isLoaded:
            return
        self.SOSPanel.load()
        if hasattr(base, 'wantPets') and base.wantPets:
            self.SOSPetSearchPanel.load()
            self.SOSPetInfoPanel.load()
        self.isLoaded = 1

    def unload(self):
        if not self.isLoaded:
            return
        self.waitPanel.unload()
        self.choosePanel.unload()
        self.FireCogPanel.unload()
        self.SOSPanel.unload()
        if hasattr(base, 'wantPets') and base.wantPets:
            self.SOSPetSearchPanel.unload()
            self.SOSPetInfoPanel.unload()
        self.isLoaded = 0

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

    def updateChosenAttacks(self, toonIndices, gagIds, targets):
        self.notify.debug('updateChosenAttacks(%s, %s, %s)' % (toonIndices, gagIds, targets))
        for i in xrange(4):
            if toonIndices[i] == -1:
                # Toon is missing, continue
                continue
            else:
                numTargets = 0
                target = -2
                gag = InventoryGlobals.Gags.get(gagIds[i], None)
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
                self.toonPanels[toonIndices[i]].setValues(toonIndices[i], gag, numTargets, target, self.localNum)

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
        self.accept(EventGlobals.GagInventorySelection, self.__handleAttackSelected)

    def exitAttack(self):
        self.notify.debug('Exit Attack')
        base.localAvatar.gagPanel.hide()
        self.ignore(EventGlobals.GagInventorySelection)

    def __handleAttackSelected(self, slot):
        self.notify.debug('attackSelected: %s' % slot)
        self.slot = slot
        self.chosenGag = base.localAvatar.inventory.getGagAtSlot(slot)
        self.toonPanels[self.localNum].setValues(self.localNum, self.chosenGag)
        if self.chosenGag.isTargetted():
            self.fsm.request('ChooseTarget')
        else:
            self.fsm.request('AttackWait')
            response = {
                'mode': 'Attack',
                'slot': slot,
                'target': 0
            }
            messenger.send(self.battleEvent, [response])

    def enterChooseTarget(self):
        if self.choosePanel is None:
            return
        self.choosePanel.setAttack(self.chosenGag)
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
            'slot': self.slot,
            'target': self.target
        }
        messenger.send(self.battleEvent, [response])

    def __handleChoosePanelBack(self):
        self.fsm.request('Attack')

    def enterAttackWait(self):
        self.waitPanel.show()
        self.accept(EventGlobals.WaitPanelBack, self.__handleAttackWaitBack)

    def exitAttackWait(self):
        self.ignore(EventGlobals.WaitPanelBack)
        self.waitPanel.hide()

    def __handleAttackWaitBack(self):
        if self.chosenGag.isTargetted():
            self.fsm.request('ChooseTarget')
        else:
            self.fsm.request('Attack')

        response = {
            'mode': 'UnAttack'
        }
        messenger.send(self.battleEvent, [response])

    def enterRun(self):
        self.runPanel.show()

    def exitRun(self):
        self.runPanel.hide()

    def __handleRunPanelDone(self, doneStatus):
        if doneStatus == DGG.DIALOG_OK:
            response = {}
            response['mode'] = 'Run'
            messenger.send(self.battleEvent, [response])
        else:
            self.fsm.request('Attack')

    def enterFire(self):
        canHeal, canTrap, canLure = self.checkHealTrapLure()
        self.FireCogPanel.enter(self.numCogs, luredIndices=self.luredIndices, trappedIndices=self.trappedIndices, track=self.track, fireCosts=self.cogFireCosts)
        self.accept(self.fireCogPanelDoneEvent, self.__handleCogFireDone)
        return None

    def exitFire(self):
        self.ignore(self.fireCogPanelDoneEvent)
        self.FireCogPanel.exit()
        return None

    def __handleCogFireDone(self, doneStatus):
        mode = doneStatus['mode']
        if mode == 'Back':
            self.fsm.request('Attack')
        elif mode == 'Avatar':
            self.cog = doneStatus['avatar']
            self.target = self.cog
            self.fsm.request('AttackWait')
            response = {}
            response['mode'] = 'Fire'
            response['target'] = self.cog
            messenger.send(self.battleEvent, [response])
        else:
            self.notify.warning('unknown mode: %s' % mode)

    def enterSOS(self):
        canHeal, canTrap, canLure = self.checkHealTrapLure()
        self.SOSPanel.enter(canLure, canTrap)
        self.accept(self.SOSPanelDoneEvent, self.__handleSOSPanelDone)
        return None

    def exitSOS(self):
        self.ignore(self.SOSPanelDoneEvent)
        self.SOSPanel.exit()
        return None

    def __handleSOSPanelDone(self, doneStatus):
        mode = doneStatus['mode']
        if mode == 'Friend':
            doId = doneStatus['friend']
            response = {}
            response['mode'] = 'SOS'
            response['id'] = doId
            messenger.send(self.battleEvent, [response])
            self.fsm.request('AttackWait')
        elif mode == 'Pet':
            self.petId = doneStatus['petId']
            self.petName = doneStatus['petName']
            self.fsm.request('SOSPetSearch')
        elif mode == 'NPCFriend':
            doId = doneStatus['friend']
            response = {}
            response['mode'] = 'NPCSOS'
            response['id'] = doId
            messenger.send(self.battleEvent, [response])
            self.fsm.request('AttackWait')
        elif mode == 'Back':
            self.fsm.request('Attack')

    def enterSOSPetSearch(self):
        response = {}
        response['mode'] = 'PETSOSINFO'
        response['id'] = self.petId
        self.SOSPetSearchPanel.enter(self.petId, self.petName)
        self.proxyGenerateMessage = 'petProxy-%d-generated' % self.petId
        self.accept(self.proxyGenerateMessage, self.__handleProxyGenerated)
        self.accept(self.SOSPetSearchPanelDoneEvent, self.__handleSOSPetSearchPanelDone)
        messenger.send(self.battleEvent, [response])
        return None

    def exitSOSPetSearch(self):
        self.ignore(self.proxyGenerateMessage)
        self.ignore(self.SOSPetSearchPanelDoneEvent)
        self.SOSPetSearchPanel.exit()
        return None

    def __handleSOSPetSearchPanelDone(self, doneStatus):
        mode = doneStatus['mode']
        if mode == 'Back':
            self.fsm.request('SOS')
        else:
            self.notify.error('invalid mode in handleSOSPetSearchPanelDone')

    def __handleProxyGenerated(self):
        self.fsm.request('SOSPetInfo')

    def enterSOSPetInfo(self):
        self.SOSPetInfoPanel.enter(self.petId)
        self.accept(self.SOSPetInfoPanelDoneEvent, self.__handleSOSPetInfoPanelDone)
        return None

    def exitSOSPetInfo(self):
        self.ignore(self.SOSPetInfoPanelDoneEvent)
        self.SOSPetInfoPanel.exit()
        return None

    def __handleSOSPetInfoPanelDone(self, doneStatus):
        mode = doneStatus['mode']
        if mode == 'OK':
            response = {}
            response['mode'] = 'PETSOS'
            response['id'] = self.petId
            response['trickId'] = doneStatus['trickId']
            messenger.send(self.battleEvent, [response])
            self.fsm.request('AttackWait')
            bboard.post(PetConstants.OurPetsMoodChangedKey, True)
        elif mode == 'Back':
            self.fsm.request('SOS')

    def __isCogChoiceNecessary(self):
        return self.numCogs > 1 and self.chosenGag.isTargetted()

    def __isGroupAttack(self, trackNum, levelNum):
        retval = BattleBase.attackAffectsGroup(trackNum, levelNum)
        return retval

    def __isGroupHeal(self, levelNum):
        retval = BattleBase.attackAffectsGroup(HEAL_TRACK, levelNum)
        return retval
