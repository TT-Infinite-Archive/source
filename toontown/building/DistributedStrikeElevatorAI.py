from toontown.building.DistributedElevatorExtAI import DistributedElevatorExtAI
from toontown.strike.DistributedOperationSaveToontownAI import DistributedOperationSaveToontownAI
from toontown.strike import StrikeAreaGlobals


STRIKES = {
    StrikeAreaGlobals.STRIKE_BOSS: DistributedOperationSaveToontownAI
}


class DistributedStrikeElevatorAI(DistributedElevatorExtAI):
    def __init__(self, air, strikeLobby, strikeId):
        DistributedElevatorExtAI.__init__(self, air, strikeLobby)

        self.strikeId = strikeId

    def getStrikeId(self):
        return self.strikeId

    def generateStrike(self, avIds):
        zoneId = self.air.allocateZone()

        strike = STRIKES[self.strikeId](self.air, avIds)
        strike.generateWithRequired(zoneId)
        strike.start()

        return zoneId

    def sendAvatarsToDestination(self, avIds):
        avIds = [x for x in avIds]  # Remove avIds that are either zero or none

        if len(avIds) > 0:
            zoneId = self.generateStrike(avIds)
            for avId in avIds:
                self.sendUpdateToAvatarId(avId, 'setStrikeZone', [zoneId])
