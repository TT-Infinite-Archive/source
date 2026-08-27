from panda3d.core import ConfigVariableBool, ConfigVariableString, MultiplexStream, Notify, StreamWriter, UniqueIdAllocator
from direct.distributed.PyDatagram import *

from otp.ai.AIZoneData import AIZoneDataStore
from otp.ai.MagicWordGlobal import spellbook
from otp.ai.MagicWordManagerAI import MagicWordManagerAI
from otp.ai.TimeManagerAI import TimeManagerAI
from otp.ai import BanManagerAI
from otp.distributed.OtpDoGlobals import *
from otp.friends.FriendManagerAI import FriendManagerAI
from otp.ai.CrashLogManagerAI import CrashLogManagerAI
from toontown.ai.ToontownAIMsgTypes import CONTROL_ADD_POST_REMOVE, CONTROL_MESSAGE, PARTY_MANAGER_UD_TO_ALL_AI
from toontown.ai.AchievementsManagerAI import AchievementsManagerAI
from toontown.fishing.FishManagerAI import FishManagerAI
from toontown.ai.HolidayManagerAI import HolidayManagerAI
from toontown.ai.NewsManagerAI import NewsManagerAI
from toontown.quest.QuestManagerAI import QuestManagerAI
from toontown.ai import BankManagerAI
from toontown.battle.BehaviorManagerAI import BehaviorManagerAI
from toontown.building.DistributedTrophyMgrAI import DistributedTrophyMgrAI
from toontown.catalog.CatalogManagerAI import CatalogManagerAI
from toontown.catalog.PopularItemManagerAI import PopularItemManagerAI
from toontown.coderedemption.TTCodeRedemptionMgrAI import TTCodeRedemptionMgrAI
from toontown.coghq import CogSuitManagerAI
from toontown.shtiker import CogPageManagerAI
from toontown.coghq import CountryClubManagerAI
from toontown.coghq import FactoryManagerAI
from toontown.coghq import LawOfficeManagerAI
from toontown.coghq import MintManagerAI
from toontown.coghq import PromotionManagerAI
from toontown.collectibles.StatManagerAI import StatManagerAI
from toontown.collectibles.CollectibleInventoryManagerAI import CollectibleInventoryManagerAI
from toontown.distributed.ToontownDistrictAI import ToontownDistrictAI
from toontown.distributed.ToontownDistrictStatsAI import ToontownDistrictStatsAI
from toontown.distributed.ToontownInternalRepository import ToontownInternalRepository
from toontown.dna.DNAParser import loadDNAFile, loadDNAFileAI, DNAStorage, DNAGroup, DNAVisGroup
from toontown.dna.DNAProp import DNAProp
from toontown.estate.EstateManagerAI import EstateManagerAI
from toontown.estate.DistributedBankMgrAI import DistributedBankMgrAI
from toontown.fishing import DistributedFishingPondAI
from toontown.safezone import DistributedFishingSpotAI
from toontown.hood import BRHoodDataAI
from toontown.hood import BossbotHQDataAI
from toontown.hood import CashbotHQDataAI
from toontown.hood import DDHoodDataAI
from toontown.hood import DGHoodDataAI
from toontown.hood import DLHoodDataAI
from toontown.hood import GSHoodDataAI
from toontown.hood import GZHoodDataAI
from toontown.hood import LawbotHQDataAI
from toontown.hood import MMHoodDataAI
from toontown.hood import OZHoodDataAI
from toontown.hood import CSHoodDataAI
from toontown.hood import TTHoodDataAI
from toontown.hood import ZoneUtil

from toontown.quest.Quests import assertAllQuestsValid
from toontown.pets.PetManagerAI import PetManagerAI

from toontown.racing.RaceManagerAI import RaceManagerAI
from toontown.racing.DistributedLeaderBoardAI import DistributedLeaderBoardAI
from toontown.racing.DistributedRacePadAI import DistributedRacePadAI
from toontown.racing.DistributedViewPadAI import DistributedViewPadAI
from toontown.racing.DistributedStartingBlockAI import DistributedStartingBlockAI
from toontown.racing.DistributedStartingBlockAI import DistributedViewingBlockAI

