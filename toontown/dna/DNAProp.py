from panda3d.core import LVector4f, ModelNode
from . import DNANode
from . import DNAUtil

class DNAProp(DNANode.DNANode):
    COMPONENT_CODE = 4

    def __init__(self, name):
        DNANode.DNANode.__init__(self, name)
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
        if self.code == 'DCS':
            node = ModelNode(self.name)
            node.setPreserveTransform(ModelNode.PTNet)
            node = nodePath.attachNewNode(node)
        else:
            node = dnaStorage.findNode(self.code)
            if node is None:
                node = nodePath.attachNewNode(self.name, 0)
            else:
                node.reparentTo(nodePath, 0)
                node.setName(self.name)

        node.setPosHprScale(self.pos, self.hpr, self.scale)
        node.setColorScale(self.color, 0)

        # TEMPORARY (remove this once Toffee is finished):
        if self.code == 'the_burrrgh':
            npc = node.findAllMatches('**/+CollisionNode')
            for np in npc:
                if 'snow' in np.getName():
                    np.setTag('footstepCode', 'snow')
        elif self.code == 'donalds_dock':
            npc = node.findAllMatches('**/+CollisionNode')
            for np in npc:
                if 'pier' in np.getName() or 'donalds_boat_floor' in np.getName():
                    np.setTag('footstepCode', 'wood')
        elif self.code == 'daisys_garden':
            npc = node.findAllMatches('**/+CollisionNode')
            for np in npc:
                if 'street_floor_collisions' == np.getName():
                    np.setTag('footstepCode', 'dirt')
        elif self.code in ('prop_snow_pile_full', 'prop_snow_pile_half',
                           'prop_snow_pile_quarter'):
            node.find('**/+CollisionNode').setTag('footstepCode', 'snow')
        elif self.code in ('prop_crate', 'prop_trolley_station'):
            npc = node.findAllMatches('**/+CollisionNode')
            for np in npc:
                np.setTag('footstepCode', 'wood')
        elif self.code == 'prop_snowman':
            node.find('**/floor').setTag('footstepCode', 'snow')
        elif self.code == 'prop_DD_street_water':
            node.find('**/DD_street_water_floor_collisions').setTag('footstepCode', 'wood')
            node.find('**/floor').setTag('footstepCode', 'water')
        elif self.code == 'fishing_spot':
            node.find('**/floor_collision').setTag('footstepCode', 'wood')
        elif self.code == 'daisys_garden_ext':
            npc = node.findAllMatches('**/+CollisionNode')
            for np in npc:
                np.setTag('footstepCode', 'dirt')

        for child in self.children:
            child.traverse(node, dnaStorage)
