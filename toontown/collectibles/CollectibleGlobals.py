from toontown.collectibles import CollectibleItem, CollectibleReward
from toontown.collectibles.CollectibleInventoryGlobals import *
from toontown.collectibles.StatGlobals import *

# Reward Definitions
CollectibleRewardValentines = CollectibleReward.CollectibleItemReward(
    id=0,
    name='Love Struck',
    category=CICategoryParticleEffect,
    itemId=ParticleEffectHeart
)
CollectibleRewardFishingLaff01 = CollectibleReward.HealthCollectibleItemReward(
    id=1,
    name='+1 Laff',
    category=CICategoryLaff,
    itemId=LaffPointFishing01,
    amount=1
)
CollectibleRewardFishingLaff02 = CollectibleReward.HealthCollectibleItemReward(
    id=2,
    name='+1 Laff',
    category=CICategoryLaff,
    itemId=LaffPointFishing02,
    amount=1
)
CollectibleRewardFishingLaff03 = CollectibleReward.HealthCollectibleItemReward(
    id=3,
    name='+1 Laff',
    category=CICategoryLaff,
    itemId=LaffPointFishing03,
    amount=1
)
CollectibleRewardFishingLaff04 = CollectibleReward.HealthCollectibleItemReward(
    id=4,
    name='+1 Laff',
    category=CICategoryLaff,
    itemId=LaffPointFishing04,
    amount=1
)
CollectibleRewardFishingLaff05 = CollectibleReward.HealthCollectibleItemReward(
    id=5,
    name='+1 Laff',
    category=CICategoryLaff,
    itemId=LaffPointFishing05,
    amount=1
)
CollectibleRewardFishingLaff06 = CollectibleReward.HealthCollectibleItemReward(
    id=6,
    name='+1 Laff',
    category=CICategoryLaff,
    itemId=LaffPointFishing06,
    amount=1
)
CollectibleRewardFishingLaff07 = CollectibleReward.HealthCollectibleItemReward(
    id=7,
    name='+1 Laff',
    category=CICategoryLaff,
    itemId=LaffPointFishing07,
    amount=1
)
CollectibleRewardGolfingLaff01 = CollectibleReward.HealthCollectibleItemReward(
    id=8,
    name='+1 Laff',
    category=CICategoryLaff,
    itemId=LaffPointGolfing01,
    amount=1
)
CollectibleRewardGolfingLaff02 = CollectibleReward.HealthCollectibleItemReward(
    id=9,
    name='+1 Laff',
    category=CICategoryLaff,
    itemId=LaffPointGolfing02,
    amount=1
)
CollectibleRewardGolfingLaff03 = CollectibleReward.HealthCollectibleItemReward(
    id=10,
    name='+1 Laff',
    category=CICategoryLaff,
    itemId=LaffPointGolfing03,
    amount=1
)
CollectibleRewardRacingLaff01 = CollectibleReward.HealthCollectibleItemReward(
    id=11,
    name='+1 Laff',
    category=CICategoryLaff,
    itemId=LaffPointRacing01,
    amount=1
)
CollectibleRewardRacingLaff02 = CollectibleReward.HealthCollectibleItemReward(
    id=12,
    name='+1 Laff',
    category=CICategoryLaff,
    itemId=LaffPointRacing02,
    amount=1
)
CollectibleRewardRacingLaff03 = CollectibleReward.HealthCollectibleItemReward(
    id=13,
    name='+1 Laff',
    category=CICategoryLaff,
    itemId=LaffPointRacing03,
    amount=1
)
CollectibleRewardPatricksDay = CollectibleReward.CollectibleItemReward(
    id=14,
    name='Green Toon',
    category=CICategoryCheesyEffect,
    itemId=CheesyEffectGreenToon
)
CollectibleRewardAprilFools = CollectibleReward.CollectibleItemReward(
    id=15,
    name='Gooby',
    category=CICategoryCheesyEffect,
    itemId=CheesyEffectGoofy
)
CollectibleRewardBigHead = CollectibleReward.CollectibleItemReward(
    id=16,
    name='Big Head',
    category=CICategoryCheesyEffect,
    itemId=CheesyEffectBigHead
)
CollectibleRewardSmallHead = CollectibleReward.CollectibleItemReward(
    id=17,
    name='Small Head',
    category=CICategoryCheesyEffect,
    itemId=CheesyEffectSmallHead
)
CollectibleRewardBigLegs = CollectibleReward.CollectibleItemReward(
    id=18,
    name='Big Legs',
    category=CICategoryCheesyEffect,
    itemId=CheesyEffectBigLegs
)
CollectibleRewardSmallLegs = CollectibleReward.CollectibleItemReward(
    id=19,
    name='Small Legs',
    category=CICategoryCheesyEffect,
    itemId=CheesyEffectSmallLegs
)
CollectibleRewardBigToon = CollectibleReward.CollectibleItemReward(
    id=20,
    name='Big Toon',
    category=CICategoryCheesyEffect,
    itemId=CheesyEffectBigToon
)
CollectibleRewardSmallToon = CollectibleReward.CollectibleItemReward(
    id=21,
    name='Small Toon',
    category=CICategoryCheesyEffect,
    itemId=CheesyEffectSmallToon
)
CollectibleRewardFlatPortrait = CollectibleReward.CollectibleItemReward(
    id=22,
    name='Flat Portrait',
    category=CICategoryCheesyEffect,
    itemId=CheesyEffectFlatPortrait
)

