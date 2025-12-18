from direct.directnotify import DirectNotifyGlobal
from direct.gui.DirectGui import *
from direct.task.Task import Task
from pandac.PandaModules import *
from toontown.distributed import ToontownDistrictStats
from toontown.hood import ZoneUtil
from toontown.shtiker import ShtikerPage
from toontown.toonbase import TTLocalizer, EventGlobals, ToontownGlobals
from toontown.toontowngui import WarningDialog

POP_COLORS = (
    Vec4(0.4, 0.4, 1.0, 1.0),
    Vec4(0.4, 1.0, 0.4, 1.0),
    Vec4(1.0, 0.4, 0.4, 1.0)
)


def compareShardTuples(a, b):
    if a[1] < b[1]:
        return -1
    elif b[1] < a[1]:
        return 1
    else:
        return 0


class ShardPage(ShtikerPage.ShtikerPage):
    notify = DirectNotifyGlobal.directNotify.newCategory('ShardPage')

    def __init__(self):
        ShtikerPage.ShtikerPage.__init__(self)

        self.ShardInfoUpdateInterval = 5.0
        self.showTotalPop = config.GetBool('show-total-population', 0)
        self.midPop = config.GetInt('shard-mid-pop', 300)
        self.highPop = -1

        self.shards = []

        self.mainFrame = None
        self.nameHeading = None
        self.invasionLabel = None
        self.popLabel = None
        self.timezoneLabel = None
        self.totalPopLabel = None
        self.shardList = None

    def load(self):
        self.clearPage()
        listGui = loader.loadModel('phase_3.5/models/gui/friendslist_gui')
        arrowButton = (listGui.find('**/FndsLst_ScrollUp'), listGui.find('**/FndsLst_ScrollDN'), listGui.find('**/FndsLst_ScrollUp_Rllvr'), listGui.find('**/FndsLst_ScrollUp'))
        incButtonScale = (1.3, 1.3, -1.3)
        decButtonScale = (1.3, 1.3, 1.3)
        headingTextScale = (0.05, 0.05, 0.05)

        self.mainFrame = DirectFrame(self, relief=None)

        self.nameHeading = DirectLabel(
            self.mainFrame,
            relief=None,
            text=TTLocalizer.ShardPageHeadingName,
            text_scale=headingTextScale,
            text_align=TextNode.ACenter,
            text_font=ToontownGlobals.getInterfaceFont(),
            pos=(-0.45, 0.0, 0.6)
        )
        self.invasionLabel = DirectLabel(
            self.mainFrame,
            relief=None,
            text=TTLocalizer.ShardPageHeadingInvasion,
            text_scale=headingTextScale,
            text_align=TextNode.ACenter,
            text_font=ToontownGlobals.getInterfaceFont(),
            pos=(-0.1, 0.0, 0.6)
        )
        self.popLabel = DirectLabel(
            self.mainFrame,
            relief=None,
            text=TTLocalizer.ShardPageHeadingPop,
            text_scale=headingTextScale,
            text_align=TextNode.ACenter,
            text_font=ToontownGlobals.getInterfaceFont(),
            pos=(0.1, 0.0, 0.6)
        )
        self.timezoneLabel = DirectLabel(
            self.mainFrame,
            relief=None,
            text=TTLocalizer.ShardPageHeadingTimezone,
            text_scale=headingTextScale,
            text_align=TextNode.ACenter,
            text_font=ToontownGlobals.getInterfaceFont(),
            pos=(0.3, 0.0, 0.6)
        )
        self.totalPopLabel = OnscreenText(
            parent=self.mainFrame,
            text='',
            scale=0.06,
            wordwrap=30,
            align=TextNode.ACenter,
            font=ToontownGlobals.getInterfaceFont(),
            pos=(-0.3, -0.625, 0.0)
        )
        self.shardList = DirectScrolledList(
            parent=self.mainFrame,
            relief=None,
            pos=(0.0, 0.0, 0.0),
            numItemsVisible=10,
            forceHeight=0.11,
            items=self.shards,
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
        self.unsupportedWarning = OnscreenText(
            parent=self.mainFrame,
            text=TTLocalizer.ShardPageUnsupported,
            scale=0.06,
            wordwrap=20,
            align=TextNode.ACenter,
            font=ToontownGlobals.getInterfaceFont(),
            fg=(1, 0, 0, 1),
            pos=(0, -0.4, 0.0)
        )
        self.updateEntries()

        listGui.removeNode()
        for item in arrowButton:
            item.removeNode()

    def updateEntries(self):
        selectedIndex = 0
        if self.shardList:
            selectedIndex = self.shardList.getSelectedIndex()
            self.shardList.removeAllItems()

        curShardTuples = base.cr.listActiveShards()
        curShardTuples.sort(compareShardTuples)
        totalPop = 0

        for i in range(len(curShardTuples)):
            shardId, name, pop, WVPop, invasionStatus, timeZone = curShardTuples[i]

            # Get the formatted timezone string
            timezone = base.cr.shardTimeManager.formatTimeZone(timeZone)

            # Accumulate our total population
            totalPop += pop

            # Make our shard widget
            shardWidget = ShardWidget(render2d, shardId, name, invasionStatus, pop, timezone, i, self.shardList)
            self.shards.append(shardWidget)
            self.shardList.addItem(shardWidget)

        self.totalPopLabel['text'] = TTLocalizer.ShardPagePopulationTotal % totalPop

        if self.shardList:
            self.shardList.scrollTo(selectedIndex)

    def clearPage(self):
        for shard in self.shards:
            shard.destroy()

        del self.shards[:]
        self.shards = []

        if self.mainFrame is not None:
            self.mainFrame.destroy()
            self.mainFrame = None

    def unload(self):
        self.ignore(EventGlobals.ShardInfoUpdated)
        taskMgr.remove('ShardPageUpdateTask-doLater')
        self.clearPage()
        ShtikerPage.ShtikerPage.unload(self)

    def enter(self):
        self.askForShardInfoUpdate()
        self.updateEntries()
        currentShardId = self.getCurrentShardId()
        for index, shard in enumerate(self.shards):
            if self.shardList is not None and shard.shardId == currentShardId:
                self.shardList.scrollTo(index, centered=1)

        ShtikerPage.ShtikerPage.enter(self)
        self.accept(EventGlobals.ShardInfoUpdated, self.updateEntries)

    def exit(self):
        self.ignore(EventGlobals.ShardInfoUpdated)
        taskMgr.remove('ShardPageUpdateTask-doLater')

        ShtikerPage.ShtikerPage.exit(self)

    def askForShardInfoUpdate(self, task=None):
        ToontownDistrictStats.refresh('shardInfoUpdated')
        taskMgr.doMethodLater(self.ShardInfoUpdateInterval, self.askForShardInfoUpdate, 'ShardPageUpdateTask-doLater')
        return Task.done

    def getCurrentShardId(self):
        return base.localAvatar.defaultShard


class ShardWidget(DirectButton):
    def __init__(self, parent, shardId, shardName, invasion, population, timezone, index, listObject):
        self._parent = parent
        self.shardId = shardId
        self.shardName = shardName
        self.invasion = invasion            # [CogDeptIndex, CogSuitIndex]
        self.population = population
        self.listObject = listObject

        self.lowPop = config.GetInt('shard-low-pop', 150)
        self.midPop = config.GetInt('shard-mid-pop', 300)
        self.noTeleport = config.GetBool('shard-page-disable', 0)

        frameColor = (0.9, 0.9, 0.9, 0)
        self.timezone = timezone
        textScale = (0.06, 0.06)
        activeTextColor = (0.4, 0.8, 0.4, 1)
        textColor = (0, 0, 0, 1)
        self.buttonColor = (0.65, 0.75, 1.0, 1.0)
        icons = loader.loadModel('phase_3/models/gui/cog_icons')

        listFrameSize = listObject['frameSize']
        matchingGameGui = loader.loadModel('phase_3.5/models/gui/matching_game_gui')
        if index % 2 == 0:
            frameColor = (0.9, 0.9, 0.9, 0)
        pointingArrowButton = (matchingGameGui.find('**/*minnieArrow'), matchingGameGui.find('**/*minnieArrow'), matchingGameGui.find('**/*minnieArrow'))

        shardButton = matchingGameGui.find('**/minnieCircle')

        DirectButton.__init__(self, listObject, relief=None, frameSize=listFrameSize)
        self.mainFrame = DirectFrame(self, relief=DGG.SUNKEN, pos=(0.0, 0.0, 0.49), borderWidth=(0.001, 0.001), frameSize=(listFrameSize[0], listFrameSize[1], -0.05, 0.05), frameColor=frameColor)
        self.nameLabel = DirectLabel(self.mainFrame, relief=None, pos=(-0.45, 0.0, 0), text=shardName, text_fg=textColor, text_scale=self.getShardNameScale(shardName), text_pos=(0.0, -0.015, 0.0), text_align=TextNode.ACenter)
        self.invasionLabel = DirectButton(self.mainFrame, relief=None, text_scale=0.06, pos=(-0.1, 0.0, 0), text_pos=(0.0, -0.015, 0.0), image_pos=(0.0, 0.0, 0.1))
        self.populationLabel = DirectButton(self.mainFrame, relief=None, image=(shardButton, None, None, shardButton), image_scale=(0.35, 1, 0.35), image_color=self.getPopColor(self.population), pos=(0.11, 0.0, 0.0), text=('', self.getPopText(self.population, 1), self.getPopText(self.population, 1), ''), text_pos=(-0.01, -0.0125), text_fg=textColor, text_scale=textScale, text_align=TextNode.ACenter)
        self.timezoneLabel = DirectLabel(self.mainFrame, relief=None, pos=(0.29, 0.0, -0.015), text=timezone, text_fg=textColor, text_scale=textScale, text_align=TextNode.ACenter)
        self.goToButton = DirectButton(self.mainFrame, relief=None, pos=(0.525, 0.0, 0.0), geom=pointingArrowButton, geom_scale=0.3, geom_color=self.buttonColor, command=self.handleSelectShard)

        self.reject = None
        self.invasionDisplay = None
        icon = None

        self.goToButton.bind(DGG.WITHIN, self.__handleEnter, extraArgs=[self.goToButton])
        self.goToButton.bind(DGG.WITHOUT, self.__handleExit, extraArgs=[self.goToButton])
        if self.invasion is None or len(self.invasion) == 0:
            self.invasionLabel['text'] = TTLocalizer.ShardPageNoInvasion
            self.invasionLabel['text_scale'] = textScale
            self.invasionLabel['text_pos'] = (0.0, -0.02, 0.0)
        else:
            cogDeptIndex = invasion[0]
            if cogDeptIndex == 0:
                icon = icons.find('**/CorpIcon')
            elif cogDeptIndex == 1:
                icon = icons.find('**/LegalIcon')
            elif cogDeptIndex == 2:
                icon = icons.find('**/MoneyIcon')
            else:
                icon = icons.find('**/SalesIcon')
            self.invasionLabel['geom'] = icon
            self.invasionLabel['geom_scale'] = 0.055
            self.invasionLabel['geom_pos'] = (0.0, 0.0, 0.0)

        #node = NodePath()
        #head = Suit.attachSuitHead(node, self.invasion)
        #head.detachNode()
        #head.setDepthTest(True)
        #head.setDepthWrite(True)
        #self.invasionLabel['image'] = head
        #self.invasionLabel['image_scale'] = 0.05
        #self.invasionLabel['image_pos'] = (0.0, 0.0, -0.025)
        #node.removeNode()

        # We're in this district, highlight stuff, disable button
        if self.shardId == self.getCurrentShardId():
            self.goToButton['state'] = DGG.DISABLED
            self.goToButton['geom_color'] = (0.65, 0.75, 1.0, 0.2)
            self.nameLabel['text_fg'] = activeTextColor

        matchingGameGui.removeNode()
        shardButton.removeNode()
        for item in pointingArrowButton:
            item.removeNode()
        icons.removeNode()
        if icon is not None:
            icon.removeNode()

    def destroy(self):
        self._parent = None
        if self.mainFrame is not None:
            self.mainFrame.destroy()
            self.mainFrame = None

    def getShardNameScale(self, shardName):
        if len(shardName) >= 20:
            return 0.05, 0.05
        elif len(shardName) >= 15:
            return 0.055, 0.055
        else:
            return 0.06, 0.06
    def getPopColor(self, pop):
        if pop <= self.lowPop:
            newColor = POP_COLORS[0]
        elif pop <= self.midPop:
            newColor = POP_COLORS[1]
        else:
            newColor = POP_COLORS[2]
        return newColor

    def getPopText(self, pop, flag=0):
        if flag == 1:
            popText = str(pop)
        elif pop <= self.lowPop:
            popText = TTLocalizer.ShardPageLow
        elif pop <= self.midPop:
            popText = TTLocalizer.ShardPageMed
        else:
            popText = TTLocalizer.ShardPageHigh
        return popText

    def getCurrentShardId(self):
        return base.localAvatar.defaultShard

    def handleSelectShard(self):
        canonicalHoodId = ZoneUtil.getCanonicalHoodId(base.localAvatar.lastHood)
        currentShardId = self.getCurrentShardId()
        if self.reject is not None:
            self.reject.destroy()

        if self.noTeleport:
            self.reject = WarningDialog.WarningDialog(parent=self.listObject, text=TTLocalizer.ShardPageChoiceRejectNoTeleport)
            return
        elif self.shardId == currentShardId:
            self.reject = WarningDialog.WarningDialog(parent=self.listObject, text=TTLocalizer.ShardPageChoiceRejectAlreadyIn)
            return
        elif self.population > self.midPop:
            self.reject = WarningDialog.WarningDialog(parent=self.listObject, text=TTLocalizer.ShardPageChoiceRejectFull)
            return
        elif self.shardId == base.localAvatar.defaultShard:
            self.doneStatus = {'mode': 'teleport', 'hood': canonicalHoodId}
            messenger.send(self.doneEvent)
        else:
            try:
                place = base.cr.playGame.getPlace()
            except:
                try:
                    place = base.cr.playGame.hood.loader.place
                except:
                    place = base.cr.playGame.hood.place

            place.requestTeleport(canonicalHoodId, canonicalHoodId, self.shardId, -1)

    def __handleEnter(self, button, e):
        button['geom_color'] = (1, 1, 0.2, 1.0)

    def __handleExit(self, button, e):
        button['geom_color'] = self.buttonColor
