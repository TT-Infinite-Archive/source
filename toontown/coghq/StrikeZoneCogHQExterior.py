from direct.fsm import State
from direct.interval.IntervalGlobal import *
from pandac.PandaModules import *
from toontown.building import Elevator
from toontown.coghq.CogHQExterior import CogHQExterior
from toontown.safezone import Train


class StrikeZoneCogHQExterior(CogHQExterior):
    notify = directNotify.newCategory('SZHQExterior')

    def __init__(self, loader, parentFSM, doneEvent):
        CogHQExterior.__init__(self, loader, parentFSM, doneEvent)
        self.elevatorDoneEvent = 'elevatorDone'
        self.fsm.addState(State.State('elevator', self.enterElevator, self.exitElevator, ['walk', 'stopped']))
        state = self.fsm.getStateNamed('walk')
        state.addTransition('elevator')
        state = self.fsm.getStateNamed('stopped')
        state.addTransition('elevator')
        state = self.fsm.getStateNamed('stickerBook')
        state.addTransition('elevator')
        state = self.fsm.getStateNamed('squished')
        state.addTransition('elevator')

    def load(self):
        CogHQExterior.load(self)

    def unload(self):
        CogHQExterior.unload(self)

    def enter(self, requestStatus):
        CogHQExterior.enter(self, requestStatus)

    def exit(self):
        CogHQExterior.exit(self)

    def enterElevator(self, distElevator, skipDFABoard = 0):
        self.accept(self.elevatorDoneEvent, self.handleElevatorDone)
        self.elevator = Elevator.Elevator(self.fsm.getStateNamed('elevator'), self.elevatorDoneEvent, distElevator)
        if skipDFABoard:
            self.elevator.skipDFABoard = 1
        self.elevator.load()
        self.elevator.enter()

    def exitElevator(self):
        self.ignore(self.elevatorDoneEvent)
        self.elevator.unload()
        self.elevator.exit()
        del self.elevator

    def detectedElevatorCollision(self, distElevator):
        self.fsm.request('elevator', [distElevator])

    def handleElevatorDone(self, doneStatus):
        self.notify.debug('handling elevator done event')
        where = doneStatus['where']
        if where == 'reject':
            if hasattr(base.localAvatar, 'elevatorNotifier') and base.localAvatar.elevatorNotifier.isNotifierOpen():
                pass
            else:
                self.fsm.request('walk')
        elif where == 'exit':
            self.fsm.request('walk')
        elif where == 'mintInterior':
            self.doneStatus = doneStatus
            messenger.send(self.doneEvent)
        else:
            self.notify.error('Unknown mode: ' + where + ' in handleElevatorDone')
