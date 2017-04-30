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

    def toonOnline(self, avId):
        self.notify.debug('Av %s online' % avId)
        if avId in self.players:
            self.notify.warning('Toon %s came online but is already online.' % avId)
            return
        av = self.air.doId2do.get(avId)
        if av is None:
            self.notify.warning('Toon %s online but avatar doesn\'t exist.' % avId)
            return
        player = PlayerManagerPlayer({
            'name': av.name,
            'species': av.dna.species,
            'laff': av.getHp(),
            'access': av.getAccess()
        })
        self.players[avId] = player
        self.d_setPlayerList(avId)
        self.accept(self.air.getAvatarExitEvent(avId), self.toonOffline, extraArgs=[avId])

    def toonOffline(self, avId):
        self.notify.debug('Av %s offline' % avId)
        if avId not in self.players:
            self.notify.warning('Toon %s went offline but is already offline.' % avId)
            return
        event = simbase.air.getAvatarExitEvent(avId)
        self.playerExitEvents.remove(event)
        del self.players[avId]

    def getPlayerList(self):
        avId = self.air.getAvatarIdFromSender()
        self.d_setPlayerList(avId)

    def d_setPlayerList(self, avId):
        self.sendUpdateToAvatarId(avId, 'setPlayerList', [self.players])

    def getPlayerLists(self):
        return [player.toList() for player in self.players]