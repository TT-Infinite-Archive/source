import enum
from panda3d.core import BitMask32, Point3, VBase4
from direct.showbase import PythonUtil
from toontown.toonbase import TTLocalizer
KICK_TO_PLAYGROUND_EVENT = 'parties_kickToPlayground'
MaxSetInvites = 1000
MaxSetPartiesInvitedTo = 100
MaxSetHostedParties = 50
MaxPlannedYear = 2030
MinPlannedYear = 1975
JellybeanMultiplier = 1.5
JellyBeanDayMultiplier = 2
PARTY_DURATION = 1800
EventsPageGuestNameMaxWidth = 0.42
EventsPageGuestNameMaxLetters = 18
EventsPageHostNameMaxWidth = 0.37
PartyRefundPercentage = 0.95
PartyPlannerAsapMinuteRounding = 5
UberdogCheckPartyStartFrequency = 5.0
UberdogPurgePartyPeriod = 24.0
UberdogPartiesSanityCheckFrequency = 60
JarLabelTextColor = (0.95,
 0.95,
 0.0,
 1.0)
JarLabelMaxedTextColor = (1.0,
 0.0,
 0.0,
 1.0)
TuftsOfGrass = 75
MaxToonsAtAParty = 20
DefaultPartyDuration = 0.5
DelayBeforeAutoKick = 1.0
MaxHostedPartiesPerToon = 1
PartyEditorGridBounds = ((-0.11, 0.289), (0.55, -0.447))
PartyEditorGridCenter = (PartyEditorGridBounds[0][0] + (PartyEditorGridBounds[1][0] - PartyEditorGridBounds[0][0]) / 2.0, PartyEditorGridBounds[1][1] + (PartyEditorGridBounds[0][1] - PartyEditorGridBounds[1][1]) / 2.0)
PartyEditorGridSize = (18, 15)
PartyEditorGridSquareSize = ((PartyEditorGridBounds[1][0] - PartyEditorGridBounds[0][0]) / float(PartyEditorGridSize[0]), (PartyEditorGridBounds[0][1] - PartyEditorGridBounds[1][1]) / float(PartyEditorGridSize[1]))
PartyEditorGridRotateThreshold = 0.08
AvailableGridSquares = 202
TrashCanPosition = (-0.24, 0.0, -0.65)
TrashCanScale = 0.7
PartyEditorTrashBounds = ((-0.16, -0.38), (-0.05, -0.56))


class EActivityRequestStatus(enum.IntEnum):
    JOINING = 0
    EXITING = 1


class EInviteStatus(enum.IntEnum):
    NOT_READ = 0
    READ_BUT_NOT_REPLIED = 1
    ACCEPTED = 2
    REJECTED = 3


class EInviteTheme(enum.IntEnum):
    BIRTHDAY = 0
    GENERIC_MALE = 1
    GENERIC_FEMALE = 2
    RACING = 3
    VALENTOONS = 4
    VICTORY_PARTY = 5
    WINTER = 6


class EPartyStatus(enum.IntEnum):
    PENDING = 0
    CANCELLED = 1
    FINISHED = 2
    CAN_START = 3
    STARTED = 4
    NEVER_STARTED = 5


class EAddPartyErrorCode(enum.IntEnum):
    ALL_OK = 0
    VALIDATION_ERROR = 1
    DATABASE_ERROR = 2
    TOO_MANY_HOSTED_PARTIES = 3


class EChangePartyFieldErrorCode(enum.IntEnum):
    ALL_OK = 0
    VALIDATION_ERROR = 1
    DATABASE_ERROR = 2
    ALREADY_STARTED = 3
    ALREADY_REFUNDED = 4


class EActivityType(enum.IntEnum):
    HOST_INITIATED = 0
    GUEST_INITIATED = 1
    CONTINUOUS = 2


class EPartyGateDenialReason(enum.IntEnum):
    UNAVAILABLE = 0
    FULL = 1


class EActivityId(enum.IntEnum):
    PartyJukebox = 0
    PartyCannon = 1
    PartyTrampoline = 2
    PartyCatch = 3
    PartyDance = 4
    PartyTugOfWar = 5
    PartyFireworks = 6
    PartyClock = 7
    PartyJukebox40 = 8
    PartyDance20 = 9
    PartyCog = 10
    PartyVictoryTrampoline = 11
    PartyWinterCatch = 12
    PartyWinterTrampoline = 13
    PartyWinterCog = 14
    PartyValentineDance = 15
    PartyValentineDance20 = 16
    PartyValentineJukebox = 17
    PartyValentineJukebox40 = 18
    PartyValentineTrampoline = 19


PartyEditorActivityOrder = [EActivityId.PartyClock,
 EActivityId.PartyJukebox,
 EActivityId.PartyJukebox40,
 EActivityId.PartyValentineJukebox,
 EActivityId.PartyValentineJukebox40,
 EActivityId.PartyCannon,
 EActivityId.PartyTrampoline,
 EActivityId.PartyValentineTrampoline,
 EActivityId.PartyVictoryTrampoline,
 EActivityId.PartyWinterTrampoline,
 EActivityId.PartyDance,
 EActivityId.PartyDance20,
 EActivityId.PartyValentineDance,
 EActivityId.PartyValentineDance20,
 EActivityId.PartyCatch,
 EActivityId.PartyWinterCatch,
 EActivityId.PartyWinterCog,
 EActivityId.PartyTugOfWar,
 EActivityId.PartyCog,
 EActivityId.PartyFireworks]
UnreleasedEActivityId = (
 # These AIs need to be written before they can be used:
 EActivityId.PartyJukebox,
 EActivityId.PartyJukebox40,
 # --------------------
 EActivityId.PartyWinterCog,
 EActivityId.PartyValentineJukebox,
 EActivityId.PartyValentineJukebox40,
 EActivityId.PartyValentineTrampoline,
 EActivityId.PartyWinterTrampoline,
 EActivityId.PartyWinterCatch,
 EActivityId.PartyValentineDance,
 EActivityId.PartyValentineDance20)
