import random

from . import DistributedLawOfficeAI
from . import DistributedStageAI
from direct.directnotify import DirectNotifyGlobal
from direct.showbase import DirectObject
from toontown.toonbase import ToontownGlobals


StageId2Layouts = {
    ToontownGlobals.LawbotStageIntA: (0, 1, 2),
    ToontownGlobals.LawbotStageIntB: (3, 4, 5),
    ToontownGlobals.LawbotStageIntC: (6, 7, 8),
    ToontownGlobals.LawbotStageIntD: (9, 10, 11)
}


class LawOfficeManagerAI(DirectObject.DirectObject):
    notify = DirectNotifyGlobal.directNotify.newCategory('LawOfficeManagerAI')
    lawOfficeId = None

    def __init__(self, air):
        DirectObject.DirectObject.__init__(self)
        self.air = air

    def getDoId(self):
        return 0

    def createLawOffice(self, StageId, entranceId, players):
        floor = 0
        StageZone = self.air.allocateZone()
        layoutIndex = random.choice(StageId2Layouts[StageId])
        Stage = DistributedStageAI.DistributedStageAI(self.air, StageId, StageZone, floor, players, layoutIndex)
        Stage.generateWithRequired(StageZone)
        return StageZone