# Items
CollectibleFishing01 = CollectibleItem.CollectibleModelItem(
    name='Guppy',
    reward=CollectibleRewardFishingLaff01,
    category=StatCategoryFish,
    objective=FishNewSpecies,
    goal=10,
    desc='A trophy to display your fishing achievements. Grants health when obtained.',
    flavorText='%d/%d Unique Fish Species',
    filepath='phase_3.5/models/gui/fishingTrophy.bam',
    scale=0.02,
    pos=(0.0, 0.0, -0.075),
    color=(0.9, 0.6, 0.33, 1)
)
CollectibleFishing02 = CollectibleItem.CollectibleModelItem(
    name='Minnow',
    reward=CollectibleRewardFishingLaff02,
    category=StatCategoryFish,
    objective=FishNewSpecies,
    goal=20,
    desc='A trophy to display your fishing achievements. Grants health when obtained.',
    flavorText='%d/%d Unique Fish Species',
    filepath='phase_3.5/models/gui/fishingTrophy.bam',
    scale=0.02,
    pos=(0.0, 0.0, -0.075),
    color=(1, 0.7, 0.35, 1)
)
CollectibleFishing03 = CollectibleItem.CollectibleModelItem(
    name='Fish',
    reward=CollectibleRewardFishingLaff03,
    category=StatCategoryFish,
    objective=FishNewSpecies,
    goal=30,
    desc='A trophy to display your fishing achievements. Grants health when obtained.',
    flavorText='%d/%d Unique Fish Species',
    filepath='phase_3.5/models/gui/fishingTrophy.bam',
    scale=0.02,
    pos=(0.0, 0.0, -0.075),
    color=(1, 1, 1, 1)
)
CollectibleFishing04 = CollectibleItem.CollectibleModelItem(
    name='Flying Fish',
    reward=CollectibleRewardFishingLaff04,
    category=StatCategoryFish,
    objective=FishNewSpecies,
    goal=40,
    desc='A trophy to display your fishing achievements. Grants health when obtained.',
    flavorText='%d/%d Unique Fish Species',
    filepath='phase_3.5/models/gui/fishingTrophy.bam',
    scale=0.02,
    pos=(0.0, 0.0, -0.075),
    color=(0.95, 0.95, 1, 1)
)
CollectibleFishing05 = CollectibleItem.CollectibleModelItem(
    name='Shark',
    reward=CollectibleRewardFishingLaff05,
    category=StatCategoryFish,
    objective=FishNewSpecies,
    goal=50,
    desc='A trophy to display your fishing achievements. Grants health when obtained.',
    flavorText='%d/%d Unique Fish Species',
    filepath='phase_3.5/models/gui/fishingTrophy.bam',
    scale=0.02,
    pos=(0.0, 0.0, -0.075),
    color=(1, 0.9, 0.2, 1)
)
CollectibleFishing06 = CollectibleItem.CollectibleModelItem(
    name='Swordfish',
    reward=CollectibleRewardFishingLaff06,
    category=StatCategoryFish,
    objective=FishNewSpecies,
    goal=60,
    desc='A trophy to display your fishing achievements. Grants health when obtained.',
    flavorText='%d/%d Unique Fish Species',
    filepath='phase_3.5/models/gui/fishingTrophy.bam',
    scale=0.02,
    pos=(0.0, 0.0, -0.075),
    color=(1, 0.95, 0.1, 1)
)
CollectibleFishing07 = CollectibleItem.CollectibleModelItem(
    name='Killer Whale',
    reward=CollectibleRewardFishingLaff07,
    category=StatCategoryFish,
    objective=FishNewSpecies,
    goal=70,
    desc='A trophy to display your fishing achievements. Grants health when obtained.',
    flavorText='%d/%d Unique Fish Species',
    filepath='phase_3.5/models/gui/fishingTrophy.bam',
    scale=0.02,
    pos=(0.0, 0.0, -0.075),
    color=(0.9, 0.9, 1, 1)
)

