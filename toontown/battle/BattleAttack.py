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
