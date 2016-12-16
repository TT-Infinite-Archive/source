from toontown.data.Effect import DamageEffect


class BattleAttack:
    def __init__(self, attackerId=0, attackId=0, targetId=0):
        self.attackerId = attackerId
        self.attackId = attackId
        self.targetId = targetId

    def toList(self):
        return [
            self.attackerId,
            self.attackId,
            self.targetId
        ]

    def fromList(self, ls):
        self.attackerId = ls[0]
        self.attackId = ls[1]
        self.targetId = ls[2]


class ToonBattleAttack(BattleAttack):
    def __init__(self, toonId=0, attackId=0, targetId=0):
        BattleAttack.__init__(self, toonId, attackId, targetId)


class SuitBattleAttack(BattleAttack):
    def __init__(self, suitId=0, attackId=0, targetId=0):
        BattleAttack.__init__(self, suitId, attackId, targetId)


class MovieAttack(BattleAttack):
    def __init__(self, suitId=0, attackId=0, targetId=0, hit=False):
        BattleAttack.__init__(self, suitId, attackId, targetId)
        self.hit = hit

    def toList(self):
        return BattleAttack.toList(self) + [self.hit]

    def fromList(self, ls):
        BattleAttack.fromList(self, ls)
        self.hit = ls[3]


class SuitAttack:
    TargetNone = 0
    TargetAlly = 1
    TargetEnemy = 2

    def __init__(self, attackId, name, effect, accuracy, targetType, targetCount=1):
        self.attackId = attackId
        self.name = name
        self.effect = effect
        self.accuracy = accuracy
        self.targetType = targetType
        self.targetCount = targetCount

    def targetsAlly(self):
        return self.targetType == self.TargetAlly

    def targetsEnemy(self):
        return self.targetType == self.TargetEnemy

SAPound = 1
SAShred = 2
SuitAttacks = {
    0: SuitAttack(0, 'Nothing', None, 0, 0),
    1: SuitAttack(1, 'Pound Key', DamageEffect(0, 3), 0.9, SuitAttack.TargetEnemy),
    2: SuitAttack(2, 'Shred', DamageEffect(0, 5), 0.5, SuitAttack.TargetEnemy)
}
