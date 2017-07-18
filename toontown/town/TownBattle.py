from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.fsm import ClassicFSM, State
from direct.fsm import StateData

import TownBattleChooseAvatarPanel
import TownBattleToonPanel
import TownBattleWaitPanel
from toontown.data import Gag, GagDefs
from toontown.toonbase import ToontownTimer, EventGlobals


class TownBattle(StateData.StateData):
    notify = directNotify.newCategory('TownBattle')
    xPositions = (
        (0.0,),
        (0.25, -0.25),
        (0.5, 0.0, -0.5),
        (0.75, 0.25, -0.25, -0.75)
    )

    def __init__(self, doneEvent):
        StateData.StateData.__init__(self, doneEvent)
        self.numCogs = 1
        self.creditLevel = None
        self.luredIndices = []
        self.trappedIndices = []
        self.numToons = 1
        self.toons = []
        self.time = 0
        self.bldg = 0
        self.track = -1
        self.level = -1
        self.target = 0
        self.battle = None
        self.fsm = ClassicFSM.ClassicFSM('TownBattle', [
            State.State('Off', self.enterOff, self.exitOff, ['Attack']),
            State.State('Attack', self.enterAttack, self.exitAttack, ['ChooseTarget', 'AttackWait', 'Waiting']),
            State.State('ChooseTarget', self.enterChooseTarget, self.exitChooseTarget, ['AttackWait', 'Attack']),
            State.State('AttackWait', self.enterAttackWait, self.exitAttackWait, ['ChooseTarget', 'Attack']),
            State.State('Waiting', self.enterWaiting, self.exitWaiting, ['Attack', 'Off']),
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
        self.timer = None
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
        for toonPanel in self.toonPanels:
            toonPanel.setBattle(battle)

    def update(self):
        self.notify.debug('Updating')
        self.updatePanels()
        if self.choosePanel:
            self.choosePanel.updateButtons()

    def updatePanels(self):
        # Updates toon panel positions and visibility
        self.notify.debug('Updating toon panels using dictionary: %s' % self.battle.activeToons)
        if self.battle is None:
            return
        num = len(self.battle.activeToons)
        positions = self.xPositions[num - 1]
        for index, toonPanel in enumerate(self.toonPanels):
            toonPanel.setPos(0, 0, -0.9)
            if index >= num:
                # Hide the toon panel, this toon doesnt exist
                toonPanel.hide()
            else:
                # Show the toon panel for this toon
                toonPanel.setX(positions[index])
                toonPanel.show()
                # Set the avatar
                toonPanel.setAvatar(self.battle.activeToons[index])
                # Update the attack shown
                toonPanel.updateAttack()

    def updateChosenAttacks(self):
        self.notify.debug('Updating chosen attacks using dictionary: %s' % self.battle.toonAttacks)
        # Update the toon attacks on the toon panels
        for toonPanel in self.toonPanels:
            toonPanel.updateAttack()

    def updateLaffMeter(self, index):
        self.notify.debug('Updating laff meter for toon index %d' % index)
        self.toonPanels[index].updateLaffMeter()

    def enterOff(self):
        self.notify.debug('Entering off')
        for toonPanel in self.toonPanels:
            toonPanel.hide()
        self.target = 0
        if self.timer:
            self.timer.hide()

    def exitOff(self):
        self.updatePanels()
        self.timer.show()

    def enterAttack(self):
        self.notify.debug('Enter Attack')
        if base.localAvatar.doId in self.battle.toonsThatAttacked:
            self.fsm.request('Waiting')
            return
        base.localAvatar.gagPanel.showOnscreen()
        self.accept(EventGlobals.GagSlotClick, self.__handleGagSelected)

    def exitAttack(self):
        self.notify.debug('Exit Attack')
        base.localAvatar.gagPanel.hideOnscreen()
        self.ignore(EventGlobals.GagSlotClick)

    def enterChooseTarget(self):
        if self.choosePanel is None:
            return
        self.choosePanel.setAttack(GagDefs.Gags.get(self.attackId))
        self.accept(EventGlobals.ChooserPick, self.__handleChoosePanelPick)
        self.accept(EventGlobals.ChooserBack, self.__handleChoosePanelBack)
        self.choosePanel.show()

    def exitChooseTarget(self):
        self.ignore(EventGlobals.ChooserBack)
        self.ignore(EventGlobals.ChooserPick)
        self.choosePanel.hide()

    def __handleGagSelected(self, slotIndex):
        gag = base.localAvatar.loadout.getGagAtSlot(slotIndex)
        self.__handleAttackSelected(gag.uid)

    def __handleAttackSelected(self, attackId):
        self.notify.debug('attackSelected: %s' % attackId)
        self.attackId = attackId
        self.updateChosenAttacks()
        gag = GagDefs.Gags[attackId]
        if gag.requiresTarget():
            self.fsm.request('ChooseTarget')

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

    def enterAttackWait(self):
        self.waitPanel.show()

    def exitAttackWait(self):
        self.waitPanel.hide()

    def enterWaiting(self):
        pass

    def exitWaiting(self):
        pass