from direct.fsm.FSM import FSM

from toontown.nametag.NametagGroup import *
from direct.distributed.DistributedObjectAI import DistributedObjectAI
from direct.directnotify import DirectNotifyGlobal
from direct.interval.IntervalGlobal import *
from otp.ai.MagicWordGlobal import *


class DistributedStormEventAI(DistributedObjectAI, FSM):
    notify = DirectNotifyGlobal.directNotify.newCategory("DistributedStormEventAI")

    def __init__(self, air):
        DistributedObjectAI.__init__(self, air)
        FSM.__init__(self, 'StormAIFSM')
        self.air = air
        self.stateTime = globalClockDelta.getRealNetworkTime()
        self.defaultTransitions = {
            'Off': ['Idle'],
            'Idle': ['Off']
        }

    def setState(self, state):
        self.request(state)

    def d_setState(self, state):
        self.stateTime = globalClockDelta.getRealNetworkTime()
        self.sendUpdate('setState', [state, self.stateTime])

    def b_setState(self, state):
        self.setState(state)
        self.d_setState(state)

    def getState(self):
        return (self.state, self.stateTime)

    def enterIdle(self):
        pass

    def exitIdle(self):
        pass

@magicWord(category=CATEGORY_SYSTEM_ADMINISTRATOR)
def stormState(state):
    if (not simbase.air.newsManager.getStormEnabled()) or (not simbase.config.GetBool('want-storm-cutscene', False)):
        simbase.air.writeServerEvent('warning', avId=spellbook.getInvoker().doId, issue="Attempted to change the storm state while it's disabled.")
        return 'Not so fast! The storm is currently not happening in Toontown. Your request has been logged.'

    event = simbase.air.doFind('StormEvent')
    if event is None:
        event = DistributedStormEventAI(simbase.air)
        event.generateWithRequired(2000)

    event.b_setState(state)