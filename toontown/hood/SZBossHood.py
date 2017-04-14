from toontown.hood.Hood import Hood
from toontown.hood.Place import Place

from direct.fsm.ClassicFSM import ClassicFSM
from direct.fsm.State import State


class SZBossPlace(Place):
    def __init__(self, loader, doneEvent):
        Place.__init__(self, loader, doneEvent)

        self.fsm = ClassicFSM('SZBossPlace', [
            State('start', self.enterStart, self.exitStart, ['walk']),
            State('walk', self.enterWalk, self.exitWalk, ['start', 'dead']),
            State('dead', self.enterDead, self.exitDead, ['walk']),
            State('final', self.enterFinal, self.exitFinal, ['start'])], 'start', 'final')
        self.fsm.enterInitialState()

    def enterStart(self):
        base.localAvatar.setTeleportAvailable(0)
        base.localAvatar.setTeleportAllowed(0)
        base.localAvatar.cantLeaveGame = 0
        base.localAvatar.questPage.hideQuestsOnscreen()
        base.localAvatar.questPage.ignoreOnscreenHooks()
        base.localAvatar.invPage.ignoreOnscreenHooks()
        base.localAvatar.invPage.hideInventoryOnscreen()
        base.localAvatar.questMap.hide()
        base.localAvatar.questMap.ignoreOnscreenHooks()
        base.localAvatar.book.hideButton()
        base.localAvatar.laffMeter.stop()

    def enterWalk(self, teleportIn=False):
        self.walkStateData.enter()
        self.acceptOnce(self.walkDoneEvent, self.handleWalkDone)
        self.walkStateData.fsm.request('walking')
        base.localAvatar.book.hideButton()
        base.localAvatar.laffMeter.stop()

    def exitWalk(self):
        messenger.send('wakeup')
        self.walkStateData.exit()
        self.ignore(self.walkDoneEvent)

    def enterDead(self):
        pass

    def exitDead(self):
        pass

class SZBossHood(Hood):
    def __init__(self, parentFSM, doneEvent, dnaStore, hoodId):
        Hood.__init__(self, parentFSM, doneEvent, dnaStore, hoodId)

        self.place = None

    def enter(self, requestStatus):
        pass

    def load(self):
        pass

    def loadLoader(self, requestStatus):
        self.place = SZBossPlace(self, 'strike-place-done')
        self.place.load()
