from toontown.data import Missile, Track, IconGlobals, Model, EffectGlobals
from toontown.data.Gag import Gag, ThrowGag, PASS
from toontown.data.Effect import DamageEffect
from toontown.data.DataLoader import DataLoader

DefaultGag = Gag(0, 'Nothing but a chuckle', None, 0, Track.TrackNone, Gag.RarityCommon, 0)

gdl = DataLoader('resources/data/gags.xml')
print('Loading Gags...')
data = gdl.loadData()

Gags = {
    0: DefaultGag,
}

typeToClass = {
    'ThrowGag': ThrowGag,
    'Gag': Gag,
}

for item in data:
    if item['type'] == 'ThrowGag':
        gag = ThrowGag(
            int(item['id']),
            item['name'],
            EffectGlobals.getEffect(int(item['effect'])),
            int(item['targettype']),
            int(item['rarity']),
            int(item['level']),
            Missile.getMissile(int(item['missile'])),
            float(item['chance']),
            int(item['track'])
        )
    elif item['type'] == 'Gag':
        gag = Gag(
            int(item['id']),
            item['name'],
            EffectGlobals.getEffect(int(item['effect'])),
            int(item['targettype']),
            int(item['track']),
            int(item['rarity']),
            int(item['level']),
            float(item['chance'])
        )
    else:
        continue

    Gags[int(item['id'])] = gag

'''
Cupcake = ThrowGag(1, 'Cupcake', EffectGlobals.CupcakeDamage, Gag.TargetSingleEnemy, Gag.RarityCommon, 1, Missile.CupcakeMissile)
SlicedFruitPie = ThrowGag(2, 'Sliced Fruit Pie', DamageEffect(0, 12), Gag.TargetSingleEnemy, Gag.RarityCommon, 2, Missile.PieSliceMissile)
GoldenCupcake = ThrowGag(3, 'Golden Cupcake', DamageEffect(0, 999), Gag.TargetEnemies, Gag.RarityLegendary, 9, Missile.GoldenCupcakeMissile)
RedCupcake = ThrowGag(4, 'Red Cupcake', DamageEffect(0, 1), Gag.TargetEnemies, Gag.RarityRare, 1, Missile.RedCupcakeMissile, chance=0.5)
SlicedCreamPie = ThrowGag(5, 'Sliced Cream Pie', DamageEffect(0, 16), Gag.TargetSingleEnemy, Track.TrackThrow, Gag.RarityCommon, 3)
Gags = {
    0: DefaultGag,
    1: Gag(1, 'Cupcake', DamageEffect(0, 6), Gag.TargetSingleEnemy, Track.TrackThrow, Gag.RarityCommon, 1),
    2: Gag(2, 'Sliced Fruit Pie', DamageEffect(0, 12), Gag.TargetSingleEnemy, Track.TrackThrow, Gag.RarityCommon, 2),
    3: Gag(3, 'Golden Cupcake', DamageEffect(0, 999), Gag.TargetEnemies, Track.TrackThrow, Gag.RarityLegendary, 9),
    4: Gag(4, 'Red Cupcake', DamageEffect(0, 1), Gag.TargetEnemies, Track.TrackThrow, Gag.RarityRare, 1, chance=0.5),
    5: Gag(5, 'Sliced Cream Pie', DamageEffect(0, 16), Gag.TargetSingleEnemy, Track.TrackThrow, Gag.RarityCommon, 3),
    6: Gag(6, 'Fruit Pie', DamageEffect(0, 24), Gag.TargetSingleEnemy, Track.TrackThrow, Gag.RarityCommon, 4),
    7: Gag(7, 'Cream Pie', DamageEffect(0, 32), Gag.TargetSingleEnemy, Track.TrackThrow, Gag.RarityCommon, 5),
    8: Gag(8, 'Birthday Cake', DamageEffect(0, 80), Gag.TargetSingleEnemy, Track.TrackThrow, Gag.RarityCommon, 6),
    9: Gag(9, 'Cannon', DamageEffect(0, 80), Gag.TargetSingleEnemy, Track.TrackNone, Gag.RarityEpic, 6),
    10: Gag(10, 'Bike Horn', DamageEffect(0, 6), Gag.TargetEnemies, Track.TrackSound, Gag.RarityCommon, 1),
    PASS: Gag(99, 'Pass', None, 0, Track.TrackNone, Gag.RarityCommon, 0),
}
'''
