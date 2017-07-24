from toontown.data.Effect import Effect, HealEffect, DamageEffect
from toontown.data.DataLoader import DataLoader

DefaultEffect = Effect(0)

edl = DataLoader('resources/data/effects.xml')
print('Loading Effects...')
data = edl.loadData()

# Dict to hold effect data for game
EffectDict = {}

# Insert data into game dict
for item in data:
    if item['type'] == 'Effect':
        effect = Effect(int(item['id']))
    elif item['type'] == 'DamageEffect':
        effect = DamageEffect(int(item['id']), int(item['amount']))
    elif item['type'] == 'HealEffect':
        effect = HealEffect(int(item['id']), int(item['amount']))
    else:
        continue

    EffectDict[int(item['id'])] = effect


# Function for game to fetch effects
def getEffect(effectId):
    return EffectDict.get(effectId, DefaultEffect)