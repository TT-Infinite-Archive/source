from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.showbase.DirectObject import DirectObject

from toontown.data import Missile
from toontown.data.Effect import DamageEffect
from toontown.data import IconGlobals


class Gag(DirectObject):
    notify = directNotify.newCategory('Gag')
    TargetNone = 0
    TargetSingleEnemy = 1
    TargetSingleAlly = 2
    TargetEnemies = 3
    TargetAllies = 4
    TargetSelf = 5
    TargetSelfAndAllies = 6

    def __init__(self, uid, name, effect, targetType, chance=1.0):
        DirectObject.__init__(self)
        self.uid = uid
        self.name = name
        self.effect = effect
        self.targetType = targetType
        self.chance = chance

    def __str__(self):
        return '%s' % self.name

    def toList(self):
        return [
            self.uid
        ]

    def getDescription(self):
        typeToString = {
            self.TargetNone: '',
            self.TargetSingleEnemy: ' to a single Cog',
            self.TargetSingleAlly: ' to a single Toon',
            self.TargetEnemies: ' to all Cogs',
            self.TargetAllies: ' to all other Toons',
            self.TargetSelf: ' to yourself',
            self.TargetSelfAndAllies: ' to all Toons'
        }
        return '%s%s.' % (self.effect.getDescription(), typeToString[self.targetType])

    def getDisplayObject(self):
        return GagToIcon.get(self.uid, None)

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


class GagItemSlot:
    def __init__(self, gagId, amount, equipped):
        self.gag = Gags.get(gagId, None)
        self.amount = amount
        self.equipped = equipped

    def addOne(self):
        self.amount += 1

    def useOne(self):
        self.amount = max(0, self.amount - 1)

    def setAmount(self, amount):
        self.amount = amount

    def toList(self):
        return self.gag.toList() + [self.amount, self.equipped]

    def fromList(self, ls):
        self.gag = Gags.get(ls[0], None)
        self.amount = ls[1]
        self.equipped = ls[2]

NO_ATTACK = 0
PASS = 99

Gags = {
    0: Gag(0, 'Nothing but a chuckle', None, 0),
    1: Gag(1, 'Cupcake', DamageEffect(0, 6), Gag.TargetSingleEnemy),
    2: Gag(2, 'Sliced Fruit Pie', DamageEffect(0, 12), Gag.TargetSingleEnemy),
    3: Gag(3, 'Golden Cupcake', DamageEffect(0, 999), Gag.TargetEnemies),
    4: Gag(4, 'Red Cupcake', DamageEffect(0, 1), Gag.TargetEnemies, chance=0.5),
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