# Golf
CollectibleGolf01 = CollectibleItem.CollectibleModelItem(
    name='Bronze Trophy',
    reward=CollectibleRewardGolfingLaff01,
    category=StatCategoryGolf,
    objective=GolfTrophy,
    goal=10,
    desc='A trophy to display your golfing achievements. Grants health when obtained.',
    flavorText='%d/%d Golf Trophies',
    filepath='phase_6/models/golf/golfTrophy.bam',
    scale=0.02,
    pos=(0.0, 0.0, -0.075),
    color=(0.9, 0.6, 0.33, 1)
)
CollectibleGolf02 = CollectibleItem.CollectibleModelItem(
    name='Silver Trophy',
    reward=CollectibleRewardGolfingLaff02,
    category=StatCategoryGolf,
    objective=GolfTrophy,
    goal=20,
    desc='A trophy to display your golfing achievements. Grants health when obtained.',
    flavorText='%d/%d Golf Trophies',
    filepath='phase_6/models/golf/golfTrophy.bam',
    scale=0.02,
    pos=(0.0, 0.0, -0.075),
    color=(0.9, 0.9, 1, 1)
)
CollectibleGolf03 = CollectibleItem.CollectibleModelItem(
    name='Gold Trophy',
    reward=CollectibleRewardGolfingLaff03,
    category=StatCategoryGolf,
    objective=GolfTrophy,
    goal=30,
    desc='A trophy to display your golfing achievements. Grants health when obtained.',
    flavorText='%d/%d Golf Trophies',
    filepath='phase_6/models/golf/golfTrophy.bam',
    scale=0.02,
    pos=(0.0, 0.0, -0.075),
    color=(1, 0.9, 0.2, 1)
)

# Racing
CollectibleRacing01 = CollectibleItem.CollectibleModelItem(
    name='Bronze Trophy',
    reward=CollectibleRewardRacingLaff01,
    category=StatCategoryRace,
    objective=RacingTrophy,
    goal=10,
    desc='A trophy to display your racing achievements. Grants laff when obtained.',
    flavorText='%d/%d Racing Trophies',
    filepath='phase_6/models/gui/racingTrophy.bam',
    scale=0.02,
    pos=(0.0, 0.0, -0.075),
    color=(0.9, 0.6, 0.33, 1)
)
CollectibleRacing02 = CollectibleItem.CollectibleModelItem(
    name='Silver Trophy',
    reward=CollectibleRewardRacingLaff02,
    category=StatCategoryRace,
    objective=RacingTrophy,
    goal=20,
    desc='A trophy to display your racing achievements. Grants laff when obtained.',
    flavorText='%d/%d Racing Trophies',
    filepath='phase_6/models/gui/racingTrophy.bam',
    scale=0.02,
    pos=(0.0, 0.0, -0.075),
    color=(0.9, 0.9, 1, 1)
)
CollectibleRacing03 = CollectibleItem.CollectibleModelItem(
    name='Gold Trophy',
    reward=CollectibleRewardRacingLaff03,
    category=StatCategoryRace,
    objective=RacingTrophy,
    goal=30,
    desc='A trophy to display your racing achievements. Grants laff when obtained.',
    flavorText='%d/%d Racing Trophies',
    filepath='phase_6/models/gui/racingTrophy.bam',
    scale=0.02,
    pos=(0.0, 0.0, -0.075),
    color=(1, 0.9, 0.2, 1)
)

# Seasonal
CollectibleSeasonal01 = CollectibleItem.CollectibleImageItem(
    name='Love Struck',
    reward=CollectibleRewardValentines,
    category=StatCategoryCog,
    objective=CogValentines,
    goal=200,
    desc='Participate in the ValenToon\'s 2016 event by taking down love struck cogs!',
    flavorText='%d/%d Love Struck Cogs Destroyed',
    filepath='phase_3.5/maps/love_struck.png',
    scale=0.001
)
CollectibleSeasonal02 = CollectibleItem.CollectibleImageItem(
    name='Treasure Hunt',
    reward=CollectibleRewardPatricksDay,
    category=StatCategoryTreasure,
    objective=TreasurePatrickDay,
    goal=5,
    desc='Participate in the Saint Patrick\'s 2016 event by collecting four leaf clovers!',
    flavorText='%d/%d Four Leaf Clovers Found',
    filepath='phase_3.5/maps/st_patricks_day.png',
    scale=0.001
)

# Categories
CCFishingId = 0
CCGolfId = 1
CCRacingId = 2
CCSeasonalId = 3

