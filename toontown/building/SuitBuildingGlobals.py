from ElevatorConstants import *
from toontown.toonbase import ToontownGlobals


SuitBuildingInfo = (
 ((1, 1),  # Amount of Floors
  (1, 3),  # Suit Levels
  (4, 4),  # Boss Suit Levels
  (13, 17),  # Suit Level Pool(All cog levels on floor must add up to be between this)
  (1,)),  # Suit Level Pool Multipliers(Multiplies the Suit Level Pool, Each Value is a different floor) Index 0
 ((1, 2),
  (2, 4),
  (4, 6),
  (13, 17),
  (1, 1.2)),  # Index 1
 ((1, 3),
  (3, 5),
  (6, 6),
  (13, 17),
  (1, 1.3, 1.6)),  # 2
 ((2, 3),
  (4, 6),
  (6, 8),
  (13, 17),
  (1, 1.4, 1.8)),  # 3
 ((2, 4),
  (5, 7),
  (7, 8),
  (13, 17),
  (1, 1.6, 1.8, 2)),  # 4
 ((3, 4),
  (6, 8),
  (8, 9),
  (15, 18),
  (1, 1.6, 2, 2.4)),  # 5
 ((3, 5),
  (7, 9),
  (8, 10),
  (20, 23),
  (1, 1.6, 1.8, 2.2, 2.1)),  # 6
 ((4, 5),
  (7, 10),
  (11, 11),
  (23, 26),
  (1.5, 1.0, 2.4, 3, 2.0)),  # 7
 ((5, 5),
  (7, 11),
  (12, 12),
  (25, 32),
  (2.2, 1.8, 2.6, 2.0, 2.3)),  # 8
 ((1, 5),
  (1, 12),
  (12, 12),
  (20, 32),
  (1.6, 1.0, 2.6, 1.0, 2.3)),  # 9
 ((1, 5),
  (1, 12),
  (12, 12),
  (20, 35),
  (1.0, 1.4, 2.0, 1.8, 2.3)),  # 10
 ((1, 1),
  (1, 12),
  (12, 12),
  (50, 50),
  (1, 1, 1, 1, 1)),  # 11 CFO Cogs
 ((1, 1),
  (8, 12),
  (12, 12),
  (75, 75),
  (1, 1, 1, 1, 1)),  # 12 CFO Skelecogs
 ((1, 1),
  (8, 12),
  (12, 12),
  (275, 275),
  (1, 1, 1, 1, 1)),  # 13 CJ
 ((1, 1),
  (9, 12),
  (12, 12),
  (206, 206),
  (1, 1, 1, 1, 1),
  (1,)),  # 14 CEO
 ((1, 1),
  (1, 5),
  (5, 5),
  (33, 33),
  (1, 1, 1, 1, 1)),  # 15
 ((1, 1),
  (4, 5),
  (5, 5),
  (50, 50),
  (1, 1, 1, 1, 1)),  # 16
 ((1, 1),
  (11, 12),
  (12, 12),
  (206, 206),
  (1, 1, 1, 1, 1),
  (1,)),  # 17
 ((1, 1),
  (2, 9),
  (10, 10),
  (50, 50),
  (1, 1, 1, 1, 1)),  # 18(VP Revised Battle 1, Difficulty 1)
 ((1, 1),
  (4, 10),
  (11, 11),
  (75, 75),
  (1, 1, 1, 1, 1)),  # 19(VP Revised Battle 1, Difficulty 2)
 ((1, 1),
  (6, 11),
  (12, 12),
  (100, 100),
  (1, 1, 1, 1, 1)),  # 20(VP Revised Battle 1, Difficulty 3)
 ((1, 1),
  (6, 9),
  (10, 10),
  (75, 75),
  (1, 1, 1, 1, 1)),  # 21(VP Revised Battle 2, Difficulty 1)
 ((1, 1),
  (7, 10),
  (11, 11),
  (100, 100),
  (1, 1, 1, 1, 1)),  # 22(VP Revised Battle 2, Difficulty 2)
 ((1, 1),
  (8, 11),
  (12, 12),
  (125, 125),
  (1, 1, 1, 1, 1)),  # 23(VP Revised Battle 2, Difficulty 3)
 ((1, 1),
  (4, 10),
  (11, 11),
  (60, 60),
  (1, 1, 1, 1, 1)),  # 24(CFO Revised Battle 1, Difficulty 1)
 ((1, 1),
  (5, 11),
  (12, 12),
  (80, 80),
  (1, 1, 1, 1, 1)),  # 25(CFO Revised Battle 1, Difficulty 2)
 ((1, 1),
  (6, 12),
  (12, 12),
  (100, 100),
  (1, 1, 1, 1, 1)),  # 26(CFO Revised Battle 1, Difficulty 3)
 ((1, 1),
  (3, 8),
  (9, 9),
  (30, 30),
  (1, 1, 1, 1, 1)),  # 27(CFO Revised Battle 2, Difficulty 1)
 ((1, 1),
  (4, 9),
  (10, 10),
  (45, 45),
  (1, 1, 1, 1, 1)),  # 28(CFO Revised Battle 2, Difficulty 2)
 ((1, 1),
  (6, 10),
  (11, 11),
  (60, 60),
  (1, 1, 1, 1, 1)),  # 29(CFO Revised Battle 2, Difficulty 3))

 # ADDITIONAL BUILDINGS
 ((1, 2),
  (2, 4),
  (5, 5),
  (20, 20),
  (1, 1.5)),  # 30
 ((1, 2),
  (2, 4),
  (5, 7),
  (22, 22),
  (1, 1.5)),  # 31
 ((2, 2),
  (3, 6),
  (7, 8),
  (10, 25),
  (1.75, 2.0)),  # 32
 ((2, 2),
  (3, 7),
  (9, 9),
  (10, 16),
  (1.75, 1.0)),  # 33
 ((2, 3),
  (3, 5),
  (6, 6),
  (16, 24),
  (1.0, 1.5, 2.0)),  # 34
 ((3, 3),
  (3, 6),
  (7, 7),
  (10, 15),
  (1.5, 1.0, 2.0)),  # 35
 ((3, 4),
  (4, 7),
  (8, 9),
  (17, 24),
  (1.33, 1.0, 1.66, 1.75)),  # 36
 ((3, 4),
  (4, 6),
  (10, 10),
  (17, 24),
  (1.33, 1.0, 1.4, 1.6)),  # 37
 ((4, 4),
  (5, 8),
  (9, 10),
  (20, 26),
  (1.1, 1.0, 1.25, 1.5)),  # 38
 ((4, 4),
  (6, 9),
  (10, 10),
  (20, 25),
  (1.5, 1.0, 1.1, 1.6)),  # 39
 ((3, 5),
  (4, 9),
  (11, 11),
  (20, 25),
  (1.7, 1.0, 1.22, 1.33, 1.2)),  # 40
 ((3, 5),
  (4, 8),
  (10, 10),
  (20, 25),
  (1.7, 1.1, 1.5, 1.7, 1.4)),  # 41
 ((4, 5),
  (1, 7),
  (9, 9),
  (20, 25),
  (1.7, 1.1, 1.5, 1.7, 1.4)),  # 42
 ((4, 5),
  (5, 10),
  (11, 11),
  (16, 28),
  (1.75, 1.0, 2.0, 1.0, 2.5)),  # 43
 ((4, 5),
  (5, 10),
  (11, 11),
  (16, 28),
  (1.0, 1.75, 1.0, 2.0, 2.5)),  # 44
 ((4, 5),
  (7, 11),
  (12, 12),
  (15, 25),
  (1.0, 1.0, 1.0, 2.0, 2.5)),  # 45
 ((5, 5),
  (5, 10),
  (11, 11),
  (20, 30),
  (1.0, 2.0, 1.0, 2.0, 1.5)),  # 46
)

