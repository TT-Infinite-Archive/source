from direct.gui.DirectGui import DirectFrame, DirectButton, DirectLabel, DirectScrolledList, DGG
from panda3d.core import CardMaker, TransparencyAttrib, NodePath, Vec4, TextNode
from toontown.toonbase import ToontownGlobals, TTLocalizer, EventGlobals


class GuildLeaderboard(DirectFrame):
    def __init__(self, parent, text, pos=(0.0, 0.0, 0.0), scale=(1.0, 1.0, 1.0), backCommand=None):
        self.parent = parent
        self.text = text
        self.scale = scale
        self.pos = pos
        DirectFrame.__init__(self, parent=parent, relief=None, pos=pos, scale=scale)

        self.entries = []
        
        listGui = loader.loadModel('phase_3.5/models/gui/friendslist_gui')
        arrowButton = (listGui.find('**/FndsLst_ScrollUp'), listGui.find('**/FndsLst_ScrollDN'), listGui.find('**/FndsLst_ScrollUp_Rllvr'), listGui.find('**/FndsLst_ScrollUp'))
        matchingGameGui = loader.loadModel('phase_3.5/models/gui/matching_game_gui')
        mArrow = (matchingGameGui.find('**/*minnieArrow'), matchingGameGui.find('**/*minnieArrow'), matchingGameGui.find('**/*minnieArrow'))
        incButtonScale = (1.3, 1.3, -1.3)
        decButtonScale = (1.3, 1.3, 1.3)
        primaryColor = (0.75, 0.85, 1, 1)
        secondaryColor = (0.5, 0.6, 1, 1)
        self.buttonColor = secondaryColor

        filepath = 'phase_3/maps/curved-gui-square.png'
        tex = loader.loadTexture(filepath)
        cm = CardMaker(filepath + ' card')
        cm.setFrame(-tex.getOrigFileXSize(), tex.getOrigFileXSize(), -tex.getOrigFileYSize(), tex.getOrigFileYSize())

        background = NodePath(cm.generate())
        background.setTexture(tex)
        background.setTransparency(TransparencyAttrib.MAlpha)
        
        self.mainFrame = DirectFrame(self.parent, relief=None, image=background, image_scale=(0.0009, 1, 0.0009), image_color=primaryColor, scale=scale, pos=pos)
        self.title = DirectLabel(self.mainFrame, relief=None, pos=(0.0, 0.0, 0.65), text=text, text_scale=(0.06, 0.1, 0.5), text_font=ToontownGlobals.getMinnieFont())
        
        self.entryList = DirectScrolledList(parent=self.mainFrame,
                                            relief=None,
                                            pos=(0.0, 0.0, 0.0),
                                            numItemsVisible=10,
                                            forceHeight=0.11,
                                            items=self.entries,
                                            frameSize=(-0.675, 0.675, -0.6, 0.6),

                                            incButton_image=arrowButton,
                                            incButton_relief=None,
                                            incButton_scale=incButtonScale,
                                            incButton_pos=(0.0, 0.0, -0.65),
                                            incButton_image3_color=Vec4(1, 1, 1, 0),

                                            decButton_image=arrowButton,
                                            decButton_relief=None,
                                            decButton_scale=decButtonScale,
                                            decButton_pos=(0.0, 0.0, 0.65),
                                            decButton_image3_color=Vec4(1, 1, 1, 0),

                                            itemFrame_relief=DGG.SUNKEN,
                                            itemFrame_frameSize=(-0.675, 0.675, -0.55, 0.55),
                                            itemFrame_frameColor=(0.85, 0.95, 1, 1),
                                            itemFrame_borderWidth=(0.0025, 0.0025))

        self.backToGuild = DirectButton(self.mainFrame, relief=None, image=mArrow, image_scale=(-1, -0.65, -1), image_color=self.buttonColor, pos=(-0.6, 0.0, -0.95), text=TTLocalizer.GuildLeaderboardBack, text_scale=(0.06, 0.08), text_pos=(0.02, -0.03, 0.0), command=backCommand)
        self.backToGuild.bind(DGG.WITHIN, self.__handleEnter, extraArgs=[self.backToGuild])
        self.backToGuild.bind(DGG.WITHOUT, self.__handleExit, extraArgs=[self.backToGuild])
        listGui.removeNode()
        matchingGameGui.removeNode()

        self.statusMessage = DirectLabel(self.mainFrame, relief=None, text='', text_scale=(0.06, 0.1, 0.5))

        self.accept(EventGlobals.GotLeaderboardInfo, self.updateEntries)

        self.enterLeaderboard()

    def destroy(self):
        self.exitLeaderboard()

        if self.mainFrame is not None:
            self.mainFrame.destroy()
            self.mainFrame = None

        DirectFrame.destroy(self)

    def enterLeaderboard(self):
        base.cr.guildManager.enterLeaderboard()
        self.setStatusMessage(TTLocalizer.lLoading)
        taskMgr.doMethodLater(10, self.timedOutTask, 'leaderboardTimedOutTask')

    def exitLeaderboard(self):
        base.cr.guildManager.exitLeaderboard()
        taskMgr.remove('leaderboardTimedOutTask')
        self.ignore(EventGlobals.GotLeaderboardInfo)

    def updateEntries(self):
        taskMgr.remove('leaderboardTimedOutTask')
        self.setStatusMessage('')
        self.entryList.removeAllItems()
        entries = base.cr.guildManager.leaderboardRankEntries
        if len(entries) == 0:
            self.setStatusMessage(TTLocalizer.GuildLeaderboardNoEntries)
        for index, entry in enumerate(entries):
            id = entry[0]
            name = entry[1]
            points = entry[2]
            thisEntry = LeaderboardEntry(self, id, index + 1, name, points, index, self.entryList)
            self.entries.append(thisEntry)
            self.entryList.addItem(thisEntry)

    def timedOutTask(self, task=None):
        self.setStatusMessage(TTLocalizer.GuildLeaderboardTimedOut)

    def setStatusMessage(self, text):
        if text == '':
            self.statusMessage.hide()
        else:
            self.statusMessage['text'] = text
            self.statusMessage.show()

    def __handleEnter(self, button, e):
        button['image_color'] = (1, 1, 0.2, 1.0)

    def __handleExit(self, button, e):
        button['image_color'] = self.buttonColor