UnreleasedEActivityIdSP = (
 # These AIs need to be written before they can be used:
 EActivityId.PartyJukebox,
 EActivityId.PartyJukebox40,
 EActivityId.PartyTugOfWar,
 EActivityId.PartyCog,
 # --------------------
 EActivityId.PartyWinterCog,
 EActivityId.PartyValentineJukebox,
 EActivityId.PartyValentineJukebox40,
 EActivityId.PartyValentineTrampoline,
 EActivityId.PartyWinterTrampoline,
 EActivityId.PartyWinterCatch,
 EActivityId.PartyValentineDance,
 EActivityId.PartyValentineDance20)

MutuallyExclusiveActivities = ((EActivityId.PartyJukebox, EActivityId.PartyJukebox40),
 (EActivityId.PartyValentineJukebox, EActivityId.PartyValentineJukebox40),
 (EActivityId.PartyDance, EActivityId.PartyDance20),
 (EActivityId.PartyValentineDance, EActivityId.PartyValentineDance20))
VictoryPartyEActivityId = frozenset([EActivityId.PartyVictoryTrampoline])
VictoryPartyReplacementEActivityId = frozenset([EActivityId.PartyTrampoline])
WinterPartyEActivityId = frozenset([EActivityId.PartyWinterCatch, EActivityId.PartyWinterTrampoline, EActivityId.PartyWinterCog])
WinterPartyReplacementEActivityId = frozenset([EActivityId.PartyCatch, EActivityId.PartyTrampoline, EActivityId.PartyCog])
ValentinePartyEActivityId = frozenset([EActivityId.PartyValentineDance,
 EActivityId.PartyValentineDance20,
 EActivityId.PartyValentineJukebox,
 EActivityId.PartyValentineJukebox40,
 EActivityId.PartyValentineTrampoline])
ValentinePartyReplacementEActivityId = frozenset([EActivityId.PartyDance,
 EActivityId.PartyDance20,
 EActivityId.PartyJukebox,
 EActivityId.PartyJukebox40,
 EActivityId.PartyTrampoline])

class EDecorationId(enum.IntEnum):
    BalloonAnvil = 0
    BalloonStage = 1
    Bow = 2
    Cake = 3
    Castle = 4
    GiftPile = 5
    Horn = 6
    MardiGras = 7
    NoiseMakers = 8
    Pinwheel = 9
    GagGlobe = 10
    BannerJellyBean = 11
    CakeTower = 12
    HeartTarget = 13
    HeartBanner = 14
    FlyingHeart = 15
    Hydra = 16
    BannerVictory = 17
    CannonVictory = 18
    CogStatueVictory = 19
    TubeCogVictory = 20
    CogIceCreamVictory = 21
    cogIceCreamWinter = 22
    StageWinter = 23
    CogStatueWinter = 24
    snowman = 25
    snowDoodle = 26
    BalloonAnvilValentine = 27

TTIUnreleasedDecor = [EDecorationId.HeartTarget,
 EDecorationId.HeartBanner,
 EDecorationId.FlyingHeart,
 EDecorationId.Hydra,
 EDecorationId.BannerVictory,
 EDecorationId.CannonVictory,
 EDecorationId.CogStatueVictory,
 EDecorationId.TubeCogVictory,
 EDecorationId.CogIceCreamVictory,
 EDecorationId.cogIceCreamWinter,
 EDecorationId.StageWinter,
 EDecorationId.CogStatueWinter,
 EDecorationId.snowman,
 EDecorationId.snowDoodle,
 EDecorationId.BalloonAnvilValentine]
DECORATION_VOLUME = 1.0
DECORATION_CUTOFF = 45
VictoryPartyEDecorationId = frozenset([EDecorationId.Hydra,
 EDecorationId.BannerVictory,
 EDecorationId.CannonVictory,
 EDecorationId.CogStatueVictory,
 EDecorationId.TubeCogVictory,
 EDecorationId.CogIceCreamVictory])
WinterPartyEDecorationId = frozenset([EDecorationId.cogIceCreamWinter,
 EDecorationId.StageWinter,
 EDecorationId.CogStatueWinter,
 EDecorationId.snowman,
 EDecorationId.snowDoodle])
VictoryPartyReplacementEDecorationId = frozenset([EDecorationId.BannerJellyBean])
ValentinePartyEDecorationId = frozenset([EDecorationId.BalloonAnvilValentine,
 EDecorationId.HeartBanner,
 EDecorationId.HeartTarget,
 EDecorationId.FlyingHeart])
ValentinePartyReplacementEDecorationId = frozenset([EDecorationId.BalloonAnvil, EDecorationId.BannerJellyBean])
UnreleasedEDecorationId = ()

class EGoToPartyStatus(enum.IntEnum):
    ALLOWED_TO_GO = 0
    PARTY_FULL = 1
    PRIVATE_PARTY = 2
    PARTY_OVER = 3
    PARTY_NOT_ACTIVE = 4

PlayGroundToPartyClockColors = {'the_burrrgh': (53.0 / 255.0,
                 116.0 / 255.0,
                 148.0 / 255.0,
                 1.0),
 'daisys_garden': (52.0 / 255.0,
                   153.0 / 255.0,
                   95.0 / 255.0,
                   1.0),
 'donalds_dock': (60.0 / 255.0,
                  98.0 / 255.0,
                  142.0 / 255.0,
                  1.0),
 'donalds_dreamland': (79.0 / 255.0,
                       92.0 / 255.0,
                       120.0 / 255.0,
                       1.0),
 'minnies_melody_land': (128.0 / 255.0,
                         62.0 / 255.0,
                         142.0 / 255.0,
                         1.0),
 'toontown_central': (77.0 / 255.0,
                      137.0 / 255.0,
                      52.0 / 255.0,
                      1.0)}
