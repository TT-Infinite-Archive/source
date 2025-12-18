from . import DNALandmarkBuilding
from . import DNAUtil

class DNAAnimBuilding(DNALandmarkBuilding.DNALandmarkBuilding):
    COMPONENT_CODE = 16

    def __init__(self, name):
        DNALandmarkBuilding.DNALandmarkBuilding.__init__(self, name)
        self.animName = ''

    def setAnim(self, anim):
        self.animName = anim

    def getAnim(self):
        return self.animName

    def makeFromDGI(self, dgi):
        DNALandmarkBuilding.DNALandmarkBuilding.makeFromDGI(self, dgi)
        self.animName = DNAUtil.dgiExtractString8(dgi)

    def traverse(self, nodePath, dnaStorage):
        node = dnaStorage.findNode(self.code)
        node.reparentTo(nodePath, 0)
        node.setName(self.name)
        node.setPosHprScale(self.pos, self.hpr, self.scale)
        node.setTag('DNAAnim', self.animName)
        self.setupSuitBuildingOrigin(nodePath, node)

        for child in self.children:
            child.traverse(nodePath, dnaStorage)

        nodePath.flattenStrong()
