from panda3d.core import NodePath, TextNode, Vec4

from direct.gui.DirectGui import DGG, DirectButton, DirectFrame

TabScale = (0.033, 0.033, 0.030)
ArtWidth = 0.325
ArtZ = 0.028
TabPadding = 0.08
TabGap = 0.035

NormalColor = (1, 1, 1, 1)
ClickColor = (0.8, 0.8, 0, 1)
RolloverColor = (0.15, 0.82, 1.0, 1)
ActiveColor = (1.0, 0.98, 0.15, 1)

Preloaded = {}


def loadTabs():
    if Preloaded:
        return

    gui = loader.loadModel('phase_3.5/models/gui/fishingBook.bam')
    for name in ('polySurface1', 'polySurface2', 'polySurface3'):
        pivot = NodePath(name)
        geom = gui.find('**/tabs/%s' % name).copyTo(pivot)
        geom.setHpr(0, 0, -90)
        geom.setScale(TabScale)
        low, high = pivot.getTightBounds()
        center = (low + high) / 2
        geom.setPos(-center[0], -center[1], ArtZ - center[2])
        Preloaded[name] = pivot
    gui.removeNode()


class TTTab(DirectButton):
    def __init__(self, parent, shape = 'polySurface2', text = '', textScale = 0.07, **kw):
        loadTabs()

        optiondefs = (
            ('relief', None, None),
            ('image', Preloaded[shape], None),
            ('image_color', NormalColor, None),
            ('image1_color', ClickColor, None),
            ('image2_color', RolloverColor, None),
            ('image3_color', ActiveColor, None),
            ('text', text, None),
            ('text_align', TextNode.ACenter, None),
            ('text_fg', Vec4(0.2, 0.1, 0, 1), None),
            ('text_scale', textScale, None),
            ('text_pos', (0, 0), None)
        )

        self.defineoptions(kw, optiondefs)
        DirectButton.__init__(self, parent)
        self.initialiseoptions(TTTab)

        # Like the Social page's tabs, each one is only as wide as its label.
        self.width = self.component('text0').textNode.getWidth() * textScale + TabPadding
        self['image_scale'] = (self.width / ArtWidth, 1, 1)
        self.resetFrameSize()


class TTTabBar(DirectFrame):
    def __init__(self, parent, tabs = (), pos = (0, 0, 0), textScale = 0.07, command = None):
        DirectFrame.__init__(self, parent = parent, relief = None, pos = pos)

        self.command = command
        self.tabs = {}
        self.active = None

        last = len(tabs) - 1
        for index, (value, text) in enumerate(tabs):
            if index == 0:
                shape = 'polySurface1'
            elif index == last:
                shape = 'polySurface3'
            else:
                shape = 'polySurface2'
            self.tabs[value] = TTTab(
                self,
                shape = shape,
                text = text,
                textScale = textScale,
                command = self.__clicked,
                extraArgs = [value]
            )

        x = -(sum(tab.width for tab in self.tabs.values()) + TabGap * last) / 2.0
        for tab in self.tabs.values():
            tab.setX(x + tab.width / 2.0)
            x += tab.width + TabGap

    def __clicked(self, value):
        if self.command:
            self.command(value)

    def setActive(self, value):
        self.active = value
        for key, tab in self.tabs.items():
            tab['state'] = DGG.DISABLED if key == value else DGG.NORMAL
