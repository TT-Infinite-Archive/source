from panda3d.core import ConfigVariableBool
from .ElevatorConstants import *
from . import DistributedBossElevatorAI

class DistributedBBElevatorAI(DistributedBossElevatorAI.DistributedBossElevatorAI):

    def __init__(self, air, bldg, zone, antiShuffle = 0, minLaff = 0):
        DistributedBossElevatorAI.DistributedBossElevatorAI.__init__(self, air, bldg, zone, antiShuffle=antiShuffle, minLaff=0)
        self.type = ELEVATOR_BB
        if simbase.wantSinglePlayer:
            self.countdownTime = ElevatorData[self.type]['solo_countdown']
        else:
            self.countdownTime = ElevatorData[self.type]['countdown']

    def checkBoard(self, av):
        result = 0
        if ConfigVariableBool('allow-ceo-elevator', True).getValue():
            result = DistributedBossElevatorAI.DistributedBossElevatorAI.checkBoard(self, av)
        else:
            result = REJECT_NOT_YET_AVAILABLE
        return result
