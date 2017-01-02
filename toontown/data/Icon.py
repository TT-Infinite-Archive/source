from direct.gui.DirectButton import DirectButton, DGG


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

        model.setDepthTest(1)
        model.setDepthWrite(1)
        shadow = loader.loadModel('phase_3/models/props/drop_shadow')
        shadow.reparentTo(model)
        shadow.setScale(0.2)
        shadow.setColorScale(0.0, 0.0, 0.0, 0.5)
        return model

    @property
    def buttonIcon(self):
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
