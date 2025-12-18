from panda3d.core import DecalEffect
from . import DNADoor

class DNAFlatDoor(DNADoor.DNADoor):
    COMPONENT_CODE = 18

    def traverse(self, nodePath, dnaStorage):
        node = dnaStorage.findNode(self.code)
        node.reparentTo(nodePath, 0)
        node.setScale(hidden, 1, 1, 1)
        node.setPosHpr((0.5, 0, 0), (0, 0, 0))
        node.setColor(self.color)
        node.getNode(0).setEffect(DecalEffect.make())
        node.flattenStrong()