CCGolf = CollectibleItem.CollectibleCategory(
    CCGolfId,
    'Golf',
    {
        0: CollectibleGolf01,
        1: CollectibleGolf02,
        2: CollectibleGolf03
    }

)
CCFishing = CollectibleItem.CollectibleCategory(
    CCFishingId,
    'Fishing',
    {
        0: CollectibleFishing01,
        1: CollectibleFishing02,
        2: CollectibleFishing03,
        3: CollectibleFishing04,
        4: CollectibleFishing05,
        5: CollectibleFishing06,
        6: CollectibleFishing07
    }
)
CCRacing = CollectibleItem.CollectibleCategory(
    CCRacingId,
    'Racing',
    {
        0: CollectibleRacing01,
        1: CollectibleRacing02,
        2: CollectibleRacing03
    }
)
# Hide this category until we are ready to introduce seasonal collectibles
"""
CCSeasonal = CollectibleItem.CollectibleCategory(
    CCSeasonalId,
    'Seasonal',
    {
        0: CollectibleSeasonal01,
        1: CollectibleSeasonal02
    }
)
"""
CollectibleCategories = {
    CCGolfId: CCGolf,
    CCFishingId: CCFishing,
    CCRacingId: CCRacing,
    # CCSeasonalId: CCSeasonal
}

# Un-lockable Item Definitions

# Fishing Rods
CollectibleFishingRod01 = CollectibleItem.FishingRodItem(
    name='Twig Rod',
    category=CICategoryFishingRod,
    id=FishingRodTwig,
    desc='A weak fishing rod; awarded to all Toons of Toontown when they are created.',
    flavorText='Costs 1 jellybean to use',
    filepath='phase_4/models/props/pole_treebranch-mod',
    scale=0.03,
    pos=(0.05, 0.0, -0.075),
    color=(1.0, 1.0, 1.0, 1.0)
)
CollectibleFishingRod02 = CollectibleItem.FishingRodItem(
    name='Bamboo Rod',
    category=CICategoryFishingRod,
    id=FishingRodBamboo,
    desc='An average fishing rod; catches larger fish than the Twig Rod.',
    flavorText='Costs 2 jellybeans to use',
    filepath='phase_4/models/props/pole_bamboo-mod',
    scale=0.03,
    pos=(0.05, 0.0, -0.075),
    color=(1.0, 1.0, 1.0, 1.0)
)
CollectibleFishingRod03 = CollectibleItem.FishingRodItem(
    name='Hardwood Rod',
    category=CICategoryFishingRod,
    id=FishingRodHardwood,
    desc='A sturdy fishing rod; catches larger fish than the Bamboo Rod',
    flavorText='Costs 3 jellybeans to use',
    filepath='phase_4/models/props/pole_wood-mod',
    scale=0.03,
    pos=(0.05, 0.0, -0.075),
    color=(1.0, 1.0, 1.0, 1.0)
)
CollectibleFishingRod04 = CollectibleItem.FishingRodItem(
    name='Steel Rod',
    category=CICategoryFishingRod,
    id=FishingRodSteel,
    desc='A very sturdy fishing rod; catches larger fish than the Hardwood Rod.',
    flavorText='Costs 4 jellybeans to use',
    filepath='phase_4/models/props/pole_steel-mod',
    scale=0.03,
    pos=(0.05, 0.0, -0.075),
    color=(1.0, 1.0, 1.0, 1.0)
)
CollectibleFishingRod05 = CollectibleItem.FishingRodItem(
    name='Gold Rod',
    category=CICategoryFishingRod,
    id=FishingRodGold,
    desc='The strongest fishing rod; catches the largest fish in Toontown.',
    flavorText='Costs 5 jellybeans to use',
    filepath='phase_4/models/props/pole_gold-mod',
    scale=0.03,
    pos=(0.05, 0.0, -0.075),
    color=(1.0, 1.0, 1.0, 1.0)
)

