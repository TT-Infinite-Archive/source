from direct.distributed.DistributedObjectGlobal import DistributedObjectGlobal
from PlayerManagerPlayer import PlayerManagerPlayer

class PlayerManager(DistributedObjectGlobal):
    notify = directNotify.newCategory('PlayerManager')

    def __init__(self, cr):
        DistributedObjectGlobal.__init__(self, cr)
        self.players = []

    def announceGenerate(self):
        DistributedObjectGlobal.announceGenerate(self)
        self.players = []

    def setPlayerList(self, players):
        self.notify.debug('Got update player list %s' % players)
        for p in players:
            player = PlayerManagerPlayer()
            player.fromList(p)
            self.players.append(player)
