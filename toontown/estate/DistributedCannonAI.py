from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectAI import DistributedObjectAI

class DistributedCannonAI(DistributedObjectAI):
    notify = DirectNotifyGlobal.directNotify.newCategory("DistributedCannonAI")

    def __init__(self, air, estateId, targetId, x, y, z, h, p, r):
        DistributedObjectAI.__init__(self, air)
        self.estateId = estateId
        self.targetId = targetId
        self.pos = (x, y, z)
        self.hpr = (h, p, r)
        self.occAvId = 0 # Toon that is currently inside the cannon
        self.bumperPositions = ToontownGlobals.PinballCannonBumperInitialPos
        
    def delete(self):
        self.ignoreAll()
        self.stopTimeout()
        DistributedObjectAI.delete(self)
        
    def setEstateId(self, todo0):
        pass

    def setTargetId(self, todo0):
        pass

    def setPosHpr(self, todo0, todo1, todo2, todo3, todo4, todo5):
        pass

    def setActive(self, todo0):
        pass

    def setActiveState(self, todo0):
        pass

    def requestEnter(self):
        avId = self.air.getAvatarIdFromSender()
        if not self.occAvId:
            self.occAvId = avId
            self.stopTimeout()
            self.setMovie(CannonGlobals.CANNON_MOVIE_LOAD, self.occAvId)
            self.acceptOnce(self.air.getAvatarExitEvent(avId), self.handleUnexpectedExit, extraArgs = [avId])
            self.acceptOnce("bootAvFromEstate-%s" % str(avId), self.handleBootMessage, extraArgs = [avId])
            self.startTimeout(CannonGlobals.CANNON_TIMEOUT)
        else: # another toon is already in the cannon
            self.notify.warning("requestEnter: a toon is already in the cannon")
            self.sendUpdateToAvatarId(avId, "requestExit", [])

    def requestExit(self):
        self.setMovie(CannonGlobals.CANNON_MOVIE_FORCE_EXIT, self.occAvId)

    def setMovie(self, movie, avId):
        self.occAvId = avId
        self.sendUpdate("setMovie", [mode, avId])

    def setCannonPosition(self, zRot, angle):
        avId = self.air.getAvatarIdFromSender()
        self.sendUpdate("updateCannonPosition", [avId, zRot, angle])

    def setCannonLit(self, zRot, angle):
        avId = self.air.getAvatarIdFromSender()
        self.stopTimeout()
        self.sendUpdate("setCannonWillFire", [avId, CannonGameGlobals.FUSE_TIME, zRot, angle, globalClockDelta.getRealNetworkTime()])

    def setFired(self):
        pass

    def setLanded(self):
        pass

    def updateCannonPosition(self, todo0, todo1, todo2):
        pass

    def setCannonWillFire(self, todo0, todo1, todo2, todo3, todo4):
        pass

    def setCannonExit(self, todo0):
        pass

    def requestBumperMove(self, todo0, todo1, todo2):
        pass

    def setCannonBumperPos(self, todo0, todo1, todo2):
        pass

