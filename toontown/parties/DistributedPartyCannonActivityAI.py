from direct.directnotify import DirectNotifyGlobal
from toontown.parties.DistributedPartyActivityAI import DistributedPartyActivityAI
from toontown.toonbase import TTLocalizer
from . import PartyGlobals


class DistributedPartyCannonActivityAI(DistributedPartyActivityAI):
    notify = DirectNotifyGlobal.directNotify.newCategory("DistributedPartyCannonActivityAI")
    
    def __init__(self, air, parent, activityTuple):
        DistributedPartyActivityAI.__init__(self, air, parent, activityTuple)
        self.cloudColors = {}
        self.cloudsHit = {}

    def setMovie(self, movie, avId):
        self.sendUpdate('setMovie', [movie, avId])

    def setLanded(self, toonId):
        avId = self.air.getAvatarIdFromSender()
        if avId != toonId:
            self.air.writeServerEvent('suspicious',avId,'Toon tried to land someone else!')
            return
        if not avId in self.toonsPlaying:
            self.air.writeServerEvent('suspicious',avId,'Toon tried to land while not playing the cannon activity!')
            return
        del self.toonsPlaying[avId]
        reward = self.cloudsHit[avId] * PartyGlobals.CannonJellyBeanReward
        if reward > PartyGlobals.CannonMaxTotalReward:
            reward = PartyGlobals.CannonMaxTotalReward
        if self.isDoubleJelleybeans():
            reward *= 2
        av = self.air.doId2do.get(avId, None)
        if not av:
            self.air.writeServerEvent('suspicious',avId,'Toon tried to award beans while not in district!')
            return
        # TODO: Pass a msgId(?) to the client so the client can use whatever localizer it chooses.
        # Ideally, we shouldn't even be passing strings that *should* be localized.
        self.sendUpdateToAvatarId(avId, 'showJellybeanReward', [reward, av.getMoney(), TTLocalizer.PartyCannonResults % (reward, self.cloudsHit[avId])])
        av.addMoney(reward)
        self.sendUpdate('setMovie', [PartyGlobals.CANNON_MOVIE_LANDED, avId])
        del self.cloudsHit[avId]

    def d_setCannonWillFire(self, cannonId, rot, angle, toonId):
        self.sendUpdate('setCannonWillFire', [cannonId, rot, angle])
        self.toonsPlaying[toonId] = True
        self.cloudsHit[toonId] = 0

    def cloudsColorRequest(self):
        avId = self.air.getAvatarIdFromSender()
        self.sendUpdateToAvatarId(avId, 'cloudsColorResponse', [list(self.cloudColors.values())])

    def requestCloudHit(self, cloudId, r, g, b):
        avId = self.air.getAvatarIdFromSender()
        if not avId in self.toonsPlaying:
            self.air.writeServerEvent('suspicious',avId,'Toon tried to hit cloud in cannon activity they\'re not using!')
            return
        self.cloudColors[cloudId] = [cloudId, r, g, b]
        self.sendUpdate('setCloudHit', [cloudId, r, g, b])
        self.cloudsHit[avId] += 1

    def setToonTrajectoryAi(self, launchTime, x, y, z, h, p, r, vx, vy, vz):
        self.sendUpdate('setToonTrajectory', [self.air.getAvatarIdFromSender(), launchTime, x, y, z, h, p, r, vx, vy, vz])

    def setToonTrajectory(self, avId, launchTime, x, y, z, h, p, r, vx, vy, vz):
        return

    def updateToonTrajectoryStartVelAi(self, vx, vy, vz):
        avId = self.air.getAvatarIdFromSender()
        self.sendUpdate('updateToonTrajectoryStartVel', [avId, vx, vy, vz])

    def updateToonTrajectoryStartVel(self, avId, vx, vy, vz):
        pass
