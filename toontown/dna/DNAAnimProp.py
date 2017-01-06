import DNAProp
from DNAUtil import *

class DNAAnimProp(DNAProp.DNAProp):
    COMPONENT_CODE = 14

    def __init__(self, name):
        DNAProp.DNAProp.__init__(self, name)
        self.animName = ''

    def setAnim(self, anim):
        self.animName = anim

    def getAnim(self):
        return self.animName

    def makeFromDGI(self, dgi):
        DNAProp.DNAProp.makeFromDGI(self, dgi)
        self.animName = dgiExtractString8(dgi)

    def traverse(self, nodePath, dnaStorage):
        if self.code == 'DCS':
            node = ModelNode(self.name)
            node.setPreserveTransform(ModelNode.PTNet)
            node = nodePath.attachNewNode(node, 0)
        else:
            node = dnaStorage.findNode(self.code)
            node.reparentTo(nodePath, 0)
            node.setName(self.name)

        node.setTag('DNAAnim', self.animName)
        node.setPosHprScale(self.pos, self.hpr, self.scale)
        node.setColorScale(self.color, 0)
        node.flattenStrong()

        for child in self.children:
            child.traverse(node, dnaStorage)