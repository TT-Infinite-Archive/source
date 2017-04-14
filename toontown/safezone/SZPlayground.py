from toontown.safezone import Playground
from toontown.hood import ZoneUtil
from toontown.dna.DNAStorage import DNAStorage
from toontown.dna import DNAParser

class SZPlayground(Playground.Playground):
    def enter(self, requestStatus):
        Playground.Playground.enter(self, requestStatus)

        dnaStorage = DNAStorage()
        dnaFileName = ZoneUtil.genDNAFileName(19000)  # self.zoneId)

        if not dnaFileName.endswith('19001.pdna'):
            DNAParser.loadDNAFileAI(dnaStorage, dnaFileName)

            zoneVisDict = {}
            for i in xrange(dnaStorage.getNumDNAVisGroupsAI()):
                groupFullName = dnaStorage.getDNAVisGroupName(i)
                visGroup = dnaStorage.getDNAVisGroupAI(i)
                visZoneId = int(base.cr.hoodMgr.extractGroupName(groupFullName))
                visZoneId = ZoneUtil.getTrueZoneId(visZoneId, self.zoneId)
                visibles = []
                for i in xrange(visGroup.getNumVisibles()):
                    visibles.append(int(visGroup.visibles[i]))
                visibles.append(ZoneUtil.getBranchZone(visZoneId))
                zoneVisDict[visZoneId] = visibles

            dnaStorage.cleanup()
            base.cr.sendSetZoneMsg(self.zoneId, zoneVisDict.values()[0])

            self.loadDestroyedBuildings()

    def loadDestroyedBuildings(self):
        self.toonHall = loader.loadModel('phase_4/models/corpstrike/destroyed_toonhall')
        self.toonHall.reparentTo(render)
        self.toonHall.setPos(116.66, 24.29, 4)
        self.toonHall.setHpr(-90, 0, 0)

        self.bank = loader.loadModel('phase_4/models/corpstrike/destroyed_bank')
        self.bank.reparentTo(render)
        self.bank.setPos(57.1796, 38.6656, 0.3)

        self.library = loader.loadModel('phase_4/models/corpstrike/destroyed_library')
        self.library.reparentTo(render)
        self.library.setPos(91.4475, -44.9255, 4)
        self.library.setHpr(180, 0, 0)

    def unloadDestroyedBuildings(self):
        self.toonHall.removeNode()
        del self.toonHall

        self.bank.removeNode()
        del self.bank

        self.library.removeNode()
        del self.library

    def exit(self):
        Playground.Playground.exit(self)
        self.unloadDestroyedBuildings()

    dnaStorage = DNAStorage()
