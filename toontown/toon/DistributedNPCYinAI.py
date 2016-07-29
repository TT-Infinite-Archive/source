from DistributedNPCToonBaseAI import *
from toontown.toon import ToonDNA


class DistributedNPCYinAI(DistributedNPCToonBaseAI):
    def requestTransformation(self):
        avId = self.air.getAvatarIdFromSender()
        av = self.air.doId2do.get(avId)
        if av is None:
            return

        if not hasattr(av, 'dna'):
            return

        if av.dna.getAnimal() == 'cat':
            newDNA = ToonDNA.ToonDNA()
            newDNA.makeFromNetString(av.getDNAString())

            blackRgb = ToonDNA.allColorsList[0x1a]
            newDNA.colorDNA.headColor.resetRgb(*blackRgb)
            newDNA.colorDNA.armColor.resetRgb(*blackRgb)
            newDNA.colorDNA.legColor.resetRgb(*blackRgb)

            taskMgr.doMethodLater(1.0, lambda task: av.b_setDNAString(newDNA.makeNetString()), 'transform-%d' % avId)
            self.sendUpdate('doTransformation', [avId])
