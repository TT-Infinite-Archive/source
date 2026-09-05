from direct.showbase.DirectObject import DirectObject

class ShardStatusReceiver(DirectObject):
    def __init__(self, air):
        self.air = air

        self.shards = {}

        # Accept the shardStatus event:
        self.accept('shardStatus', self.handleShardStatus)

        # Query the status of any existing shards:
        self.air.sendNetEvent('queryShardStatus')

    def handleShardStatus(self, channel, status):
        self.shards.setdefault(channel, {}).update(status)

    def getShards(self):
        return self.shards
