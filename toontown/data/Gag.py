from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.showbase.DirectObject import DirectObject

from toontown.data import Missile, IconGlobals, Model, Track, EffectGlobals
from toontown.data.Effect import DamageEffect
from toontown.toonbase import ColorGlobals, TTLocalizer


class Gag(DirectObject):
    notify = directNotify.newCategory('Gag')
    TargetNone = 0
    TargetSingleEnemy = 1
    TargetSingleAlly = 2
    TargetEnemies = 3
    TargetAllies = 4
    TargetSelf = 5
    TargetSelfAndAllies = 6

    RarityCommon = 0
    RarityRare = 1
    RarityEpic = 2
    RarityLegendary = 3

    def __init__(self, uid, name, effectId, targetType, track, rarity, level, chance=1.0):
        DirectObject.__init__(self)
        self.uid = uid
        self.name = name
        self.effectId = effectId
        self.effect = EffectGlobals.getEffect(effectId)
        self.targetType = targetType
        self.track = track
        self.chance = chance
        self.rarity = rarity
        self.level = level

    def __str__(self):
        return 'Gag-%s' % self.name

    def toList(self):
        return [
            self.uid
        ]

    @property
    def description(self):
        typeToString = {
            self.TargetNone: '',
            self.TargetSingleEnemy: 'Affects: One Cog',
            self.TargetSingleAlly: 'Affects: One Toon',
            self.TargetEnemies: 'Affects: All Cogs',
            self.TargetAllies: 'Affects: Other Toons',
            self.TargetSelf: 'Affects: Yourself',
            self.TargetSelfAndAllies: 'Affects: All Toons'
        }
        string = self.effect.description + '\n'
        string += typeToString[self.targetType] + '\n\n'
        if self.chance < 1.0:
            string += 'Has a %s%% chance to miss' % (100 - int(self.chance * 100)) + '\n'
        return string

    @property
    def rarityColor(self):
        rarityToColor = {
            Gag.RarityCommon: ColorGlobals.CDarkGray,
            Gag.RarityRare: ColorGlobals.CEmerald,
            Gag.RarityEpic: ColorGlobals.CDarkViolet,
            Gag.RarityLegendary: ColorGlobals.COrange
        }
        return rarityToColor[self.rarity]

    @property
    def displayObject(self):
        return GagToIcon.get(self.uid, None)

    @property
    def icon(self):
        return self.displayObject.icon

    @property
    def glow(self):
        glow = IconGlobals.getIcon(IconGlobals.ICON_GLOW).icon
        color = self.rarityColor
        color[3] = 0.75
        glow.setColorScale(color)
        return glow

    def requiresTarget(self):
        return self.targetType in (self.TargetSingleEnemy, self.TargetSingleAlly)

    def getTargets(self, battle, targetId):
        # Returns the targets from the battle given
        targets = []
        if self.targetType == self.TargetSingleEnemy:
            targets.append(battle.findSuit(targetId))
        elif self.targetType == self.TargetSingleAlly:
            targets.append(battle.findToon(targetId))
        else:
            self.notify.warning('Getting targets for target type %d not yet implemented' % self.targetType)
        return targets

    def getDamage(self):
        if isinstance(self.effect, DamageEffect):
            return self.effect.amount
        else:
            return 0


class ThrowGag(Gag):
    def __init__(self, uid, name, effectId, targetType, rarity, level, missile, chance=1.0, track=Track.TrackThrow):
        Gag.__init__(self, uid, name, effectId, targetType, track, rarity, level, chance)
        self.missile = missile


NO_ATTACK = 0
PASS = 99

AlwaysEquipped = [
    NO_ATTACK,
    PASS
]

GagToIcon = {
    0: None,
    1: IconGlobals.getIcon(IconGlobals.ICON_CUPCAKE_NEW),
    2: IconGlobals.getIcon(IconGlobals.ICON_PIESLICE),
    3: IconGlobals.getIcon(IconGlobals.ICON_GOLD_TART),
    4: IconGlobals.getIcon(IconGlobals.ICON_RED_TART),
    5: IconGlobals.getIcon(IconGlobals.ICON_CREAM_PIE_SLICE),
    6: IconGlobals.getIcon(IconGlobals.ICON_FRUIT_PIE),
    7: IconGlobals.getIcon(IconGlobals.ICON_CREAM_PIE),
    8: IconGlobals.getIcon(IconGlobals.ICON_BIRTHDAY_CAKE),
    9: IconGlobals.getIcon(IconGlobals.ICON_CANNON),
    10: IconGlobals.getIcon(IconGlobals.ICON_BIKE_HORN),
    PASS: IconGlobals.getIcon(IconGlobals.ICON_PASS)
}

'''
GagToMissile = {
    0: None,
    1: Missile.MissileDict,
    2: Missile.PieSliceMissile,
    3: Missile.GoldenCupcakeMissile,
    4: Missile.RedCupcakeMissile,
    5: Missile.CreamPieSliceMissile,
    6: Missile.FruitPieMissile,
    7: Missile.CreamPieMissile,
    8: Missile.BirthdayCakeMissile,
}

GagToProp = {
    10: Model.BikeHornModel
}
'''
