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

    def exit(self):
        Playground.Playground.exit(self)

    dnaStorage = DNAStorage()
