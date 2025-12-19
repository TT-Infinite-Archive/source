from panda3d.physics import ActorNode
from panda3d.core import ConfigVariableInt, FadeLODNode, GeomNode, LODNode, NodePath, Point3, Texture
from direct.directnotify import DirectNotifyGlobal
from direct.gui.DirectGui import *
from direct.interval.IntervalGlobal import *
from otp.avatar import ShadowCaster
from toontown.racing.KartDNA import *
from toontown.toonbase import TTLocalizer

class Kart(NodePath, ShadowCaster.ShadowCaster):
    notify = DirectNotifyGlobal.directNotify.newCategory('Kart')
    index = 0
    baseScale = 2.0
    RFWHEEL = 0
    LFWHEEL = 1
    RRWHEEL = 2
    LRWHEEL = 3
    wheelData = [{'node': 'wheel*Node2'},
     {'node': 'wheel*Node1'},
     {'node': 'wheel*Node3'},
     {'node': 'wheel*Node4'}]
    ShadowScale = 2.5
    SFX_BaseDir = 'phase_6/audio/sfx/'
    SFX_KartStart = SFX_BaseDir + 'KART_Engine_start_%d.ogg'
    SFX_KartLoop = SFX_BaseDir + 'KART_Engine_loop_%d.ogg'

    def __init__(self):
        NodePath.__init__(self)
        an = ActorNode('vehicle-test')
        anp = NodePath(an)
        NodePath.assign(self, anp)
        self.actorNode = an
        ShadowCaster.ShadowCaster.__init__(self, False)
        Kart.index += 1
        self.updateFields = []
        self.kartDNA = [-1] * getNumFields()
        self.kartAccessories = {EKartDNA.EB_TYPE: None,
         EKartDNA.SP_TYPE: None,
         EKartDNA.FWW_TYPE: (None, None),
         EKartDNA.BWW_TYPE: (None, None)}
        self.texCount = 1
        return

    def delete(self):
        self.__stopWheelSpin()
        del self.kartDNA
        del self.updateFields
        self.kartLoopSfx.stop()
        NodePath.removeNode(self)
        ShadowCaster.ShadowCaster.delete(self)

    def getKartBounds(self):
        return self.geom[0].getTightBounds()

    def generateKart(self, forGui = 0):
        self.LODnode = FadeLODNode('lodNode')
        self.LODpath = self.attachNewNode(self.LODnode)
        self.LODnode.setFadeTime(0.15)
        self.geom = {}
        self.pitchNode = {}
        self.toonNode = {}
        self.rotateNode = self.attachNewNode('rotate')
        levelIn = [ConfigVariableInt('lod1-in', 30).getValue(), ConfigVariableInt('lod2-in', 80).getValue(), ConfigVariableInt('lod2-in', 200).getValue()]
        levelOut = [ConfigVariableInt('lod1-out', 0).getValue(), ConfigVariableInt('lod2-out', 30).getValue(), ConfigVariableInt('lod2-out', 80).getValue()]
        lodRequired = 3
        if forGui:
            lodRequired = 1
            levelIn[0] = ConfigVariableInt('lod1-in', 2500).getValue()
            levelIn[1] = ConfigVariableInt('lod1-out', 0).getValue()
        self.toonSeat = NodePath('toonSeat')
        for level in range(lodRequired):
            self.__createLODKart(level)
            self.LODnode.addSwitch(levelIn[level], levelOut[level])

        self.setScale(self.baseScale)
        self.flattenMedium()
        for level in range(lodRequired):
            self.toonSeat = self.toonSeat.instanceTo(self.toonNode[level])

        self.LODpath.reparentTo(self.rotateNode)
        tempNode = NodePath('tempNode')
        self.accGeomScale = tempNode.getScale(self.pitchNode[0]) * self.baseScale
        tempNode.removeNode()
        self.__applyBodyColor()
        self.__applyEngineBlock()
        self.__applySpoiler()
        self.__applyFrontWheelWells()
        self.__applyBackWheelWells()
        self.__applyRims()
        self.__applyDecals()
        self.__applyAccessoryColor()
        self.wheelCenters = []
        self.wheelBases = []
        for wheel in self.wheelData:
            center = self.geom[0].find('**/' + wheel['node'])
            self.wheelCenters.append(center)
            wheelBase = center.getParent().attachNewNode('wheelBase')
            wheelBase.setPos(center.getPos())
            wheelBase.setZ(0)
            self.wheelBases.append(wheelBase)

        self.wheelBaseH = self.wheelCenters[0].getH()
        self.__startWheelSpin()
        self.setWheelSpinSpeed(0)
        if not forGui:
            self.shadowJoint = self.geom[0]
            self.initializeDropShadow()
            self.setActiveShadow()
            self.dropShadow.setScale(self.ShadowScale)
        else:
            self.shadowJoint = self.LODpath
            self.initializeDropShadow()
            self.setActiveShadow()
            self.dropShadow.setScale(1.3, 3, 1)
        kartType = self.kartDNA[EKartDNA.BODY_TYPE]
        self.kartStartSfx = loader.loadSfx(self.SFX_KartStart % kartType)
        self.kartLoopSfx = loader.loadSfx(self.SFX_KartLoop % kartType)
        self.kartLoopSfx.setLoop()

    def __createLODKart(self, level):
        kartBodyPath = getKartModelPath(self.kartDNA[EKartDNA.BODY_TYPE], level)
        self.geom[level] = loader.loadModel(kartBodyPath)
        self.geom[level].reparentTo(self.LODpath)
        self.geom[level].setH(180)
        self.geom[level].setPos(0.0, 0, 0.025)
        self.pitchNode[level] = self.geom[level].find('**/suspensionNode')
        self.toonNode[level] = self.geom[level].find('**/toonNode')
        scale = 1.0 / self.pitchNode[level].getScale()[0]
        scale /= self.baseScale
        self.toonNode[level].setScale(scale)
        h = (180 + self.pitchNode[level].getH()) % 360
        self.toonNode[level].setH(h)
        pos = Point3(0, -1.3, -7)
        self.toonNode[level].setPos(pos)

    def resetGeomPos(self):
        for level in list(self.geom.keys()):
            self.geom[level].setPos(0, 0, 0.025)

    def __update(self):
        for field in self.updateFields:
            if field == EKartDNA.BODY_TYPE:
                if hasattr(self, 'geom'):
                    for kart in self.geom:
                        self.geom[kart].removeNode()
                        self.__createLODKart(kart)
                        self.geom[kart].reparentTo(self.rotateNode)

                    self.__applyBodyColor()
                    self.__applyEngineBlock()
                    self.__applySpoiler()
                    self.__applyFrontWheelWells()
                    self.__applyRims()
                    self.__applyDecals()
                    self.__applyAccessoryColor()
                else:
                    raise Exception('Kart::__update - Has this method been called before generateKart?')
            elif field == EKartDNA.BODY_COLOR:
                self.__applyBodyColor()
            elif field == EKartDNA.ACC_COLOR:
                self.__applyAccessoryColor()
            elif field == EKartDNA.EB_TYPE:
                if self.kartAccessories[EKartDNA.EB_TYPE] != None:
                    name = self.kartAccessories[EKartDNA.EB_TYPE].getName()
                    for key in list(self.geom.keys()):
                        self.geom[key].find('**/%s' % name).removeNode()

                    self.kartAccessories[EKartDNA.EB_TYPE].removeNode()
                    self.kartAccessories[EKartDNA.EB_TYPE] = None
                self.__applyEngineBlock()
            elif field == EKartDNA.SP_TYPE:
                if self.kartAccessories[EKartDNA.SP_TYPE] != None:
                    name = self.kartAccessories[EKartDNA.SP_TYPE].getName()
                    for key in list(self.geom.keys()):
                        self.geom[key].find('**/%s' % name).removeNode()

                    self.kartAccessories[EKartDNA.SP_TYPE].removeNode()
                    self.kartAccessories[EKartDNA.SP_TYPE] = None
                self.__applySpoiler()
            elif field == EKartDNA.FWW_TYPE:
                if self.kartAccessories[EKartDNA.FWW_TYPE] != (None, None):
                    left, right = self.kartAccessories[EKartDNA.FWW_TYPE]
                    for key in list(self.geom.keys()):
                        self.geom[key].find('**/%s' % left.getName()).removeNode()
                        self.geom[key].find('**/%s' % right.getName()).removeNode()

                    left.removeNode()
                    right.removeNode()
                    self.kartAccessories[EKartDNA.FWW_TYPE] = (None, None)
                self.__applyFrontWheelWells()
            elif field == EKartDNA.BWW_TYPE:
                if self.kartAccessories[EKartDNA.BWW_TYPE] != (None, None):
                    left, right = self.kartAccessories[EKartDNA.BWW_TYPE]
                    for key in list(self.geom.keys()):
                        self.geom[key].find('**/%s' % left.getName()).removeNode()
                        self.geom[key].find('**/%s' % right.getName()).removeNode()

                    left.removeNode()
                    right.removeNode()
                    self.kartAccessories[EKartDNA.BWW_TYPE] = (None, None)
                self.__applyBackWheelWells()
            else:
                if field == EKartDNA.RIMS_TYPE:
                    self.__applyRims()
                elif field == EKartDNA.DECAL_TYPE:
                    self.__applyDecals()
                self.__applyAccessoryColor()

        self.updateFields = []
        return

    def updateDNAField(self, field, fieldValue):
        if field == EKartDNA.BODY_TYPE:
            self.setBodyType(fieldValue)
        elif field == EKartDNA.BODY_COLOR:
            self.setBodyColor(fieldValue)
        elif field == EKartDNA.ACC_COLOR:
            self.setAccessoryColor(fieldValue)
        elif field == EKartDNA.EB_TYPE:
            self.setEngineBlockType(fieldValue)
        elif field == EKartDNA.SP_TYPE:
            self.setSpoilerType(fieldValue)
        elif field == EKartDNA.FWW_TYPE:
            self.setFrontWheelWellType(fieldValue)
        elif field == EKartDNA.BWW_TYPE:
            self.setBackWheelWellType(fieldValue)
        elif field == EKartDNA.RIMS_TYPE:
            self.setRimType(fieldValue)
        elif field == EKartDNA.DECAL_TYPE:
            self.setDecalType(fieldValue)
        self.updateFields.append(field)
        self.__update()

    def __applyBodyColor(self):
        if self.kartDNA[EKartDNA.BODY_COLOR] == InvalidEntry:
            bodyColor = getDefaultColor()
        else:
            bodyColor = getAccessory(self.kartDNA[EKartDNA.BODY_COLOR])
        for kart in self.geom:
            kartBody = self.geom[kart].find('**/chasse')
            kartBody.setColorScale(bodyColor)

    def __applyAccessoryColor(self):
        if self.kartDNA[EKartDNA.ACC_COLOR] == InvalidEntry:
            accColor = getDefaultColor()
        else:
            accColor = getAccessory(self.kartDNA[EKartDNA.ACC_COLOR])
        for kart in self.geom:
            hoodDecal = self.geom[kart].find('**/hoodDecal')
            rightSideDecal = self.geom[kart].find('**/rightSideDecal')
            leftSideDecal = self.geom[kart].find('**/leftSideDecal')
            hoodDecal.setColorScale(accColor)
            rightSideDecal.setColorScale(accColor)
            leftSideDecal.setColorScale(accColor)

        for type in [EKartDNA.EB_TYPE, EKartDNA.SP_TYPE]:
            model = self.kartAccessories.get(type, None)
            if model != None and not model.find('**/vertex').isEmpty():
                if self.kartDNA[EKartDNA.ACC_COLOR] == InvalidEntry:
                    accColor = getDefaultColor()
                else:
                    accColor = getAccessory(self.kartDNA[EKartDNA.ACC_COLOR])
                model.find('**/vertex').setColorScale(accColor)

        for type in [EKartDNA.FWW_TYPE, EKartDNA.BWW_TYPE]:
            lModel, rModel = self.kartAccessories.get(type, (None, None))
            if lModel != None and not lModel.find('**/vertex').isEmpty():
                if self.kartDNA[EKartDNA.ACC_COLOR] == InvalidEntry:
                    accColor = getDefaultColor()
                else:
                    accColor = getAccessory(self.kartDNA[EKartDNA.ACC_COLOR])
                lModel.find('**/vertex').setColorScale(accColor)
                rModel.find('**/vertex').setColorScale(accColor)

        return

    def __applyEngineBlock(self):
        ebType = self.kartDNA[EKartDNA.EB_TYPE]
        if ebType == InvalidEntry:
            return
        ebPath = getAccessory(ebType)
        attachNode = getAccessoryAttachNode(ebType)
        model = loader.loadModel(ebPath)
        self.kartAccessories[EKartDNA.EB_TYPE] = model
        model.setScale(self.accGeomScale)
        if not model.find('**/vertex').isEmpty():
            if self.kartDNA[EKartDNA.ACC_COLOR] == InvalidEntry:
                accColor = getDefaultColor()
            else:
                accColor = getAccessory(self.kartDNA[EKartDNA.ACC_COLOR])
            model.find('**/vertex').setColorScale(accColor)
        for kart in self.geom:
            engineBlockNode = self.geom[kart].find('**/%s' % attachNode)
            model.setPos(engineBlockNode.getPos(self.pitchNode[kart]))
            model.setHpr(engineBlockNode.getHpr(self.pitchNode[kart]))
            model.instanceTo(self.pitchNode[kart])

    def __applySpoiler(self):
        spType = self.kartDNA[EKartDNA.SP_TYPE]
        if spType == InvalidEntry:
            return
        spPath = getAccessory(spType)
        attachNode = getAccessoryAttachNode(spType)
        model = loader.loadModel(spPath)
        self.kartAccessories[EKartDNA.SP_TYPE] = model
        model.setScale(self.accGeomScale)
        for kart in self.geom:
            spoilerNode = self.geom[kart].find('**/%s' % attachNode)
            model.setPos(spoilerNode.getPos(self.pitchNode[kart]))
            model.setHpr(spoilerNode.getHpr(self.pitchNode[kart]))
            model.instanceTo(self.pitchNode[kart])

    def __applyRims(self):
        if self.kartDNA[EKartDNA.RIMS_TYPE] == InvalidEntry:
            rimTexPath = getAccessory(getDefaultRim())
        else:
            rimTexPath = getAccessory(self.kartDNA[EKartDNA.RIMS_TYPE])
        rimTex = loader.loadTexture('%s.jpg' % rimTexPath, '%s_a.rgb' % rimTexPath)
        for kart in self.geom:
            leftFrontWheelRim = self.geom[kart].find('**/leftFrontWheelRim')
            rightFrontWheelRim = self.geom[kart].find('**/rightFrontWheelRim')
            leftRearWheelRim = self.geom[kart].find('**/leftRearWheelRim')
            rightRearWheelRim = self.geom[kart].find('**/rightRearWheelRim')
            rimTex.setMinfilter(Texture.FTLinearMipmapLinear)
            leftFrontWheelRim.setTexture(rimTex, self.texCount)
            rightFrontWheelRim.setTexture(rimTex, self.texCount)
            leftRearWheelRim.setTexture(rimTex, self.texCount)
            rightRearWheelRim.setTexture(rimTex, self.texCount)

        self.texCount += 1

    def __applyFrontWheelWells(self):
        fwwType = self.kartDNA[EKartDNA.FWW_TYPE]
        if fwwType == InvalidEntry:
            return
        fwwPath = getAccessory(fwwType)
        attachNode = getAccessoryAttachNode(fwwType)
        leftAttachNode = attachNode % 'left'
        rightAttachNode = attachNode % 'right'
        leftModel = loader.loadModel(fwwPath)
        rightModel = loader.loadModel(fwwPath)
        self.kartAccessories[EKartDNA.FWW_TYPE] = (leftModel, rightModel)
        if not leftModel.find('**/vertex').isEmpty():
            if self.kartDNA[EKartDNA.ACC_COLOR] == InvalidEntry:
                accColor = getDefaultColor()
            else:
                accColor = getAccessory(self.kartDNA[EKartDNA.ACC_COLOR])
            leftModel.find('**/vertex').setColorScale(accColor)
            rightModel.find('**/vertex').setColorScale(accColor)
        for kart in self.geom:
            leftNode = self.geom[kart].find('**/%s' % leftAttachNode)
            rightNode = self.geom[kart].find('**/%s' % rightAttachNode)
            leftNodePath = leftModel.instanceTo(self.pitchNode[kart])
            leftNodePath.setPos(rightNode.getPos(self.pitchNode[kart]))
            leftNodePath.setHpr(rightNode.getHpr(self.pitchNode[kart]))
            leftNodePath.setScale(self.accGeomScale)
            leftNodePath.setSx(-1.0 * leftNodePath.getSx())
            leftNodePath.setTwoSided(True)
            rightNodePath = rightModel.instanceTo(self.pitchNode[kart])
            rightNodePath.setPos(leftNode.getPos(self.pitchNode[kart]))
            rightNodePath.setHpr(leftNode.getHpr(self.pitchNode[kart]))
            rightNodePath.setScale(self.accGeomScale)

    def __applyBackWheelWells(self):
        bwwType = self.kartDNA[EKartDNA.BWW_TYPE]
        if bwwType == InvalidEntry:
            return
        bwwPath = getAccessory(bwwType)
        attachNode = getAccessoryAttachNode(bwwType)
        leftAttachNode = attachNode % 'left'
        rightAttachNode = attachNode % 'right'
        leftModel = loader.loadModel(bwwPath)
        rightModel = loader.loadModel(bwwPath)
        self.kartAccessories[EKartDNA.BWW_TYPE] = (leftModel, rightModel)
        if not leftModel.find('**/vertex').isEmpty():
            if self.kartDNA[EKartDNA.ACC_COLOR] == InvalidEntry:
                accColor = getDefaultColor()
            else:
                accColor = getAccessory(self.kartDNA[EKartDNA.ACC_COLOR])
            leftModel.find('**/vertex').setColorScale(accColor)
            rightModel.find('**/vertex').setColorScale(accColor)
        for kart in self.geom:
            leftNode = self.geom[kart].find('**/%s' % leftAttachNode)
            rightNode = self.geom[kart].find('**/%s' % rightAttachNode)
            leftNodePath = leftModel.instanceTo(self.pitchNode[kart])
            leftNodePath.setPos(rightNode.getPos(self.pitchNode[kart]))
            leftNodePath.setHpr(rightNode.getHpr(self.pitchNode[kart]))
            leftNodePath.setScale(self.accGeomScale)
            leftNodePath.setSx(-1.0 * leftNodePath.getSx())
            leftNodePath.setTwoSided(True)
            rightNodePath = rightModel.instanceTo(self.pitchNode[kart])
            rightNodePath.setPos(leftNode.getPos(self.pitchNode[kart]))
            rightNodePath.setHpr(leftNode.getHpr(self.pitchNode[kart]))
            rightNodePath.setScale(self.accGeomScale)

    def __applyDecals(self):
        if self.kartDNA[EKartDNA.DECAL_TYPE] != InvalidEntry:
            decalId = getAccessory(self.kartDNA[EKartDNA.DECAL_TYPE])
            kartDecal = getDecalId(self.kartDNA[EKartDNA.BODY_TYPE])
            hoodDecalTex = loader.loadTexture('phase_6/maps/%s_HoodDecal_%s.jpg' % (kartDecal, decalId), 'phase_6/maps/%s_HoodDecal_%s_a.rgb' % (kartDecal, decalId))
            sideDecalTex = loader.loadTexture('phase_6/maps/%s_SideDecal_%s.jpg' % (kartDecal, decalId), 'phase_6/maps/%s_SideDecal_%s_a.rgb' % (kartDecal, decalId))
            hoodDecalTex.setMinfilter(Texture.FTLinearMipmapLinear)
            sideDecalTex.setMinfilter(Texture.FTLinearMipmapLinear)
            for kart in self.geom:
                hoodDecal = self.geom[kart].find('**/hoodDecal')
                rightSideDecal = self.geom[kart].find('**/rightSideDecal')
                leftSideDecal = self.geom[kart].find('**/leftSideDecal')
                hoodDecal.setTexture(hoodDecalTex, self.texCount)
                rightSideDecal.setTexture(sideDecalTex, self.texCount)
                leftSideDecal.setTexture(sideDecalTex, self.texCount)
                hoodDecal.show()
                rightSideDecal.show()
                leftSideDecal.show()

        else:
            for kart in self.geom:
                hoodDecal = self.geom[kart].find('**/hoodDecal')
                rightSideDecal = self.geom[kart].find('**/rightSideDecal')
                leftSideDecal = self.geom[kart].find('**/leftSideDecal')
                hoodDecal.hide()
                rightSideDecal.hide()
                leftSideDecal.hide()

        self.texCount += 1

    def rollSuspension(self, roll):
        for kart in self.pitchNode:
            self.pitchNode[kart].setR(roll)

    def pitchSuspension(self, pitch):
        for kart in self.pitchNode:
            self.pitchNode[kart].setP(pitch)

    def getDNA(self):
        return self.kartDNA

    def setDNA(self, dna):
        if self.kartDNA != [-1] * getNumFields():
            for field in range(len(self.kartDNA)):
                if dna[field] != self.kartDNA[field]:
                    self.updateDNAField(field, dna[field])

            return
        self.kartDNA = dna

    def setBodyType(self, bodyType):
        self.kartDNA[EKartDNA.BODY_TYPE] = bodyType

    def getBodyType(self):
        return self.kartDNA[EKartDNA.BODY_TYPE]

    def setBodyColor(self, bodyColor):
        self.kartDNA[EKartDNA.BODY_COLOR] = bodyColor

    def getBodyColor(self):
        return self.kartDNA[EKartDNA.BODY_COLOR]

    def setAccessoryColor(self, accColor):
        self.kartDNA[EKartDNA.ACC_COLOR] = accColor

    def getAccessoryColor(self):
        return self.kartDNA[EKartDNA.ACC_COLOR]

    def setEngineBlockType(self, ebType):
        self.kartDNA[EKartDNA.EB_TYPE] = ebType

    def getEngineBlockType(self):
        return self.kartDNA[EKartDNA.EB_TYPE]

    def setSpoilerType(self, spType):
        self.kartDNA[EKartDNA.SP_TYPE] = spType

    def getSpoilerType(self):
        return self.kartDNA[EKartDNA.SP_TYPE]

    def setFrontWheelWellType(self, fwwType):
        self.kartDNA[EKartDNA.FWW_TYPE] = fwwType

    def getFrontWheelWellType(self):
        return self.kartDNA[EKartDNA.FWW_TYPE]

    def setBackWheelWellType(self, bwwType):
        self.kartDNA[EKartDNA.BWW_TYPE] = bwwType

    def getBackWheelWellType(self):
        return self.kartDNA[EKartDNA.BWW_TYPE]

    def setRimType(self, rimsType):
        self.kartDNA[EKartDNA.RIMS_TYPE] = rimsType

    def getRimType(self):
        return self.kartDNA[EKartDNA.RIMS_TYPE]

    def setDecalType(self, decalType):
        self.kartDNA[EKartDNA.DECAL_TYPE] = decalType

    def getDecalType(self):
        return self.kartDNA[EKartDNA.DECAL_TYPE]

    def getGeomNode(self):
        return self.geom[0]

    def spinWheels(self, amount):
        newSpin = (self.oldSpinAmount + amount) % 360
        for wheelNode in self.wheelCenters:
            wheelNode.setP(newSpin)

        self.oldSpinAmount = newSpin

    def setWheelSpinSpeed(self, speed):
        pass

    def __startWheelSpin(self):
        self.oldSpinAmount = 0

    def __stopWheelSpin(self):
        pass

    def turnWheels(self, amount):
        amount += self.wheelBaseH
        node = self.wheelCenters[self.RFWHEEL]
        node.setH(amount)
        node = self.wheelCenters[self.LFWHEEL]
        node.setH(amount)

    def generateEngineStartTrack(self):
        length = self.kartStartSfx.length()

        def printVol():
            print(self.kartLoopSfx.getVolume())

        track = Parallel(SoundInterval(self.kartStartSfx), Func(self.kartLoopSfx.play), LerpFunctionInterval(self.kartLoopSfx.setVolume, fromData=0, toData=0.4, duration=length))
        return Sequence(track, Func(printVol))

    def generateEngineStopTrack(self, duration = 0):
        track = Parallel(LerpFunctionInterval(self.kartLoopSfx.setVolume, fromData=0.4, toData=0, duration=duration))
        return track
