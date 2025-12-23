from . import DistributedLawnDecor
from direct.directnotify import DirectNotifyGlobal
from direct.showbase.ShowBase import *
from . import GardenGlobals
from .DistributedGardenPlot import DistributedGardenPlot
from .DistributedFlower import DistributedFlower
from toontown.toonbase import TTLocalizer
from toontown.estate import PlantingGUI
from toontown.estate import PlantTreeGUI
from direct.distributed import DistributedNode
from panda3d.core import NodePath, Vec3

class DistributedGardenBox(DistributedLawnDecor.DistributedLawnDecor):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedGardenPlot')

    def __init__(self, cr):
        DistributedLawnDecor.DistributedLawnDecor.__init__(self, cr)
        self.plantPath = NodePath('plantPath')
        self.plantPath.reparentTo(self)
        self.plotScale = 1.0
        self.plantingGuiDoneEvent = 'plantingGuiDone'
        self.defaultModel = 'phase_5.5/models/estate/planterC'

    def announceGenerate(self):
        self.notify.debug('announceGenerate')
        DistributedLawnDecor.DistributedLawnDecor.announceGenerate(self)
        messenger.send('boxGenerated_%s' % self.getDoId())

    def doModelSetup(self):
        if self.typeIndex == GardenGlobals.BOX_THREE:
            self.defaultModel = 'phase_5.5/models/estate/planterA'
        elif self.typeIndex == GardenGlobals.BOX_TWO:
            self.defaultModel = 'phase_5.5/models/estate/planterC'
        else:
            self.defaultModel = 'phase_5.5/models/estate/planterD'
            self.collSphereOffset = 0.0
            self.collSphereRadius = self.collSphereRadius * 1.41
            self.plotScale = Vec3(1.0, 1.0, 1.0)

    def setupShadow(self):
        pass

    def loadModel(self):
        self.rotateNode = self.plantPath.attachNewNode('rotate')
        self.model = None
        self.model = loader.loadModel(self.defaultModel)
        self.model.setScale(self.plotScale)
        self.model.reparentTo(self.rotateNode)
        house = base.cr.playGame.hood.loader.geom.find('**/esHouse_%d' % self.ownerIndex)
        self.reparentTo(house)
        self.wrtReparentTo(render)
        self.stick2Ground()
        return

    def setPosition(self, *pos):
        previousHpr = self.getHpr()
        DistributedLawnDecor.DistributedLawnDecor.setPosition(self, *pos)
        if self.model:
            house = base.cr.playGame.hood.loader.geom.find('**/esHouse_%d' % self.ownerIndex)
            self.reparentTo(house)
            self.wrtReparentTo(render)
            self.stick2Ground()
            self.setHpr(previousHpr)

            # Fix plots/flowers
            for plot in self.cr.doFindAllInstances(DistributedGardenPlot):
                if plot.getBox() == self.doId:
                    plot.linkBox()
            for flower in self.cr.doFindAllInstances(DistributedFlower):
                if flower.getBox() == self.doId:
                    flower.linkBox()

    def handleEnterPlot(self, entry = None):
        pass

    def handleExitPlot(self, entry = None):
        DistributedLawnDecor.DistributedLawnDecor.handleExitPlot(self, entry)

    def setTypeIndex(self, typeIndex):
        self.typeIndex = typeIndex
