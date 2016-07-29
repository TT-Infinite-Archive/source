from direct.distributed.DistributedObjectAI import DistributedObjectAI
from toontown.toon import ToonDNA
from toontown.toonbase.ToontownGlobals import HALLOWEEN


class DistributedBlackCatMgrAI(DistributedObjectAI):
    notify = directNotify.newCategory('DistributedBlackCatMgrAI')

    def requestBlackCatTransformation(self):
        avId = self.air.getAvatarIdFromSender()
        av = self.air.doId2do.get(avId)
        if not av:
            return

        if not simbase.air.wantHalloween and not simbase.air.holidayManager.isHolidayRunning(HALLOWEEN):
            return

        if av.dna.getAnimal() == 'cat':
            newDNA = ToonDNA.ToonDNA()
            newDNA.makeFromNetString(av.getDNAString())

            blackRgb = ToonDNA.allColorsList[0x1a]
            newDNA.colorDNA.headColor.resetRgb(*blackRgb)
            newDNA.colorDNA.armColor.resetRgb(*blackRgb)
            newDNA.colorDNA.legColor.resetRgb(*blackRgb)

            taskMgr.doMethodLater(1.0, lambda task: av.b_setDNAString(newDNA.makeNetString()), 'transform-%d' % avId)
            self.sendUpdate('doBlackCatTransformation', [avId])