from toontown.safezone.SafeZoneManagerAI import SafeZoneManagerAI
from toontown.suit.SuitInvasionManagerAI import SuitInvasionManagerAI
from toontown.toon import NPCToons
from toontown.toonbase import ToontownGlobals, ServerSettingsGlobals
from toontown.tutorial.TutorialManagerAI import TutorialManagerAI
from toontown.server import Readiness
from toontown.web.GatewaySocket import openSocket
from toontown.web.ShardStatusReporter import ShardStatusReporter
from toontown.uberdog.DistributedPartyManagerAI import DistributedPartyManagerAI
from toontown.safezone import DistributedPartyGateAI
from toontown.parties.ToontownTimeManager import ToontownTimeManager
from toontown.distributed.ShardTimeManagerAI import ShardTimeManagerAI
import threading

if ConfigVariableBool('want-leak-graph-ai', False).getValue():
    from toontown.debug.LeakGraph import LeakGraph


class ToontownAIRepository(ToontownInternalRepository):
    # The zone table determines which dnaStores are created and
    # whether bulding manager or suit planner ai objects are created.
    # The elements consist of:
    # (int the_zone_ID, bool create_building_manager, bool create_suit_planner)
    zoneTable = {
        ToontownGlobals.ToontownCentral: ([ToontownGlobals.ToontownCentral, 1, 0],
                          [ToontownGlobals.ToontownCentral + 100, 1, 1],
                          [ToontownGlobals.ToontownCentral + 200, 1, 1],
                          [ToontownGlobals.ToontownCentral + 300, 1, 1],
                          ),

        ToontownGlobals.DonaldsDock: ([ToontownGlobals.DonaldsDock, 1, 0],
                      [ToontownGlobals.DonaldsDock + 100, 1, 1],
                      [ToontownGlobals.DonaldsDock + 200, 1, 1],
                      [ToontownGlobals.DonaldsDock + 300, 1, 1],
                      ),

        ToontownGlobals.MinniesMelodyland: ([ToontownGlobals.MinniesMelodyland, 1, 0],
                            [ToontownGlobals.MinniesMelodyland + 100, 1, 1],
                            [ToontownGlobals.MinniesMelodyland + 200, 1, 1],
                            [ToontownGlobals.MinniesMelodyland + 300, 1, 1],
                            ),

        ToontownGlobals.TheBrrrgh: ([ToontownGlobals.TheBrrrgh, 1, 0],
                    [ToontownGlobals.TheBrrrgh + 100, 1, 1],
                    [ToontownGlobals.TheBrrrgh + 200, 1, 1],
                    [ToontownGlobals.TheBrrrgh + 300, 1, 1],
                    ),

        ToontownGlobals.DonaldsDreamland: ([ToontownGlobals.DonaldsDreamland, 1, 0],
                           [ToontownGlobals.DonaldsDreamland + 100, 1, 1],
                           [ToontownGlobals.DonaldsDreamland + 200, 1, 1],
                           ),

        ToontownGlobals.DaisyGardens: ([ToontownGlobals.DaisyGardens, 1, 0],
                       [ToontownGlobals.DaisyGardens + 100, 1, 1],
                       [ToontownGlobals.DaisyGardens + 200, 1, 1],
                       [ToontownGlobals.DaisyGardens + 300, 1, 1],
                       ),

        ToontownGlobals.GoofySpeedway: ([ToontownGlobals.GoofySpeedway, 1, 0],
                       ),

        ToontownGlobals.OutdoorZone: ([ToontownGlobals.OutdoorZone, 0, 0],
                       ),

        ToontownGlobals.SellbotHQ: ([ToontownGlobals.SellbotHQ, 0, 1],
                    [ToontownGlobals.SellbotHQ + 200, 0, 1],
                    ),

        ToontownGlobals.CashbotHQ: ([ToontownGlobals.CashbotHQ, 0, 1],
                    ),

        ToontownGlobals.LawbotHQ: ([ToontownGlobals.LawbotHQ, 0, 1],
                    ),

        ToontownGlobals.GolfZone: ([ToontownGlobals.GolfZone, 0, 0],
                   ),

        ToontownGlobals.BossbotHQ: ([ToontownGlobals.BossbotHQ, 0, 0],
                       ),

        }


    def __init__(self, baseChannel, stateServerChannel, districtName, gateway=None):
        ToontownInternalRepository.__init__(
            self, baseChannel, stateServerChannel, dcSuffix='AI')

        self.districtName = districtName

        # The district's own line to the website, and the commands it is
        # currently answering. Both stay None/empty if the gateway is off.
        self.gateway = gateway
        self.gatewayReporter = None
        self.gatewayCommands = set()

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
        self.lawMgr = None
        self.countryClubMgr = None

        self.zoneAllocator = UniqueIdAllocator(
            ToontownGlobals.DynamicZonesBegin,
            ToontownGlobals.DynamicZonesEnd
        )
        self.zoneDataStore = AIZoneDataStore()

        self.wantFishing = ConfigVariableBool('want-fishing', True).getValue()
        self.wantBingo = ConfigVariableBool('want-bingo', True).getValue()
        self.wantRacing = ConfigVariableBool('want-racing', True).getValue()
        self.wantHousing = ConfigVariableBool('want-housing', True).getValue()
        self.wantPets = ConfigVariableBool('want-pets', True).getValue()
        self.wantParties = ConfigVariableBool('want-parties', True).getValue()
        self.wantCogbuildings = ConfigVariableBool('want-cogbuildings', True).getValue()
        self.wantCogdominiums = ConfigVariableBool('want-cogdominiums', True).getValue()
        self.wantEmblems = ConfigVariableBool('want-emblems', False).getValue()
        self.wantAchievements = ConfigVariableBool('want-achievements', True).getValue()
        self.wantCodeRedemption = ConfigVariableBool('want-code-redemption', True).getValue()
        self.wantGroupTracker = ConfigVariableBool('want-grouptracker', False).getValue()
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
        self.wantCheats = ConfigVariableBool(
            'want-cheats', serverSettings[ServerSettingsGlobals.WantCheats]).getValue()

        if ConfigVariableBool('magic-word-live-access', False).getValue():
            spellbook.useLiveAccess()
            self.notify.info('Magic words re-gated to live access levels.')

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
        #self.zoneManager = self.generateGlobalObject(OTP_DO_ID_ZONE_MANAGER, 'ZoneManager')
        self.crashLogManager = CrashLogManagerAI(self)
        self.newsManager = NewsManagerAI(self)
        self.newsManager.generateWithRequired(2)
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
        self.cogPageManager = CogPageManagerAI.CogPageManagerAI(self)
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
        self.bingoMgr = None
        if self.wantPets:
            self.petMgr = PetManagerAI(self)
        if self.wantHousing:
            self.estateMgr = EstateManagerAI(self)
            self.estateMgr.generateWithRequired(2)
            if self.wantPets:
                self.petMgr.listenEvents()
            self.bankMgr = DistributedBankMgrAI(self)
            self.bankMgr.generateWithRequired(2)
            self.catalogManager = CatalogManagerAI(self)
            self.catalogManager.generateWithRequired(2)
            self.popularItemManager = PopularItemManagerAI(self)
            self.deliveryManager = self.generateGlobalObject(
                OTP_DO_ID_TOONTOWN_DELIVERY_MANAGER,
                'DistributedDeliveryManager')
        if self.wantRacing:
            self.raceMgr = RaceManagerAI(self)
        if self.wantParties:
            self.partyManager = DistributedPartyManagerAI(self)
            self.partyManager.generateWithRequired(2)
        if self.wantGroupTracker:
            self.globalGroupTracker = self.generateGlobalObject(
                OTP_DO_ID_GLOBAL_GROUP_TRACKER, 'GlobalGroupTracker')
        self.chatAgent = self.generateGlobalObject(OTP_DO_ID_CHAT_MANAGER,
                                                   'ChatAgent')

    def createSafeZones(self):
        NPCToons.generateZone2NpcDict()
        if serverSettings[ServerSettingsGlobals.EnabledZones]["ToontownCentral"]:
            self.startupHood(TTHoodDataAI.TTHoodDataAI(self))
        if serverSettings[ServerSettingsGlobals.EnabledZones]["TheHarbor"]:
            self.startupHood(DDHoodDataAI.DDHoodDataAI(self))
        if serverSettings[ServerSettingsGlobals.EnabledZones]["DaisyGardens"]:
            self.startupHood(DGHoodDataAI.DGHoodDataAI(self))

        while self.readerPollOnce():
            pass

        if ConfigVariableBool('want-minnies-melodyland', True).getValue():
            self.startupHood(MMHoodDataAI.MMHoodDataAI(self))
        if ConfigVariableBool('want-the-burrrgh', True).getValue():
            self.startupHood(BRHoodDataAI.BRHoodDataAI(self))
        if ConfigVariableBool('want-donalds-dreamland', True).getValue():
            self.startupHood(DLHoodDataAI.DLHoodDataAI(self))

        while self.readerPollOnce():
            pass

        if ConfigVariableBool('want-goofy-speedway', True).getValue():
            self.startupHood(GSHoodDataAI.GSHoodDataAI(self))
        if ConfigVariableBool('want-outdoor-zone', True).getValue():
            self.startupHood(OZHoodDataAI.OZHoodDataAI(self))
        if ConfigVariableBool('want-golf-zone', True).getValue():
            self.startupHood(GZHoodDataAI.GZHoodDataAI(self))

        while self.readerPollOnce():
            pass

    def createCogHeadquarters(self):
        NPCToons.generateZone2NpcDict()
        if ConfigVariableBool('want-sellbot-headquarters', True).getValue():
            self.factoryMgr = FactoryManagerAI.FactoryManagerAI(self)
            self.startupCogHQ(CSHoodDataAI.CSHoodDataAI(self))
        if ConfigVariableBool('want-cashbot-headquarters', True).getValue():
            self.mintMgr = MintManagerAI.MintManagerAI(self)
            self.startupCogHQ(CashbotHQDataAI.CashbotHQDataAI(self))
        if ConfigVariableBool('want-lawbot-headquarters', True).getValue():
            self.lawMgr = LawOfficeManagerAI.LawOfficeManagerAI(self)
            self.startupCogHQ(LawbotHQDataAI.LawbotHQDataAI(self))
        if ConfigVariableBool('want-bossbot-headquarters', True).getValue():
            self.countryClubMgr = CountryClubManagerAI.CountryClubManagerAI(self)
            self.startupCogHQ(BossbotHQDataAI.BossbotHQDataAI(self))

    def handleConnected(self):
        ToontownInternalRepository.handleConnected(self)
        self.registerForChannel(MESSENGER_CHANNEL_AI)

        self.startGateway()

        if ConfigVariableBool('want-threaded-ai-start', False).getValue():
            threading.Thread(target=self.startDistrict).start()
        else:
            self.startDistrict()

    def startGateway(self):
        """
        Takes over this district's socket to the website.
        """
        if self.gateway is None:
            self.gateway = openSocket()

        if self.gateway is None:
            return

        self.gateway.onCommand = self.handleGatewayCommand
        self.gateway.onReady = self.handleGatewayReady

        self.gatewayReporter = ShardStatusReporter(self, self.gateway)

    def handleGatewayReady(self, message):
        if self.gatewayReporter:
            self.gatewayReporter.flush()

    def handleGatewayCommand(self, message):
        """
        Runs a command the website sent straight to this district.
        """
        commandId = message.get('id')
        op = message.get('op')
        commandArgs = message.get('args') or {}

        if op == 'startInvasion':
            self.gatewayCommands.add(commandId)
            messenger.send('startInvasion', [
                commandId, self.ourChannel,
                commandArgs.get('cogType'), commandArgs.get('numCogs'),
                commandArgs.get('skeleton'), commandArgs.get('duration')])
        elif op == 'stopInvasion':
            self.gatewayCommands.add(commandId)
            messenger.send('stopInvasion', [commandId, self.ourChannel])
        else:
            self.notify.warning('Ignoring an unknown gateway op: %s' % op)
            self.gateway.sendResult(
                commandId, False, {'error': 'Unknown op: %s' % op})

    def sendNetEvent(self, message, sentArgs=[]):
        """
        Passes the event through the gateway if applicable.
        """
        if message == 'shardStatus' and self.gatewayReporter:
            self.gatewayReporter.update(sentArgs[1])

        elif message.startswith('invasionResponse-') and self.gateway:
            commandId = message[len('invasionResponse-'):]
            if commandId in self.gatewayCommands:
                self.gatewayCommands.discard(commandId)
                ok, error = sentArgs
                self.gateway.sendResult(
                    commandId, ok, {'error': error} if error else None)

        ToontownInternalRepository.sendNetEvent(self, message, sentArgs)

    def startDistrict(self):
        self.loadDNA()

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



        if ConfigVariableBool('want-ddsm', True).getValue():
            self.dataStoreManager = self.generateGlobalObject(
                OTP_DO_ID_TOONTOWN_TEMP_STORE_MANAGER,
                "DistributedDataStoreManager")

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

        if ConfigVariableBool('want-cog-headquarters', True).getValue():
            self.notify.info('Creating Cog headquarters...')
            self.createCogHeadquarters()

        self.notify.info('Starting Holiday Manager...')
        # The Holiday Manager should be instantiated after the each
        # of the hoods and estateMgrAI are generated because Bingo Night
        # needs to reference the HoodDataAI and EstateMgrAI for pond
        # information
        self.holidayManager = HolidayManagerAI(self)

        self.notify.info('Making district available...')
        self.distributedDistrict.b_setAvailable(1)
        self.notify.info('Done.')
        Readiness.markReady()

        if ConfigVariableBool('want-leak-graph-ai', False).getValue():
            self.leakGraph = LeakGraph(f'tti-ai-process-{self.ourChannel}')
            self.leakGraph.start()

    def claimOwnership(self, channelId):
        datagram = PyDatagram()
        datagram.addServerHeader(
            channelId, self.ourChannel, STATESERVER_OBJECT_SET_AI)
        datagram.addChannel(self.ourChannel)
        self.send(datagram)

    def addPostSocketClose(self, theMessage):
        # Time to send a register for channel message to the msgDirector
        datagram = PyDatagram()    
        datagram.addInt8(1)
        datagram.addChannel(CONTROL_MESSAGE)
        datagram.addUint16(CONTROL_ADD_POST_REMOVE)

        datagram.addBlob(theMessage.getMessage())
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

    def loadDNAFile(self, dnastore, filename):
        return loadDNAFile(dnastore, filename)

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

    def getEstate(self, avId, accId, zoneId, callback):
        self.notify.debug(f'getEstate avId={avId}, accId={accId}, zoneId={zoneId}, callback={callback}')
        estateId = 0
        estateVal = {} # {estateFieldName: packedValues}
        avIds = []

        avatars = {} # {avId: {fieldName: [fieldValue]}}

        def __handleGetEstate(dclass, fields):
            if dclass != self.dclassesByName['DistributedEstateAI']:
                self.notify.warning(
                    f'Account {accId} has non-estate dclass {dclass}!'
                )
                return

            nonlocal estateVal
            # Convert Astron response to OTP
            estateVal = self.packDclassValueDict(dclass, fields)

            # Now to do the houses:
            self.getHouses(avId, accId, zoneId, estateId, estateVal, avIds, avatars, callback)

        def __gotAllAvatars():
            self.notify.debug(f'__gotAllAvatars: {estateId, avIds, len(avatars)}')

            if estateId:
                self.dbInterface.queryObject(self.dbId, estateId, __handleGetEstate)
            else:
                def __handleEstateCreated(newEstateId):
                    nonlocal estateId
                    estateId = newEstateId
                    # Update Account object with the new estate id
                    self.dbInterface.updateObject(self.dbId, accId, self.dclassesByName['AccountAI'],
                                                          {'ESTATE_ID': estateId})

                    self.dbInterface.queryObject(self.dbId, estateId, __handleGetEstate)

                self.dbInterface.createObject(self.dbId, self.dclassesByName['DistributedEstateAI'], {},
                                                  __handleEstateCreated)


        def __handleGetAvatar(dclass, fields, index):
            if dclass != self.dclassesByName['DistributedToonAI']:
                self.notify.warning(
                    f'Account {accId} has avatar {avIds[index]} with non-Toon dclass {dclass}!')
                return


            fields['avId'] = avIds[index]
            avatars[index] = fields
            if len(avatars) == 6:
                __gotAllAvatars()

        def __handleGetAccount(dclass, fields):
            if dclass != self.dclassesByName['AccountAI']:
                self.notify.warning(f'Account {accId} has non-account dclass {dclass}!')
                return

            nonlocal estateId, avIds, avatars
            estateId = fields.get('ESTATE_ID', 0)
            avIds = fields.get('ACCOUNT_AV_SET', [0] * 6)
            # Sanitize the avIds list in case its too long/short
            avIds = avIds[:6]
            avIds += [0] * (6 - len(avIds))
            for index, avId in enumerate(avIds):
                if avId == 0:
                    avatars[index] = None
                    continue

                # Get the avatar object for each avId.
                self.dbInterface.queryObject(self.dbId, avId,
                                             lambda dclass, fields, idx=index: __handleGetAvatar(dclass, fields, idx))

        # Get the account object.
        self.dbInterface.queryObject(self.dbId, accId, __handleGetAccount)

    def getHouses(self, avId, accId, zoneId, estateId, estateVal, avIds, avatars, callback):
        '''
        Continuation of getEstate
        '''
        self.notify.debug(f'getHouses avId={avId}, accId={accId}, zoneId={zoneId}, estateId={estateId}, avIds={avIds}, callback={callback}')

        # numHouses = 0
        houseIds = [0] * len(avIds)
        houseVal = [None] * len(avIds) # [packedHouseValues]

        def __gotAllHouses():
            # Get pet ids
            petIds = [0] * len(avIds)
            for index in avatars:
                if avatars[index] != None:
                    petId = avatars[index].get('setPetId', [0])[0]
                    if petId != 0:
                        petIds[index] = petId

            # Get Gardens started.
            gardensStarted = [False] * len(avIds)
            for index in avatars:
                if avatars[index] != None:
                    gardenStarted = avatars[index].get('setGardenStarted', [0])[0]
                    if gardenStarted:
                        gardensStarted[index] = True

            self.notify.debug(f'__gotAllHouses {estateId, estateVal, len(houseIds), houseIds, houseVal, petIds, gardensStarted, estateVal}')

            # That's a lot of work, time to finally call our callback.  Whew!
            callback(estateId, estateVal, len(houseIds), houseIds, houseVal,
                     petIds, gardensStarted, estateVal)

        def __handleGetHouse(dclass, fields, index):
            nonlocal houseVal
            if dclass != self.dclassesByName['DistributedHouseAI']:
                self.notify.warning(f'Avatar {avIds[index]} has non-house object {houseId} with dclass {dclass}!')
                return

            # Set the most important fields here.
            fields['setAvatarId'] = [avIds[index]]
            fields['setName'] = avatars[index]['setName']

            # Convert Astron response to OTP
            houseVal[index] = self.packDclassValueDict(dclass, fields)

            if None not in houseVal:
                __gotAllHouses()

        def __handleHouseCreated(houseId, index):
            nonlocal houseIds, houseVal

            houseIds[index] = houseId
            av = self.doId2do.get(avIds[index])
            if av:
                # Update house id
                av.b_setHouseId(houseId)
            else:
                self.dbInterface.updateObject(self.dbId, avIds[index],
                                                      self.dclassesByName['DistributedToonAI'],
                                                      {'setHouseId': [houseId]})

            __handleGetHouse(self.dclassesByName['DistributedHouseAI'], {}, index)


        for index in avatars:
            if avatars[index] == None:
                # No avatar, no house. Allocate an ID in it's place
                # (it'll be generated into an empty house)
                houseId = self.allocateChannel()
                houseIds[index] = houseId
                houseVal[index] = {}
                if None not in houseVal:
                    __gotAllHouses()
                    return
                else:
                    continue
            houseId = avatars[index].get('setHouseId', [0])[0]
            if houseId == 0:
                # No house
                self.dbInterface.createObject(self.dbId, self.dclassesByName['DistributedHouseAI'],
                                              {},
                                              lambda houseId, idx=index: __handleHouseCreated(houseId, idx))
            else:
                houseIds[index] = houseId
                self.dbInterface.queryObject(self.dbId, houseId,
                                             lambda dclass, fields, idx=index: __handleGetHouse(dclass, fields, idx))

    def handleAvCatch(self, avId, zoneId, catch):
        """
        avId - ID of avatar to update
        zoneId - zoneId of the pond the catch was made in.
                This is used by the BingoManagerAI to
                determine which PBMgrAI needs to update
                the catch.
        catch - a fish tuple of (genus, species)
        returns: None

        This method instructs the BingoManagerAI to
        tell the appropriate PBMgrAI to update the
        catch of an avatar at the particular pond. This
        method is called in the FishManagerAI's
        RecordCatch method.
        """
        # Guard for publish
        if simbase.wantBingo:
            if self.bingoMgr:
                self.bingoMgr.setAvCatchForPondMgr(avId, zoneId, catch)

    def loadDNA(self):
        """
        Return a dictionary of zoneId to DNAStorage objects
        """
        self.dnaStoreMap = {}
        self.dnaDataMap = {}
        for zones in list(self.zoneTable.values()):
            for zone in zones:
                zoneId = zone[0]
                if zoneId == ToontownGlobals.BossbotHQ:
                    continue
                dnaStore = DNAStorage()
                dnaFileName = self.lookupDNAFileName(zoneId)
                dnaData = self.loadDNAFileAI(dnaStore, dnaFileName)
                self.dnaStoreMap[zoneId] = dnaStore
                self.dnaDataMap[zoneId] = dnaData


    def startupHood(self, hood):
        hood.startup()
        self.hoods.append(hood)

    def startupCogHQ(self, cogHQ):
        cogHQ.startup()
        self.cogHeadquarters.append(cogHQ)

    def findPartyHats(self, dnaGroup, zoneId, overrideDNAZone = 0):
        """
        Recursively scans the given DNA tree for party hats.  These
        are defined as all the groups whose code includes the string
        "party_gate".  For each such group, creates a
        DistributedPartyGateAI.  Returns the list of distributed
        objects.
        """
        partyHats = []

        if ((isinstance(dnaGroup, DNAGroup)) and
            # If it is a DNAGroup, and the name has party_gate, count it
            (dnaGroup.getName().find('party_gate') >= 0)):
            # Here's a party hat!
            ph = DistributedPartyGateAI.DistributedPartyGateAI(self)
            ph.generateWithRequired(zoneId)
            partyHats.append(ph)
        else:
            # Now look in the children
            # Party hats cannot have other party hats in them,
            # so do not search the one we just found:
            # If we come across a visgroup, note the zoneId and then recurse
            if (isinstance(dnaGroup, DNAVisGroup) and not overrideDNAZone):
                # Make sure we get the real zone id, in case we are in welcome valley
                zoneId = ZoneUtil.getTrueZoneId(
                        int(dnaGroup.getName().split(':')[0]), zoneId)
            for i in range(dnaGroup.getNumChildren()):
                childPartyHats = self.findPartyHats(dnaGroup.at(i), zoneId, overrideDNAZone)
                partyHats += childPartyHats

        return partyHats

    def findFishingPonds(self, dnaGroup, zoneId, area, overrideDNAZone = 0):
        """
        Recursively scans the given DNA tree for fishing ponds.  These
        are defined as all the groups whose code includes the string
        "fishing_pond".  For each such group, creates a
        DistributedFishingPondAI.  Returns the list of distributed
        objects and a list of the DNAGroups so we can search them for
        spots and targets.
        """
        fishingPonds = []
        fishingPondGroups = []

        if ((isinstance(dnaGroup, DNAGroup)) and
            # If it is a DNAGroup, and the name starts with fishing_pond, count it
            (dnaGroup.getName().find('fishing_pond') >= 0)):
            # Here's a fishing pond!
            fishingPondGroups.append(dnaGroup)
            fp = DistributedFishingPondAI.DistributedFishingPondAI(self, area)
            fp.generateWithRequired(zoneId)
            fishingPonds.append(fp)
        else:
            # Now look in the children
            # Fishing ponds cannot have other ponds in them,
            # so do not search the one we just found:
            # If we come across a visgroup, note the zoneId and then recurse
            if (isinstance(dnaGroup, DNAVisGroup) and not overrideDNAZone):
                # Make sure we get the real zone id, in case we are in welcome valley
                zoneId = ZoneUtil.getTrueZoneId(
                        int(dnaGroup.getName().split(':')[0]), zoneId)
            for i in range(dnaGroup.getNumChildren()):
                childFishingPonds, childFishingPondGroups = self.findFishingPonds(
                        dnaGroup.at(i), zoneId, area, overrideDNAZone)
                fishingPonds += childFishingPonds
                fishingPondGroups += childFishingPondGroups
        return fishingPonds, fishingPondGroups


    def findFishingSpots(self, dnaPondGroup, distPond):
        """
        Scans the given DNAGroup pond for fishing spots.  These
        are defined as all the props whose code includes the string
        "fishing_spot".  Fishing spots should be the only thing under a pond
        node. For each such prop, creates a DistributedFishingSpotAI.
        Returns the list of distributed objects created.
        """
        fishingSpots = []
        # Search the children of the pond
        for i in range(dnaPondGroup.getNumChildren()):
            dnaGroup = dnaPondGroup.at(i)
            if ((isinstance(dnaGroup, DNAProp)) and
                (dnaGroup.getCode().find('fishing_spot') >= 0)):
                # Here's a fishing spot!
                pos = dnaGroup.getPos()
                hpr = dnaGroup.getHpr()
                fs = DistributedFishingSpotAI.DistributedFishingSpotAI(
                     self, distPond, pos[0], pos[1], pos[2], hpr[0], hpr[1], hpr[2])
                fs.generateWithRequired(distPond.zoneId)
                fishingSpots.append(fs)
            else:
                self.notify.debug("Found dnaGroup that is not a fishing_spot under a pond group")
        return fishingSpots

    def findRacingPads(self, dnaGroup, zoneId, area, overrideDNAZone = 0, propType = 'racing_pad'):
        racingPads = []
        racingPadGroups = []
        if isinstance(dnaGroup, DNAGroup) and propType in dnaGroup.getName():
            racingPadGroups.append(dnaGroup)
            if (propType == 'racing_pad'):
                nameInfo = dnaGroup.getName().split('_')
                #pdb.set_trace()
                #print "Name Info: ", nameInfo
                #print "Race Info: ", raceInfo
                racingPad = DistributedRacePadAI(self, area, nameInfo[3], int(nameInfo[2]))
            else:
                racingPad = DistributedViewPadAI(self, area)
            racingPad.generateWithRequired(zoneId)
            racingPads.append(racingPad)
        else:
            if (isinstance(dnaGroup, DNAVisGroup) and not overrideDNAZone):
                zoneId = ZoneUtil.getTrueZoneId(int(dnaGroup.getName().split(':')[0]), zoneId)
            for i in range(dnaGroup.getNumChildren()):
                childRacingPads, childRacingPadGroups = self.findRacingPads(dnaGroup.at(i), zoneId, area, overrideDNAZone, propType)
                racingPads += childRacingPads
                racingPadGroups += childRacingPadGroups
        return racingPads, racingPadGroups

    def findStartingBlocks(self, dnaRacingPadGroup, distRacePad):
        """
        Comment goes here...
        """
        startingBlocks = []
        # Search the children of the racing pad
        for i in range(dnaRacingPadGroup.getNumChildren()):
            dnaGroup = dnaRacingPadGroup.at(i)

            # TODO - check if DNAProp instance
            if 'starting_block' in dnaGroup.getName():
                padLocation = dnaGroup.getName().split('_')[2]
                pos = dnaGroup.getPos()
                hpr = dnaGroup.getHpr()

                if (isinstance(distRacePad, DistributedRacePadAI)):
                    sb = DistributedStartingBlockAI(self, distRacePad, pos[0], pos[1], pos[2], hpr[0], hpr[1], hpr[2], int(padLocation))
                else:
                    sb = DistributedViewingBlockAI(self, distRacePad, pos[0], pos[1], pos[2], hpr[0], hpr[1], hpr[2], int(padLocation))
                sb.generateWithRequired(distRacePad.zoneId)
                startingBlocks.append(sb)
            else:
                self.notify.debug("Found dnaGroup that is not a starting_block under a race pad group")
        return startingBlocks

    def findLeaderBoards(self, dnaPool, zoneID):
        '''
        Find and return leader boards
        '''
        leaderBoards = []
        if 'leaderBoard' in dnaPool.getName():
            #found a leader board
            pos = dnaPool.getPos()
            hpr = dnaPool.getHpr()

            lb = DistributedLeaderBoardAI(self, dnaPool.getName(), zoneID, [], pos, hpr)
            lb.generateWithRequired(zoneID)
            leaderBoards.append(lb)
        else:
            for i in range(dnaPool.getNumChildren()):
                result = self.findLeaderBoards(dnaPool.at(i), zoneID)
                if result:
                    leaderBoards += result

        return leaderBoards

    def handleDatagram(self, di):
        msgType = self.getMsgType()
        # Handle Toontown specific message types
        # before calling the base class
        if msgType == PARTY_MANAGER_UD_TO_ALL_AI:
            self.__handlePartyManagerUdToAllAi(di)
        else:
            ToontownInternalRepository.handleDatagram(self, di)

    def __handlePartyManagerUdToAllAi(self, di):
        """
        Send all msgs of this type to the party manager on our District.
        """
        do = self.partyManager
        if do:
            globalId = di.getUint32()
            if globalId != OTP_DO_ID_TOONTOWN_PARTY_MANAGER:
                self.notify.error(f'__handlePartyManagerUdToAllAi(): globalId={globalId}, not equal to {OTP_DO_ID_TOONTOWN_PARTY_MANAGER}')
            # Let the dclass finish the job
            do.dclass.receiveUpdate(do, di)
