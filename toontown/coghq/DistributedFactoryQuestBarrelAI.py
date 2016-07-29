from direct.distributed import DistributedObjectAI
from toontown.coghq.FactoryQuestGlobals import FQLootId

class DistributedFactoryQuestBarrelAI(DistributedObjectAI.DistributedObjectAI):

    def __init__(self, factory, x, y, z, h, p=0.0, r=0.0):
        DistributedObjectAI.DistributedObjectAI.__init__(self, factory.air)
        self.factory = factory
        self.posHpr = [x, y, z, h, p, r]
        self.grabbed = False

    def delete(self):
        self.factory = None
        DistributedObjectAI.DistributedObjectAI.delete(self)

    def requestGrab(self):
        avId = self.air.getAvatarIdFromSender()
        self.d_setGrab(avId)

    def d_setGrab(self, avId):
        if self.grabbed:
            return
        if avId not in self.factory.avIdList:
            self.notify.warning('Avatar %d tried to grab a quest barrel in a factory it is not in.' % avId)
            return
        self.notify.debug('d_setGrab %s' % avId)

        self.grabbed = True
        self.factory.questManager.incrementQuestProgress(FQLootId)
        self.factory.questManager.removeEntity(self)
        self.sendUpdate('setGrab', [avId])

    def getPosHpr(self):
        return self.posHpr

