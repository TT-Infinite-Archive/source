from toontown.estate import DistributedPlantBaseAI
from direct.directnotify import DirectNotifyGlobal
from . import GardenGlobals

class DistributedGagTreeAI(DistributedPlantBaseAI.DistributedPlantBaseAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedGagTreeAI')

    def __init__(self, typeIndex = 0, waterLevel = 0, growthLevel = 0, optional = False, ownerIndex = 0, plot = 0):
        DistributedPlantBaseAI.DistributedPlantBaseAI.__init__(self, typeIndex, waterLevel, growthLevel, optional, ownerIndex, plot)

        track, level = GardenGlobals.getTreeTrackAndLevel(typeIndex)
        self.gagTrack = track
        self.gagLevel = level

        self.maxFruit = GardenGlobals.PlantAttributes[typeIndex]['maxFruit']

    def hasFruit(self):
        return self.growthLevel >= self.growthThresholds[2]

    def getFruiting(self):
        return self.hasFruit()

    def d_setFruiting(self, fruiting):
        self.sendUpdate('setFruiting', [fruiting])

    def doEpoch(self, numEpochs):
        for i in range(numEpochs):
            waterLevel = self.getWaterLevel()
            growthLevel = self.getGrowthLevel()

            if waterLevel > 0:
                #print "growing plant"
                # grow the plant if it's not wilted
                if self.isWilted():
                    self.b_setWilted(False)
                else:
                    growthLevel += 1
                waterLevel -= 1
            else:
                waterLevel -= 1
                waterLevel = max (waterLevel, self.minWaterLevel)

            if waterLevel == self.minWaterLevel and not self.isWilted():
                # the toon let us die!
                self.b_setWilted(True)
                growthLevel = self.getWiltedLevel(growthLevel)

            self.b_setWaterLevel(waterLevel, False)

            # if we have duplicate gag trees, only 1 of it should bear fruit
            estate = simbase.air.doId2do.get(self.estateId)
            if estate:
                lowestPlotIndex = estate.findLowestGagTreePlot(self.ownerIndex, self.gagTrack,
                                                               self.gagLevel)
                if lowestPlotIndex != self.plot:
                    # aha we are a duplicate tree, force us not to fruit
                    if growthLevel >= self.growthThresholds[2]:
                        growthLevel = self.growthThresholds[2] -1

            self.b_setGrowthLevel(growthLevel, False)

        return (growthLevel, waterLevel)

    def setGrowthLevel(self, growthLevel, finalize):
        DistributedPlantBaseAI.DistributedPlantBaseAI.setGrowthLevel(self, growthLevel, finalize)
        if self.hasFruit():
            # We're fruiting! :D
            self.d_setFruiting(True)
        else:
            # The fruit died! D:
            self.d_setFruiting(False)

    # use this to find the adjusted growth level when a tree wilts
    def getWiltedLevel(self, growthLevel):
        if self.isFruiting():
            growthLevel = self.growthThresholds[2]-1

        return growthLevel

    def getWilted(self):
        return self.optional

    def setWilted(self, wilted, finalize):
        self.optional = wilted
        self.updateEstate(variety=wilted, finalize=finalize)

    def d_setWilted(self, wilted):
        self.sendUpdate('setWilted', [wilted])

    def b_setWilted(self, wilted, finalize=True):
        self.setWilted(wilted, finalize)
        self.d_setWilted(wilted)

    def isWilted(self):
        return self.getWilted()

    def requestHarvest(self):
        senderId = self.air.getAvatarIdFromSender()
        toon = simbase.air.doId2do.get(senderId)
        if not toon:
            self.sendInteractionDenied(senderId)
            return

        if not self.requestInteractingToon(senderId):
            self.sendInteractionDenied(senderId)
            return

        if not self.doActualHarvest(toon):
            self.sendInteractionDenied(senderId)
            return

        # tell the toon to display a movie
        self.setMovie(GardenGlobals.MOVIE_HARVEST, senderId)

    def doActualHarvest(self, toon):
        zoneId = self.zoneId
        estateOwnerDoId = simbase.air.estateMgr.zone2owner.get(zoneId)
        if not toon.doId == estateOwnerDoId:
            self.notify.warning("how did this happen, harvesting a tree you don't own")
            return False

        if not self.isFruiting() or self.isWilted():
            return False

        # add the fruit to the toon's inventory
        for i in range(self.maxFruit):
            toon.inventory.addItem(self.gagTrack, self.gagLevel)

        toon.d_setInventory(toon.inventory.makeNetString())

        growthLevel = self.growthThresholds[2] - 1
        self.b_setGrowthLevel(growthLevel)

        #log that they're harvesting gags
        self.air.writeServerEvent("garden_gag_harvest", toon.doId, '%d|%d|%d' % (self.doId,self.gagTrack, self.gagLevel))

        return True

    def hasGagBonus(self):
        """
        gag trees give a bonus when they are 1 day away from fruiting, are not wilted.
        The check that you have the necessary lower level gag trees is done elsewhere
        """
        retval = (self.growthLevel >= self.growthThresholds[2] -1) and not self.isWilted() and self.gagTrack != 9
        return retval
