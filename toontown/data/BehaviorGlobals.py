from toontown.data.Behavior import PeriodicBehavior, Behavior
from toontown.data.DataLoader import DataLoader

BehaviorDict = {
    0: None
}

bdl = DataLoader('resources/data/behaviors.xml')
data = bdl.loadData()

for item in data:
    if item['type'] == 'PeriodicBehavior':
        behavior = PeriodicBehavior(int(item['id']), item['name'], float(item['interval']), int(item['intervaleffectid']))
    else:
        behavior = Behavior(int(item['id']), item['name'])

    BehaviorDict[int(item['id'])] = behavior


def getBehavior(behaviorId):
    return BehaviorDict.get(behaviorId, BehaviorDict[0])
