from toontown.hood import HoodAI
from toontown.toonbase import ToontownGlobals
#from toontown.palooza import DistributedPaloozaElevatorAI

class TPHoodAI(HoodAI.HoodAI):
    def __init__(self, air):
        HoodAI.HoodAI.__init__(self, air,
                               ToontownGlobals.ToonPalooza,
                               ToontownGlobals.ToonPalooza)

        self.startup()
        
        self.elevators = []

        self.air = air
        
    def startup(self):
        HoodAI.HoodAI.startup(self)

        self.createGames()
        
        self.createBoardingGroups()
        
    def createGames(self):
        pass # TODO
        '''
        for gameId in ToontownGlobals.MinigameIDs:
            # Create the elevator that corresponds with the gameID
            elevator = DistributedPaloozaElevatorAI.DistributedPaloozaElevatorAI(self.air) # Inside here will be basically a trolley
            elevator.generateWithRequired(self.zoneId)
            self.elevators.append(elevator)
        '''
        
    def createBoardingGroups(self):
        pass
        '''
        for elevator in self.elevator:
            elevator.createBoardingParty()
        '''