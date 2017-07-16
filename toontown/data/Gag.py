from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.showbase.DirectObject import DirectObject

from toontown.data import IconGlobals, Track, EffectGlobals
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

    def __init__(self, uid, name, effectId, targetType, track, rarity, level, iconId, chance=1.0):
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
        self.iconId = iconId

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
    def icon(self):
        return IconGlobals.getIcon(self.iconId)

    @property
    def glow(self):
        glow = IconGlobals.getIcon(6).icon
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

AlwaysEquipped = [
    NO_ATTACK
]

