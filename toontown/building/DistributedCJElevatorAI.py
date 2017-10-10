from ElevatorConstants import *
import DistributedBossElevatorAI

class DistributedCJElevatorAI(DistributedBossElevatorAI.DistributedBossElevatorAI):

    def __init__(self, air, bldg, zone, antiShuffle = 0, minLaff = 0):
        DistributedBossElevatorAI.DistributedBossElevatorAI.__init__(self, air, bldg, zone, antiShuffle=antiShuffle, minLaff=minLaff)
        self.type = ELEVATOR_CJ
        if simbase.wantSinglePlayer:
            self.countdownTime = ElevatorData[self.type]['solo_countdown']
        else:
            self.countdownTime = ElevatorData[self.type]['countdown']

