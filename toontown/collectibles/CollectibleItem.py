from panda3d.core import NodePath, CardMaker, TransparencyAttrib
from direct.actor import Actor
from direct.gui.DirectGui import DirectButton, DGG
from toontown.battle import ParticleDefs
from direct.particles.ParticleEffect import ParticleEffect


class Item:
    def __init__(self, name, category, id, desc='Nondescript', flavorText='Nondescript', filepath=None, scale=1.0, pos=(0.0, 0.0, 0.0), color=(1.0, 1.0, 1.0, 1.0)):
        self.name = name
        self.category = category
        self.id = id
        self.desc = desc
        self.flavorText = flavorText
        self.filepath = filepath
        self.scale = scale
        self.pos = pos
        self.color = color

    def loadFile(self):
        return None

    def getButtonIcon(self):
        return None

    def isEquippable(self):
        return False


class ModelItem(Item):
    def __init__(self, name, category, id, desc='Nondescript', flavorText='Nondescript', filepath=None, scale=1.0, pos=(0.0, 0.0, 0.0), color=(1.0, 1.0, 1.0, 1.0)):
        Item.__init__(self, name, category, id, desc, flavorText, filepath, scale, pos, color)

    def loadFile(self):
        model = loader.loadModel(self.filepath)
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


class ImageItem(Item):
    def __init__(self, name, category, id, desc='Nondescript', flavorText='Nondescript', filepath=None, scale=1.0, pos=(0.0, 0.0, 0.0), color=(1.0, 1.0, 1.0, 1.0)):
        Item.__init__(self, name, category, id, desc, flavorText, filepath, scale, pos, color)

    def loadFile(self):
        if self.filepath is None:
            return None
        tex = loader.loadTexture(self.filepath)
        cm = CardMaker(self.filepath + ' card')
        cm.setFrame(-tex.getOrigFileXSize(), tex.getOrigFileXSize(), -tex.getOrigFileYSize(), tex.getOrigFileYSize())
        np = NodePath(cm.generate())
        np.setTexture(tex)
        np.setTransparency(TransparencyAttrib.MAlpha)
        return np

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


class FishingRodItem(Item):
    def __init__(self, name, category, id, desc='Nondescript', flavorText='Nondescript', filepath=None, scale=1.0, pos=(0.0, 0.0, 0.0), color=(1.0, 1.0, 1.0, 1.0)):
        Item.__init__(self, name, category, id, desc, flavorText, filepath, scale, pos, color)

    def loadFile(self):
        pole = Actor.Actor(self.filepath, {'cast': 'phase_4/models/props/fishing-pole-chan'})
        pole.setHpr(90, 55, -90)
        pole.setDepthTest(1)
        pole.setDepthWrite(1)
        pole.pose('cast', 130)
        return pole

    def getButtonIcon(self):
        icon = DirectButton(
            hidden,
            relief=None,
            image=self.loadFile(),
            scale=self.scale,
            color=self.color,
            suppressMouse=True,
            state=DGG.DISABLED
        )
        icon.setPos(self.pos)
        return icon

    def isEquippable(self):
        return True


class NametagItem(Item):
    def __init__(self, name, category, id, desc='Nondescript', flavorText='Nondescript', filepath=None, scale=1.0, pos=(0.0, 0.0, 0.0), color=(1.0, 1.0, 1.0, 1.0)):
        Item.__init__(self, name, category, id, desc, flavorText, filepath, scale, pos, color)

    def loadFile(self):
        return loader.loadFont(self.filepath, lineHeight=1.0)

    def getButtonIcon(self):
        icon = DirectButton(
            hidden,
            relief=None,
            scale=self.scale,
            text=self.name,
            text_fg=self.color,
            text_font=self.loadFile(),
            suppressMouse=True,
            state=DGG.DISABLED
        )
        icon.setPos(self.pos)
        return icon

    def isEquippable(self):
        return True


class ParticleEffectItem(Item):
    def __init__(self, name, category, id, particleName, desc='Nondescript', flavorText='Nondescript', filepath=None, scale=1.0, pos=(0.0, 0.0, 0.0), color=(1.0, 1.0, 1.0, 1.0)):
        Item.__init__(self, name, category, id, desc, flavorText, filepath, scale, pos, color)
        self.particleName = particleName

    def loadFile(self):
        if self.particleName == '':
            return None
        particleFunc = ParticleDefs.ParticleTable[self.particleName]
        effect = ParticleEffect()
        particleFunc(effect)
        return effect

    def getButtonIcon(self):
        icon = DirectButton(
            hidden,
            relief=None,
            suppressMouse=True,
            state=DGG.DISABLED
        )
        icon.setPos(self.pos)
        particle = self.loadFile()
        if particle is None:
            return icon
        particle.start(icon)
        particle.setScale(self.scale)
        return icon

    def isEquippable(self):
        return True

class CheesyEffectItem(ImageItem):
    def isEquippable(self):
        return True

class CollectibleModelItem(ModelItem):
    def __init__(self, name, reward, category, objective, goal, desc='Nondescript', flavorText='Nondescript', filepath=None, scale=1.0, pos=(0.0, 0.0, 0.0), color=(1.0, 1.0, 1.0, 1.0)):
        Item.__init__(self, name, category, objective, desc, flavorText, filepath, scale, pos, color)
        self.reward = reward
        self.goal = goal


class CollectibleImageItem(ImageItem):
    def __init__(self, name, reward, category, objective, goal, desc='Nondescript', flavorText='Nondescript', filepath=None, scale=1.0, pos=(0.0, 0.0, 0.0), color=(1.0, 1.0, 1.0, 1.0)):
        Item.__init__(self, name, category, objective, desc, flavorText, filepath, scale, pos, color)
        self.reward = reward
        self.goal = goal


class CollectibleCategory:
    def __init__(self, id, name, items=None):
        self.id = id
        self.name = name

        if items is None:
            items = {}
        self.items = items

    def getItems(self, objective=None):
        return [i for i in self.getOrderedItems() if i.id == objective]

    def getOrderedItems(self, minId=0, maxId=None):
        if maxId is None:
            maxId = len(list(self.items.values()))
        # Sort our items by id
        sortedItems = sorted(list(self.items.values()), key=lambda item: item.id)
        # Return the range of items we want
        return sortedItems[minId:maxId]
