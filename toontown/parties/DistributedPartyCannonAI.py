from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.distributed.DistributedObjectAI import DistributedObjectAI
from toontown.parties import PartyGlobals


class DistributedPartyCannonAI(DistributedObjectAI):
    notify = directNotify.newCategory('DistributedPartyCannonAI')

    def __init__(self, air):
        DistributedObjectAI.__init__(self, air)
        self.actId = 0
        self.posHpr = [0, 0, 0, 0, 0, 0]
        self.avId = 0
        self.movie = 0

    def delete(self):
        taskMgr.remove('removeToon%d' % self.doId)
        DistributedObjectAI.delete(self)

    def setActivityDoId(self, actId):
        self.actId = actId

    def getActivityDoId(self):
        return self.actId

    def setPosHpr(self, x, y, z, h, p, r):
        self.posHpr = [x, y, z, h, p, r]

    def getPosHpr(self):
        return self.posHpr

    def requestEnter(self):
        avId = self.air.getAvatarIdFromSender()
        if self.movie not in (0, PartyGlobals.CANNON_MOVIE_LANDED) or self.avId != 0:
            return

        self.avId = avId
        self.d_setMovie(PartyGlobals.CANNON_MOVIE_LOAD, avId)

    def requestExit(self):
        avId = self.air.getAvatarIdFromSender()
        if avId != self.avId:
            return

        self.sendUpdate('setCannonExit', [avId])
        self.avId = 0

    def setMovie(self, movie, _):
        self.movie = movie

    def d_setMovie(self, movie, avId):
        self.sendUpdate('setMovie', [movie, avId])

    def b_setMovie(self, movie, avId):
        self.setMovie(self, movie, avId)
        self.d_setMovie(self, movie, avId)

    def getMovie(self):
        return self.movie

    def setCannonPosition(self, rot, angle):
        avId = self.air.getAvatarIdFromSender()
        if avId != self.avId:
            return

        self.sendUpdate('updateCannonPosition', [avId, rot, angle])

    def setCannonLit(self, rot, angle):
        avId = self.air.getAvatarIdFromSender()
        if avId != self.avId:
            return

        activity = self.air.doId2do.get(self.actId)
        if not activity:
            return

        activity.b_setCannonWillFire(self.doId, rot, angle, avId)
        self.d_setMovie(PartyGlobals.CANNON_MOVIE_CLEAR, avId)
        self.sendUpdate('setCannonExit', [avId])
        self.avId = 0

    def setLanded(self, avId):
        _avId = self.air.getAvatarIdFromSender()
        if avId != _avId:
            self.air.writeServerEvent('suspicious', _avId, 'Toon claimed to be another toon in cannon!')
            return

        self.d_setMovie(PartyGlobals.CANNON_MOVIE_LANDED, _avId)

    def setTimeout(self):
        avId = self.air.getAvatarIdFromSender()
        if avId != self.avId:
            self.air.writeServerEvent('suspicious', avId, 'Toon tried to start timer for someone else!')

        taskMgr.doMethodLater(PartyGlobals.CANNON_TIMEOUT, self.__removeToon, 'removeToon%d' % self.doId,
                              extraArgs=[avId])

    def __removeToon(self, avId):
        if avId != self.avId:
            return

        self.avId = 0
        self.d_setMovie(PartyGlobals.CANNON_MOVIE_FORCE_EXIT, avId)
        self.sendUpdate('setCannonExit', [avId])
