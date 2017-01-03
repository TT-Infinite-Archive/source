from panda3d.core import CardMaker, NodePath, TransparencyAttrib


def makeCard(filepath):
    tex = loader.loadTexture(filepath)
    cm = CardMaker('%s-card' % filepath)
    cm.setFrame(-tex.getOrigFileXSize(), tex.getOrigFileXSize(), -tex.getOrigFileYSize(), tex.getOrigFileYSize())
    cardNp = NodePath(cm.generate())
    cardNp.setTexture(tex)
    cardNp.setTransparency(TransparencyAttrib.MAlpha)
    return cardNp
