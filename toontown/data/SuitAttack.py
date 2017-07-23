from toontown.data import DataLoader


class SuitAttack:
    TargetNone = 0
    TargetAllies = 1
    TargetEnemies = 2
    TargetEnemy = 3
    TargetAlly = 4

    def __init__(self, attackId, name, effect, accuracy, targetType):
        self.attackId = attackId
        self.name = name
        self.effect = effect
        self.accuracy = accuracy
        self.targetType = targetType

    def targetsAlly(self):
        return self.targetType in [self.TargetAllies, self.TargetAlly]

    def targetsEnemy(self):
        return self.targetType == [self.TargetEnemy, self.TargetEnemies]


sadl = DataLoader.DataLoader('resources/data/suitattacks.xml')
data = sadl.loadData()

SuitAttacks = {
    0: SuitAttack(0, 'Nothing', None, 0, 0)
}

for item in data:
    sa = SuitAttack(int(item['id']), item['name'], item['effect'], item['accuracy'], item['targettype'])
    SuitAttacks[int(item['id'])] = sa


def getSuitAttack(attackId):
    SuitAttacks.get(attackId, SuitAttacks[0])