PartyGridUnitLength = [14.4, 14.6]
PartyGridHeadingConverter = 15.0
PartyGridToPandaOffset = (-PartyGridUnitLength[0] * PartyEditorGridSize[0] / 2.0, -PartyGridUnitLength[1] * PartyEditorGridSize[1] / 2.0)
PartyCostMultiplier = 0 # ALPHA ONLY - remove after parties are legit
MinimumPartyCost = 100 * PartyCostMultiplier
ActivityInformationDict = {EActivityId.PartyJukebox: {'cost': int(50 * PartyCostMultiplier),
                            'gridsize': (1, 1),
                            'numberPerPurchase': 1,
                            'limitPerParty': 1,
                            'paidOnly': False,
                            'gridAsset': 'PartyJukebox_activity_1x1'},
 EActivityId.PartyJukebox40: {'cost': int(100 * PartyCostMultiplier),
                              'gridsize': (1, 1),
                              'numberPerPurchase': 1,
                              'limitPerParty': 1,
                              'paidOnly': False,
                              'gridAsset': 'PartyJukebox_activity_1x1'},
 EActivityId.PartyValentineJukebox: {'cost': int(50 * PartyCostMultiplier),
                                     'gridsize': (1, 1),
                                     'numberPerPurchase': 1,
                                     'limitPerParty': 1,
                                     'paidOnly': False,
                                     'gridAsset': 'PartyJukebox_activity_1x1'},
 EActivityId.PartyValentineJukebox40: {'cost': int(100 * PartyCostMultiplier),
                                       'gridsize': (1, 1),
                                       'numberPerPurchase': 1,
                                       'limitPerParty': 1,
                                       'paidOnly': False,
                                       'gridAsset': 'PartyJukebox_activity_1x1'},
 EActivityId.PartyCannon: {'cost': int(50 * PartyCostMultiplier),
                           'gridsize': (1, 1),
                           'numberPerPurchase': 5,
                           'limitPerParty': 10,
                           'paidOnly': False,
                           'gridAsset': 'PartyCannon_activity_1x1'},
 EActivityId.PartyTrampoline: {'cost': int(50 * PartyCostMultiplier),
                               'gridsize': (2, 2),
                               'numberPerPurchase': 1,
                               'limitPerParty': 8,
                               'paidOnly': False,
                               'gridAsset': 'PartyTrampoline_activity_2x2'},
 EActivityId.PartyValentineTrampoline: {'cost': int(50 * PartyCostMultiplier),
                                        'gridsize': (2, 2),
                                        'numberPerPurchase': 1,
                                        'limitPerParty': 8,
                                        'paidOnly': False,
                                        'gridAsset': 'PartyTrampoline_activity_2x2'},
 EActivityId.PartyVictoryTrampoline: {'cost': int(50 * PartyCostMultiplier),
                                      'gridsize': (2, 2),
                                      'numberPerPurchase': 1,
                                      'limitPerParty': 8,
                                      'paidOnly': False,
                                      'gridAsset': 'PartyTrampoline_activity_2x2'},
 EActivityId.PartyWinterTrampoline: {'cost': int(50 * PartyCostMultiplier),
                                     'gridsize': (2, 2),
                                     'numberPerPurchase': 1,
                                     'limitPerParty': 8,
                                     'paidOnly': False,
                                     'gridAsset': 'PartyTrampoline_activity_2x2'},
 EActivityId.PartyCatch: {'cost': int(300 * PartyCostMultiplier),
                          'gridsize': (5, 5),
                          'numberPerPurchase': 1,
                          'limitPerParty': 1,
                          'paidOnly': True,
                          'gridAsset': 'PartyCatch_activity_5x5'},
 EActivityId.PartyWinterCatch: {'cost': int(300 * PartyCostMultiplier),
                                'gridsize': (5, 5),
                                'numberPerPurchase': 1,
                                'limitPerParty': 1,
                                'paidOnly': True,
                                'gridAsset': 'PartyCatch_activity_5x5'},
 EActivityId.PartyCog: {'cost': int(300 * PartyCostMultiplier),
                        'gridsize': (5, 5),
                        'numberPerPurchase': 1,
                        'limitPerParty': 1,
                        'paidOnly': True,
                        'gridAsset': 'PartyCog_activity_5x5'},
 EActivityId.PartyWinterCog: {'cost': int(300 * PartyCostMultiplier),
                              'gridsize': (5, 5),
                              'numberPerPurchase': 1,
                              'limitPerParty': 1,
                              'paidOnly': True,
                              'gridAsset': 'PartyCog_activity_5x5'},
 EActivityId.PartyDance: {'cost': int(100 * PartyCostMultiplier),
                          'gridsize': (3, 3),
                          'numberPerPurchase': 1,
                          'limitPerParty': 1,
                          'paidOnly': True,
                          'gridAsset': 'PartyDance_activity_3x3'},
 EActivityId.PartyDance20: {'cost': int(200 * PartyCostMultiplier),
                            'gridsize': (3, 3),
                            'numberPerPurchase': 1,
                            'limitPerParty': 1,
                            'paidOnly': True,
                            'gridAsset': 'PartyDance_activity_3x3'},
 EActivityId.PartyValentineDance: {'cost': int(100 * PartyCostMultiplier),
                                   'gridsize': (3, 3),
                                   'numberPerPurchase': 1,
                                   'limitPerParty': 1,
                                   'paidOnly': True,
                                   'gridAsset': 'PartyDance_activity_3x3'},
 EActivityId.PartyValentineDance20: {'cost': int(200 * PartyCostMultiplier),
                                     'gridsize': (3, 3),
                                     'numberPerPurchase': 1,
                                     'limitPerParty': 1,
                                     'paidOnly': True,
                                     'gridAsset': 'PartyDance_activity_3x3'},
 EActivityId.PartyTugOfWar: {'cost': int(200 * PartyCostMultiplier),
                             'gridsize': (4, 4),
                             'numberPerPurchase': 1,
                             'limitPerParty': 1,
                             'paidOnly': False,
                             'gridAsset': 'PartyTufOfWar_activity_4x4'},
 EActivityId.PartyFireworks: {'cost': int(200 * PartyCostMultiplier),
                              'gridsize': (4, 2),
                              'numberPerPurchase': 1,
                              'limitPerParty': 1,
                              'paidOnly': False,
                              'gridAsset': 'PartyFireworks_activity_2x4'},
 EActivityId.PartyClock: {'cost': MinimumPartyCost,
                          'gridsize': (1, 1),
                          'numberPerPurchase': 1,
                          'limitPerParty': 1,
                          'paidOnly': False,
                          'gridAsset': 'PartyClock_activity_1x1'}}
