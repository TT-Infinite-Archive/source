CICategoryFishingRod = 0
CICategoryNametag = 1
CICategoryParticleEffect = 2
CICategoryLaff = 3
CICategoryCheesyEffect = 4

# Fishing Rods
FishingRodTwig = 0
FishingRodBamboo = 1
FishingRodHardwood = 2
FishingRodSteel = 3
FishingRodGold = 4

# Nametag Styles
NametagDefault = 0
NametagPlain = 1
NametagShivering = 2
NametagWonky = 3
NametagFancy = 4
NametagSilly = 5
NametagZany = 6
NametagPractical = 7
NametagNautical = 8
NametagWhimsical = 9
NametagSpooky = 10
NametagAction = 11
NametagPoetic = 12
NametagBoardwalk = 13
NametagWestern = 14
NametagBasic = 15

# Particle Effects
ParticleEffectNone = 0
ParticleEffectHeart = 1

# Extra Laff
LaffPointFishing01 = 0
LaffPointFishing02 = 1
LaffPointFishing03 = 2
LaffPointFishing04 = 3
LaffPointFishing05 = 4
LaffPointFishing06 = 5
LaffPointFishing07 = 6
LaffPointGolfing01 = 7
LaffPointGolfing02 = 8
LaffPointGolfing03 = 9
LaffPointRacing01 = 10
LaffPointRacing02 = 11
LaffPointRacing03 = 12

# CheesyEffects
CheesyEffectNone = 0
CheesyEffectBigHead = 1
CheesyEffectSmallHead = 2
CheesyEffectBigLegs = 3
CheesyEffectSmallLegs = 4
CheesyEffectBigToon = 5
CheesyEffectSmallToon = 6
CheesyEffectFlatPortrait = 7
CheesyEffectFlatProfile = 8
CheesyEffectTransparent = 9
CheesyEffectNoColor = 10
CheesyEffectInvisible = 11
CheesyEffectPumpkin = 12
CheesyEffectBigWhite = 13
CheesyEffectSnowMan = 14
CheesyEffectGreenToon = 15
CheesyEffectTinyToon = 16
CheesyEffectGiantToon = 17
CheesyEffectGhost = 18
CheesyEffectGoofy = 19

CICategoryToItemIds = {
    CICategoryFishingRod: (FishingRodTwig, FishingRodBamboo, FishingRodHardwood, FishingRodSteel, FishingRodGold),
    CICategoryNametag: (
        NametagDefault,
        NametagPlain,
        NametagShivering,
        NametagWonky,
        NametagFancy,
        NametagSilly,
        NametagZany,
        NametagPractical,
        NametagNautical,
        NametagWhimsical,
        NametagSpooky,
        NametagAction,
        NametagPoetic,
        NametagBoardwalk,
        NametagWestern
    ),
    CICategoryParticleEffect: (ParticleEffectNone, ParticleEffectHeart),
    CICategoryLaff: (
        LaffPointFishing01,
        LaffPointFishing02,
        LaffPointFishing03,
        LaffPointFishing04,
        LaffPointFishing05,
        LaffPointFishing06,
        LaffPointFishing07,
        LaffPointGolfing01,
        LaffPointGolfing02,
        LaffPointGolfing03,
        LaffPointRacing01,
        LaffPointRacing02,
        LaffPointRacing03
    ),
    CICategoryCheesyEffect: (CheesyEffectNone, CheesyEffectGreenToon, CheesyEffectGoofy),
}

# Items you gain at the start of the game { category: [(id, equip), (id, equip)]
DefaultItems = {
    CICategoryFishingRod: (
        (FishingRodTwig, 1),
    ),
    CICategoryParticleEffect: (
        (ParticleEffectNone, 1),
    ),
    CICategoryNametag: (
        (NametagDefault, 1),
    ),
    CICategoryCheesyEffect: (
        (CheesyEffectNone, 1),
    ),
}