SUIT_BLDG_INFO_FLOORS = 0
SUIT_BLDG_INFO_SUIT_LVLS = 1
SUIT_BLDG_INFO_BOSS_LVLS = 2
SUIT_BLDG_INFO_LVL_POOL = 3
SUIT_BLDG_INFO_LVL_POOL_MULTS = 4
SUIT_BLDG_INFO_REVIVES = 5
VICTORY_RUN_TIME = ElevatorData[ELEVATOR_NORMAL]['openTime'] + TOON_VICTORY_EXIT_TIME
TO_TOON_BLDG_TIME = 8
VICTORY_SEQUENCE_TIME = VICTORY_RUN_TIME + TO_TOON_BLDG_TIME
CLEAR_OUT_TOON_BLDG_TIME = 4
TO_SUIT_BLDG_TIME = 8

buildingMinMax = {
    ToontownGlobals.SillyStreet: [config.GetInt('silly-street-building-min', 0),
                                  config.GetInt('silly-street-building-max', 3)],
    ToontownGlobals.LoopyLane: [config.GetInt('loopy-lane-building-min', 0),
                                config.GetInt('loopy-lane-building-max', 3)],
    ToontownGlobals.PunchlinePlace: [config.GetInt('punchline-place-building-min', 0),
                                     config.GetInt('punchline-place-building-max', 3)],
    ToontownGlobals.BarnacleBoulevard: [config.GetInt('barnacle-boulevard-building-min', 1),
                                        config.GetInt('barnacle-boulevard-building-max', 5)],
    ToontownGlobals.SeaweedStreet: [config.GetInt('seaweed-street-building-min', 1),
                                    config.GetInt('seaweed-street-building-max', 5)],
    ToontownGlobals.LighthouseLane: [config.GetInt('lighthouse-lane-building-min', 1),
                                     config.GetInt('lighthouse-lane-building-max', 5)],
    ToontownGlobals.ElmStreet: [config.GetInt('elm-street-building-min', 2),
                                config.GetInt('elm-street-building-max', 6)],
    ToontownGlobals.MapleStreet: [config.GetInt('maple-street-building-min', 2),
                                  config.GetInt('maple-street-building-max', 6)],
    ToontownGlobals.OakStreet: [config.GetInt('oak-street-building-min', 2),
                                config.GetInt('oak-street-building-max', 6)],
    ToontownGlobals.AltoAvenue: [config.GetInt('alto-avenue-building-min', 3),
                                 config.GetInt('alto-avenue-building-max', 7)],
    ToontownGlobals.BaritoneBoulevard: [config.GetInt('baritone-boulevard-building-min', 3),
                                        config.GetInt('baritone-boulevard-building-max', 7)],
    ToontownGlobals.TenorTerrace: [config.GetInt('tenor-terrace-building-min', 3),
                                   config.GetInt('tenor-terrace-building-max', 7)],
    ToontownGlobals.WalrusWay: [config.GetInt('walrus-way-building-min', 5),
                                config.GetInt('walrus-way-building-max', 10)],
    ToontownGlobals.SleetStreet: [config.GetInt('sleet-street-building-min', 5),
                                  config.GetInt('sleet-street-building-max', 10)],
    ToontownGlobals.PolarPlace: [config.GetInt('polar-place-building-min', 5),
                                 config.GetInt('polar-place-building-max', 10)],
    ToontownGlobals.LullabyLane: [config.GetInt('lullaby-lane-building-min', 6),
                                  config.GetInt('lullaby-lane-building-max', 12)],
    ToontownGlobals.PajamaPlace: [config.GetInt('pajama-place-building-min', 6),
                                  config.GetInt('pajama-place-building-max', 12)],
    ToontownGlobals.StrikeZone: [config.GetInt('pajama-place-building-min', 0),
                                  config.GetInt('pajama-place-building-max', 0)],
    ToontownGlobals.SellbotHQ: [0, 0],
    ToontownGlobals.SellbotFactoryExt: [0, 0],
    ToontownGlobals.CashbotHQ: [0, 0],
    ToontownGlobals.LawbotHQ: [0, 0],
    ToontownGlobals.BossbotHQ: [0, 0]
}

