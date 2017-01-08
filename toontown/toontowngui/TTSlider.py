from panda3d.core import TextNode
from direct.gui.DirectGui import DirectButton, DirectSlider, DirectLabel, DGG
from toontown.toonbase.ColorGlobals import CToontownBlue, CGray, CDefault


class TTSlider(DirectButton):
    def __init__(self, parent=aspect2d, pos=(0, 0, 0), value=0, scale=1.0, enabled=True, command=None):
        DirectButton.__init__(self, parent, relief=None)
        self._parent = parent
        self.command = command
        self.pos = pos
        self.scale = (0.375 * scale, 0.1 * scale, 0.25 * scale)
        self.enabled = enabled

        gui = loader.loadModel('phase_3/models/gui/tt_m_gui_mat_nameShop')
        thumb = gui.find('**/tt_t_gui_mat_namePanelCircle')

        self.slider = DirectSlider(
            parent=self,
            value=value,
            range=(0,100),
            pageSize=1,
            scale=self.scale,
            frameColor=CToontownBlue,
            pos=self.pos,
            orientation=DGG.HORIZONTAL,
            thumb_relief=None,
            thumb_geom=thumb,
            thumb_geom_scale=(1 * scale, 1 * scale, 1.5 * scale),
            command=self.onChange
        )

        self.percent = DirectLabel(
            parent=self.slider,
            relief=None,
            scale=(1 / self.scale[0], 1 / self.scale[1], 1 / self.scale[2]),
            text='',
            text_scale=0.05,
            text_pos=(0.375, 0.055),
            text_align=TextNode.ARight
        )

        gui.removeNode()
        self.updatePercentText()
        if not self.enabled:
            self.disable()

    def getValue(self):
        return self.slider['value']

    def setValue(self, value):
        self.slider['value'] = value

    def onChange(self):
        if self.command:
            self.command()
        self.updatePercentText()

    def updatePercentText(self):
        value = self.slider['value']
        self.percent['text'] = '%d%%' % value

    def enable(self):
        self.enabled = True
        self.slider['frameColor'] = CToontownBlue
        self.slider['thumb_geom_color'] = CDefault
        self.slider['state'] = DGG.NORMAL

    def disable(self):
        self.enabled = False
        self.slider['frameColor'] = CGray
        self.slider['thumb_geom_color'] = CGray
        self.slider['state'] = DGG.DISABLED
