from panda3d.core import Point3
from direct.directnotify import DirectNotifyGlobal
from . import HoodDataAI, ZoneUtil
from toontown.dna.DNAGroup import DNAGroup
from toontown.dna.DNAVisGroup import DNAVisGroup
from toontown.toonbase import ToontownGlobals
from toontown.racing.RaceGlobals import *
from toontown.safezone import DistributedGolfKartAI


class GZHoodDataAI(HoodDataAI.HoodDataAI):
    notify = DirectNotifyGlobal.directNotify.newCategory("GZHoodDataAI")

    def __init__(self, air, zoneId=None):
        hoodId = ToontownGlobals.GolfZone
        if zoneId == None:
            zoneId = hoodId
        HoodDataAI.HoodDataAI.__init__(self, air, zoneId, hoodId)

    def startup(self):
        HoodDataAI.HoodDataAI.startup(self)

        # create the golf karts from the dna
        self.createGolfKarts()

    def findAndCreateGolfKarts(self, dnaGroup, zoneId, area, overrideDNAZone=0, propType='golf_kart'):
        """Find and create golf karts from the given dna."""
        golfKarts = []
        golfKartGroups = []

        if isinstance(dnaGroup, DNAGroup) and propType in dnaGroup.getName():
            golfKartGroups.append(dnaGroup)
            if (propType == 'golf_kart'):
                nameInfo = dnaGroup.getName().split('_')
                golfCourse = int(nameInfo[2])

                pos = Point3(0, 0, 0)
                hpr = Point3(0, 0, 0)
                for i in range(dnaGroup.getNumChildren()):
                    childDnaGroup = dnaGroup.at(i)
                    # TODO - check if DNAProp instance
                    if 'starting_block' in childDnaGroup.getName():
                        pos = childDnaGroup.getPos()
                        hpr = childDnaGroup.getHpr()
                        break

                # lift the karts off the ground a bit so we can see their shadows in the tunnel
                pos += Point3(0, 0, 0.05)

                golfKart = DistributedGolfKartAI.DistributedGolfKartAI(self.air, golfCourse,
                                                                       pos[0], pos[1], pos[2],
                                                                       hpr[0], hpr[1], hpr[2])
            else:
                self.notify.warning('unhandled case')
            golfKart.generateWithRequired(zoneId)
            golfKarts.append(golfKart)
        else:
            if isinstance(dnaGroup, DNAVisGroup) and not overrideDNAZone:
                zoneId = ZoneUtil.getTrueZoneId(int(dnaGroup.getName().split(':')[0]), zoneId)

            for i in range(dnaGroup.getNumChildren()):
                childGolfKarts, childGolfKartGroups = self.findAndCreateGolfKarts(dnaGroup.at(i), zoneId, area,
                                                                                  overrideDNAZone, propType)
                golfKarts += childGolfKarts
                golfKartGroups += childGolfKartGroups
        return golfKarts, golfKartGroups

    def createGolfKarts(self):
        """Create the golf karts in this hood."""
        self.golfKarts = []
        self.golfKartGroups = []
        for zone in self.air.zoneTable[self.canonicalHoodId]:
            zoneId = ZoneUtil.getTrueZoneId(zone[0], self.zoneId)
            dnaData = self.air.dnaDataMap.get(zone[0], None)

            if isinstance(dnaData, DNAGroup):
                area = ZoneUtil.getCanonicalZoneId(zoneId)
                foundKarts, foundKartGroups = self.findAndCreateGolfKarts(dnaData, zoneId, area, overrideDNAZone=True)
                self.golfKarts += foundKarts
                self.golfKartGroups += foundKartGroups

        # Place each Golf Kart into the proper WaitEmpty State. Handle this
        # after each they have generated so that they are
        # placed in the proper active state.
        for golfKart in self.golfKarts:
            golfKart.start()
            self.addDistObj(golfKart)

