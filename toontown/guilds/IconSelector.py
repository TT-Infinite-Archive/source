from direct.gui.DirectGui import DirectFrame, DirectButton, OnscreenText, DGG
from panda3d.core import TextNode

from toontown.data import IconGlobals
from toontown.toonbase import ToontownGlobals
from toontown.util import TTCardMaker


class IconSelectionDialog(DirectFrame):
    def __init__(self, parent, text, iconList, color=(1.0, 1.0, 1.0, 1.0), scale=(1.0, 1.0, 1.0), command=None):
        self._parent = parent
        self.text = text
        self.command = command
        self.iconList = iconList        # List of iconIds to display
        self.iconButtonList = []
        self.page = 1
        maxPerPage = 20
        maxPages = float(len(iconList) / maxPerPage)
        self.maxPages = int(maxPages + 1)

        DirectFrame.__init__(self, parent=self._parent, relief=None)

        background = TTCardMaker.makeCard('phase_3/maps/curved-gui-square.png')
        matchingGameGui = loader.loadModel('phase_3.5/models/gui/matching_game_gui')
        arrow = matchingGameGui.find('**/minnieArrow')

        self.mainFrame = DirectFrame(self._parent, relief=None, image=background, image_color=color, image_scale=(0.0008, 1, 0.0008), scale=scale)
        self.heading = OnscreenText(parent=self.mainFrame, text=self.text, scale=0.08, wordwrap=10, align=TextNode.ACenter, pos=(0.0, 0.5, 0.0), font=ToontownGlobals.getMinnieFont())
        self.previousPage = DirectButton(self.mainFrame, relief=None, geom=arrow, geom_scale=-0.4, pos=(-0.6, 0.0, -0.615), command=self.__handlePreviousPage)
        self.previousPage.bind(DGG.WITHIN, self.__handleEnter, extraArgs=[self.previousPage])
        self.previousPage.bind(DGG.WITHOUT, self.__handleExit, extraArgs=[self.previousPage])
        self.nextPage = DirectButton(self.mainFrame, relief=None, geom=arrow, geom_scale=0.4, pos=(0.6, 0.0, -0.615), command=self.__handleNextPage)
        self.nextPage.bind(DGG.WITHIN, self.__handleEnter, extraArgs=[self.nextPage])
        self.nextPage.bind(DGG.WITHOUT, self.__handleExit, extraArgs=[self.nextPage])
        self.loadIcons(self.iconList, self.page)
        # We are on page 1, you cant go back
        self.disableButton(self.previousPage)
        if self.page == self.maxPages:
            # We are on the last page, you cant go forward
            self.disableButton(self.nextPage)

    def loadIcons(self, iconList, page):
        self.unloadIcons()
        xStart = -0.5
        xMax = 5
        xMaxThisPage = xMax * page
        xCount = xMax * (page - 1)
        xSpace = 0.25
        x = xStart
        yStart = 0.3
        yMax = 4
        yMaxThisPage = yMax * page
        yCount = yMax * (page - 1)
        ySpace = 0.25
        y = yStart
        itemsPerPage = xMax * yMax
        index = itemsPerPage * (page - 1)

        while yCount < yMaxThisPage:
            if index < len(iconList):
                iconId = iconList[index]
            else:
                iconId = 0
            pos = (x, 0.0, y)
            icon = IconSelector(self.mainFrame, iconId, pos, (1.0, 1.0, 1.0, 1.0), self.handleIconSelected)
            self.iconButtonList.append(icon)
            index += 1
            x += xSpace
            xCount += 1
            if xCount == xMaxThisPage:
                xCount = xMax * (page - 1)
                x = xStart
                y -= ySpace
                yCount += 1
                if yCount == yMaxThisPage:
                    return

    def unloadIcons(self):
        for icon in self.iconButtonList:
            icon.destroy()
        del self.iconButtonList[:]
        self.iconButtonList = []

    def destroy(self):
        self._parent = None
        self.mainFrame.destroy()
        DirectFrame.destroy(self)

    def handleIconSelected(self, iconId):
        if self.command is not None:
            self.command(iconId)
        self.destroy()

    def __handlePreviousPage(self):
        if self.page == 1:
            self.page = 1
        else:
            self.page -= 1

        if self.page == 1:
            self.disableButton(self.previousPage)
        else:
            self.enableButton(self.previousPage)
        
        if self.page != self.maxPages:
            self.enableButton(self.nextPage)
            
        self.loadIcons(self.iconList, self.page)

    def __handleNextPage(self):
        if self.page == self.maxPages:
            self.page = self.maxPages
        else:
            self.page += 1

        if self.page == self.maxPages:
            self.disableButton(self.nextPage)
        else:
            self.enableButton(self.nextPage)
        
        if self.page != 1:
            self.enableButton(self.previousPage)

        self.loadIcons(self.iconList, self.page)

    def disableButton(self, button):
        button['state'] = DGG.DISABLED
        button.setColorScale(1.0, 1.0, 1.0, 0.2)

    def enableButton(self, button):
        button['state'] = DGG.NORMAL
        button.setColorScale(1.0, 1.0, 1.0, 1.0)

    def __handleEnter(self, button, e):
        button['geom_color'] = (1, 1, 0.2, 1.0)

    def __handleExit(self, button, e):
        button['geom_color'] = (1, 1, 1, 1)


class IconSelector(DirectButton):
    def __init__(self, parent, iconId, pos, color, command):

        self._parent = parent
        self.iconId = iconId
        self.pos = pos
        self.command = command
        self.color = color

        DirectButton.__init__(self, parent, relief=None, pos=pos)

        background = TTCardMaker.makeCard('phase_3/maps/gui-circle.png')

        # Use icon Id to load this
        icon = IconGlobals.ICON_REPOSITORY.get(iconId)

        self.mainButton = DirectButton(
            self,
            relief=None,
            image=background,
            image_color=color,
            image_scale=(0.0025, 1, 0.0025),
            command=self.__handleClick
        )
        self.mainButton.bind(DGG.WITHIN, self.__handleEnter)
        self.mainButton.bind(DGG.WITHOUT, self.__handleExit)
        if icon is not None:
            self.icon = DirectButton(
                self.mainButton, relief=None, image=icon.icon, suppressMouse=True, state=DGG.DISABLED
            )
        else:
            self.disable()

    def destroy(self):
        self._parent = None
        self.command = None
        if self.mainButton is not None:
            self.mainButton.destroy()
            self.mainButton = None
        DirectButton.destroy(self)

    def disable(self):
        self.mainButton['state'] = DGG.DISABLED
        self.mainButton['image_color'] = (self.color[0], self.color[1], self.color[2], 0.3)

    def enable(self):
        self.mainButton['state'] = DGG.NORMAL
        self.mainButton['image_color'] = self.color

    def __handleClick(self):
        self.command(self.iconId)
        self.destroy()

    def __handleEnter(self, e):
        self.mainButton['image_color'] = (1, 1, 0.2, 1.0)

    def __handleExit(self, e):
        self.mainButton['image_color'] = (1, 1, 1, 1.0)
