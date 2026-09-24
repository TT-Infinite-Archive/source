import random
import sys
import uuid
from panda3d.core import Vec4
from toontown.hood import ZoneUtil
from toontown.toonbase import TTLocalizer
from toontown.toonbase.ToontownGlobals import BossbotHQ, BossbotLobby, CashbotHQ, CashbotLobby, DaisyGardens, \
    DonaldsDock, DonaldsDreamland, FunnyFarm, GolfZone, GoofySpeedway, LawbotHQ, LawbotLobby, MinniesMelodyland, \
    MyEstate, OutdoorZone, PartyHood, SellbotHQ, SellbotLobby, TheBrrrgh, ToontownCentral, Tutorial

MapHotkeyOn = 'alt'
MapHotkeyOff = 'alt-up'
MapHotkey = 'alt'
CogHQCameraFov = 60.0
BossBattleCameraFov = 72.0
MakeAToonCameraFov = 48.0
CogdoFov = 56.9
VPElevatorFov = 53.0
CFOElevatorFov = 43.0
CJElevatorFov = 47.0
CBElevatorFov = 42.0
CashbotHQCameraFar = 2000.0
CashbotHQCameraNear = 1.0
LawbotHQCameraFar = 3000.0
LawbotHQCameraNear = 1.0
BossbotHQCameraFar = 3000.0
BossbotHQCameraNear = 1.0
SpeedwayCameraFar = 8000.0
SpeedwayCameraNear = 1.0
DreamlandCameraNear = 1.0
DreamlandCameraFar = 2000.0
SellbotHQCameraNear = 1.0
SellbotHQCameraFar = 2000.0
ToonFont = None
BuildingNametagFont = None
MinnieFont = None
SuitFont = None
FontAwesome = None


def getMac():
    if sys.platform == 'android':
        if 'uuid' in settings and isinstance(settings['uuid'], int):
            uid = settings['uuid']
        else:
            uid = random.SystemRandom().getrandbits(50)
            settings['uuid'] = uid
    else:
        uid = uuid.getnode()

    return ':'.join(('%012X' % uid)[i:i+2] for i in range(0, 12, 2))


def getIp():
    import socket
    hostname = socket.gethostname()
    return socket.gethostbyname(hostname)


def getToonFont():
    global ToonFont
    if ToonFont == None:
        ToonFont = loader.loadFont(TTLocalizer.ToonFont, lineHeight=1.0)
    return ToonFont


def getBuildingNametagFont():
    global BuildingNametagFont
    if BuildingNametagFont == None:
        BuildingNametagFont = loader.loadFont(TTLocalizer.BuildingNametagFont)
    return BuildingNametagFont


def getMinnieFont():
    global MinnieFont
    if MinnieFont == None:
        MinnieFont = loader.loadFont(TTLocalizer.MinnieFont)
    return MinnieFont


def getSuitFont():
    global SuitFont
    if SuitFont == None:
        SuitFont = loader.loadFont(TTLocalizer.SuitFont, spaceAdvance=0.25, lineHeight=1.0)
    return SuitFont


def getFontAwesome():
    global FontAwesome
    if FontAwesome is None:
        FontAwesome = loader.loadFont(TTLocalizer.FontAwesome)
    return FontAwesome


EstateWakeWaterHeight = -.3
ZoneIdToWakeHeight = {
    ToontownCentral: -4.79,
    DonaldsDock: 1.669,
    TheBrrrgh: 0,
    MinniesMelodyland: -16,
    DaisyGardens: -1,
    DonaldsDreamland: -19,
    OutdoorZone: -0.5,
}


def getWakeInfo(hoodId=None, zoneId=None):
    wakeWaterHeight = 0
    showWake = 0
    try:
        if hoodId is None:
            hoodId = base.cr.playGame.getPlaceId()
        if zoneId is None:
            zoneId = base.cr.playGame.getPlace().getZoneId()
        canonicalZoneId = ZoneUtil.getCanonicalZoneId(zoneId)
        if canonicalZoneId in ZoneIdToWakeHeight:
            wakeWaterHeight = ZoneIdToWakeHeight[canonicalZoneId]
            showWake = 1
        elif hoodId == MyEstate:
            wakeWaterHeight = EstateWakeWaterHeight
            showWake = 1
        else:
            showWake = 0
            wakeWaterHeight = -9999
    except AttributeError:
        pass

    return (showWake, wakeWaterHeight)


