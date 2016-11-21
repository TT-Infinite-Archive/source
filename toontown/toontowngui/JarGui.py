from direct.gui.DirectGui import DirectLabel
from toontown.toonbase import ToontownGlobals


class JarGui(DirectLabel):
    def __init__(self, parent=aspect2d, pos=(0.0, 0.0, 0.0), scale=0.8):
        DirectLabel.__init__(self, parent, pos=pos, scale=scale)

        jarGui = loader.loadModel('phase_3.5/models/gui/jar_gui')
        self.moneyDisplay = DirectLabel(
            parent=self,
            relief=None,
            text=str(base.localAvatar.getMoney()),
            text_scale=0.18,
            text_fg=(0.95, 0.95, 0, 1),
            text_shadow=(0, 0, 0, 1),
            text_pos=(0, -0.1, 0),
            image=jarGui.find('**/Jar'),
            text_font=ToontownGlobals.getSignFont()
        )
        self.listen()
        self.update()

    def destroy(self):
        self.unlisten()
        DirectLabel.destroy(self)

    def hide(self):
        DirectLabel.hide(self)
        self.unlisten()

    def show(self):
        DirectLabel.show(self)
        self.listen()
        self.update()

    def update(self):
        self.moneyDisplay['text'] = str(base.localAvatar.getMoney())

    def listen(self):
        self.accept(base.localAvatar.uniqueName('moneyChange'), self.update)

    def unlisten(self):
        self.ignore(base.localAvatar.uniqueName('moneyChange'))

