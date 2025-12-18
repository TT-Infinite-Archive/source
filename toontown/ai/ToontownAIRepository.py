from panda3d.core import ConfigVariableBool, MultiplexStream, Notify, StreamWriter, UniqueIdAllocator
from direct.distributed.PyDatagram import *

from otp.ai.AIZoneData import AIZoneDataStore
from otp.ai.MagicWordManagerAI import MagicWordManagerAI
from otp.ai.TimeManagerAI import TimeManagerAI
from otp.ai import BanManagerAI
from otp.distributed.OtpDoGlobals import *
from otp.friends.FriendManagerAI import FriendManagerAI
from otp.ai.CrashLogManagerAI import CrashLogManagerAI
from toontown.ai import CogPageManagerAI
from toontown.ai import CogSuitManagerAI
from toontown.ai import PromotionManagerAI
from toontown.ai.AchievementsManagerAI import AchievementsManagerAI
from toontown.ai.FishManagerAI import FishManagerAI
from toontown.ai.HolidayManagerAI import HolidayManagerAI
from toontown.ai.NewsManagerAI import NewsManagerAI
from toontown.ai.QuestManagerAI import QuestManagerAI
from toontown.ai import BankManagerAI
from toontown.battle.BehaviorManagerAI import BehaviorManagerAI
from toontown.building.DistributedTrophyMgrAI import DistributedTrophyMgrAI
from toontown.catalog.CatalogManagerAI import CatalogManagerAI
from toontown.catalog.PopularItemManagerAI import PopularItemManagerAI
from toontown.coderedemption.TTCodeRedemptionMgrAI import TTCodeRedemptionMgrAI
from toontown.coghq import CountryClubManagerAI
from toontown.coghq import FactoryManagerAI
from toontown.coghq import LawOfficeManagerAI
from toontown.coghq import MintManagerAI
from toontown.collectibles.StatManagerAI import StatManagerAI
from toontown.collectibles.CollectibleInventoryManagerAI import CollectibleInventoryManagerAI
from toontown.distributed.ToontownDistrictAI import ToontownDistrictAI
from toontown.distributed.ToontownDistrictStatsAI import ToontownDistrictStatsAI
from toontown.distributed.ToontownInternalRepository import ToontownInternalRepository
from toontown.dna.DNAParser import loadDNAFileAI
from toontown.estate.EstateManagerAI import EstateManagerAI
from toontown.hood import BRHoodAI
from toontown.hood import BossbotHQAI
from toontown.hood import CashbotHQAI
from toontown.hood import DDHoodAI
from toontown.hood import DGHoodAI
from toontown.hood import DLHoodAI
from toontown.hood import GSHoodAI
from toontown.hood import GZHoodAI
from toontown.hood import LawbotHQAI
from toontown.hood import MMHoodAI
from toontown.hood import OZHoodAI
from toontown.hood import SellbotHQAI
from toontown.hood import TTHoodAI
from toontown.hood import ZoneUtil
from toontown.quest.Quests import assertAllQuestsValid
from toontown.pets.PetManagerAI import PetManagerAI
from toontown.safezone.SafeZoneManagerAI import SafeZoneManagerAI
from toontown.suit.SuitInvasionManagerAI import SuitInvasionManagerAI
from toontown.toon import NPCToons
from toontown.toonbase import ToontownGlobals, ServerSettingsGlobals
from toontown.tutorial.TutorialManagerAI import TutorialManagerAI
from toontown.uberdog.DistributedPartyManagerAI import DistributedPartyManagerAI
from toontown.parties.ToontownTimeManager import ToontownTimeManager
from toontown.distributed.ShardTimeManagerAI import ShardTimeManagerAI
import threading

if ConfigVariableBool('want-leak-graph-ai', False).getValue():
    from toontown.debug.LeakGraph import LeakGraph