# Name-tag Styles
CollectibleNametag01 = CollectibleItem.NametagItem(
    name='Default',
    category=CICategoryNametag,
    id=NametagDefault,
    desc='Default nametag style.',
    flavorText='Awarded when your Toon is created',
    filepath='phase_3/models/fonts/ImpressBT.ttf',
    scale=0.05,
    color=(0.0, 0.0, 0.0, 1.0),
    pos=(0.0, 0.0, -0.01)
)
CollectibleNametag02 = CollectibleItem.NametagItem(
    name='Plain',
    category=CICategoryNametag,
    id=NametagPlain,
    desc='Plain nametag style.',
    flavorText='Bought in the cattlelog',
    filepath='phase_3/models/fonts/AnimGothic.bam',
    scale=0.05,
    color=(0.0, 0.0, 0.0, 1.0),
    pos=(0.0, 0.0, -0.01)
)
CollectibleNametag03 = CollectibleItem.NametagItem(
    name='Shivering',
    category=CICategoryNametag,
    id=NametagShivering,
    desc='Shivering nametag style.',
    flavorText='Bought in the cattlelog',
    filepath='phase_3/models/fonts/Aftershock.bam',
    scale=0.05,
    color=(0.0, 0.0, 0.0, 1.0),
    pos=(0.0, 0.0, -0.01)
)
CollectibleNametag04 = CollectibleItem.NametagItem(
    name='Wonky',
    category=CICategoryNametag,
    id=NametagWonky,
    desc='Wonky nametag style.',
    flavorText='Bought in the cattlelog',
    filepath='phase_3/models/fonts/JiggeryPokery.bam',
    scale=0.05,
    color=(0.0, 0.0, 0.0, 1.0),
    pos=(0.0, 0.0, -0.01)
)
CollectibleNametag05 = CollectibleItem.NametagItem(
    name='Fancy',
    category=CICategoryNametag,
    id=NametagFancy,
    desc='Fancy nametag style.',
    flavorText='Bought in the cattlelog',
    filepath='phase_3/models/fonts/Ironwork.bam',
    scale=0.05,
    color=(0.0, 0.0, 0.0, 1.0),
    pos=(0.0, 0.0, -0.01)
)
CollectibleNametag06 = CollectibleItem.NametagItem(
    name='Silly',
    category=CICategoryNametag,
    id=NametagSilly,
    desc='Silly nametag style.',
    flavorText='Bought in the cattlelog',
    filepath='phase_3/models/fonts/HastyPudding.bam',
    scale=0.05,
    color=(0.0, 0.0, 0.0, 1.0),
    pos=(0.0, 0.0, -0.01)
)
CollectibleNametag07 = CollectibleItem.NametagItem(
    name='Zany',
    category=CICategoryNametag,
    id=NametagZany,
    desc='Zany nametag style.',
    flavorText='Bought in the cattlelog',
    filepath='phase_3/models/fonts/Comedy.bam',
    scale=0.05,
    color=(0.0, 0.0, 0.0, 1.0),
    pos=(0.0, 0.0, -0.01)
)
CollectibleNametag08 = CollectibleItem.NametagItem(
    name='Practical',
    category=CICategoryNametag,
    id=NametagPractical,
    desc='Practical nametag style.',
    flavorText='Bought in the cattlelog',
    filepath='phase_3/models/fonts/Humanist.bam',
    scale=0.04,
    color=(0.0, 0.0, 0.0, 1.0),
    pos=(0.0, 0.0, -0.01)
)
CollectibleNametag09 = CollectibleItem.NametagItem(
    name='Nautical',
    category=CICategoryNametag,
    id=NametagNautical,
    desc='Nautical nametag style.',
    flavorText='Bought in the cattlelog',
    filepath='phase_3/models/fonts/Portago.bam',
    scale=0.05,
    color=(0.0, 0.0, 0.0, 1.0),
    pos=(0.0, 0.0, -0.01)
)
CollectibleNametag10 = CollectibleItem.NametagItem(
    name='Whimsical',
    category=CICategoryNametag,
    id=NametagWhimsical,
    desc='Whimsical nametag style.',
    flavorText='Bought in the cattlelog',
    filepath='phase_3/models/fonts/Musicals.bam',
    scale=0.045,
    color=(0.0, 0.0, 0.0, 1.0),
    pos=(0.0, 0.0, -0.01)
)
CollectibleNametag11 = CollectibleItem.NametagItem(
    name='Spooky',
    category=CICategoryNametag,
    id=NametagSpooky,
    desc='Spooky nametag style. Can only be found during halloween.',
    flavorText='Bought in the cattlelog',
    filepath='phase_3/models/fonts/Scurlock.bam',
    scale=0.05,
    color=(0.0, 0.0, 0.0, 1.0),
    pos=(0.0, 0.0, -0.01)
)
CollectibleNametag12 = CollectibleItem.NametagItem(
    name='Action',
    category=CICategoryNametag,
    id=NametagAction,
    desc='Action nametag style.',
    flavorText='Bought in the cattlelog',
    filepath='phase_3/models/fonts/Danger.bam',
    scale=0.05,
    color=(0.0, 0.0, 0.0, 1.0),
    pos=(0.0, 0.0, -0.01)
)
CollectibleNametag13 = CollectibleItem.NametagItem(
    name='Poetic',
    category=CICategoryNametag,
    id=NametagPoetic,
    desc='Poetic nametag style.',
    flavorText='Bought in the cattlelog',
    filepath='phase_3/models/fonts/Alie.bam',
    scale=0.05,
    color=(0.0, 0.0, 0.0, 1.0),
    pos=(0.0, 0.0, -0.01)
)
CollectibleNametag14 = CollectibleItem.NametagItem(
    name='Boardwalk',
    category=CICategoryNametag,
    id=NametagBoardwalk,
    desc='Boardwalk nametag style.',
    flavorText='Bought in the cattlelog',
    filepath='phase_3/models/fonts/OysterBar.bam',
    scale=0.04,
    color=(0.0, 0.0, 0.0, 1.0),
    pos=(0.0, 0.0, -0.01)
)
CollectibleNametag15 = CollectibleItem.NametagItem(
    name='Western',
    category=CICategoryNametag,
    id=NametagWestern,
    desc='Western nametag style.',
    flavorText='Bought in the cattlelog',
    filepath='phase_3/models/fonts/RedDogSaloon.bam',
    scale=0.045,
    color=(0.0, 0.0, 0.0, 1.0),
    pos=(0.0, 0.0, -0.01)
)

