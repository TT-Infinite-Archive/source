from panda3d.core import NodePath

from direct.gui.DirectButton import DirectButton, DGG

from toontown.util import TTCardMaker


class Icon:
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
        return model
    
    @property
    def icon(self):
        icon = self.loadFile()
        icon.setPos(self.pos)
        icon.setScale(self.scale)
        icon.setColorScale(self.color)
        return icon

    @property
    def button(self):
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


class ImageIcon(Icon):
    def __init__(self, name, filepath=None, scale=1.0, pos=(0.0, 0.0, 0.0), color=(1.0, 1.0, 1.0, 1.0)):
        Icon.__init__(self, name, filepath, scale, pos, color)

    def loadFile(self):
        model = NodePath('%s-node' % self.filepath)
        card = TTCardMaker.makeCard(self.filepath)
        card.reparentTo(model)
        return model
