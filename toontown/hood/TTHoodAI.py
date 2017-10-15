from toontown.classicchars import DistributedMickeyAI
from toontown.hood import HoodAI
from toontown.safezone import DistributedTrolleyAI
from toontown.toon import NPCToons
from toontown.toonbase import TTLocalizer
from toontown.toonbase import ToontownGlobals, ServerSettingsGlobals
from toontown.safezone.DistributedJukeboxAI import DistributedJukeboxAI
from toontown.safezone import JukeboxGlobals


class TTHoodAI(HoodAI.HoodAI):
    def __init__(self, air):
        HoodAI.HoodAI.__init__(self, air,
                               ToontownGlobals.ToontownCentral,
                               ToontownGlobals.ToontownCentral)

        self.trolley = None
        self.classicChar = None
        self.butterflies = []
        self.jukebox = None

        self.startup()

    def startup(self):
        HoodAI.HoodAI.startup(self)

        if simbase.wantTTCJukebox:
            self.createJukeBox()
        if simbase.config.GetBool('want-minigames', True):
            self.createTrolley()
        if simbase.config.GetBool('want-classic-chars', True):
            if simbase.config.GetBool('want-mickey', True):
                self.createClassicChar()

        if simbase.wantYinYang or simbase.air.holidayManager.isHolidayRunning(ToontownGlobals.HALLOWEEN):
            NPCToons.createNPC(
                simbase.air, 2021,
                (ToontownGlobals.ToontownCentral, TTLocalizer.NPCToonNames[2021], ('css', 'ms', 'm', 'm', 26, 0, 26, 26, 0, 27, 0, 27, 0, 27), 'm', 1, NPCToons.NPC_YIN),
                ToontownGlobals.ToontownCentral, posIndex=0)

        if simbase.wantYinYang:
            NPCToons.createNPC(
                simbase.air, 2022,
                (ToontownGlobals.ToontownCentral, TTLocalizer.NPCToonNames[2022], ('bss', 'ms', 'm', 'm', 0, 0, 0, 0, 0, 31, 0, 31, 0, 31), 'm', 1, NPCToons.NPC_YANG),
                ToontownGlobals.ToontownCentral, posIndex=0)

    def createTrolley(self):
        self.trolley = DistributedTrolleyAI.DistributedTrolleyAI(self.air)
        self.trolley.generateWithRequired(self.zoneId)
        self.trolley.start()

    def createClassicChar(self):
        self.classicChar = DistributedMickeyAI.DistributedMickeyAI(self.air)
        self.classicChar.generateWithRequired(self.zoneId)
        self.classicChar.start()

    def createJukeBox(self):
        self.jukebox = DistributedJukeboxAI(self.air, 5)
        self.jukebox.setPosHpr(-105.604, 88.585, 0.525, 34, 0, 0)
        self.jukebox.generateWithRequired(self.zoneId)
