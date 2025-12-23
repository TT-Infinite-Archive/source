from otp.ai.AIBase import *
from otp.otpbase import OTPGlobals
from direct.interval.IntervalGlobal import *
from direct.directnotify import DirectNotifyGlobal
from direct.distributed import ClockDelta
from direct.task import Task
from direct.directnotify import DirectNotifyGlobal
from direct.distributed import DistributedObjectAI
from direct.distributed import DistributedNodeAI
from toontown.estate import GardenGlobals

def recurseParent(intoNode, ParentName):
    parent = intoNode.getParent(0)
    if not parent or parent.getName() == 'render':
        return 0
    elif parent.getName() == ParentName:
        return 1
    else:
        return recurseParent(parent, ParentName)

class DistributedLawnDecorAI(DistributedNodeAI.DistributedNodeAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedLawnDecorAI')

    def __init__(self, air, ownerIndex = 0, plot = 0):
        DistributedNodeAI.DistributedNodeAI.__init__(self, air)
        self.ownerIndex = ownerIndex
        self.plot = plot
        self.occupied = True
        self.estateId = 0
        self.occupantId = None
        self.lastMovie = None
        self.box = None
        self.colNode = None
        #self.node = hidden.attachNewNode('DistributedPlantAI')

        #only one toon can be interacting with it
        self.interactingToonId = 0

    def generate(self):
        DistributedNodeAI.DistributedNodeAI.generate(self)

    def delete(self):
        #del self.pos
        #taskMgr.remove(self.detectName)
        self.ignoreAll()
        if self.colNode:
            self.colNode.removeNode()
        DistributedNodeAI.DistributedNodeAI.delete(self)

    def destroy(self):
        self.notify.info('destroy entity(elevatorMaker) %s' % self.entId)
        DistributedNodeAI.DistributedNodeAI.destroy(self)

    def setPos(self, x,y,z):
        DistributedNodeAI.DistributedNodeAI.setPos(self, x ,y ,z )
        #self.sendUpdate("setPos", [x,y,z])

    def setPlot(self, plot):
        self.plot = plot

    def getPlot(self):
        return self.plot

    def setBox(self, box):
        self.box = box

    def getBox(self):
        return self.box.doId if self.box else 0

    def getIndex(self):
        return self.box.objects.index(self) if self.box else 0

    def setOwnerIndex(self, index):
        self.ownerIndex = index

    def getOwnerIndex(self):
        return self.ownerIndex

    def setEstateId(self, estateId):
        self.estateId = estateId

    def plotEntered(self, optional = None):
        self.occupantId = self.air.getAvatarIdFromSender()
        #print("entered %s" % (senderId))
        #this is called when the plot has been entered

    def setH(self, h):
        DistributedNodeAI.DistributedNodeAI.setH(self, h)
        #self.sendUpdate('setH', [h])

    def getHeading(self):
        return DistributedNodeAI.DistributedNodeAI.getH(self)

    def d_setH(self, h):
        #print("Sending Distributed H")
        self.sendUpdate('setHeading', [h])

    def b_setH(self, h):
        self.setH(h)
        self.d_setH(h)

    def getPosition(self):
        position = self.getPos()
        return position[0], position[1], position[2]

    def d_setPosition(self, x, y, z):
        self.sendUpdate('setPosition', [x,y,z])

    def b_setPosition(self, x, y, z):
        self.setPosition(x,y,z)
        self.d_setPosition(x,y,z)


    def setPosition(self, x, y, z):
        self.setPos(x,y,z)

    def removeItem(self):
        senderId = self.air.getAvatarIdFromSender()

        zoneId = self.zoneId
        estateOwnerDoId = simbase.air.estateMgr.zone2owner.get(zoneId)

        if not senderId == estateOwnerDoId:
            self.notify.warning("how did this happen, picking a flower you don't own")
            return

        if not self.requestInteractingToon(senderId):
            self.sendInteractionDenied(senderId)
            return

        if estateOwnerDoId:
            estate = simbase.air.estateMgr.estate.get(estateOwnerDoId)
            if estate:
                #we should have a valid DistributedEstateAI at this point
                self.setMovie(GardenGlobals.MOVIE_REMOVE, senderId)

    def doEpoch(self, numEpochs):
        return (0, 0)

    def hasFruit(self):
        return False

    def hasGagBonus(self):
        return False

    def setMovie(self, mode, avId, extraArgs = None):
        self.lastMovie = mode
        self.lastMovieAvId = avId
        self.lastMovieArgs = extraArgs
        self.sendUpdate("setMovie", [mode, avId])

        if (mode == GardenGlobals.MOVIE_CLEAR):
            self.clearInteractingToon()

    def movieDone(self):
        self.clearInteractingToon()
        self.notify.debug('---- got movieDone, self.lastMovie=%d lastMovieAvId=%d---')
        if self.lastMovie == GardenGlobals.MOVIE_REMOVE:
            self.lastMovie = None
            zoneId = self.zoneId
            avId = self.lastMovieAvId
            estateOwnerDoId = simbase.air.estateMgr.zone2owner.get(zoneId)
            estate = simbase.air.estateMgr.estate.get(estateOwnerDoId)
            if estate:
                itemId = estate.removePlantAndPlaceGardenPlot(self.ownerIndex, self.plot)

                # tell the gardenplot to tell the toon to finish 'removing'
                item = simbase.air.doId2do.get(itemId)
                item.setMovie(GardenGlobals.MOVIE_FINISHREMOVING, avId)
        elif self.lastMovie == GardenGlobals.MOVIE_FINISHPLANTING or\
             self.lastMovie == GardenGlobals.MOVIE_HARVEST:
            self.lastMovie = None
            zoneId = self.zoneId
            avId = self.lastMovieAvId
            estateOwnerDoId = simbase.air.estateMgr.zone2owner.get(zoneId)
            estate = simbase.air.estateMgr.estate.get(estateOwnerDoId)
            if estate:
                itemId = self.doId
                # tell the gardenplot to tell the toon to clear the movie, so the
                # results dialog doesn't come up again when he exits from his house
                item = simbase.air.doId2do.get(itemId)
                item.setMovie(GardenGlobals.MOVIE_CLEAR, avId)


    def requestInteractingToon(self, toonId):
        """
        if no one else is interacting with this plant, return true
        and note which toon is now interacting with it
        """
        #debug only, will cause all actions to be denied
        if simbase.config.GetBool('garden-approve-all-actions', 0):
            return True

        #debug only, will cause all actions to be denied
        if simbase.config.GetBool('garden-deny-all-actions', 0):
            return False

        retval = False
        if self.interactingToonId == 0:
            self.setInteractingToon(toonId)
            retval = True
            self.notify.debug('returning True in requestInteractingToon')
        else:
            self.notify.debug( 'denying interaction by %d since %s is using it' % (toonId, self.getInteractingToon()))

        return retval

    def clearInteractingToon(self):
        self.setInteractingToon(0)

    def setInteractingToon(self, toonId):
        """
        which toon is interacting with this plant
        """
        self.notify.debug('setting interactingToonId=%d' % toonId)
        self.interactingToonId = toonId

    def getInteractingToon(self):
        return self.interactingToonId

    def sendInteractionDenied(self, toonId):
        self.notify.debug('sending interaction denied to %d' % toonId)
        self.sendUpdate('interactionDenied', [toonId])

    def setupPetCollision(self):
        if simbase.wantPets:
            collSphereOffset = 0.0
            collSphereRadius = 1.0
            estate = self.air.doId2do[self.estateId]
            if collSphereOffset <= 0.1:
                colSphere = CollisionSphere(0, 0, 0, collSphereRadius)
            else:
                colSphere = CollisionTube(0, -collSphereOffset, 0, 0, collSphereOffset, 0, collSphereRadius)
            colSphere.setTangible(1)
            colNode = CollisionNode(f'petColl-{self.plot}')
            colNode.addSolid(colSphere)
            self.colNode = self.attachNewNode(colNode)
            self.colNode.wrtReparentTo(estate.petColls)

    def stick2Ground(self, estate):
        if simbase.wantPets:
            if self.isEmpty():
                return
            geomPreviouslyStashed = False
            if estate.geom.isStashed():
                geomPreviouslyStashed = True
                estate.geom.unstash()
            testPath = NodePath('testPath')
            testPath.reparentTo(estate.geom)
            cRay = CollisionRay(0.0, 0.0, 40000.0, 0.0, 0.0, -1.0)
            cRayNode = CollisionNode(f'estate-FloorRay-{self.plot}')
            cRayNode.addSolid(cRay)
            cRayNode.setFromCollideMask(OTPGlobals.FloorBitmask)
            cRayNode.setIntoCollideMask(BitMask32.allOff())
            cRayNodePath = testPath.attachNewNode(cRayNode)
            queue = CollisionHandlerQueue()
            picker = CollisionTraverser()
            picker.addCollider(cRayNodePath, queue)

            testPath.setPos(self.getX(), self.getY(), 0)
            picker.traverse(estate.geom)
            if queue.getNumEntries() > 0:
                queue.sortEntries()
                for index in range(queue.getNumEntries()):
                    entry = queue.getEntry(index)
                    if recurseParent(entry.getIntoNode(), 'terrain_DNARoot'):
                        self.setZ(entry.getSurfacePoint(estate.geom)[2] + 0.1)
            if geomPreviouslyStashed:
                estate.geom.stash()