DecorationInformationDict = {EDecorationId.BalloonAnvil: {'cost': int(10 * PartyCostMultiplier),
                              'gridsize': (1, 1),
                              'numberPerPurchase': 1,
                              'limitPerParty': 5,
                              'paidOnly': False,
                              'gridAsset': 'decoration_1x1'},
 EDecorationId.BalloonAnvilValentine: {'cost': int(10 * PartyCostMultiplier),
                                       'gridsize': (1, 1),
                                       'numberPerPurchase': 1,
                                       'limitPerParty': 5,
                                       'paidOnly': False,
                                       'gridAsset': 'decoration_1x1'},
 EDecorationId.BalloonStage: {'cost': int(25 * PartyCostMultiplier),
                              'gridsize': (1, 1),
                              'numberPerPurchase': 1,
                              'limitPerParty': 5,
                              'paidOnly': False,
                              'gridAsset': 'decoration_1x1'},
 EDecorationId.Bow: {'cost': int(10 * PartyCostMultiplier),
                     'gridsize': (1, 1),
                     'numberPerPurchase': 1,
                     'limitPerParty': 5,
                     'paidOnly': False,
                     'gridAsset': 'decoration_1x1'},
 EDecorationId.Cake: {'cost': int(10 * PartyCostMultiplier),
                      'gridsize': (1, 1),
                      'numberPerPurchase': 1,
                      'limitPerParty': 5,
                      'paidOnly': False,
                      'gridAsset': 'decoration_1x1'},
 EDecorationId.Castle: {'cost': int(25 * PartyCostMultiplier),
                        'gridsize': (1, 1),
                        'numberPerPurchase': 1,
                        'limitPerParty': 5,
                        'paidOnly': False,
                        'gridAsset': 'decoration_1x1'},
 EDecorationId.GiftPile: {'cost': int(10 * PartyCostMultiplier),
                          'gridsize': (1, 1),
                          'numberPerPurchase': 1,
                          'limitPerParty': 5,
                          'paidOnly': False,
                          'gridAsset': 'decoration_1x1'},
 EDecorationId.Horn: {'cost': int(10 * PartyCostMultiplier),
                      'gridsize': (1, 1),
                      'numberPerPurchase': 1,
                      'limitPerParty': 5,
                      'paidOnly': False,
                      'gridAsset': 'decoration_1x1'},
 EDecorationId.MardiGras: {'cost': int(25 * PartyCostMultiplier),
                           'gridsize': (1, 1),
                           'numberPerPurchase': 1,
                           'limitPerParty': 5,
                           'paidOnly': False,
                           'gridAsset': 'decoration_1x1'},
 EDecorationId.NoiseMakers: {'cost': int(10 * PartyCostMultiplier),
                             'gridsize': (1, 1),
                             'numberPerPurchase': 1,
                             'limitPerParty': 5,
                             'paidOnly': False,
                             'gridAsset': 'decoration_1x1'},
 EDecorationId.Pinwheel: {'cost': int(10 * PartyCostMultiplier),
                          'gridsize': (1, 1),
                          'numberPerPurchase': 1,
                          'limitPerParty': 5,
                          'paidOnly': False,
                          'gridAsset': 'decoration_1x1'},
 EDecorationId.GagGlobe: {'cost': int(25 * PartyCostMultiplier),
                          'gridsize': (1, 1),
                          'numberPerPurchase': 1,
                          'limitPerParty': 5,
                          'paidOnly': False,
                          'gridAsset': 'decoration_1x1'},
 EDecorationId.BannerJellyBean: {'cost': int(25 * PartyCostMultiplier),
                                 'gridsize': (1, 1),
                                 'numberPerPurchase': 1,
                                 'limitPerParty': 5,
                                 'paidOnly': False,
                                 'gridAsset': 'decoration_1x1'},
 EDecorationId.CakeTower: {'cost': int(25 * PartyCostMultiplier),
                           'gridsize': (1, 1),
                           'numberPerPurchase': 1,
                           'limitPerParty': 5,
                           'paidOnly': False,
                           'gridAsset': 'decoration_1x1'},
 EDecorationId.HeartTarget: {'cost': int(25 * PartyCostMultiplier),
                             'gridsize': (1, 1),
                             'numberPerPurchase': 1,
                             'limitPerParty': 5,
                             'paidOnly': False,
                             'gridAsset': 'decoration_1x1'},
 EDecorationId.HeartBanner: {'cost': int(25 * PartyCostMultiplier),
                             'gridsize': (1, 1),
                             'numberPerPurchase': 1,
                             'limitPerParty': 5,
                             'paidOnly': False,
                             'gridAsset': 'decoration_1x1'},
 EDecorationId.FlyingHeart: {'cost': int(25 * PartyCostMultiplier),
                             'gridsize': (1, 1),
                             'numberPerPurchase': 1,
                             'limitPerParty': 5,
                             'paidOnly': False,
                             'gridAsset': 'decoration_1x1'},
 EDecorationId.Hydra: {'cost': int(25 * PartyCostMultiplier),
                       'gridsize': (2, 2),
                       'numberPerPurchase': 1,
                       'limitPerParty': 5,
                       'paidOnly': False,
                       'gridAsset': 'decoration_propStage_2x2'},
 EDecorationId.BannerVictory: {'cost': int(25 * PartyCostMultiplier),
                               'gridsize': (1, 1),
                               'numberPerPurchase': 1,
                               'limitPerParty': 5,
                               'paidOnly': False,
                               'gridAsset': 'decoration_1x1'},
 EDecorationId.CannonVictory: {'cost': int(25 * PartyCostMultiplier),
                               'gridsize': (1, 1),
                               'numberPerPurchase': 1,
                               'limitPerParty': 5,
                               'paidOnly': False,
                               'gridAsset': 'decoration_1x1'},
 EDecorationId.CogStatueVictory: {'cost': int(25 * PartyCostMultiplier),
                                  'gridsize': (1, 1),
                                  'numberPerPurchase': 1,
                                  'limitPerParty': 5,
                                  'paidOnly': False,
                                  'gridAsset': 'decoration_1x1'},
 EDecorationId.TubeCogVictory: {'cost': int(25 * PartyCostMultiplier),
                                'gridsize': (1, 1),
                                'numberPerPurchase': 1,
                                'limitPerParty': 5,
                                'paidOnly': False,
                                'gridAsset': 'decoration_1x1'},
 EDecorationId.CogIceCreamVictory: {'cost': int(25 * PartyCostMultiplier),
                                    'gridsize': (1, 1),
                                    'numberPerPurchase': 1,
                                    'limitPerParty': 5,
                                    'paidOnly': False,
                                    'gridAsset': 'decoration_1x1'},
 EDecorationId.cogIceCreamWinter: {'cost': int(25 * PartyCostMultiplier),
                                   'gridsize': (1, 1),
                                   'numberPerPurchase': 1,
                                   'limitPerParty': 5,
                                   'paidOnly': False,
                                   'gridAsset': 'decoration_1x1'},
 EDecorationId.StageWinter: {'cost': int(25 * PartyCostMultiplier),
                             'gridsize': (2, 2),
                             'numberPerPurchase': 1,
                             'limitPerParty': 5,
                             'paidOnly': False,
                             'gridAsset': 'decoration_propStage_2x2'},
 EDecorationId.CogStatueWinter: {'cost': int(25 * PartyCostMultiplier),
                                 'gridsize': (1, 1),
                                 'numberPerPurchase': 1,
                                 'limitPerParty': 5,
                                 'paidOnly': False,
                                 'gridAsset': 'decoration_1x1'},
 EDecorationId.snowman: {'cost': int(25 * PartyCostMultiplier),
                         'gridsize': (1, 1),
                         'numberPerPurchase': 1,
                         'limitPerParty': 5,
                         'paidOnly': False,
                         'gridAsset': 'decoration_1x1'},
 EDecorationId.snowDoodle: {'cost': int(25 * PartyCostMultiplier),
                            'gridsize': (1, 1),
                            'numberPerPurchase': 1,
                            'limitPerParty': 5,
                            'paidOnly': False,
                            'gridAsset': 'decoration_1x1'}}
