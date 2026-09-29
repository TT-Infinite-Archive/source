from panda3d.core import ColorBlendAttrib, ConfigVariableBool
ModelPhase = 5
ModelTypes = {'animation': 'a',
 'model': 'm',
 'rig': 'r'}
ModelGroups = {'area': 'ara',
 'gui': 'gui'}
Games = {'flying': 'cfg',
 'maze': 'cmg',
 'shared': 'csa'}

def loadFlyingModel(baseName, type = 'model', group = 'area'):
    return loadModel(baseName, 'flying', type=type, group=group)


def loadMazeModel(baseName, type = 'model', group = 'area'):
    return loadModel(baseName, 'maze', type=type, group=group)


def getModelPath(baseName, game = 'shared', type = 'model', group = 'area'):
    extension = ''
    if hasattr(getBase(), 'air'):
        extension = '.bam'
    return 'phase_%i/models/cogdominium/tt_%s_%s_%s_%s%s' % (ModelPhase,
     ModelTypes[type],
     ModelGroups[group],
     Games[game],
     baseName,
     extension)


def loadModel(baseName, game = 'shared', type = 'model', group = 'area'):
    return loader.loadModel(getModelPath(baseName, game, type, group))


class VariableContainer:
    pass

class DevVariableContainer:

    def __init__(self, name):
        self.__dict__['_enabled'] = ConfigVariableBool('%s-dev' % name, False).getValue()

    def __setattr__(self, name, value):
        self.__dict__[name] = self._enabled and value


def getRandomDialogueLine(lineList, rng):
    return lineList[rng.randint(0, len(lineList) - 1)]


def initializeLightCone(np, bin = 'fixed', sorting = 3):
    np.node().setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.MAdd, ColorBlendAttrib.OIncomingAlpha, ColorBlendAttrib.OOne))
    if bin:
        np.setBin(bin, sorting)
    np.setDepthWrite(False)
    np.setTwoSided(True, 10000)


ROTATE_TABLE_ALLOWED_ANGLES = (0, 90, 180, 270)

def rotateTable(table, angle):
    if angle == 0:
        t = table[:]
    elif angle == 90:
        t = []
        width = len(table[0])
        height = len(table)
        for j in range(width):
            row = []
            for i in range(height):
                row.append(table[height - 1 - i][j])

            t.append(row)

    elif angle == 180:
        t = table[:]
        for row in t:
            row.reverse()

        t.reverse()
    elif angle == 270:
        t = []
        width = len(table[0])
        height = len(table)
        for j in range(width):
            row = []
            for i in range(height):
                row.append(table[i][width - 1 - j])

            t.append(row)

    return t
