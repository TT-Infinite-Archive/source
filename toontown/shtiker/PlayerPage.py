from panda3d.core import Vec4, TextNode
from direct.gui.DirectGui import DirectFrame, DGG, OnscreenText, DirectScrolledList
from toontown.shtiker import ShtikerPage
from toontown.toonbase import TTLocalizer, ToontownGlobals
from toontown.toontowngui.TTGui import TTLabel


class PlayerPage(ShtikerPage.ShtikerPage):
    notify = directNotify.newCategory('PlayerPage')

    def __init__(self):
        ShtikerPage.ShtikerPage.__init__(self)
        self.playerList = None
        self.playerListItems = []
        self.mainFrame = None
        self.nameHeading = None
        self.speciesHeading = None
        self.laffHeading = None
        self.accessLevelHeading = None
        self.totalPopLabel = None

    def load(self):
        listGui = loader.loadModel('phase_3.5/models/gui/friendslist_gui')
        arrowButton = (
            listGui.find('**/FndsLst_ScrollUp'),
            listGui.find('**/FndsLst_ScrollDN'),
            listGui.find('**/FndsLst_ScrollUp_Rllvr'),
            listGui.find('**/FndsLst_ScrollUp')
        )
        incButtonScale = (1.3, 1.3, -1.3)
        decButtonScale = (1.3, 1.3, 1.3)
        headingTextScale = (0.05, 0.05, 0.05)

        self.mainFrame = DirectFrame(self, relief=None)

        self.nameHeading = TTLabel(
            self.mainFrame,
            relief=None,
            text=TTLocalizer.PlayerPageHeadingName,
            text_scale=headingTextScale,
            text_align=TextNode.ACenter,
            text_font=ToontownGlobals.getInterfaceFont(),
            pos=(-0.45, 0.0, 0.6)
        )
        '''
        self.speciesHeading = TTLabel(
            self.mainFrame,
            relief=None,
            text=TTLocalizer.PlayerPageHeadingSpecies,
            text_scale=headingTextScale,
            text_align=TextNode.ACenter,
            text_font=ToontownGlobals.getInterfaceFont(),
            pos=(-0.1, 0.0, 0.6)
        )
        '''
        self.laffHeading = TTLabel(
            self.mainFrame,
            relief=None,
            text=TTLocalizer.PlayerPageHeadingHealth,
            text_scale=headingTextScale,
            text_align=TextNode.ACenter,
            text_font=ToontownGlobals.getInterfaceFont(),
            pos=(0.1, 0.0, 0.6)
        )
        '''
        self.accessLevelHeading = TTLabel(
            self.mainFrame,
            relief=None,
            text=TTLocalizer.PlayerPageHeadingAccessLevel,
            text_scale=headingTextScale,
            text_align=TextNode.ACenter,
            text_font=ToontownGlobals.getInterfaceFont(),
            pos=(0.3, 0.0, 0.6)
        )
        '''
        self.totalPopLabel = OnscreenText(
            parent=self.mainFrame,
            text='',
            scale=0.06,
            wordwrap=30,
            align=TextNode.ACenter,
            font=ToontownGlobals.getInterfaceFont(),
            pos=(-0.3, -0.625, 0.0)
        )
        self.playerList = DirectScrolledList(
            parent=self.mainFrame,
            relief=None,
            pos=(0.0, 0.0, 0.0),
            numItemsVisible=10,
            forceHeight=0.11,
            items=self.playerListItems,
            frameSize=(-0.675, 0.675, -0.6, 0.6),

            incButton_image=arrowButton,
            incButton_relief=None,
            incButton_scale=incButtonScale,
            incButton_pos=(0.0, 0.0, -0.7),
            incButton_image3_color=Vec4(1, 1, 1, 0.2),

            decButton_image=arrowButton,
            decButton_relief=None,
            decButton_scale=decButtonScale,
            decButton_pos=(0.0, 0.0, 0.7),
            decButton_image3_color=Vec4(1, 1, 1, 0.2),

            itemFrame_relief=DGG.SUNKEN,
            itemFrame_frameSize=(-0.675, 0.675, -0.55, 0.55),
            itemFrame_frameColor=(0.85, 0.95, 1, 1),
            itemFrame_borderWidth=(0.0025, 0.0025)
        )
        listGui.removeNode()

    def update(self):
        for player in base.cr.playerManager.players:
            plItem = PlayerListItem(self.playerList, player, base.cr.playerManager.players.index(player))
            self.playerList.addItem(plItem, refresh=0)
            self.playerListItems.append(plItem)
        self.playerList.refresh()

    def unload(self):
        for plItem in self.playerListItems:
            plItem.destroy()
        if self.mainFrame is not None:
            self.mainFrame.destroy()
            self.mainFrame = None
        ShtikerPage.ShtikerPage.unload(self)

    def enter(self):
        base.cr.playerManager.d_getPlayerList()
        self.update()
        ShtikerPage.ShtikerPage.enter(self)


class PlayerListItem(DirectFrame):
    def __init__(self, parent, player, index):
        DirectFrame.__init__(self, parent)
        self.player = player

        frameColor = (0.9, 0.9, 0.9, 0)
        textScale = (0.06, 0.06)
        textColor = (0, 0, 0, 1)

        listFrameSize = self.parent['frameSize']
        if index % 2 == 0:
            frameColor = (0.9, 0.9, 0.9, 0)

        self.mainFrame = DirectFrame(
            self,
            relief=DGG.SUNKEN,
            pos=(0.0, 0.0, 0.49),
            borderWidth=(0.001, 0.001),
            frameSize=(listFrameSize[0], listFrameSize[1], -0.05, 0.05),
            frameColor=frameColor
        )
        self.nameLabel = TTLabel(
            self.mainFrame,
            pos=(-0.45, 0.0, 0),
            text=self.shortenedName,
            text_fg=textColor
        )
        '''
        self.speciesLabel = TTLabel(
            self.mainFrame,
            pos=(-0.45, 0.0, 0),
            text=self.player.species,
            text_fg=textColor,
        )
        '''
        self.laffLabel = TTLabel(
            self.mainFrame,
            pos=(-0.45, 0.0, 0),
            text=self.player.laff,
            text_fg=textColor
        )
        '''
        self.accessLabel = TTLabel(
            self.mainFrame,
            pos=(0.29, 0.0, -0.015),
            text=self.player.access,
            text_fg=textColor,
            text_scale=textScale
        )
        '''

    def destroy(self):
        if self.mainFrame is not None:
            self.mainFrame.destroy()
            self.mainFrame = None
        DirectFrame.destroy(self)

    @property
    def shortenedName(self):
        name = self.player.name
        if len(name) >= 20:
            name = '%s...' % name[0:20]
        return name
