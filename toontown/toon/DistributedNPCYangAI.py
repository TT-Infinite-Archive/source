from DistributedNPCToonBaseAI import *
from toontown.toon import ToonDNA


class DistributedNPCYangAI(DistributedNPCToonBaseAI):
    def requestTransformation(self):
        avId = self.air.getAvatarIdFromSender()
        av = self.air.doId2do.get(avId)
        if av is None:
            return
        if not hasattr(av, 'dna'):
            return
        if av.dna.getAnimal() == 'bear':
            newDNA = ToonDNA.ToonDNA()
            newDNA.makeFromNetString(av.getDNAString())

            whiteRgb = ToonDNA.allColorsList[0x00]
            newDNA.colorDNA.headColor.resetRgb(*whiteRgb)
            newDNA.colorDNA.armColor.resetRgb(*whiteRgb)
            newDNA.colorDNA.legColor.resetRgb(*whiteRgb)

            taskMgr.doMethodLater(1.0, lambda task: av.b_setDNAString(newDNA.makeNetString()), 'transform-%d' % avId)
            self.sendUpdate('doTransformation', [avId])