class LeaderboardEntry(DirectButton):
    def __init__(self, parent, doId, rank, name, points, index, listObject):
        self.parent = parent
        self.doId = doId
        self.rank = rank
        self.name = name
        self.points = points

        frameColor = (0.5, 0.6, 1, 0.2)
        textScale = (0.04, 0.06)
        textColor = (0, 0, 0, 1)

        if index % 2 == 0:
            frameColor = (0.5, 0.6, 1, 0.1)

        listFrameSize = listObject['frameSize']

        DirectButton.__init__(self, listObject, relief=None, frameSize=listFrameSize)
        self.mainFrame = DirectFrame(self, relief=DGG.SUNKEN, pos=(0.0, 0.0, 0.49), borderWidth=(0.001, 0.001), frameSize=(listFrameSize[0], listFrameSize[1], -0.05, 0.05), frameColor=frameColor)
        self.rankLabel = DirectLabel(self.mainFrame, relief=None, pos=(-0.6, 0.0, -0.025), text=str(rank)+'.', text_fg=(0.0, 0.4, 1.0, 1.0), text_scale=(0.06, 0.08), text_align=TextNode.ACenter, text_font=ToontownGlobals.getMinnieFont())
        self.nameLabel = DirectLabel(self.mainFrame, relief=None, pos=(-0.525, 0.0, -0.01), text=name, text_fg=textColor, text_scale=textScale, text_align=TextNode.ABoxedLeft)
        self.pointsLabel = DirectLabel(self.mainFrame, relief=None, pos=(0.55, 0.0, -0.01), text=str(points), text_fg=textColor, text_scale=textScale, text_align=TextNode.ACenter)

    def destroy(self):
        self.ignoreAll()

        self.mainFrame.destroy()
        del self.mainFrame

        DirectButton.destroy(self)