DefaultRulesTimeout = 10.0

class EDenialReason(enum.IntEnum):
    DEFAULT = 0
    FULL = 1
    SILENT_FAIL = 2


class EFireworkShow(enum.IntEnum):
    SUMMER = 200

FireworksGlobalXOffset = 160.0
FireworksGlobalYOffset = -20.0
FireworksPostLaunchDelay = 5.0
RocketSoundDelay = 2.0
RocketDirectionDelay = 2.0
FireworksStartedEvent = 'PartyFireworksStarted'
FireworksFinishedEvent = 'PartyFireworksFinished'
FireworksTransitionToDisabledDelay = 3.0

class ETeamActivityTeam(enum.IntEnum):
    LEFT = 0
    RIGHT = 1

TeamActivityNeitherTeam = 3
TeamActivityTextScale = 0.135
TeamActivityStartDelay = 8.0
TeamActivityClientWaitDelay = 30.0
TeamActivityDefaultMinPlayersPerTeam = 1
TeamActivityDefaultMaxPlayersPerTeam = 4
TeamActivityDefaultDuration = 60.0
TeamActivityDefaultConclusionDuration = 4.0
TeamActivityStatusColor = VBase4(1.0, 1.0, 0.65, 1.0)
CogActivityBalanceTeams = True
CogActivityStartDelay = 15.0
CogActivityConclusionDuration = 12
CogActivityDuration = 90
CogActivityMinPlayersPerTeam = 1
CogActivityMaxPlayersPerTeam = 4
CogActivityColors = (VBase4(0.22, 0.4, 0.98, 1.0), VBase4(1.0, 0.43, 0.04, 1.0))
CogActivitySplatColorBase = VBase4(0.98, 0.9, 0.094, 1.0)
CogActivitySplatColors = (VBase4(CogActivityColors[0][0] / CogActivitySplatColorBase[0], CogActivityColors[0][1] / CogActivitySplatColorBase[1], CogActivityColors[0][2] / CogActivitySplatColorBase[2], 1.0), VBase4(CogActivityColors[1][0] / CogActivitySplatColorBase[0], CogActivityColors[1][1] / CogActivitySplatColorBase[1], CogActivityColors[1][2] / CogActivitySplatColorBase[2], 1.0))
CogPinataHeadZ = 4.7
CogActivityHitPoints = 1
CogActivityHitPointsForHead = 3
CogPinataPushBodyFactor = 0.05
CogPinataPushHeadFactor = CogPinataPushBodyFactor * abs(CogActivityHitPointsForHead - CogActivityHitPoints)
CogActivityAvgBeansPerSecond = 0.15
CogActivityBeansToAward = round(CogActivityAvgBeansPerSecond * CogActivityDuration * 2.0)
CogActivityWinBeans = int(round(CogActivityBeansToAward * 0.6))
CogActivityLossBeans = int(round(CogActivityBeansToAward * 0.4))
CogActivityTieBeans = int(round(CogActivityBeansToAward * 0.4))
CogActivityPerfectWinBeans = int(round(CogActivityBeansToAward * 0.75))
CogActivityPerfectLossBeans = int(round(CogActivityBeansToAward * 0.25))
CogActivityArenaLength = 50.0
CogActivityPieMinDist = 0.0
CogActivityPieMaxDist = 110.0
CogActivityPowerMeterHeight = 0.4
CogActivityPowerMeterWidth = 0.1
CogActivityPowerMeterPos = (0.33, 0.0, 0.0)
CogActivityPowerMeterTextPos = (0.33, -0.26)
CogActivityVictoryBarPos = (-0.55, 0.0, 0.825)
CogActivityVictoryBarOrangePos = (0.1725, 0.0, -0.0325)
CogActivityVictoryBarPiePos = (0.47, 0.0, -0.015)
CogActivityVictoryBarArrow = (0.0, 0.0, 0.1)
CogActivityBarUnitScale = 1.1
CogActivityBarStartScale = CogActivityBarUnitScale * 5
CogActivityBarPieUnitMove = 0.07
CogActivityBarPieScale = 1.5
CogActivityScorePos = (1.25, -0.45)
CogActivityScoreTitle = (1.24, -0.5)
CogActivityPowerMeterTime = 1.0
CogActivityShortThrowTime = 0.1
ToonAttackIdleThreshold = 5.0
ToonMoveIdleThreshold = 5.0
CogActivityShortThrowSpam = 3
CogActivitySpamWarningShowTime = 5.0
CogActivityControlsShowTime = 2.0
PARTY_COG_CUTOFF = 60
TugOfWarStartDelay = 8.0
TugOfWarReadyDuration = 1.5
TugOfWarGoDuration = 0.75
TugOfWarDuration = 40.0
TugOfWarMinimumPlayersPerTeam = 1
TugOfWarMaximumPlayersPerTeam = 4
TugOfWarStartGameTimeout = 8
TugOfWarJoinCollisionEndPoints = [Point3(6.0, 0.0, 0.0), Point3(-6.0, 0.0, 0.0)]
TugOfWarJoinCollisionRadius = 1.75
TugOfWarJoinCollisionPositions = [Point3(-10.5, 0.25, 4.5), Point3(10.5, -0.25, 4.5)]
TugOfWarInitialToonPositionsXOffset = 8.0
TugOfWarToonPositionXSeparation = 2.0
TugOfWarToonPositionZ = 2.55
TugOfWarTextWordScale = 0.135
TugOfWarTextCountdownScale = 4.0
TugOfWarCameraPos = Point3(0.0, -33.0, 10.0)
TugOfWarCameraInitialHpr = Point3(0.0, -6.91123, 0.0)
TugOfWarCameraLookAtHeightOffset = 6.0
TugOfWarPowerMeterSize = 17
TugOfWarPowerMeterRulesTarget = 8
TugOfWarDisabledArrowColor = VBase4(1.0, 0.0, 0.0, 0.3)
TugOfWarEnabledArrowColor = VBase4(1.0, 0.0, 0.0, 1.0)
TugOfWarHilightedArrowColor = VBase4(1.0, 0.7, 0.0, 1.0)
TugOfWarTargetRateList = [(8.0, 6),
 (5.0, 7),
 (6.0, 8),
 (6.0, 10),
 (7.0, 11),
 (8.0, 12)]
