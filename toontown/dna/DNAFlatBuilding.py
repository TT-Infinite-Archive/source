from panda3d.core import NodePath, DecalEffect
import DNANode
import DNAWall

import random

class DNAFlatBuilding(DNANode.DNANode):
    COMPONENT_CODE = 9
    currentWallHeight = 0

    def __init__(self, name):
        DNANode.DNANode.__init__(self, name)
        self.width = 0
        self.hasDoor = False

    def setWidth(self, width):
        self.width = width

    def getWidth(self):
        return self.width

    def setCurrentWallHeight(self, currentWallHeight):
        DNAFlatBuilding.currentWallHeight = currentWallHeight

    def getCurrentWallHeight(self):
        return DNAFlatBuilding.currentWallHeight

    def setHasDoor(self, hasDoor):
        self.hasDoor = hasDoor

    def getHasDoor(self):
        return self.hasDoor

    def makeFromDGI(self, dgi):
        DNANode.DNANode.makeFromDGI(self, dgi)
        self.width = dgi.getInt16() / 100.0
        self.hasDoor = dgi.getBool()

    def setupSuitFlatBuilding(self, nodePath, dnaStorage):
        if self.name[:2] != 'tb':
            return

        name = 'sb' + self.name[2:]
        node = nodePath.attachNewNode(name)
        node.setPosHpr(self.pos, self.hpr)

        numCodes = dnaStorage.getNumCatalogCodes('suit_wall')
        if numCodes < 1:
            return

        code = dnaStorage.getCatalogCode(
            'suit_wall', random.randint(0, numCodes - 1))
        wallNode = dnaStorage.findNode(code)
        if not wallNode:
            return

        wallNode.reparentTo(node, 0)
        wallScale = wallNode.getScale()
        wallScale.setX(self.width)
        wallScale.setZ(DNAFlatBuilding.currentWallHeight)
        wallNode.setScale(wallScale)

        if self.hasDoor:
            wallNodePath = node.find('wall_*')
            doorNode = dnaStorage.findNode('suit_door')
            doorNode.reparentTo(wallNodePath, 0)
            doorNode.setScale(hidden, 1, 1, 1)
            doorNode.setPosHpr(0.5, 0, 0, 0, 0, 0)
            wallNodePath.setEffect(DecalEffect.make())

        node.flattenMedium()
        node.stash()

    def setupCogdoFlatBuilding(self, nodePath, dnaStorage):
        if self.name[:2] != 'tb':
            return

        name = 'cb' + self.name[2:]
        node = nodePath.attachNewNode(name)
        node.setPosHpr(self.pos, self.hpr)

        numCodes = dnaStorage.getNumCatalogCodes('cogdo_wall')
        if numCodes < 1:
            return

        code = dnaStorage.getCatalogCode(
            'cogdo_wall', random.randint(0, numCodes - 1))
        wallNode = dnaStorage.findNode(code)
        if not wallNode:
            return

        wallNode.reparentTo(node, 0)
        wallScale = wallNode.getScale()
        wallScale.setX(self.width)
        wallScale.setZ(DNAFlatBuilding.currentWallHeight)
        wallNode.setScale(wallScale)

        if self.hasDoor:
            wallNodePath = node.find('wall_*')
            doorNode = dnaStorage.findNode('suit_door')
            doorNode.reparentTo(wallNodePath, 0)
            doorNode.setScale(hidden, 1, 1, 1)
            doorNode.setPosHpr(0.5, 0, 0, 0, 0, 0)
            wallNodePath.setEffect(DecalEffect.make())

        node.flattenMedium()
        node.stash()

    def traverse(self, nodePath, dnaStorage):
        DNAFlatBuilding.currentWallHeight = 0
        node = nodePath.attachNewNode(self.name)
        internalNode = node.attachNewNode(self.name + '-internal')
        self.scale.setX(self.width)
        internalNode.setScale(self.scale)
        node.setPosHpr(self.pos, self.hpr)

        for child in self.children:
            if isinstance(child, DNAWall.DNAWall):
                child.traverse(internalNode, dnaStorage)
            else:
                child.traverse(node, dnaStorage)

        if DNAFlatBuilding.currentWallHeight > 0:
            cameraBarrier = dnaStorage.findNode('wall_camera_barrier')
            cameraBarrier.reparentTo(internalNode, 0)
            cameraBarrier.setScale((1, 1, DNAFlatBuilding.currentWallHeight))
            internalNode.flattenStrong()
            collisionNode = node.find('**/door_*/+CollisionNode')
            if not collisionNode.isEmpty():
                collisionNode.setName('KnockKnockDoorSphere_' + dnaStorage.getBlock(self.name))
            cameraBarrier.wrtReparentTo(nodePath, 0)
            wallCollection = internalNode.findAllMatches('wall*')
            wallHolder = node.attachNewNode('wall_holder')
            wallDecal = node.attachNewNode('wall_decal')
            windowCollection = internalNode.findAllMatches('**/window*')
            doorCollection = internalNode.findAllMatches('**/door*')
            corniceCollection = internalNode.findAllMatches('**/cornice*_d')
            wallCollection.reparentTo(wallHolder)
            windowCollection.reparentTo(wallDecal)
            doorCollection.reparentTo(wallDecal)
            corniceCollection.reparentTo(wallDecal)
            for i in xrange(wallHolder.getNumChildren()):
                iNode = wallHolder.getChild(i)
                iNode.clearTag('DNACode')
                iNode.clearTag('DNARoot')
            wallHolder.flattenStrong()
            wallDecal.flattenStrong()
            holderChild0 = wallHolder.getChild(0)
            wallDecal.getChildren().reparentTo(holderChild0)
            holderChild0.reparentTo(internalNode)
            holderChild0.setEffect(DecalEffect.make())
            wallHolder.removeNode()
            wallDecal.removeNode()
            self.setupSuitFlatBuilding(nodePath, dnaStorage)
            self.setupCogdoFlatBuilding(nodePath, dnaStorage)
            node.flattenStrong()