safeZoneCountMap = {
    MyEstate: 8,
    Tutorial: 6,
    ToontownCentral: 6,
    DonaldsDock: 10,
    MinniesMelodyland: 5,
    GoofySpeedway: 500,
    TheBrrrgh: 8,
    DaisyGardens: 9,
    FunnyFarm: 500,
    DonaldsDreamland: 5,
    OutdoorZone: 500,
    GolfZone: 500,
    PartyHood: 500
}
townCountMap = {
    MyEstate: 8,
    Tutorial: 40,
    ToontownCentral: 37,
    DonaldsDock: 40,
    MinniesMelodyland: 40,
    GoofySpeedway: 40,
    TheBrrrgh: 40,
    DaisyGardens: 40,
    FunnyFarm: 40,
    DonaldsDreamland: 40,
    OutdoorZone: 40,
    PartyHood: 20
}
hoodCountMap = {
    MyEstate: 2,
    Tutorial: 2,
    ToontownCentral: 2,
    DonaldsDock: 2,
    MinniesMelodyland: 2,
    GoofySpeedway: 2,
    TheBrrrgh: 2,
    DaisyGardens: 2,
    FunnyFarm: 2,
    DonaldsDreamland: 2,
    OutdoorZone: 2,
    BossbotHQ: 2,
    SellbotHQ: 43,
    CashbotHQ: 2,
    LawbotHQ: 2,
    GolfZone: 2,
    PartyHood: 2
}
NoTeleportZones = (
    CashbotLobby,
    BossbotLobby,
    SellbotLobby,
    LawbotLobby
)
TrophyStarLevels = (
    10,
    20,
    30,
    50,
    75,
    100
)
TrophyStarColors = (
    Vec4(0.9, 0.6, 0.2, 1),
    Vec4(0.9, 0.6, 0.2, 1),
    Vec4(0.8, 0.8, 0.8, 1),
    Vec4(0.8, 0.8, 0.8, 1),
    Vec4(1, 1, 0, 1),
    Vec4(1, 1, 0, 1)
)
PieThrowArc = 0
PieThrowLinear = 1
PieCodeBossCog = 1
PieCodeNotBossCog = 2
PieCodeToon = 3
PieCodeBossInsides = 4
PieCodeDefensePan = 5
PieCodeProsecutionPan = 6
PieCodeLawyer = 7
PieCodeColors = {
    PieCodeBossCog: None,
    PieCodeNotBossCog: (0.8, 0.8, 0.8, 1),
    PieCodeToon: None
}
WakeRunDelta = 0.1
WakeWalkDelta = 0.2
LOW_POP = 100
MID_POP = 200
HIGH_POP = -1
ColorPlayer = (0.3,
 0.7,
 0.3,
 1)
ColorAvatar = (0.3,
 0.3,
 0.7,
 1)
ColorFreeChat = (0.3,
 0.3,
 0.8,
 1)
ColorSpeedChat = (0.2,
 0.6,
 0.4,
 1)
ColorNoChat = (0.8,
 0.5,
 0.1,
 1)
ColorGuildMember = (0.2, 0.6, 0.4, 0.5)
ColorGuildMemberOnline = (0.2, 0.6, 0.4, 1.0)
CalendarFilterShowAll = 0
CalendarFilterShowOnlyHolidays = 1
CalendarFilterShowOnlyParties = 2
DefaultWantNewsPageSetting = 0
NewsPageScaleAdjust = 0.85
CommonDisplayResolutions = {
    (4, 3): ((800, 600), (1024, 768), (1152, 864), (1280, 960), (1600, 1200),
             (1920, 1440)),
    (5, 4): ((1280, 1024),),
    (5, 3): ((1280, 768),),
    (8, 5): ((1280, 800), (1680, 1050), (1920, 1200)),
    (16, 9): ((1280, 720), (1360, 768), (1366, 768), (1600, 900), (1920, 1080),
              (2560, 1440), (3840, 2160)),
}
