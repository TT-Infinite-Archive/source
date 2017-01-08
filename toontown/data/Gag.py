from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.showbase.DirectObject import DirectObject

from toontown.data import Missile, Track, IconGlobals
from toontown.data.Effect import DamageEffect
from toontown.toonbase import ColorGlobals


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

    def __init__(self, uid, name, effect, targetType, track=0, rarity=0, chance=1.0):
        DirectObject.__init__(self)
        self.uid = uid
        self.name = name
        self.effect = effect
        self.targetType = targetType
        self.track = track
        self.chance = chance
        self.rarity = rarity

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
            self.TargetSingleEnemy: ' to a Cog',
            self.TargetSingleAlly: ' to a Toon',
            self.TargetEnemies: ' to all Cogs',
            self.TargetAllies: ' to other Toons',
            self.TargetSelf: ' to yourself',
            self.TargetSelfAndAllies: ' to all Toons'
        }
        string = '%s%s.' % (self.effect.description, typeToString[self.targetType])
        if self.chance < 1.0:
            string += ' Has a %s%% chance to hit.' % int(self.chance * 100)
        return string

    @property
    def rarityColor(self):
        rarityToColor = {
            Gag.RarityCommon: ColorGlobals.CGray,
            Gag.RarityRare: ColorGlobals.CMediumBlue,
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

NO_ATTACK = 0
PASS = 99

DefaultGag = Gag(0, 'Nothing but a chuckle', None, 0)
Gags = {
    0: DefaultGag,
    1: Gag(1, 'Cupcake', DamageEffect(0, 6), Gag.TargetSingleEnemy, Track.TrackThrow, Gag.RarityCommon),
    2: Gag(2, 'Sliced Fruit Pie', DamageEffect(0, 12), Gag.TargetSingleEnemy, Track.TrackThrow, Gag.RarityCommon),
    3: Gag(3, 'Golden Cupcake', DamageEffect(0, 999), Gag.TargetEnemies, Track.TrackThrow, Gag.RarityLegendary),
    4: Gag(4, 'Red Cupcake', DamageEffect(0, 1), Gag.TargetEnemies, Track.TrackThrow, Gag.RarityRare, chance=0.5),
    PASS: Gag(99, 'Pass', None, 0),
}

GagToIcon = {
    0: None,
    1: IconGlobals.getIcon(IconGlobals.ICON_CUPCAKE_NEW),
    2: IconGlobals.getIcon(IconGlobals.ICON_PIESLICE),
    3: IconGlobals.getIcon(IconGlobals.ICON_GOLD_TART),
    4: IconGlobals.getIcon(IconGlobals.ICON_RED_TART),
    PASS: IconGlobals.getIcon(IconGlobals.ICON_PASS)
}

GagToMissile = {
    0: None,
    1: Missile.CupcakeMissile,
    2: Missile.CupcakeMissile,
    3: Missile.GoldenCupcakeMissile,
    4: Missile.RedCupcakeMissile
}

AlwaysEquipped = [
    NO_ATTACK,
    PASS
]