TugOfWarKeyPressTimeToLive = 1.0
TugOfWarKeyPressUpdateRate = 0.1
TugOfWarKeyPressReportRate = 0.2
TugOfWarMovementFactor = 0.03
TugOfWarSplashZOffset = 1.0
TugOfWarHeadings = [240.0, 120.0]
TugOfWarConclusionDuration = 4.0
TugOfWarFallInWinReward = 15
TugOfWarFallInLossReward = 4
TugOfWarWinReward = 12
TugOfWarLossReward = 8
TugOfWarTieReward = 5
TugOfWarTieThreshold = 0.75
TrampolineDuration = 60.0
TrampolineSignOffset = Point3(-6.0, -6.0, 0.0)
TrampolineLeverOffset = Point3(-5.0, -9.0, 0.0)
TrampolineNumJellyBeans = 12
TrampolineJellyBeanBonus = 10
CatchActivityDuration = 80
CatchActivityBitmask = BitMask32(16)
CatchLeverOffset = Point3(-3.0, -2.0, 0.0)
CatchDropShadowHeight = 0.5
CatchConclusionDuration = 3.0

class DropObject:

    def __init__(self, name, good, onscreenDurMult, modelPath):
        self.name = name
        self.good = good
        self.onscreenDurMult = onscreenDurMult
        self.modelPath = modelPath

    def isBaseline(self):
        return self.onscreenDurMult == 1.0


DropObjectTypes = [DropObject('apple', 1, 1.0, 'phase_4/models/minigames/apple'),
 DropObject('orange', 1, 1.0, 'phase_4/models/minigames/orange'),
 DropObject('pear', 1, 1.0, 'phase_4/models/minigames/pear'),
 DropObject('coconut', 1, 1.0, 'phase_4/models/minigames/coconut'),
 DropObject('watermelon', 1, 1.0, 'phase_4/models/minigames/watermelon'),
 DropObject('pineapple', 1, 1.0, 'phase_4/models/minigames/pineapple'),
 DropObject('anvil', 0, 0.4, 'phase_4/models/props/anvil-mod')]
Name2DropObjectType = {}
for type in DropObjectTypes:
    Name2DropObjectType[type.name] = type

Name2DOTypeId = {}
names = list(Name2DropObjectType.keys())
names.sort()
for i in range(len(names)):
    Name2DOTypeId[names[i]] = i