# Particle Effects
CollectibleParticleEffect01 = CollectibleItem.ParticleEffectItem(
    name='Hidden',
    category=CICategoryParticleEffect,
    id=ParticleEffectNone,
    particleName='',
    desc='Equip this to hide your particle effect.',
    flavorText='Awarded when your Toon is created',
)
CollectibleParticleEffect02 = CollectibleItem.ParticleEffectItem(
    name='Floating Hearts',
    category=CICategoryParticleEffect,
    id=ParticleEffectHeart,
    particleName='floatingHearts',
    desc='Equip this to show your love for Toons all around.',
    flavorText='Awarded via the Valentoons Event',
    scale=0.05,
    pos=(0.0, 0.0, -2.025)
)

# Laff Boosters
CollectibleLaffBoost01 = CollectibleItem.ImageItem(
    name='Fishing Laff I',
    category=CICategoryLaff,
    id=LaffPointFishing01,
    desc='Laff boost obtained by collecting unique fish. \nUn-equippable',
    flavorText='+1 Laff',
    filepath='phase_3.5/maps/plus_one.png',
    scale=0.001
)
CollectibleLaffBoost02 = CollectibleItem.ImageItem(
    name='Fishing Laff II',
    category=CICategoryLaff,
    id=LaffPointFishing02,
    desc='Laff boost obtained by collecting unique fish. \nUn-equippable',
    flavorText='+1 Laff',
    filepath='phase_3.5/maps/plus_one.png',
    scale=0.001
)
CollectibleLaffBoost03 = CollectibleItem.ImageItem(
    name='Fishing Laff III',
    category=CICategoryLaff,
    id=LaffPointFishing03,
    desc='Laff boost obtained by collecting unique fish. \nUn-equippable',
    flavorText='+1 Laff',
    filepath='phase_3.5/maps/plus_one.png',
    scale=0.001
)
CollectibleLaffBoost04 = CollectibleItem.ImageItem(
    name='Fishing Laff IV',
    category=CICategoryLaff,
    id=LaffPointFishing04,
    desc='Laff boost obtained by collecting unique fish. \nUn-equippable',
    flavorText='+1 Laff',
    filepath='phase_3.5/maps/plus_one.png',
    scale=0.001
)
CollectibleLaffBoost05 = CollectibleItem.ImageItem(
    name='Fishing Laff V',
    category=CICategoryLaff,
    id=LaffPointFishing05,
    desc='Laff boost obtained by collecting unique fish. \nUn-equippable',
    flavorText='+1 Laff',
    filepath='phase_3.5/maps/plus_one.png',
    scale=0.001
)
CollectibleLaffBoost06 = CollectibleItem.ImageItem(
    name='Fishing Laff VI',
    category=CICategoryLaff,
    id=LaffPointFishing06,
    desc='Laff boost obtained by collecting unique fish. \nUn-equippable',
    flavorText='+1 Laff',
    filepath='phase_3.5/maps/plus_one.png',
    scale=0.001
)
CollectibleLaffBoost07 = CollectibleItem.ImageItem(
    name='Fishing Laff VII',
    category=CICategoryLaff,
    id=LaffPointFishing07,
    desc='Laff boost obtained by collecting unique fish. \nUn-equippable',
    flavorText='+1 Laff',
    filepath='phase_3.5/maps/plus_one.png',
    scale=0.001
)
CollectibleLaffBoost08 = CollectibleItem.ImageItem(
    name='Golfing Laff I',
    category=CICategoryLaff,
    id=LaffPointGolfing01,
    desc='Laff boost obtained by collecting Golf trophies. \nUn-equippable',
    flavorText='+1 Laff',
    filepath='phase_3.5/maps/plus_one.png',
    scale=0.001
)
CollectibleLaffBoost09 = CollectibleItem.ImageItem(
    name='Golfing Laff II',
    category=CICategoryLaff,
    id=LaffPointGolfing02,
    desc='Laff boost obtained by collecting Golf trophies. \nUn-equippable',
    flavorText='+1 Laff',
    filepath='phase_3.5/maps/plus_one.png',
    scale=0.001
)
CollectibleLaffBoost10 = CollectibleItem.ImageItem(
    name='Golfing Laff III',
    category=CICategoryLaff,
    id=LaffPointGolfing03,
    desc='Laff boost obtained by collecting Golf trophies. \nUn-equippable',
    flavorText='+1 Laff',
    filepath='phase_3.5/maps/plus_one.png',
    scale=0.001
)
CollectibleLaffBoost11 = CollectibleItem.ImageItem(
    name='Racing Laff I',
    category=CICategoryLaff,
    id=LaffPointRacing01,
    desc='Laff boost obtained by collecting Racing trophies. \nUn-equippable',
    flavorText='+1 Laff',
    filepath='phase_3.5/maps/plus_one.png',
    scale=0.001
)
CollectibleLaffBoost12 = CollectibleItem.ImageItem(
    name='Racing Laff II',
    category=CICategoryLaff,
    id=LaffPointRacing02,
    desc='Laff boost obtained by collecting Racing trophies. \nUn-equippable',
    flavorText='+1 Laff',
    filepath='phase_3.5/maps/plus_one.png',
    scale=0.001
)
CollectibleLaffBoost13 = CollectibleItem.ImageItem(
    name='Racing Laff III',
    category=CICategoryLaff,
    id=LaffPointRacing03,
    desc='Laff boost obtained by collecting Racing trophies. \nUn-equippable',
    flavorText='+1 Laff',
    filepath='phase_3.5/maps/plus_one.png',
    scale=0.001
)

