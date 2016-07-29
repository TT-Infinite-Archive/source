from pandac.PandaModules import *
from DNAError import DNAError
from DNASuitPoint import DNASuitPoint
from DNASuitPath import DNASuitPath
from DNASuitEdge import DNASuitEdge

import gc


class DNAModelCache:
    def __init__(self):
        self.models = {}

    def clear(self):
        for path in self.models:
            self.models[path].removeNode()
            self.models[path].clear()

        self.models.clear()
        ModelPool.garbageCollect()

    def fetch(self, code, path, node):
        if path in self.models:
            modelNode = self.models[path]
            if node:
                np = modelNode.find('**/'+node).copyTo(hidden)
            else:
                np = modelNode.copyTo(hidden)
            np.setTag('DNACode', code)
            np.setTag('DNARoot', node)
            return np

        self.models[path] = loader.loadModel(path, noCache=True)
        return self.fetch(code, path, node)


class DNAStorage:
    notify = directNotify.newCategory('DNAStorage')

    def __init__(self):
        self.modelCache = DNAModelCache()
        self.suitPoints = []
        self.suitPointMap = {}
        self.DNAGroups = {}
        self.DNAVisGroups = []
        self.suitEdges = {}
        self.battleCells = []
        self.nodes = {}
        self.hoodNodes = {}
        self.placeNodes = {}
        self.fonts = {}
        self.blockTitles = {}
        self.blockArticles = {}
        self.blockBuildingTypes = {}
        self.blockDoors = {}
        self.blockNumbers = []
        self.blockZones = {}
        self.suitBlocks = {}
        self.textures = {}
        self.catalogCodes = {}

    def resetModelCache(self):
        self.modelCache.clear()

    def getSuitPath(self, startPoint, endPoint, minPathLen=40, maxPathLen=300):
        path = DNASuitPath()
        path.addPoint(startPoint)
        while path.getNumPoints() < maxPathLen:
            startPointIndex = startPoint.getIndex()
            if startPointIndex == endPoint.getIndex():
                if path.getNumPoints() >= minPathLen:
                    break
            if startPointIndex not in self.suitEdges:
                raise DNAError('Could not find DNASuitPath.')
            edges = self.suitEdges[startPointIndex]
            for edge in edges:
                startPoint = edge.getEndPoint()
                startPointType = startPoint.getPointType()
                if startPointType != DNASuitPoint.FRONT_DOOR_POINT:
                    if startPointType != DNASuitPoint.SIDE_DOOR_POINT:
                        break
            else:
                raise DNAError('Could not find DNASuitPath.')
            path.addPoint(startPoint)
        return path

    def getSuitEdgeTravelTime(self, startIndex, endIndex, suitWalkSpeed):
        startPoint = self.suitPointMap.get(startIndex)
        endPoint = self.suitPointMap.get(endIndex)
        if (not startPoint) or (not endPoint):
            return 0.0
        distance = (endPoint.getPos()-startPoint.getPos()).length()
        return distance / suitWalkSpeed

    def getSuitEdgeZone(self, startIndex, endIndex):
        return self.getSuitEdge(startIndex, endIndex).getZoneId()

    def getAdjacentPoints(self, point):
        path = DNASuitPath()
        startIndex = point.getIndex()
        if startIndex not in self.suitEdges:
            return path
        for edge in self.suitEdges[startIndex]:
            path.addPoint(edge.getEndPoint())
        return path

    def storeSuitPoint(self, suitPoint):
        if not isinstance(suitPoint, DNASuitPoint):
            raise TypeError('suitPoint must be an instance of DNASuitPoint')
        self.suitPoints.append(suitPoint)
        self.suitPointMap[suitPoint.getIndex()] = suitPoint

    def getSuitPointAtIndex(self, index):
        return self.suitPoints[index]

    def getSuitPointWithIndex(self, index):
        return self.suitPointMap.get(index)

    def resetSuitPoints(self):
        # First thing we're going to cleanup is the DNASuitEdges. The DNASuitEdges reference DNASuitPoints so we will
        # clean those up afterwards.
        for i in self.suitEdges.keys():
            for edge in self.suitEdges[i]:
                edge.destroy()
            del self.suitEdges[i][:]
            del self.suitEdges[i]

        # DNASuitPoints don't reference anything inside of them that we care about. Deleting the list should work.
        del self.suitPoints[:]

        # Clear these dictionaries.
        self.suitPointMap.clear()
        self.suitEdges.clear()

    def resetTextures(self):
        self.textures.clear()

    def resetDNAGroups(self):
        self.DNAGroups.clear()

    def getNumDNAVisGroups(self):
        return len(self.DNAVisGroups)

    def getDNAVisGroupName(self, i):
        return self.DNAVisGroups[i].getName()

    def storeDNAVisGroup(self, group):
        self.DNAVisGroups.append(group)

    def storeSuitEdge(self, startIndex, endIndex, zoneId):
        startPoint = self.getSuitPointWithIndex(startIndex)
        endPoint = self.getSuitPointWithIndex(endIndex)
        edge = DNASuitEdge(startPoint, endPoint, zoneId)
        self.suitEdges.setdefault(startIndex, []).append(edge)
        return edge

    def getSuitEdge(self, startIndex, endIndex):
        edges = self.suitEdges[startIndex]
        for edge in edges:
            if edge.getEndPoint().getIndex() == endIndex:
                return edge

    def removeBattleCell(self, cell):
        self.battleCells.remove(cell)

    def storeBattleCell(self, cell):
        self.battleCells.append(cell)

    def resetBattleCells(self):
        del self.battleCells[:]

    def findNode(self, code):
        if code in self.nodes:
            path, node = self.nodes[code]
        elif code in self.hoodNodes:
            path, node = self.hoodNodes[code]
        elif code in self.placeNodes:
            path, node = self.placeNodes[code]
        else:
            self.notify.warning('Unknown node code: '+code)
            return

        return self.modelCache.fetch(code, path, node)

    def resetNodes(self):
        self.nodes.clear()

    def resetHoodNodes(self):
        self.hoodNodes.clear()

    def resetPlaceNodes(self):
        self.placeNodes.clear()

    def storeNode(self, code, path, node):
        self.nodes[code] = (path, node)

    def storeHoodNode(self, code, path, node):
        self.hoodNodes[code] = (path, node)

    def storePlaceNode(self, code, path, node):
        self.placeNodes[code] = (path, node)

    def findFont(self, code):
        if code in self.fonts:
            return self.fonts[code]

    def resetFonts(self):
        self.fonts.clear()

    def storeFont(self, font, code):
        self.fonts[code] = font

    def getBlock(self, name):
        block = name[name.find(':')-2:name.find(':')]
        if not block[0].isdigit():
            block = block[1:]
        return block

    def getBlockBuildingType(self, blockNumber):
        if blockNumber in self.blockBuildingTypes:
            return self.blockBuildingTypes[blockNumber]

    def getTitleFromBlockNumber(self, blockNumber):
        if blockNumber in self.blockTitles:
            return self.blockTitles[blockNumber]
        return ''

    def getDoorPosHprFromBlockNumber(self, blockNumber):
        key = str(blockNumber)
        if key in self.blockDoors:
            return self.blockDoors[key]

    def storeBlockDoor(self, blockNumber, door):
        self.blockDoors[str(blockNumber)] = door

    def storeBlockTitle(self, blockNumber, title):
        self.blockTitles[blockNumber] = title

    def storeBlockArticle(self, blockNumber, article):
        self.blockArticles[blockNumber] = article

    def storeBlockBuildingType(self, blockNumber, buildingType):
        self.blockBuildingTypes[blockNumber] = buildingType

    def storeBlock(self, blockNumber, title, article, bldgType, zoneId):
        self.storeBlockNumber(blockNumber)
        self.storeBlockTitle(blockNumber, title)
        self.storeBlockArticle(blockNumber, article)
        self.storeBlockBuildingType(blockNumber, bldgType)
        self.storeBlockZone(blockNumber, zoneId)

    def storeTexture(self, name, texture):
        self.textures[name] = texture

    def resetDNAVisGroups(self):
        for visGroup in self.DNAVisGroups:
            visGroup.destroy()

        del self.DNAVisGroups[:]

    def getNumDNAVisGroupsAI(self):
        return self.getNumDNAVisGroups()

    def getNumSuitPoints(self):
        return len(self.suitPoints)

    def getNumVisiblesInDNAVisGroup(self, i):
        return self.DNAVisGroups[i].getNumVisibles()

    def getVisibleName(self, i, j):
        return self.DNAVisGroups[i].getVisibleName(j)

    def getDNAVisGroupAI(self, i):
        return self.DNAVisGroups[i]

    def storeCatalogCode(self, category, code):
        if not category in self.catalogCodes:
            self.catalogCodes[category] = []
        self.catalogCodes[category].append(code)

    def getNumCatalogCodes(self, category):
        if category not in self.catalogCodes:
            return -1
        return len(self.catalogCodes[category])

    def resetCatalogCodes(self):
        self.catalogCodes.clear()

    def getCatalogCode(self, category, index):
        return self.catalogCodes[category][index]

    def findTexture(self, name):
        if name in self.textures:
            return self.textures[name]

    def discoverContinuity(self):
        return 1  # TODO

    def resetBlockNumbers(self):
        del self.blockNumbers[:]
        self.blockZones.clear()
        self.blockArticles.clear()
        self.resetBlockDoors()
        self.blockTitles.clear()
        self.blockBuildingTypes.clear()
        self.resetSuitBlocks()

    def getNumBlockNumbers(self):
        return len(self.blockNumbers)

    def storeBlockNumber(self, blockNumber):
        self.blockNumbers.append(blockNumber)

    def getBlockNumberAt(self, index):
        return self.blockNumbers[index]

    def getZoneFromBlockNumber(self, blockNumber):
        if blockNumber in self.blockZones:
            return self.blockZones[blockNumber]

    def storeBlockZone(self, blockNumber, zoneId):
        self.blockZones[blockNumber] = zoneId

    def resetBlockZones(self):
        self.blockZones.clear()

    def resetBlockDoors(self):
        self.blockDoors.clear()

    def getSignTransformFromNodePath(self, nodePath):
        return nodePath.getNetTransform().getMat()

    def storeSuitBlock(self, blockNumber, dept):
        self.suitBlocks[blockNumber] = dept

    def resetSuitBlocks(self):
        self.suitBlocks.clear()

    def isSuitBlock(self, blockNumber):
        return blockNumber in self.suitBlocks

    def getSuitBlockTrack(self, blockNumber):
        return self.suitBlocks.get(blockNumber)

    def cleanup(self):
        self.resetBattleCells()
        self.resetBlockNumbers()
        self.resetDNAGroups()
        self.resetDNAVisGroups()
        self.resetFonts()
        self.resetHoodNodes()
        self.resetNodes()
        self.resetPlaceNodes()
        self.resetSuitPoints()
        self.resetTextures()
        self.resetCatalogCodes()
        self.resetSuitBlocks()
        self.resetModelCache()

        ModelPool.garbageCollect()
        TexturePool.garbageCollect()
        gc.collect()