DOTypeId2Name = names
NumFruits = [{2000: 18,
  1000: 19,
  5000: 22,
  4000: 24,
  3000: 27,
  9000: 28},
 {2000: 30,
  1000: 33,
  5000: 38,
  4000: 42,
  3000: 46,
  9000: 50},
 {2000: 42,
  1000: 48,
  5000: 54,
  4000: 60,
  3000: 66,
  9000: 71},
 {2000: 56,
  1000: 63,
  5000: 70,
  4000: 78,
  3000: 85,
  9000: 92}]
DancePatternToAnims = {'dduu': 'slip-backward',
 'ldddud': 'happy-dance',
 'lll': 'left',
 'rdu': 'struggle',
 'rrr': 'right',
 'rulu': 'running-jump',
 'udlr': 'good-putt',
 'udllrr': 'victory',
 'ulu': 'jump',
 'uudd': 'slip-forward'}
DancePatternToAnims20 = {'ddd': 'down',
 'dduu': 'slip-backward',
 'drul': 'sad-walk',
 'ldr': 'push',
 'ldddud': 'happy-dance',
 'ldu': 'sprinkle-dust',
 'lll': 'left',
 'llrr': 'firehose',
 'lrlr': 'wave',
 'rdu': 'struggle',
 'rlrl': 'confused',
 'rrr': 'right',
 'rulu': 'running-jump',
 'uddd': 'reel-neutral',
 'udlr': 'good-putt',
 'udud': 'angry',
 'udllrr': 'victory',
 'ulu': 'jump',
 'uudd': 'slip-forward',
 'uuu': 'up'}
DanceAnimToName = {'right': TTLocalizer.DanceAnimRight,
 'reel-neutral': TTLocalizer.DanceAnimReelNeutral,
 'conked': TTLocalizer.DanceAnimConked,
 'happy-dance': TTLocalizer.DanceAnimHappyDance,
 'confused': TTLocalizer.DanceAnimConfused,
 'walk': TTLocalizer.DanceAnimWalk,
 'jump': TTLocalizer.DanceAnimJump,
 'firehose': TTLocalizer.DanceAnimFirehose,
 'shrug': TTLocalizer.DanceAnimShrug,
 'slip-forward': TTLocalizer.DanceAnimSlipForward,
 'sad-walk': TTLocalizer.DanceAnimSadWalk,
 'wave': TTLocalizer.DanceAnimWave,
 'struggle': TTLocalizer.DanceAnimStruggle,
 'running-jump': TTLocalizer.DanceAnimRunningJump,
 'slip-backward': TTLocalizer.DanceAnimSlipBackward,
 'down': TTLocalizer.DanceAnimDown,
 'up': TTLocalizer.DanceAnimUp,
 'good-putt': TTLocalizer.DanceAnimGoodPutt,
 'victory': TTLocalizer.DanceAnimVictory,
 'push': TTLocalizer.DanceAnimPush,
 'angry': TTLocalizer.DanceAnimAngry,
 'left': TTLocalizer.DanceAnimLeft}
DanceReverseLoopAnims = ['left',
 'right',
 'up',
 'down',
 'good-putt']

class EToonDancingState(enum.Enum):
    Init = 0
    DanceMove = 1
    Run = 2
    Cleanup = 3

JUKEBOX_TIMEOUT = 30.0
MUSIC_PATH = 'phase_%s/audio/bgm/'
MUSIC_MIN_LENGTH_SECONDS = 50.0
MUSIC_GAP = 2.5
PhaseToMusicData = {3.5: {'TC_SZ.ogg': [TTLocalizer.MusicTcSz, 57]},
 3: {'create_a_toon.ogg': [TTLocalizer.MusicCreateAToon, 175],
     'tt_theme.ogg': [TTLocalizer.MusicTtTheme, 51]},
 4: {'TC_nbrhood.ogg': [TTLocalizer.MusicTcNbrhood, 59],
     'MG_TwoDGame.ogg': [TTLocalizer.MusicMgTwodgame, 60],
     'MG_Vine.ogg': [TTLocalizer.MusicMgVine, 32],
     'FF_safezone.ogg': [TTLocalizer.MusicFfSafezone, 47]},
 6: {'DD_SZ.ogg': [TTLocalizer.MusicDdSz, 33],
     'GS_SZ.ogg': [TTLocalizer.MusicGsSz, 60],
     'OZ_SZ.ogg': [TTLocalizer.MusicOzSz, 31],
     'GZ_SZ.ogg': [TTLocalizer.MusicGzSz, 59],
     'MM_SZ.ogg': [TTLocalizer.MusicMmSz, 76]},
 8: {'DG_SZ.ogg': [TTLocalizer.MusicDgSz, 48],
     'DL_SZ.ogg': [TTLocalizer.MusicDlSz, 33],
     'TB_SZ.ogg': [TTLocalizer.MusicTbSz, 54]},
 9: {'encntr_hall_of_fame.ogg': [TTLocalizer.MusicEncntrHallOfFame, 51],
     'encntr_head_suit_theme.ogg': [TTLocalizer.MusicEncntrHeadSuitTheme, 29]},
 11: {'LB_juryBG.ogg': [TTLocalizer.MusicLbJurybg, 30]},
 13: {'party_original_theme.ogg': [TTLocalizer.MusicPartyOriginalTheme, 56],
      'party_generic_theme_jazzy.ogg': [TTLocalizer.MusicPartyGenericThemeJazzy, 64]}}
