from panda3d.core import CardMaker, NodePath, Texture, TransparencyAttrib


def makeCard(filepath):
    tex = loader.loadTexture(filepath)
    cm = CardMaker(filepath + ' card')
    cm.setFrame(-tex.getOrigFileXSize(), tex.getOrigFileXSize(), -tex.getOrigFileYSize(), tex.getOrigFileYSize())
    cardNp = NodePath(cm.generate())
    cardNp.setTexture(tex)
    cardNp.setTransparency(TransparencyAttrib.MAlpha)
    return cardNp
