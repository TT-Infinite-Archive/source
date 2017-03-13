from toontown.building.DistributedBoardingPartyAI import DistributedBoardingPartyAI
from toontown.building.DistributedStrikeElevatorAI import DistributedStrikeElevatorAI
from toontown.strike.StrikeLobbyAI import StrikeLobbyAI
from toontown.strike.OSTZCalculatorAI import OSTZCalculatorAI


class CorporateStrikeManagerAI:
    def __init__(self, air):
        self.air = air

        self.strikes = []
        self.elevators = []

    def registerStrike(self, strikeId):
        self.strikes.append(strikeId)

    def generate(self, zoneId):
        OSTZCalculatorAI.createInstance()

        lobby = StrikeLobbyAI(self.air)
        lobby.generateWithRequired(zoneId)

        for strikeId in self.strikes:
            elevator = DistributedStrikeElevatorAI(self.air, lobby, strikeId)
            elevator.generateWithRequired(zoneId)
            self.elevators.append(elevator.doId)

        boardingParty = DistributedBoardingPartyAI(self.air, self.elevators)
        boardingParty.generateWithRequired(zoneId)
