import random

from toontown.coghq import DistributedCountryClubAI
from direct.directnotify import DirectNotifyGlobal
from direct.showbase import DirectObject
from toontown.toonbase import ToontownGlobals


CountryClubId2Layouts = {
    ToontownGlobals.BossbotCountryClubIntA: (0, 1, 2),
    ToontownGlobals.BossbotCountryClubIntB: (3, 4, 5),
    ToontownGlobals.BossbotCountryClubIntC: (6, 7, 8)
}


class CountryClubManagerAI(DirectObject.DirectObject):
    notify = directNotify.newCategory('CountryClubManagerAI')

    countryClubId = None

    def __init__(self, air):
        DirectObject.DirectObject.__init__(self)
        self.air = air

    def getDoId(self):
        return 0

    def createCountryClub(self, countryClubId, players):
        floor = 0
        countryClubZone = self.air.allocateZone()
        layoutIndex = random.choice(CountryClubId2Layouts[countryClubId])
        countryClub = DistributedCountryClubAI.DistributedCountryClubAI(self.air, countryClubId, countryClubZone, floor, players, layoutIndex)
        countryClub.generateWithRequired(countryClubZone)
        return countryClubZone
