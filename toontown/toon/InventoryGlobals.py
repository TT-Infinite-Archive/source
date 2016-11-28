from direct.gui.DirectButton import DirectButton, DGG
from toontown.battle.Effect import DamageEffect


class GagItem:
    def __init__(self, uid, name, effect):
        self.uid = uid
        self.name = name
        self.effect = effect

    def toList(self):
        return [
            self.uid
        ]

    def getInfoString(self):
        return ''

    def getDisplayObject(self):
        return GagDisplay.get(self.uid, None)

    def isTargeted(self):
        return False

    def targetsAlly(self):
        return False

    def __str__(self):
        return '%s' % self.name

    def targetsEnemy(self):
        return False


class TargetedGagItem(GagItem):
    TargetNone = 0
    TargetEnemy = 1
    TargetAlly = 2

    def __init__(self, uid, name, effect, accuracy, targetType, targetCount):
        GagItem.__init__(self, uid, name, effect)
        self.accuracy = accuracy
        self.targetType = targetType
        self.targetCount = targetCount

    def getInfoString(self):
        typeToString = {
            self.TargetNone: '',
            self.TargetEnemy: 'Cog',
            self.TargetAlly: 'Ally'
        }
        countToString = {
            0: '',
            1: 'One',
            2: 'Two',
            3: 'Three',
            4: 'All'
        }
        targetString = '%s %s' % (
            countToString[self.targetCount], typeToString[self.targetType] + ('s' if self.targetCount > 1 else '')
        )

        return 'Damage: %s\nAccuracy: %s%%\n\nHits %s' % (self.effect.amount, int(self.accuracy * 100), targetString)

    def getDisplayObject(self):
        return GagDisplay.get(self.uid, None)

    def isTargeted(self):
        return True

    def targetsAlly(self):
        return self.targetType == self.TargetAlly

    def targetsEnemy(self):
        return self.targetType == self.TargetEnemy


class GagItemSlot:
    def __init__(self, gagId, amount, equipped):
        self.gag = Gags.get(gagId, None)
        self.amount = amount
        self.equipped = equipped

    def addOne(self):
        self.amount += 1

    def useOne(self):
        self.amount = max(0, self.amount - 1)

    def setAmount(self, amount):
        self.amount = amount

    def toList(self):
        return self.gag.toList() + [self.amount, self.equipped]

    def fromList(self, ls):
        self.gag = Gags.get(ls[0], None)
        self.amount = ls[1]
        self.equipped = ls[2]


class GagImageDisplay:
    def __init__(self, name, filepath=None, scale=1.0, pos=(0.0, 0.0, 0.0), color=(1.0, 1.0, 1.0, 1.0), nodePathName=None):
        self.name = name
        self.filepath = filepath
        self.scale = scale
        self.pos = pos
        self.color = color
        self.nodePathName = nodePathName

    def loadFile(self):
        if self.filepath is None:
            return None

        model = loader.loadModel(self.filepath)

        if self.nodePathName is not None:
            old = model
            model = old.find('**/' + self.nodePathName)
            old.removeNode()

        model.setDepthTest(1)
        model.setDepthWrite(1)
        shadow = loader.loadModel('phase_3/models/props/drop_shadow')
        shadow.reparentTo(model)
        shadow.setScale(0.2)
        shadow.setColorScale(0.0, 0.0, 0.0, 0.5)
        return model

    def getButtonIcon(self):
        icon = DirectButton(
            hidden,
            relief=None,
            image=self.loadFile(),
            suppressMouse=True,
            state=DGG.DISABLED
        )
        icon.setPos(self.pos)
        icon.setScale(self.scale)
        icon.setColorScale(self.color)
        return icon

Gags = {
    0: GagItem(0, 'Nothing but a chuckle', None),
    1: TargetedGagItem(1, 'Cupcake', DamageEffect(0, 6), 0.6, TargetedGagItem.TargetEnemy, 1),
    2: TargetedGagItem(2, 'Sliced Fruit Pie', DamageEffect(0, 12), 0.6, TargetedGagItem.TargetEnemy, 1),
    3: TargetedGagItem(3, 'Golden Cupcake', DamageEffect(0, 999), 1, TargetedGagItem.TargetEnemy, 4),
    99: GagItem(99, 'Pass', None),
}

GagDisplay = {
    0: GagImageDisplay(Gags[0].name, 'phase_3.5/models/gui/battle_gui', nodePathName='tt_t_gui_bat_pass', scale=0.2),
    1: GagImageDisplay(Gags[1].name, 'phase_3.5/models/gui/inventory_icons', nodePathName='inventory_tart'),
    2: GagImageDisplay(Gags[2].name, 'phase_3.5/models/gui/inventory_icons', nodePathName='inventory_fruit_pie_slice'),
    3: GagImageDisplay(Gags[3].name, 'phase_3.5/models/gui/inventory_icons', nodePathName='inventory_tart', color=(1, 0.84, 0.0, 1.0))
}

AlwaysEquipped = [
    99
]



