from panda3d.core import CardMaker, NodePath, TransparencyAttrib
from direct.actor import Actor
from direct.gui.DirectGui import DirectButton, DGG
from toontown.battle import ParticleDefs
from direct.particles.ParticleEffect import ParticleEffect
from toontown.collectibles import CollectibleItem


def loadModel(item):
    model = loader.loadModel(item.filepath)
    model.setDepthTest(1)
    model.setDepthWrite(1)
    shadow = loader.loadModel('phase_3/models/props/drop_shadow')
    shadow.reparentTo(model)
    shadow.setScale(0.2)
    shadow.setColorScale(0.0, 0.0, 0.0, 0.5)
    return model


def loadImage(item):
    if item.filepath is None:
        return None
    tex = loader.loadTexture(item.filepath)
    cm = CardMaker(item.filepath + ' card')
    cm.setFrame(-tex.getOrigFileXSize(), tex.getOrigFileXSize(), -tex.getOrigFileYSize(), tex.getOrigFileYSize())
    np = NodePath(cm.generate())
    np.setTexture(tex)
    np.setTransparency(TransparencyAttrib.MAlpha)
    return np


def loadFishingRod(item):
    pole = Actor.Actor(item.filepath, {'cast': 'phase_4/models/props/fishing-pole-chan'})
    pole.setHpr(90, 55, -90)
    pole.setDepthTest(1)
    pole.setDepthWrite(1)
    pole.pose('cast', 130)
    return pole


def loadNametagFont(item):
    return loader.loadFont(item.filepath, lineHeight=1.0)


def loadParticleEffect(item):
    if item.particleName == '':
        return None
    particleFunc = ParticleDefs.ParticleTable[item.particleName]
    effect = ParticleEffect()
    particleFunc(effect)
    return effect


def getImageIcon(item):
    icon = DirectButton(
        hidden,
        relief=None,
        image=loadFile(item),
        suppressMouse=True,
        state=DGG.DISABLED
    )
    icon.setPos(item.pos)
    icon.setScale(item.scale)
    icon.setColorScale(item.color)
    return icon


def getFishingRodIcon(item):
    icon = DirectButton(
        hidden,
        relief=None,
        image=loadFile(item),
        scale=item.scale,
        color=item.color,
        suppressMouse=True,
        state=DGG.DISABLED
    )
    icon.setPos(item.pos)
    return icon


def getNametagIcon(item):
    icon = DirectButton(
        hidden,
        relief=None,
        scale=item.scale,
        text=item.name,
        text_fg=item.color,
        text_font=loadFile(item),
        suppressMouse=True,
        state=DGG.DISABLED
    )
    icon.setPos(item.pos)
    return icon


def getParticleEffectIcon(item):
    icon = DirectButton(
        hidden,
        relief=None,
        suppressMouse=True,
        state=DGG.DISABLED
    )
    icon.setPos(item.pos)
    particle = loadFile(item)
    if particle is None:
        return icon
    particle.start(icon)
    particle.setScale(item.scale)
    return icon


Files = {
    CollectibleItem.ModelItem: loadModel,
    CollectibleItem.ImageItem: loadImage,
    CollectibleItem.FishingRodItem: loadFishingRod,
    CollectibleItem.NametagItem: loadNametagFont,
    CollectibleItem.ParticleEffectItem: loadParticleEffect,
}

Icons = {
    CollectibleItem.ModelItem: getImageIcon,
    CollectibleItem.ImageItem: getImageIcon,
    CollectibleItem.FishingRodItem: getFishingRodIcon,
    CollectibleItem.NametagItem: getNametagIcon,
    CollectibleItem.ParticleEffectItem: getParticleEffectIcon,
}


def loadFile(item):
    for cls in type(item).__mro__:
        if cls in Files:
            return Files[cls](item)

    return None


def getButtonIcon(item):
    for cls in type(item).__mro__:
        if cls in Icons:
            return Icons[cls](item)

    return None
