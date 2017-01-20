from direct.directnotify import DirectNotifyGlobal
from toontown.parties.DistributedPartyActivityAI import DistributedPartyActivityAI
from direct.distributed.ClockDelta import globalClockDelta
from direct.fsm.FSM import FSM
from toontown.effects import FireworkShows
import PartyGlobals
import random


class DistributedPartyFireworksActivityAI(DistributedPartyActivityAI, FSM):
    notify = DirectNotifyGlobal.directNotify.newCategory("DistributedPartyFireworksActivityAI")
    
    def __init__(self, air, parent, activityTuple):
        DistributedPartyActivityAI.__init__(self, air, parent, activityTuple)
        FSM.__init__(self, 'DistributedPartyActivityAI')
        self.state = 'Idle'
        self.parent = parent
        self.eventId = PartyGlobals.FireworkShows.Summer
        self.showStyle = random.randint(0, len(FireworkShows.shows[PartyGlobals.FireworkShows.Summer]) - 1)

    def getEventId(self):
        return self.eventId

    def getShowStyle(self):
        return self.showStyle

    def getSongId(self):
        return random.randint(0, 1)

    def toonJoinRequest(self):
        avId = self.air.getAvatarIdFromSender()
        host = self.parent.hostId
        if avId == host and self.state == 'Idle':
            self.request('Active')
            taskMgr.doMethodLater(
                FireworkShows.getShowDuration(self.getEventId(), self.getShowStyle()),
                self.finishFireworks,
                'finishFireworks-%s' % self.doId,
            )
            return
        self.sendUpdateToAvatarId(avId, 'joinRequestDenied', [1])

    def finishFireworks(self, task=None):
        self.request('Disabled')

    def enterActive(self):
        self.sendUpdate('setState', ['Active', globalClockDelta.getRealNetworkTime()])
        
    def enterIdle(self):
        self.sendUpdate('setState', ['Idle', globalClockDelta.getRealNetworkTime()])

    def enterDisabled(self):
        self.sendUpdate('setState', ['Disabled', globalClockDelta.getRealNetworkTime()])
