StatCategoryFish = 0
StatCategoryGolf = 1
StatCategoryRace = 2
StatCategoryCog = 3
StatCategoryTreasure = 4

# StatCategoryFish
FishAny = 0
FishNewSpecies = 1
FishWeight = 2

# StatCategoryGolf
GolfAny = 0
GolfTrophy = 1
GolfEasy = 2
GolfMedium = 3
GolfHard = 4

# StatCategoryRace
RacingAny = 0
RacingTrophy = 1
RacingSpeedwayAny = 2
RacingRuralAny = 3
RacingUrbanAny = 4
RacingSpeedwayWon = 5
RacingRuralWon = 6
RacingUrbanWon = 7


# StatCategoryCog
CogAny = 0
CogSellbot = 1
CogCashbot = 2
CogLawbot = 3
CogBossbot = 4
CogSkelecog = 5
CogV2 = 6
CogValentines = 7
CogVirtual = 8

# StatCategoryTreasure
TreasureAny = 0
TreasurePatrickDay = 1

CogDeptToObjective = {
    'c': CogBossbot,
    'l': CogLawbot,
    'm': CogCashbot,
    's': CogSellbot
}

CollectibleCategoryToObjective = {
    StatCategoryFish: (FishAny, FishNewSpecies, FishWeight),
    StatCategoryGolf: (GolfAny, GolfTrophy, GolfEasy, GolfMedium, GolfHard),
    StatCategoryRace: (RacingAny, RacingTrophy),
    StatCategoryCog: (
        CogAny,
        CogSellbot,
        CogCashbot,
        CogLawbot,
        CogBossbot,
        CogSkelecog,
        CogV2,
        CogValentines,
        CogVirtual
    ),
    StatCategoryTreasure: (TreasureAny, TreasurePatrickDay)
}
