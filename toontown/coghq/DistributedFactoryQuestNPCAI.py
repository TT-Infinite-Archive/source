from direct.distributed import DistributedObjectAI
from toontown.coghq.FactoryQuestGlobals import FQRescueId

class DistributedFactoryQuestNPCAI(DistributedObjectAI.DistributedObjectAI):

    def __init__(self, factory, npcId, x, y, z, h, p=0.0, r=0.0):
        DistributedObjectAI.DistributedObjectAI.__init__(self, factory.air)
        self.factory = factory
        self.posHpr = [x, y, z, h, p, r]
        self.npcId = npcId
        self.saved = False

    def delete(self):
        self.factory = None
        DistributedObjectAI.DistributedObjectAI.delete(self)

    def requestSave(self):
        avId = self.air.getAvatarIdFromSender()
        if avId not in self.factory.avIdList:
            self.notify.warning('Avatar %d tried to save an NPC in a factory it is not in.' % avId)
            return
        self.d_saveNpc(avId)

    def d_saveNpc(self, avId):
        if self.saved:
            return
        self.saved = True
        self.sendUpdate('saveNpc', [avId])

    def saveFinish(self):
        if not self.saved:
            avId = self.air.getAvatarIdFromSender()
            self.notify.warning('Avatar %d tried to make an NPC finished being saved without actually being saved' % avId)
            return
        self.factory.questManager.incrementQuestProgress(FQRescueId)
        self.factory.questManager.removeEntity(self)

    def getPosHpr(self):
        return self.posHpr

    def getNpcId(self):
        return self.npcId

