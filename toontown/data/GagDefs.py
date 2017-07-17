from toontown.data import Missile, Track
from toontown.data.Gag import Gag, ThrowGag
from toontown.data.DataLoader import DataLoader

DefaultGag = Gag(0, 'Nothing but a chuckle', None, 0, Track.TrackNone, Gag.RarityCommon, 0, 0)

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
            int(item['effect']),
            int(item['targettype']),
            int(item['rarity']),
            int(item['level']),
            Missile.getMissile(int(item['missile'])),
            int(item['icon']),
            float(item['chance']),
            int(item['track'])
        )
    elif item['type'] == 'Gag':
        gag = Gag(
            int(item['id']),
            item['name'],
            int(item['effect']),
            int(item['targettype']),
            int(item['track']),
            int(item['rarity']),
            int(item['level']),
            int(item['icon']),
            float(item['chance'])
        )
    else:
        continue

    Gags[int(item['id'])] = gag

