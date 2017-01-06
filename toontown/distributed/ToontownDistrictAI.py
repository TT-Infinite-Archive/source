from direct.directnotify.DirectNotifyGlobal import directNotify
import time

from otp.distributed.DistributedDistrictAI import DistributedDistrictAI


class ToontownDistrictAI(DistributedDistrictAI):
    notify = directNotify.newCategory('ToontownDistrictAI')

    created = 0

    def announceGenerate(self):
        DistributedDistrictAI.announceGenerate(self)

        # Remember the time of which this district was created:
        self.created = int(time.time())

        # We want to handle shard status queries so that a ShardStatusReceiver
        # being created after we're generated will know where we're at:
        self.air.netMessenger.accept('queryShardStatus', self, self.handleShardStatusQuery)

        # Send a shard status update with the information we have:
        self.handleShardStatusQuery()

        # Add a post remove shard status update in-case we go down:
        status = {
            'available': False,
            'name': self.name,
            'created': self.created
        }
        datagram = self.air.netMessenger.prepare('shardStatus', [self.air.ourChannel, status])
        self.air.addPostRemove(datagram)

    def handleShardStatusQuery(self):
        # Send a shard status update with the information we have:
        status = {
            'available': bool(self.available),
            'name': self.name,
            'created': self.created
        }
        self.air.netMessenger.send('shardStatus', [self.air.ourChannel, status])

    def setName(self, name):
        DistributedDistrictAI.setName(self, name)

        # Send a shard status update with the information we have:
        self.handleShardStatusQuery()

    def setAvailable(self, available):
        DistributedDistrictAI.setAvailable(self, available)

        # Send a shard status update with the information we have:
        self.handleShardStatusQuery()
