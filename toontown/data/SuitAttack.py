from toontown.data import DataLoader, EffectGlobals
import random


class SuitAttack:
    TargetNone = 0
    TargetAllies = 1
    TargetEnemies = 2
    TargetEnemy = 3
    TargetAlly = 4

    def __init__(self, attackId, name, effectId, accuracy, targetType, taunts):
        self.attackId = attackId
        self.name = name
        self.effectId = effectId
        self.effect = EffectGlobals.getEffect(effectId)
        self.accuracy = accuracy
        self.targetType = targetType
        self.taunts = taunts

    def __str__(self):
        return 'SuitAttack-%s' % self.name

    def targetsAlly(self):
        return self.targetType in [self.TargetAllies, self.TargetAlly]

    def targetsEnemy(self):
        return self.targetType in [self.TargetEnemy, self.TargetEnemies]

    def getRandomTaunt(self):
        return random.choice(self.taunts)


sadl = DataLoader.SuitAttackDataLoader('resources/data/suitattacks.xml')
data = sadl.loadData()

SuitAttacks = {
    0: SuitAttack(0, 'Nothing', None, 0, 0, None)
}

for item in data:
    sa = SuitAttack(int(item['id']), item['name'], int(item['effect']), float(item['accuracy']), int(item['targettype']), item['taunts'])
    SuitAttacks[int(item['id'])] = sa


def getSuitAttack(attackId):
    return SuitAttacks.get(attackId, SuitAttacks[0])
