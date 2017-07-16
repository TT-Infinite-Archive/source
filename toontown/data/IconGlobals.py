from toontown.data.Icon import Icon, ImageIcon
from toontown.data.DataLoader import IconDataLoader
from panda3d.core import VBase3, VBase4

ICON_CUPCAKE_NEW = 1
ICON_PIESLICE = 2
ICON_GOLD_TART = 3
ICON_PASS = 4
ICON_RED_TART = 5
ICON_GLOW = 6
ICON_CREAM_PIE_SLICE = 7
ICON_CREAM_PIE = 8
ICON_FRUIT_PIE = 9
ICON_BIRTHDAY_CAKE = 10
ICON_CANNON = 11
ICON_BIKE_HORN = 12

ICON_REPOSITORY = {0: None}

idl = IconDataLoader('resources/data/icons.xml')
print('Loading Icons...')
data = idl.loadData()
for item in data:
    if item['type'] == 'Icon':
        icon = Icon(
            item['filepath'],
            float(item.get('scale', 1)),
            item.get('pos', VBase3(0, 0, 0)),
            item.get('color', VBase4(1, 1, 1, 1)),
            item.get('nodepathname', None)
        )
    elif item['type'] == 'ImageIcon':
        icon = ImageIcon(
            item['filepath'],
            float(item.get('scale', 1)),
            item.get('pos', VBase3(0, 0, 0)),
            item.get('color', VBase4(1, 1, 1, 1))
        )
    else:
        continue
    ICON_REPOSITORY[int(item['id'])] = icon


def getIcon(uid):
    return ICON_REPOSITORY.get(uid, ICON_REPOSITORY[0])