buildingChance = {
    ToontownGlobals.SillyStreet: config.GetFloat('silly-street-building-chance', 2.0),
    ToontownGlobals.LoopyLane: config.GetFloat('loopy-lane-building-chance', 2.0),
    ToontownGlobals.PunchlinePlace: config.GetFloat('punchline-place-building-chance', 2.0),
    ToontownGlobals.BarnacleBoulevard: config.GetFloat('barnacle-boulevard-building-chance', 75.0),
    ToontownGlobals.SeaweedStreet: config.GetFloat('seaweed-street-building-chance', 75.0),
    ToontownGlobals.LighthouseLane: config.GetFloat('lighthouse-lane-building-chance', 75.0),
    ToontownGlobals.ElmStreet: config.GetFloat('elm-street-building-chance', 90.0),
    ToontownGlobals.MapleStreet: config.GetFloat('maple-street-building-chance', 90.0),
    ToontownGlobals.OakStreet: config.GetFloat('oak-street-building-chance', 90.0),
    ToontownGlobals.AltoAvenue: config.GetFloat('alto-avenue-building-chance', 95.0),
    ToontownGlobals.BaritoneBoulevard: config.GetFloat('baritone-boulevard-building-chance', 95.0),
    ToontownGlobals.TenorTerrace: config.GetFloat('tenor-terrace-building-chance', 95.0),
    ToontownGlobals.WalrusWay: config.GetFloat('walrus-way-building-chance', 100.0),
    ToontownGlobals.SleetStreet: config.GetFloat('sleet-street-building-chance', 100.0),
    ToontownGlobals.PolarPlace: config.GetFloat('polar-place-building-chance', 100.0),
    ToontownGlobals.LullabyLane: config.GetFloat('lullaby-lane-building-chance', 100.0),
    ToontownGlobals.PajamaPlace: config.GetFloat('pajama-place-building-chance', 100.0),
    ToontownGlobals.StrikeZone: config.GetFloat('pajama-place-building-chance', 0),
    ToontownGlobals.SellbotHQ: 0.0,
    ToontownGlobals.SellbotFactoryExt: 0.0,
    ToontownGlobals.CashbotHQ: 0.0,
    ToontownGlobals.LawbotHQ: 0.0,
    ToontownGlobals.BossbotHQ: 0.0
}

