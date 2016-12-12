from toontown.data import Missile
from toontown.data.Effect import DamageEffect
from toontown.data import IconGlobals


class GagItem:
    def __init__(self, uid, name, effect):
        self.uid = uid
        self.name = name
        self.effect = effect

    def toList(self):
        return [
            self.uid
        ]

    def getInfoString(self):
        return ''

    def getDisplayObject(self):
        return GagToIcon.get(self.uid, None)

    def isTargeted(self):
        return False

    def targetsAlly(self):
        return False

    def __str__(self):
        return '%s' % self.name

    def targetsEnemy(self):
        return False

    def getDamage(self):
        if isinstance(self.effect, DamageEffect):
            return self.effect.amount
        else:
            return 0


class TargetedGagItem(GagItem):
    TargetNone = 0
    TargetEnemy = 1
    TargetAlly = 2

    def __init__(self, uid, name, effect, accuracy, targetType, targetCount):
        GagItem.__init__(self, uid, name, effect)
        self.accuracy = accuracy
        self.targetType = targetType
        self.targetCount = targetCount

    def getInfoString(self):
        typeToString = {
            self.TargetNone: '',
            self.TargetEnemy: 'Cog',
            self.TargetAlly: 'Ally'
        }
        countToString = {
            0: '',
            1: 'One',
            2: 'Two',
            3: 'Three',
            4: 'All'
        }
        targetString = '%s %s' % (
            countToString[self.targetCount], typeToString[self.targetType] + ('s' if self.targetCount > 1 else '')
        )

        return 'Damage: %s\nAccuracy: %s%%\n\nHits %s' % (self.effect.amount, int(self.accuracy * 100), targetString)

    def getDisplayObject(self):
        return GagToIcon.get(self.uid, None)

    def isTargeted(self):
        return True

    def targetsAlly(self):
        return self.targetType == self.TargetAlly

    def targetsEnemy(self):
        return self.targetType == self.TargetEnemy


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
    0: GagItem(0, 'Nothing but a chuckle', None),
    1: TargetedGagItem(1, 'Cupcake', DamageEffect(0, 6), 0.6, TargetedGagItem.TargetEnemy, 1),
    2: TargetedGagItem(2, 'Sliced Fruit Pie', DamageEffect(0, 12), 0.6, TargetedGagItem.TargetEnemy, 1),
    3: TargetedGagItem(3, 'Golden Cupcake', DamageEffect(0, 999), 1, TargetedGagItem.TargetEnemy, 4),
    PASS: GagItem(99, 'Pass', None),
}

GagToIcon = {
    0: None,
    1: IconGlobals.getIcon(IconGlobals.ICON_CUPCAKE_NEW),
    2: IconGlobals.getIcon(IconGlobals.ICON_PIESLICE),
    3: IconGlobals.getIcon(IconGlobals.ICON_GOLD_TART),
    PASS: IconGlobals.getIcon(IconGlobals.ICON_PASS)
}

GagToMissile = {
    0: None,
    1: Missile.CupcakeMissile,
    2: Missile.CupcakeMissile,
    3: Missile.GoldenCupcakeMissile
}

AlwaysEquipped = [
    NO_ATTACK,
    PASS
]




