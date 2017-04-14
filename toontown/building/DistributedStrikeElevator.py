from direct.distributed.DistributedObject import DistributedObject

from toontown.building.DistributedElevatorExt import DistributedElevatorExt
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import TTLocalizer
from toontown.strike import StrikeAreaGlobals


class DistributedStrikeElevator(DistributedElevatorExt):
    def __init__(self, cr):
        DistributedElevatorExt.__init__(self, cr)

        self.strikeId = None

    def setStrikeId(self, strikeId):
        self.strikeId = strikeId

    def setStrikeZone(self, zoneId):
        place = self.cr.playGame.getPlace()
        requestStatus = {
            'loader': 'strike',
            'where': 'strike',
            'how': 'movie',
            'hoodId': ToontownGlobals.StrikeZoneBoss,
            'zoneId': zoneId,
            'strikeId': self.strikeId,
            'shardId': None
        }
        place.requestLeave(requestStatus)

    def setupElevator(self):
        self.isSetup = 1

    def getDestName(self):
        if self.strikeId == StrikeAreaGlobals.STRIKE_BOSS:
            return TTLocalizer.StrikeZoneBoss
        return 'unknown strike id %d' % self.strikeId

    def enterWaitEmpty(self, ts):
        pass

    def exitWaitEmpty(self):
        pass

    def enterWaitCountdown(self, ts):
        pass

    def exitWaitCountdown(self):
        pass

    def delete(self):
        DistributedObject.delete(self)
