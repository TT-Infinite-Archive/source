from direct.distributed.DistributedObjectGlobal import DistributedObjectGlobal


class PlayerManager(DistributedObjectGlobal):
    notify = directNotify.newCategory('PlayerManager')

    def __init__(self, cr):
        DistributedObjectGlobal.__init__(self, cr)
        self.players = []

    def announceGenerate(self):
        DistributedObjectGlobal.announceGenerate(self)
        self.players = []

    def d_getPlayerList(self):
        self.sendUpdate('getPlayerList', [])

    def setPlayerList(self, players):
        self.notify.debug('Got update player list %s' % players)
        self.players = players