# CheesyEffects
CollectibleCheesyEffectNone = CollectibleItem.CheesyEffectItem(
    name='Normal Effect',
    category=CICategoryCheesyEffect,
    id=CheesyEffectNone,
    desc='Equip this to hide your current cheesy effect.',
    flavorText='Acquired when your Toon is created',
    filepath='phase_3.5/maps/default_ce.png',
    scale=0.001,
)
CollectibleCheesyEffectGreenToon = CollectibleItem.CheesyEffectItem(
    name='Green Toon',
    category=CICategoryCheesyEffect,
    id=CheesyEffectGreenToon,
    desc='Equip this to make your entire Toon green!',
    flavorText='Acquired via the Saint Patrick Event',
    filepath='phase_3.5/maps/green_toon.png',
    scale=0.001,
)
CollectibleCheesyEffectGoofy = CollectibleItem.CheesyEffectItem(
    name='Gooby',
    category=CICategoryCheesyEffect,
    id=CheesyEffectGoofy,
    desc='Equip this to replace your Toon\'s body with Gooby\'s!',
    flavorText='Acquired from Crates of Amusement',
    filepath='phase_3.5/maps/gooby_ce_icon.png',
    scale=0.001,
)
CollectibleCheesyEffectBigHead = CollectibleItem.CheesyEffectItem(
    name='Big Head',
    category=CICategoryCheesyEffect,
    id=CheesyEffectBigHead,
    desc='Equip this to make your Toon\'s head big!',
    flavorText='Acquired from Crates of Amusement',
    filepath='phase_3.5/maps/big_head_ce_icon.png',
    scale=0.001,
)
CollectibleCheesyEffectSmallHead = CollectibleItem.CheesyEffectItem(
    name='Small Head',
    category=CICategoryCheesyEffect,
    id=CheesyEffectSmallHead,
    desc='Equip this to make your Toon\'s head small!',
    flavorText='Acquired from Crates of Amusement',
    filepath='phase_3.5/maps/small_head_ce_icon.png',
    scale=0.001,
)
CollectibleCheesyEffectBigLegs = CollectibleItem.CheesyEffectItem(
    name='Big Legs',
    category=CICategoryCheesyEffect,
    id=CheesyEffectBigLegs,
    desc='Equip this to make your Toon\'s legs big!',
    flavorText='Acquired from Crates of Amusement',
    filepath='phase_3.5/maps/big_legs_ce_icon.png',
    scale=0.001,
)
CollectibleCheesyEffectSmallLegs = CollectibleItem.CheesyEffectItem(
    name='Small Legs',
    category=CICategoryCheesyEffect,
    id=CheesyEffectSmallLegs,
    desc='Equip this to make your Toon\'s legs small!',
    flavorText='Acquired from Crates of Amusement',
    filepath='phase_3.5/maps/small_legs_ce_icon.png',
    scale=0.001,
)
CollectibleCheesyEffectBigToon = CollectibleItem.CheesyEffectItem(
    name='Big Toon',
    category=CICategoryCheesyEffect,
    id=CheesyEffectBigToon,
    desc='Equip this to make your Toon big!',
    flavorText='Acquired from Crates of Amusement',
    filepath='phase_3.5/maps/big_toon_ce_icon.png',
    scale=0.001,
)
CollectibleCheesyEffectSmallToon = CollectibleItem.CheesyEffectItem(
    name='Small Toon',
    category=CICategoryCheesyEffect,
    id=CheesyEffectSmallToon,
    desc='Equip this to make your Toon small!',
    flavorText='Acquired from Crates of Amusement',
    filepath='phase_3.5/maps/small_toon_ce_icon.png',
    scale=0.001,
)
CollectibleCheesyEffectFlatPortrait = CollectibleItem.CheesyEffectItem(
    name='Flat Portrait',
    category=CICategoryCheesyEffect,
    id=CheesyEffectFlatPortrait,
    desc='Equip this to make your Toon flat!',
    flavorText='Acquired from Crates of Amusement',
    filepath='phase_3.5/maps/flat_portrait_ce_icon.png',
    scale=0.001,
)