PhaseToMusicData40 = {3.5: {'encntr_general_bg.ogg': [TTLocalizer.MusicEncntrGeneralBg, 30],
       'TC_SZ.ogg': [TTLocalizer.MusicTcSz, 57]},
 3: {'create_a_toon.ogg': [TTLocalizer.MusicCreateAToon, 175],
     'tt_theme.ogg': [TTLocalizer.MusicTtiTheme, 51]},
 4: {'minigame_race.ogg': [TTLocalizer.MusicMinigameRace, 77],
     'TC_nbrhood.ogg': [TTLocalizer.MusicTcNbrhood, 59],
     'MG_TwoDGame.ogg': [TTLocalizer.MusicMgTwodgame, 60],
     'MG_CogThief.ogg': [TTLocalizer.MusicMgCogthief, 61],
     'MG_Vine.ogg': [TTLocalizer.MusicMgVine, 32],
     'MG_IceGame.ogg': [TTLocalizer.MusicMgIcegame, 56],
     'FF_safezone.ogg': [TTLocalizer.MusicFfSafezone, 47]},
 6: {'DD_SZ.ogg': [TTLocalizer.MusicDdSz, 33],
     'GZ_PlayGolf.ogg': [TTLocalizer.MusicGzPlaygolf, 61],
     'GS_SZ.ogg': [TTLocalizer.MusicGsSz, 60],
     'OZ_SZ.ogg': [TTLocalizer.MusicOzSz, 31],
     'GS_Race_CC.ogg': [TTLocalizer.MusicGsRaceCc, 58],
     'GS_Race_SS.ogg': [TTLocalizer.MusicGsRaceSs, 61],
     'GS_Race_RR.ogg': [TTLocalizer.MusicGsRaceRr, 60],
     'GZ_SZ.ogg': [TTLocalizer.MusicGzSz, 59],
     'MM_SZ.ogg': [TTLocalizer.MusicMmSz, 76],
     'DD_nbrhood.ogg': [TTLocalizer.MusicDdNbrhood, 67],
     'GS_KartShop.ogg': [TTLocalizer.MusicGsKartshop, 32]},
 7: {'encntr_general_bg_indoor.ogg': [TTLocalizer.MusicEncntrGeneralBgIndoor, 31],
     'encntr_suit_winning_indoor.ogg': [TTLocalizer.MusicEncntrGeneralSuitWinningIndoor, 36]},
 8: {'DL_nbrhood.ogg': [TTLocalizer.MusicDlNbrhood, 30],
     'DG_SZ.ogg': [TTLocalizer.MusicDgSz, 48],
     'DL_SZ.ogg': [TTLocalizer.MusicDlSz, 33],
     'TB_SZ.ogg': [TTLocalizer.MusicTbSz, 54]},
 9: {'encntr_hall_of_fame.ogg': [TTLocalizer.MusicEncntrHallOfFame, 51],
     'CHQ_FACT_bg.ogg': [TTLocalizer.MusicChqFactBg, 50],
     'encntr_suit_winning.ogg': [TTLocalizer.MusicEncntrSuitWinning, 31],
     'encntr_head_suit_theme.ogg': [TTLocalizer.MusicEncntrHeadSuitTheme, 29]},
 11: {'LB_juryBG.ogg': [TTLocalizer.MusicLbJurybg, 30],
      'LB_courtyard.ogg': [TTLocalizer.MusicLbCourtyard, 32]},
 12: {'Bossbot_Factory_v1.ogg': [TTLocalizer.MusicBossbotFactoryV1, 30],
      'BossBot_CEO_v1.ogg': [TTLocalizer.MusicBossbotCeoV1, 31]},
 13: {'party_original_theme.ogg': [TTLocalizer.MusicPartyOriginalTheme, 56],
      'party_polka_dance.ogg': [TTLocalizer.MusicPartyPolkaDance, 63],
      'party_waltz_dance.ogg': [TTLocalizer.MusicPartyWaltzDance, 63],
      'party_generic_theme_jazzy.ogg': [TTLocalizer.MusicPartyGenericThemeJazzy, 64]}}

def countMusic():
    numMusic = 0
    for key in PhaseToMusicData:
        numMusic += len(PhaseToMusicData[key])

    print('PhaseToMusicData %d' % numMusic)
    numMusic = 0
    for key in PhaseToMusicData40:
        numMusic += len(PhaseToMusicData40[key])

    print('PhaseToMusicData40 %d' % numMusic)


def getMusicRepeatTimes(length, minLength = MUSIC_MIN_LENGTH_SECONDS):
    times = round(float(minLength) / length)
    if minLength <= 0 or times < 1.0:
        times = 1.0
    return times


def sanitizePhase(phase):
    if phase == int(phase):
        phase = int(phase)
    return phase


CANNON_TIMEOUT = 30
CANNON_MOVIE_LOAD = 1
CANNON_MOVIE_CLEAR = 2
CANNON_MOVIE_FORCE_EXIT = 3
CANNON_MOVIE_LANDED = 4
CannonJellyBeanReward = 2
CannonMaxTotalReward = 200
CatchMaxTotalReward = 1000
PartyCannonCollisions = {'clouds': ['cloudSphere-0'],
 'bounce': ['wall_collision',
            'discoBall_collision',
            'platform_left_collision',
            'platform_right_collision'],
 'trampoline_bounce': 'TrampolineCollision',
 'ground': ['floor_collision',
            'danceFloor_collision',
            'danceFloorRamp_collision',
            'hill_collision',
            'fence_floor'],
 'fence': ['dockTube1_collision',
           'dockTube2_collision',
           'dockTube2_collision',
           'dockTube2_collision',
           'palm_collision_01',
           'palm_collision_02',
           'palm_collision_03',
           'wall_1_collision',
           'wall_2_collision',
           'wall_3_collision',
           'wall_4_collision',
           'wall_5_collision',
           'wall_6_collision',
           'tree_collision',
           'partyDecoration_collision',
           'launchPad_railing_collision',
           'launchPad_floor_collision',
           'launchPad_collision',
           'launchPad_railing2_collision',
           'launchPad__rocket_collision',
           'launchPad_lever_collision',
           'launchPad_bridge_collision',
           'launchPad_sphere2_collision',
           'launchPad_sphere1_collision',
           'partyClock_collision',
           'sign_collision']}

def getCostOfParty(partyInfo):
    newCost = 0
    for activityBase in partyInfo.activityList:
        newCost += ActivityInformationDict[activityBase.activityId]['cost']

    for decorBase in partyInfo.decors:
        newCost += DecorationInformationDict[decorBase.decorId]['cost']

    return newCost
