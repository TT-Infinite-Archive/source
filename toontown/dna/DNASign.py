from panda3d.core import LVector4f, NodePath, DecalEffect
import DNANode
import DNAUtil

class DNASign(DNANode.DNANode):
    COMPONENT_CODE = 5

    def __init__(self):
        DNANode.DNANode.__init__(self, '')
        self.code = ''
        self.color = LVector4f(1, 1, 1, 1)

    def getCode(self):
        return self.code

    def setCode(self, code):
        self.code = code

    def getColor(self):
        return self.color

    def setColor(self, color):
        self.color = color

    def makeFromDGI(self, dgi):
        DNANode.DNANode.makeFromDGI(self, dgi)
        self.code = DNAUtil.dgiExtractString8(dgi)
        self.color = DNAUtil.dgiExtractColor(dgi)

    def traverse(self, nodePath, dnaStorage):
        if self.code:
            node = dnaStorage.findNode(self.code)
            node.setName(self.name)
        else:
            node = NodePath(self.name)

        signOrigin = nodePath.find('**/*sign_origin')
        if not signOrigin:
            signOrigin = nodePath

        node.reparentTo(signOrigin)
        node.setDepthOffset(5)
        node.setPosHprScale(signOrigin, self.pos, self.hpr, self.scale)
        node.setPos(node, 0, -0.1, 0)
        node.setColor(self.color)

        for child in self.children:
            child.traverse(node, dnaStorage)

        node.flattenStrong()