CIFishingRod = CollectibleItem.CollectibleCategory(
    CICategoryFishingRod,
    'Fishing Rod',
    {
        FishingRodTwig: CollectibleFishingRod01,
        FishingRodBamboo: CollectibleFishingRod02,
        FishingRodHardwood: CollectibleFishingRod03,
        FishingRodSteel: CollectibleFishingRod04,
        FishingRodGold: CollectibleFishingRod05
    }
)
CINametag = CollectibleItem.CollectibleCategory(
    CICategoryNametag,
    'Nametag Style',
    {
        NametagDefault: CollectibleNametag01,
        NametagPlain: CollectibleNametag02,
        NametagShivering: CollectibleNametag03,
        NametagWonky: CollectibleNametag04,
        NametagFancy: CollectibleNametag05,
        NametagSilly: CollectibleNametag06,
        NametagZany: CollectibleNametag07,
        NametagPractical: CollectibleNametag08,
        NametagNautical: CollectibleNametag09,
        NametagWhimsical: CollectibleNametag10,
        NametagSpooky: CollectibleNametag11,
        NametagAction: CollectibleNametag12,
        NametagPoetic: CollectibleNametag13,
        NametagBoardwalk: CollectibleNametag14,
        NametagWestern: CollectibleNametag15
}
)
CIParticleEffect = CollectibleItem.CollectibleCategory(
    CICategoryParticleEffect,
    'Particle Effect',
    {
        ParticleEffectNone: CollectibleParticleEffect01,
        ParticleEffectHeart: CollectibleParticleEffect02
    }
)
CILaff = CollectibleItem.CollectibleCategory(
    CICategoryLaff,
    'Laff Boost',
    {
        LaffPointFishing01: CollectibleLaffBoost01,
        LaffPointFishing02: CollectibleLaffBoost02,
        LaffPointFishing03: CollectibleLaffBoost03,
        LaffPointFishing04: CollectibleLaffBoost04,
        LaffPointFishing05: CollectibleLaffBoost05,
        LaffPointFishing06: CollectibleLaffBoost06,
        LaffPointFishing07: CollectibleLaffBoost07,
        LaffPointGolfing01: CollectibleLaffBoost08,
        LaffPointGolfing02: CollectibleLaffBoost09,
        LaffPointGolfing03: CollectibleLaffBoost10,
        LaffPointRacing01: CollectibleLaffBoost11,
        LaffPointRacing02: CollectibleLaffBoost12,
        LaffPointRacing03: CollectibleLaffBoost13
    }
)
CICheesyEffect = CollectibleItem.CollectibleCategory(
    CICategoryCheesyEffect,
    'Cheesy Effect',
    {
        CheesyEffectNone: CollectibleCheesyEffectNone,
        CheesyEffectBigHead: CollectibleCheesyEffectBigHead,
        CheesyEffectSmallHead: CollectibleCheesyEffectSmallHead,
        CheesyEffectBigLegs: CollectibleCheesyEffectBigLegs,
        CheesyEffectSmallLegs: CollectibleCheesyEffectSmallLegs,
        CheesyEffectBigToon: CollectibleCheesyEffectBigToon,
        CheesyEffectSmallToon: CollectibleCheesyEffectSmallToon,
        CheesyEffectFlatPortrait: CollectibleCheesyEffectFlatPortrait,
        CheesyEffectGreenToon: CollectibleCheesyEffectGreenToon,
        CheesyEffectGoofy: CollectibleCheesyEffectGoofy
    }
)
CollectibleItems = {
    CICategoryFishingRod: CIFishingRod,
    CICategoryNametag: CINametag,
    CICategoryParticleEffect: CIParticleEffect,
    CICategoryLaff: CILaff,
    CICategoryCheesyEffect: CICheesyEffect
}


def getItem(category, itemId):
    return CollectibleItems[category].items[itemId]


def getCollectible(category, collectibleId):
    return CollectibleCategories[category].items[collectibleId]


def getCollectiblesForStat(category, objective):
    collectibles = []
    for otherCategory in CollectibleCategories:
        for itemKey in CollectibleCategories[otherCategory].items:
            item = CollectibleCategories[otherCategory].items[itemKey]
            if item.category == category and item.id == objective:
                collectibles.append(item)
    return collectibles
