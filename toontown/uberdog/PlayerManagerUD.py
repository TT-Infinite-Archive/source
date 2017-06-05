from direct.distributed.DistributedObjectGlobalUD import DistributedObjectGlobalUD
from PlayerManagerPlayer import PlayerManagerPlayer


class PlayerManagerUD(DistributedObjectGlobalUD):
    notify = directNotify.newCategory('PlayerManagerUD')

    def __init__(self, air):
        DistributedObjectGlobalUD.__init__(self, air)
        self.players = {}
        self.playerExitEvents = []
        self.rateLimited = []

    def announceGenerate(self):
        DistributedObjectGlobalUD.announceGenerate(self)

    def toonOnline(self, avId, avFields):
        self.notify.debug('Av %s online %s' % (avId, avFields))
        if avId in self.players:
            self.notify.warning('Toon %s came online but is already online.' % avId)
            return
        player = PlayerManagerPlayer({
            'avId': avId,
            'name': avFields.get('setName')[0],
            'laff': avFields.get('setMaxHp')[0]
        })
        self.players[avId] = player
        e = self.air.getAvatarExitEvent(avId)
        self.playerExitEvents.append(e)
        self.accept(e, self.toonOffline, extraArgs=[avId])
        self.d_setPlayerList()

    def toonOffline(self, avId):
        self.notify.debug('Av %s offline' % avId)
        if avId not in self.players:
            self.notify.warning('Toon %s went offline but is already offline.' % avId)
            return
        event = simbase.air.getAvatarExitEvent(avId)
        self.playerExitEvents.remove(event)
        del self.players[avId]
        self.d_setPlayerList()

    def d_setPlayerList(self):
        self.sendUpdate('setPlayerList', [self.getPlayerLists()])

    def getPlayerLists(self):
        return [player.toList() for player in self.players]