from panda3d.core import ConfigVariableBool, Point3
from direct.directnotify import DirectNotifyGlobal
from . import HoodDataAI, ZoneUtil
from toontown.dna.DNAGroup import DNAGroup
from toontown.dna.DNAVisGroup import DNAVisGroup
from toontown.toonbase import ToontownGlobals
from toontown.racing.RaceGlobals import *
from toontown.safezone import DistributedPicnicBasketAI
from toontown.classicchars import DistributedChipAI
from toontown.classicchars import DistributedDaleAI
from toontown.distributed import DistributedTimerAI

from toontown.safezone import DistributedPicnicTableAI
#from toontown.safezone import DistributedChineseCheckersAI
#from toontown.safezone import DistributedCheckersAI

if (__debug__):
    import pdb


class OZHoodDataAI(HoodDataAI.HoodDataAI):
    notify = DirectNotifyGlobal.directNotify.newCategory("OZHoodDataAI")

    def __init__(self, air, zoneId=None):
        hoodId = ToontownGlobals.OutdoorZone
        if zoneId == None:
            zoneId = hoodId
        HoodDataAI.HoodDataAI.__init__(self, air, zoneId, hoodId)

    def startup(self):
        HoodDataAI.HoodDataAI.startup(self)

        chip = DistributedChipAI.DistributedChipAI(self.air)
        chip.generateWithRequired(self.zoneId)
        chip.start()
        self.addDistObj(chip)

        dale = DistributedDaleAI.DistributedDaleAI(self.air, chip.doId)
        dale.generateWithRequired(self.zoneId)
        dale.start()
        self.addDistObj(dale)
        chip.setDaleId(dale.doId)

        self.timer = DistributedTimerAI.DistributedTimerAI(self.air)
        self.timer.generateWithRequired(self.zoneId)

        # create the picnic tables from the dna
        self.createPicnicTables()
        # Code Copy Paste, create game tables from dna

        if ConfigVariableBool('want-game-tables', False).getValue():
            self.createGameTables()

    # more hacks!
    # self.board = DChineseCheckersAI.DChineseCheckersAI(self.air, 'board',65,130,.2,0,0,0)
    # self.addDistObj(self.board)

    # self.newTable = DistributedPicnicTableAI.DistributedPicnicTableAI(self.air, 6000, 'table', 50, 130, .4, 0,0,0)
    # self.addDistObj(self.newTable)

    # self.checkerboard = DistributedCheckersAI.DistributedCheckersAI(self.air, self.newTable.doId, 'chinese', self.newTable.getX(),self.newTable.getY(), self.newTable.getZ(), 0,0,0)
    # self.addDistObj(self.newTable)

    # create a temporary golf kart
    # golfKart = DistributedGolfKartAI.DistributedGolfKartAI(self.air)
    # golfKart.generateWithRequired(self.zoneId)
    # golfKart.start()
    # self.addDistObj(golfKart)
    # self.golfKart = golfKart

    def cleanup(self):
        self.timer.delete()
        # put away those billboards

    def findAndCreateGameTables(self, dnaGroup, zoneId, area, overrideDNAZone=0, propType='game_table'):
        """Find and create golf karts from the given dna."""
        picnicTables = []
        picnicTableGroups = []

        # pdb.set_trace()

        if isinstance(dnaGroup, DNAGroup) and propType in dnaGroup.getName():

            if (type == 'game_table'):
                nameInfo = dnaGroup.getName().split('_')

                pos = Point3(0, 0, 0)
                hpr = Point3(0, 0, 0)
                for i in range(dnaGroup.getNumChildren()):
                    childDnaGroup = dnaGroup.at(i)
                    # TODO - check if DNAProp instance
                    if 'game_table' in childDnaGroup.getName():
                        pos = childDnaGroup.getPos()
                        hpr = childDnaGroup.getHpr()
                        break

                picnicTable = DistributedPicnicTableAI.DistributedPicnicTableAI(self.air, zoneId, nameInfo[2],
                                                                                pos[0], pos[1], pos[2],
                                                                                hpr[0], hpr[1], hpr[2])
                # checkerboard = DistributedChineseCheckersAI.DistributedChineseCheckersAI(self.air, picnicTable.doId,  'chinese', picnicTable.getX(), picnicTable.getY(), picnicTable.getZ(), hpr[0],hpr[1],hpr[2])

                # picnicTable.generateWithRequired(zoneId)
                picnicTables.append(picnicTable)
                # self.chineseCheckers.append(checkerboard)
        else:
            if (isinstance(dnaGroup, DNAVisGroup) and not overrideDNAZone):
                zoneId = ZoneUtil.getTrueZoneId(int(dnaGroup.getName().split(':')[0]), zoneId)

            for i in range(dnaGroup.getNumChildren()):
                childPicnicTables = self.findAndCreateGameTables(dnaGroup.at(i), zoneId, area, overrideDNAZone, propType)
                picnicTables += childPicnicTables
        return picnicTables

    def findAndCreatePicnicTables(self, dnaGroup, zoneId, area, overrideDNAZone=0, propType='picnic_table'):
        """Find and create golf karts from the given dna."""
        picnicTables = []
        picnicTableGroups = []

        # pdb.set_trace()
        # self.notify.debug('dnaGroup=%s' % (dnaGroup.getName()))
        # bool1 = ((isinstance(dnaGroup, DNAGroup)))
        # findresult = ((isinstance(dnaGroup, DNAGroup)))
        # import pdb; pdb.set_trace()

        if isinstance(dnaGroup, DNAGroup) and propType in dnaGroup.getName():

            if (propType == 'picnic_table'):
                nameInfo = dnaGroup.getName().split('_')

                pos = Point3(0, 0, 0)
                hpr = Point3(0, 0, 0)
                for i in range(dnaGroup.getNumChildren()):
                    childDnaGroup = dnaGroup.at(i)
                    # TODO - check if DNAProp instance
                    if 'picnic_table' in childDnaGroup.getName():
                        pos = childDnaGroup.getPos()
                        hpr = childDnaGroup.getHpr()
                        break

                picnicTable = DistributedPicnicBasketAI.DistributedPicnicBasketAI(self.air, nameInfo[2],
                                                                                  pos[0], pos[1], pos[2],
                                                                                  hpr[0], hpr[1], hpr[2])
                # checkerboard = DistributedChineseCheckersAI.DistributedChineseCheckersAI(self.air, picnicTable.doId, 'chinese', picnicTable.getX(), picnicTable.getY(), picnicTable.getZ(), 0,0,0)

                picnicTable.generateWithRequired(zoneId)

                picnicTables.append(picnicTable)
                # self.chineseCheckers.append(checkerboarD)
        else:
            if (isinstance(dnaGroup, DNAVisGroup) and not overrideDNAZone):
                zoneId = ZoneUtil.getTrueZoneId(int(dnaGroup.getName().split(':')[0]), zoneId)

            for i in range(dnaGroup.getNumChildren()):
                childPicnicTables = self.findAndCreatePicnicTables(dnaGroup.at(i), zoneId, area, overrideDNAZone, propType)
                picnicTables += childPicnicTables
        return picnicTables

    def createGameTables(self):
        """Create the golf karts in this hood."""

        # pdb.set_trace()

        self.gameTables = []
        # self.chineseCheckers = []
        for zone in self.air.zoneTable[self.canonicalHoodId]:
            zoneId = ZoneUtil.getTrueZoneId(zone[0], self.zoneId)
            dnaData = self.air.dnaDataMap.get(zone[0], None)

            if dnaData:
                area = ZoneUtil.getCanonicalZoneId(zoneId)
                foundTables = self.findAndCreateGameTables(dnaData, zoneId, area, overrideDNAZone=True)
                self.gameTables += foundTables

        # Place each Golf Kart into the proper WaitEmpty State. Handle this
        # after each they have generated so that they are
        # placed in the proper active state.
        for picnicTable in self.gameTables:
            # picnicTable.start() USELESS FSM Function for other picnic table
            self.addDistObj(picnicTable)
        # for chineseCheckers in self.chineseCheckers:
        # self.addDistObj( chineseCheckers )

    def createPicnicTables(self):
        """Create the golf karts in this hood."""

        # pdb.set_trace()

        self.picnicTables = []
        for zone in self.air.zoneTable[self.canonicalHoodId]:
            zoneId = ZoneUtil.getTrueZoneId(zone[0], self.zoneId)
            dnaData = self.air.dnaDataMap.get(zone[0], None)

            if dnaData:
                area = ZoneUtil.getCanonicalZoneId(zoneId)
                foundTables = self.findAndCreatePicnicTables(dnaData, zoneId, area, overrideDNAZone=True)
                self.picnicTables += foundTables

        # Place each Golf Kart into the proper WaitEmpty State. Handle this
        # after each they have generated so that they are
        # placed in the proper active state.
        # print "PICNIC TABLES" ,self.picnicTables
        for picnicTable in self.picnicTables:
            picnicTable.start()
            self.addDistObj(picnicTable)