zone2plannerId = {
    2100: [30, 31, 32],
    2200: [30, 31, 32],
    2300: [30, 31, 32],
    1100: [30, 31, 32, 33, 34],
    1200: [30, 31, 32, 33, 35, 36],
    1300: [30, 31, 32, 33, 35, 36],
    3100: [30, 31, 32, 33, 35, 36, 37],
    3200: [30, 31, 32, 33, 35, 36, 37, 38, 39],
    3300: [30, 31, 32, 33, 35, 36, 37, 38, 39],
    4100: [30, 31, 32, 33, 35, 36, 37, 38],
    4200: [33, 35, 36, 37, 39, 40],
    4300: [33, 35, 36, 37, 39, 40, 41],
    5100: [35, 36, 37, 39, 40, 41, 42, 43],
    5200: [35, 36, 37, 39, 40, 41, 42, 43],
    5300: [36, 37, 39, 40, 41, 42, 43, 44],
    9100: [36, 37, 39, 40, 41, 42, 43, 44, 45, 46],
    9200: [36, 37, 39, 40, 41, 42, 43, 44, 45, 46],
    19000: [36, 37, 39, 40, 41, 42, 43, 44, 45, 46],
}


def getPossibleBuildingDifficulty(level, zoneId):
    minDiff = max(level - 1, 0)
    maxDiff = min(level + 1, 10)
    zoneDiffs = zone2plannerId.get(zoneId, [])
    return range(minDiff, maxDiff) + zoneDiffs

zone2MinMaxLevel = {
    2000: (2, 7,),
    1000: (3, 8,),
    3000: (4, 9,),
    4000: (5, 10),
    5000: (6, 11),
    9000: (7, 12),
    19000: (8, 13),
}