from toontown.estate import DistributedStatuaryAI
from direct.directnotify import DirectNotifyGlobal
from otp.ai.AIBase import *
from . import GardenGlobals

class DistributedAnimatedStatuaryAI(DistributedStatuaryAI.DistributedStatuaryAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedAnimatedStatuaryAI')

    def __init__(self, typeIndex = 234, waterLevel = 0, growthLevel = 0, optional = None, ownerIndex = 0, plot = 0):
        DistributedStatuaryAI.DistributedStatuaryAI.__init__(self, typeIndex, waterLevel, growthLevel, optional, ownerIndex, plot)
        self.notify.debug('constructing DistributedAnimatedStatuaryAI')
        self.anims = GardenGlobals.PlantAttributes[typeIndex]['anims']

    def setTypeIndex(self, typeIndex):
        DistributedStatuaryAI.DistributedStatuaryAI.setTypeIndex(self, typeIndex)
        self.anims = GardenGlobals.PlantAttributes[typeIndex]['anims']

    def setupPetCollision(self):
        if simbase.wantPets:
            estate = self.air.doId2do[self.estateId]
            model = loader.loadModel(self.modelPath + self.anims[0])
            self.colNode = model.find('**/+CollisionNode')
            if self.typeIndex == 234:
                self.colNode.setScale(0.5)
            self.colNode.reparentTo(self)
            self.colNode.wrtReparentTo(estate.petColls)
            model.removeNode()