class ToontownAIRepository(ToontownInternalRepository):
    def __init__(self, baseChannel, stateServerChannel, districtName):
        ToontownInternalRepository.__init__(
            self, baseChannel, stateServerChannel, dcSuffix='AI')

        self.districtName = districtName

        self.notify.setInfo(True)  # Our AI repository should always log info.
        self.hoods = []
        self.cogHeadquarters = []
        self.dnaStoreMap = {}
        self.dnaDataMap = {}
        self.suitPlanners = {}
        self.buildingManagers = {}
        self.disconnectedToons = {}
        self.factoryMgr = None
        self.mintMgr = None
        self.lawOfficeMgr = None
        self.countryClubMgr = None

        self.zoneAllocator = UniqueIdAllocator(
            ToontownGlobals.DynamicZonesBegin,
            ToontownGlobals.DynamicZonesEnd
        )
        self.zoneDataStore = AIZoneDataStore()

        self.wantFishing = ConfigVariableBool('want-fishing', True).getValue()
        self.wantHousing = ConfigVariableBool('want-housing', True).getValue()
        self.wantPets = ConfigVariableBool('want-pets', True).getValue()
        self.wantParties = ConfigVariableBool('want-parties', True).getValue()
        self.wantCogbuildings = ConfigVariableBool('want-cogbuildings', True).getValue()
        self.wantCogdominiums = ConfigVariableBool('want-cogdominiums', True).getValue()
        self.wantEmblems = ConfigVariableBool('want-emblems', False).getValue()
        self.wantAchievements = ConfigVariableBool('want-achievements', True).getValue()
        self.wantCodeRedemption = ConfigVariableBool('want-code-redemption', True).getValue()
        self.wantGroupTracker = ConfigVariableBool('want-grouptracker', True).getValue()
        self.wantGuilds = ConfigVariableBool('want-guilds', True).getValue()
        self.wantGuildQuests = ConfigVariableBool('want-guild-quests', True).getValue()
        self.wantToonStats = ConfigVariableBool('want-toon-stats', True).getValue()
        self.wantCollectibles = ConfigVariableBool('want-collectibles', True).getValue()
        self.wantFreeGuilds = ConfigVariableBool('want-free-guilds', False).getValue()
        self.doLiveUpdates = ConfigVariableBool('want-live-updates', False).getValue()
        self.wantTrackClsends = ConfigVariableBool('want-track-clsends', False).getValue()
        self.wantHalloween = ConfigVariableBool('want-halloween', False).getValue()
        self.wantChristmas = ConfigVariableBool('want-christmas', False).getValue()
        self.wantFireworks = ConfigVariableBool('want-fireworks', False).getValue()
        self.leakGraph = None
        self.cogSuitMessageSent = False
        self.wantCheats = serverSettings[ServerSettingsGlobals.WantCheats]

        # Logging
        from direct.directnotify import Notifier
        self.nout = MultiplexStream()
        Notify.ptr().setOstreamPtr(self.nout, 0)
        Notifier.Notifier.streamWriter = StreamWriter(self.nout, False)
        self.nout.addStandardOutput()

    def createManagers(self):
        self.timeManager = TimeManagerAI(self)
        self.timeManager.generateWithRequired(2)
        self.magicWordManager = MagicWordManagerAI(self)
        self.magicWordManager.generateWithRequired(2)
        self.zoneManager = self.generateGlobalObject(OTP_DO_ID_ZONE_MANAGER, 'ZoneManager')
        self.crashLogManager = CrashLogManagerAI(self)
        self.newsManager = NewsManagerAI(self)
        self.newsManager.generateWithRequired(2)
        self.holidayManager = HolidayManagerAI(self)
        self.safeZoneManager = SafeZoneManagerAI(self)
        self.safeZoneManager.generateWithRequired(2)
        self.tutorialManager = TutorialManagerAI(self)
        self.tutorialManager.generateWithRequired(2)
        self.friendManager = FriendManagerAI(self)
        self.friendManager.generateWithRequired(2)
        self.questManager = QuestManagerAI(self)
        self.banManager = BanManagerAI.BanManagerAI(self)
        self.banManager.generateWithRequired(2)
        self.achievementsManager = AchievementsManagerAI(self)
        self.suitInvasionManager = SuitInvasionManagerAI(self)
        self.trophyMgr = DistributedTrophyMgrAI(self)
        self.trophyMgr.generateWithRequired(2)
        self.cogSuitMgr = CogSuitManagerAI.CogSuitManagerAI(self)
        self.promotionMgr = PromotionManagerAI.PromotionManagerAI(self)
        self.cogPageManager = CogPageManagerAI.CogPageManagerAI()
        self.bankManager = BankManagerAI.BankManagerAI(self)
        self.behaviorManager = BehaviorManagerAI(self)
        if self.wantToonStats:
            self.statManager = StatManagerAI(self)
        if self.wantCollectibles:
            self.ciManager = CollectibleInventoryManagerAI(self)
        if self.wantGuilds:
            self.guildManager = self.generateGlobalObject(
                OTP_DO_ID_GUILDS_MANAGER, 'GuildManager')
        if self.wantCodeRedemption:
            self.codeRedemptionMgr = TTCodeRedemptionMgrAI(self)
            self.codeRedemptionMgr.generateWithRequired(2)
        if self.wantFishing:
            self.fishManager = FishManagerAI(self)
        if self.wantHousing:
            self.estateManager = EstateManagerAI(self)
            self.estateManager.generateWithRequired(2)
            self.catalogManager = CatalogManagerAI(self)
            self.catalogManager.generateWithRequired(2)
            self.popularItemManager = PopularItemManagerAI(self)
            self.deliveryManager = self.generateGlobalObject(
                OTP_DO_ID_TOONTOWN_DELIVERY_MANAGER,
                'DistributedDeliveryManager')
        if self.wantPets:
            self.petMgr = PetManagerAI(self)
        if self.wantParties:
            self.partyManager = DistributedPartyManagerAI(self)
            self.partyManager.generateWithRequired(2)
            self.globalPartyMgr = self.generateGlobalObject(
                OTP_DO_ID_GLOBAL_PARTY_MANAGER, 'GlobalPartyManager')
        if self.wantGroupTracker:
            self.globalGroupTracker = self.generateGlobalObject(
                OTP_DO_ID_GLOBAL_GROUP_TRACKER, 'GlobalGroupTracker')
        self.chatAgent = self.generateGlobalObject(OTP_DO_ID_CHAT_MANAGER,
                                                   'ChatAgent')
        self.holidayManager = HolidayManagerAI(self)

        self.megaInvasionManager = simbase.air.generateGlobalObject(
            OTP_DO_ID_MEGA_INVASION_MANAGER, 'MegaInvasionManager')

    def createSafeZones(self):
        NPCToons.generateZone2NpcDict()
        if serverSettings[ServerSettingsGlobals.EnabledZones]["ToontownCentral"]:
            self.hoods.append(TTHoodAI.TTHoodAI(self))
        if serverSettings[ServerSettingsGlobals.EnabledZones]["TheHarbor"]:
            self.hoods.append(DDHoodAI.DDHoodAI(self))
        if serverSettings[ServerSettingsGlobals.EnabledZones]["DaisyGardens"]:
            self.hoods.append(DGHoodAI.DGHoodAI(self))

        while self.readerPollOnce():
            pass

        if ConfigVariableBool('want-minnies-melodyland', True).getValue():
            self.hoods.append(MMHoodAI.MMHoodAI(self))
        if ConfigVariableBool('want-the-burrrgh', True).getValue():
            self.hoods.append(BRHoodAI.BRHoodAI(self))
        if ConfigVariableBool('want-donalds-dreamland', True).getValue():
            self.hoods.append(DLHoodAI.DLHoodAI(self))

        while self.readerPollOnce():
            pass

        if ConfigVariableBool('want-goofy-speedway', True).getValue():
            self.hoods.append(GSHoodAI.GSHoodAI(self))
        if ConfigVariableBool('want-outdoor-zone', True).getValue():
            self.hoods.append(OZHoodAI.OZHoodAI(self))
        if ConfigVariableBool('want-golf-zone', True).getValue():
            self.hoods.append(GZHoodAI.GZHoodAI(self))

        while self.readerPollOnce():
            pass

    def createCogHeadquarters(self):
        NPCToons.generateZone2NpcDict()
        if ConfigVariableBool('want-sellbot-headquarters', True).getValue():
            self.factoryMgr = FactoryManagerAI.FactoryManagerAI(self)
            self.cogHeadquarters.append(SellbotHQAI.SellbotHQAI(self))
        if ConfigVariableBool('want-cashbot-headquarters', True).getValue():
            self.mintMgr = MintManagerAI.MintManagerAI(self)
            self.cogHeadquarters.append(CashbotHQAI.CashbotHQAI(self))
        if ConfigVariableBool('want-lawbot-headquarters', True).getValue():
            self.lawOfficeMgr = LawOfficeManagerAI.LawOfficeManagerAI(self)
            self.cogHeadquarters.append(LawbotHQAI.LawbotHQAI(self))
        if ConfigVariableBool('want-bossbot-headquarters', True).getValue():
            self.countryClubMgr = CountryClubManagerAI.CountryClubManagerAI(
                self)
            self.cogHeadquarters.append(BossbotHQAI.BossbotHQAI(self))

    def handleConnected(self):
        ToontownInternalRepository.handleConnected(self)
        self.registerForChannel(MESSENGER_CHANNEL_AI)

        if ConfigVariableBool('want-threaded-ai-start', False).getValue():
            threading.Thread(target=self.startDistrict).start()
        else:
            self.startDistrict()

    def startDistrict(self):
        self.districtId = self.allocateChannel()
        self.notify.info(f'Creating ToontownDistrictAI({self.districtId})...')
        self.distributedDistrict = ToontownDistrictAI(self)
        self.distributedDistrict.setName(self.districtName)
        self.distributedDistrict.generateWithRequiredAndId(
            self.districtId, self.getGameDoId(), 2)
        self.notify.info(f'Claiming ownership of channel ID: {self.districtId}...')
        self.claimOwnership(self.districtId)

        self.districtStats = ToontownDistrictStatsAI(self)
        self.districtStats.settoontownDistrictId(self.districtId)
        self.districtStats.generateWithRequiredAndId(
            self.allocateChannel(), self.getGameDoId(), 3)
        self.notify.info(f'Created ToontownDistrictStats({self.districtStats.doId})')

        self.toontownTimeManager = ToontownTimeManager()
        self.shardTimeManager = ShardTimeManagerAI(self)
        self.shardTimeManager.setTimeZone(self.districtStats.timeZone)
        self.notify.info('Created ShardTimeManagerAI [%s]' %
                         self.shardTimeManager.formatTimeZone(
                             self.districtStats.timeZone))

        if ConfigVariableBool('want-quest-verification', False).getValue():
            self.notify.info('Verifying Quests...')
            assertAllQuestsValid()

        self.notify.info('Creating managers...')
        self.createManagers()
        if ConfigVariableBool('want-safe-zones', True).getValue():
            self.notify.info('Creating safe zones...')
            self.createSafeZones()

        if self.wantPets:
            self.notify.info('Generating Pet seeds...')
            self.petMgr.generateSeeds()

        if ConfigVariableBool('want-cog-headquarters', True).getValue():
            self.notify.info('Creating Cog headquarters...')
            self.createCogHeadquarters()

        self.notify.info('Starting Holiday Manager...')
        self.holidayManager.start()

        self.notify.info('Making district available...')
        self.distributedDistrict.b_setAvailable(1)
        self.notify.info('Done.')

        if ConfigVariableBool('want-leak-graph-ai', False).getValue():
            self.leakGraph = LeakGraph(f'tti-ai-process-{self.ourChannel}')
            self.leakGraph.start()

    def claimOwnership(self, channelId):
        datagram = PyDatagram()
        datagram.addServerHeader(
            channelId, self.ourChannel, STATESERVER_OBJECT_SET_AI)
        datagram.addChannel(self.ourChannel)
        self.send(datagram)

    def lookupDNAFileName(self, zoneId: int) -> str:
        zoneId = ZoneUtil.getCanonicalZoneId(zoneId)
        hoodId = ZoneUtil.getCanonicalHoodId(zoneId)
        hood = ToontownGlobals.dnaMap[hoodId]
        if hoodId == zoneId:
            zoneId = 'sz'
            phaseNum = ToontownGlobals.phaseMap[hoodId]
        else:
            phaseNum = ToontownGlobals.streetPhaseMap[hoodId]
        return f'phase_{phaseNum}/dna/{hood}_{zoneId}.pdna'

    def loadDNAFileAI(self, dnastore, filename):
        return loadDNAFileAI(dnastore, filename)

    def incrementPopulation(self):
        self.districtStats.b_setAvatarCount(
            self.districtStats.getAvatarCount() + 1)

    def decrementPopulation(self):
        self.districtStats.b_setAvatarCount(
            self.districtStats.getAvatarCount() - 1)

    def allocateZone(self):
        return self.zoneAllocator.allocate()

    def deallocateZone(self, zone):
        self.zoneAllocator.free(zone)

    def getZoneDataStore(self):
        return self.zoneDataStore

    def getTrackClsends(self):
        return self.wantTrackClsends

    def getAvatarExitEvent(self, avId: int) -> str:
        return f'distObjDelete-{avId}'

    def trueUniqueName(self, name):
        return self.uniqueName(name)

    def setAvatarDisconnectReason(self, avId, reason):
        self.disconnectedToons[avId] = reason

    def getAvatarDisconnectReason(self, avId):
        if int(avId) in self.disconnectedToons:
            reason = self.disconnectedToons[int(avId)]
            return reason
