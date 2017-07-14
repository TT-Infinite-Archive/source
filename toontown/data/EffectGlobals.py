from toontown.data.Effect import Effect, HealEffect, DamageEffect
from toontown.data.DataLoader import DataLoader

DefaultEffect = Effect(0)

edl = DataLoader('resources/data/effects.xml')
data = edl.loadData()

# Dict to convert string class to actual class
typeToClass = {
    'Effect': Effect,
    'DamageEffect': DamageEffect,
    'HealEffect': HealEffect
}

# Dict to hold effect data for game
EffectDict = {}

# Insert data into game dict
print('Loading Effects...')
for item in data:
    eClass = typeToClass.get(item['type'], Effect)
    eId = int(item['id'])
    eName = item['name']
    eAmount = int(item['amount'])
    EffectDict[eId] = eClass(eId, eAmount)


# Function for game to fetch effects
def getEffect(effectId):
    return EffectDict.get(effectId, DefaultEffect)