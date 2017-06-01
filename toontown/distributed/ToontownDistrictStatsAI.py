from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.distributed.DistributedObjectAI import DistributedObjectAI

import random


class ToontownDistrictStatsAI(DistributedObjectAI):
    notify = directNotify.newCategory('ToontownDistrictStatsAI')

    districtId = 0
    avatarCount = 0
    newAvatarCount = 0
    invasionStatus = []
    timeZone = 0

    def __init__(self, air, timeZone=None):
        DistributedObjectAI.__init__(self, air)

        self.timeZone = timeZone

        # Generate a random timezone if we need to:
        if self.timeZone is None:
            self.timeZone = random.randrange(0, 6)  # The lowest time is -3 TTT and the highest is +2 TTT

        # Send a shard status update containing our timezone:
        status = {'timezone': self.timeZone}
        self.air.sendNetEvent('shardStatus', [self.air.ourChannel, status])

    def announceGenerate(self):
        DistributedObjectAI.announceGenerate(self)

        # We want to handle shard status queries so that a ShardStatusReceiver
        # being created after we're generated will know where we're at:
        self.accept('queryShardStatus', self.handleShardStatusQuery)

    def handleShardStatusQuery(self):
        # Send a shard status update containing our population:
        status = {'population': self.avatarCount}
        self.air.sendNetEvent('shardStatus', [self.air.ourChannel, status])

    def settoontownDistrictId(self, districtId):
        self.districtId = districtId

    def d_settoontownDistrictId(self, districtId):
        self.sendUpdate('settoontownDistrictId', [districtId])

    def b_settoontownDistrictId(self, districtId):
        self.settoontownDistrictId(districtId)
        self.d_settoontownDistrictId(districtId)

    def gettoontownDistrictId(self):
        return self.districtId

    def setAvatarCount(self, avatarCount):
        self.avatarCount = avatarCount

        # Send a shard status update containing our population:
        status = {'population': self.avatarCount}
        self.air.sendNetEvent('shardStatus', [self.air.ourChannel, status])

    def d_setAvatarCount(self, avatarCount):
        self.sendUpdate('setAvatarCount', [avatarCount])

    def b_setAvatarCount(self, avatarCount):
        self.d_setAvatarCount(avatarCount)
        self.setAvatarCount(avatarCount)

    def getAvatarCount(self):
        return self.avatarCount

    def setNewAvatarCount(self, newAvatarCount):
        self.newAvatarCount = newAvatarCount

    def d_setNewAvatarCount(self, newAvatarCount):
        self.sendUpdate('setNewAvatarCount', [newAvatarCount])

    def b_setNewAvatarCount(self, newAvatarCount):
        self.setNewAvatarCount(newAvatarCount)
        self.d_setNewAvatarCount(newAvatarCount)

    def getNewAvatarCount(self):
        return self.newAvatarCount

    def setInvasionStatus(self, invasionStatus):
        self.invasionStatus = invasionStatus

    def d_setInvasionStatus(self, invasionStatus):
        self.sendUpdate('setInvasionStatus', [invasionStatus])

    def b_setInvasionStatus(self, invasionStatus):
        self.setInvasionStatus(invasionStatus)
        self.d_setInvasionStatus(invasionStatus)

    def getInvasionStatus(self):
        return self.invasionStatus

    def getTimeZone(self):
        return self.timeZone
