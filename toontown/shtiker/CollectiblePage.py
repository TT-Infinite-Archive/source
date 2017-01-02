from pandac.PandaModules import *
from direct.gui.DirectGui import DirectFrame, DirectLabel, DirectScrolledList, DGG, DirectButton
from toontown.collectibles import CollectibleGlobals
from toontown.collectibles.CollectibleInventoryGlobals import DefaultItems
from toontown.toonbase import TTLocalizer, EventGlobals
from toontown.shtiker import ShtikerPage
from toontown.util import TTCardMaker


class CollectiblePage(ShtikerPage.ShtikerPage):
    notify = directNotify.newCategory('CollectiblePage')
    CollectiblePageCollectibles = 0
    CollectiblePageItems = 1

    def __init__(self):
        ShtikerPage.ShtikerPage.__init__(self)
        self.avatar = None
        self.mode = self.CollectiblePageCollectibles
        self.title = None
        self.pageContent = None
        self.collectibleTab = None
        self.itemsTab = None

    def enter(self):
        self.setMode(self.mode)
        ShtikerPage.ShtikerPage.enter(self)

    def exit(self):
        if self.pageContent is not None:
            self.pageContent.destroy()
            self.pageContent = None

        ShtikerPage.ShtikerPage.exit(self)

    def load(self):
        ShtikerPage.ShtikerPage.load(self)
        gui = loader.loadModel('phase_3.5/models/gui/fishingBook')
        self.title = DirectLabel(parent=self, relief=None, text=TTLocalizer.CollectiblePageTitle, text_scale=0.1, pos=(0, 0, 0.65))
        normalColor = (1, 1, 1, 1)
        clickColor = (0.8, 0.8, 0, 1)
        rolloverColor = (0.15, 0.82, 1.0, 1)
        diabledColor = (1.0, 0.98, 0.15, 1)
        self.collectibleTab = DirectButton(
            parent=self,
            relief=None,
            text=TTLocalizer.CollectiblePageCollectiblesTab,
            text_scale=0.065,
            text_align=TextNode.ALeft,
            text_pos=(-0.025, 0.0, 0.0),
            image=gui.find('**/tabs/polySurface1'),
            image_pos=(0.55, 1, -0.91),
            image_hpr=(0, 0, -90),
            image_scale=(0.033, 0.033, 0.035),
            image_color=normalColor,
            image1_color=clickColor,
            image2_color=rolloverColor,
            image3_color=diabledColor,
            text_fg=Vec4(0.2, 0.1, 0, 1),
            command=self.setMode,
            extraArgs=[self.CollectiblePageCollectibles],
            pos=(0.92, 0, 0.1)
        )
        self.itemsTab = DirectButton(
            parent=self,
            relief=None,
            text=TTLocalizer.CollectiblePageItemsTab,
            text_scale=0.07,
            text_align=TextNode.ALeft,
            text_pos=(0.02, 0.0, 0.0),
            image=gui.find('**/tabs/polySurface2'),
            image_pos=(0.12, 1, -0.91),
            image_hpr=(0, 0, -90),
            image_scale=(0.033, 0.033, 0.035),
            image_color=normalColor,
            image1_color=clickColor,
            image2_color=rolloverColor,
            image3_color=diabledColor,
            text_fg=Vec4(0.2, 0.1, 0, 1),
            command=self.setMode,
            extraArgs=[self.CollectiblePageItems],
            pos=(0.92, 0, 0.1)
        )
        self.collectibleTab.setPos(-0.3, 0, 0.775)
        self.itemsTab.setPos(0.1, 0, 0.775)
        gui.removeNode()

    def unload(self):
        if self.pageContent is not None:
            self.pageContent.destroy()
            self.pageContent = None

        ShtikerPage.ShtikerPage.unload(self)

    def setMode(self, mode):
        messenger.send(EventGlobals.WakeUp)
        if self.pageContent is not None:
            self.pageContent.destroy()
            self.pageContent = None
        if mode == self.CollectiblePageCollectibles:
            self.title['text'] = TTLocalizer.CollectiblePageTitle
            self.pageContent = CollectibleCategoryItemsDisplay(self, CollectibleGlobals.CollectibleCategories)
        elif mode == self.CollectiblePageItems:
            self.title['text'] = TTLocalizer.CollectiblePageItemsTab
            self.pageContent = CategoryItemsDisplay(self, CollectibleGlobals.CollectibleItems)
        else:
            self.notify.debug('Unknown mode %d' % mode)
            return
        self.mode = mode


class CategoryItemsDisplay(DirectFrame):
    notify = directNotify.newCategory('CategoryItemsDisplay')
    itemPositions = [
        (-0.3, 0.0, 0.3),
        (0.0, 0.0, 0.3),
        (0.3, 0.0, 0.3),
        (-0.3, 0.0, 0.0),
        (0.0, 0.0, 0.0),
        (0.3, 0.0, 0.0),
        (-0.3, 0.0, -0.3),
        (0.0, 0.0, -0.3),
        (0.3, 0.0, -0.3)
    ]
    maxPerPage = 9

    def __init__(self, parent, cItems):
        DirectFrame.__init__(self, parent=parent)
        self.parent = parent
        self.cItems = cItems

        self.items = []
        self.categories = []

        self.currentCat = None
        self.currentPage = None

        listGui = loader.loadModel('phase_3.5/models/gui/friendslist_gui.bam')
        gui = loader.loadModel('phase_3/models/gui/tt_m_gui_mat_mainGui.bam')
        arrowUp = gui.find('**/tt_t_gui_mat_shuffleArrowUp')
        arrowDown = gui.find('**/tt_t_gui_mat_shuffleArrowDown')
        arrowRollover = gui.find('**/tt_t_gui_mat_shuffleArrowUp')
        arrowDisabled = gui.find('**/tt_t_gui_mat_shuffleArrowDisabled')
        halfButtonScale = (0.6, 0.6, 0.6)
        halfButtonHoverScale = (0.7, 0.7, 0.7)
        halfButtonInvertScale = (-0.6, 0.6, 0.6)
        halfButtonInvertHoverScale = (-0.7, 0.7, 0.7)
        arrowButton = (
            listGui.find('**/FndsLst_ScrollUp'),
            listGui.find('**/FndsLst_ScrollDN'),
            listGui.find('**/FndsLst_ScrollUp_Rllvr'),
            listGui.find('**/FndsLst_ScrollUp')
        )
        incButtonScale = (1.3, 1.3, -1.3)
        decButtonScale = (1.3, 1.3, 1.3)

        background = TTCardMaker.makeCard('phase_3/maps/curved-gui-square.png')

        # Main
        self.mainFrame = DirectFrame(
            self.parent,
            relief=DGG.FLAT,
            scale=1.0,
            image_color=(1.0, 1.0, 1.0, 1.0),
            image_scale=(0.0009, 1, 0.0009)
        )
        # Items (Left)
        self.itemsFrame = DirectFrame(
            self.mainFrame,
            relief=None,
            pos=(-0.25, 0.0, 0.0),
            image=background,
            image_color=(1.0, 1.0, 1.0, 1.0),
            image_scale=(0.0006, 1, 0.0007)
        )
        self.itemsHeading = DirectLabel(
            self.itemsFrame,
            text='',
            text_scale=0.06,
            pos=(0.0, 0.0, 0.5)
        )
        self.itemsPageCounter = DirectLabel(
            self.itemsFrame,
            relief=None,
            text='',
            text_scale=0.06,
            pos=(0.0, 0.0, -0.515)
        )
        self.itemsPagePrev = DirectButton(
            self.itemsFrame,
            relief=None,
            image=(arrowUp, arrowDown, arrowRollover, arrowDisabled),
            image_scale=halfButtonScale,
            image1_scale=halfButtonHoverScale,
            image2_scale=halfButtonHoverScale,
            pos=(-0.2, 0.0, -0.5),
            command=self.__handlePrevClicked
        )
        self.itemsPageNext = DirectButton(
            self.itemsFrame,
            relief=None,
            image=(arrowUp, arrowDown, arrowRollover, arrowDisabled),
            image_scale=halfButtonInvertScale,
            image1_scale=halfButtonInvertHoverScale,
            image2_scale=halfButtonInvertHoverScale,
            pos=(0.2, 0.0, -0.5),
            command=self.__handleNextClicked
        )
        # Categories (Right)
        self.categoryFrame = DirectFrame(
            self.mainFrame,
            relief=None,
            pos=(0.55, 0.0, 0.0),
            image=background,
            image_color=(1.0, 1.0, 1.0, 1.0),
            image_scale=(0.00027, 1, 0.0007)
        )
        self.categoryList = DirectScrolledList(
            parent=self.categoryFrame,
            relief=DGG.SUNKEN,
            numItemsVisible=10,
            forceHeight=0.1,
            items=self.categories,
            frameSize=(-0.2, 0.2, -0.5, 0.4),
            frameColor=(0.85, 0.95, 1, 1.0),
            borderWidth=(0.0025, 0.0025),

            incButton_image=arrowButton,
            incButton_relief=None,
            incButton_scale=incButtonScale,
            incButton_pos=(0.0, 0.0, -0.55),
            incButton_image3_color=Vec4(1, 1, 1, 0.2),

            decButton_image=arrowButton,
            decButton_relief=None,
            decButton_scale=decButtonScale,
            decButton_pos=(0.0, 0.0, 0.45),
            decButton_image3_color=Vec4(1, 1, 1, 0.2),

            itemFrame_relief=DGG.SUNKEN,
            itemFrame_frameSize=(-0.2, 0.2, -0.5, 0.4),
            itemFrame_frameColor=(0.85, 0.95, 1, 0.0),
            itemFrame_pos=(0.0, 0.0, 0.3),
            itemFrame_borderWidth=(0.0025, 0.0025)
        )
        self.categoryHeading = DirectLabel(
            self.categoryFrame,
            relief=None,
            text=TTLocalizer.lCategories,
            text_scale=0.06,
            pos=(0.0, 0.0, 0.5)
        )
        self.loadCategories()
        self.loadItems(self.cItems.values()[0], 0)

        listGui.removeNode()
        gui.removeNode()
        background.removeNode()

        self.acceptUpdates()

    def destroy(self):
        self.ignoreUpdates()
        if self.mainFrame is not None:
            self.mainFrame.destroy()
            self.mainFrame = None
        DirectFrame.destroy(self)

    def acceptUpdates(self):
        self.accept(EventGlobals.CollectibleInventoryUpdated, self.__handleItemUpdated)

    def ignoreUpdates(self):
        self.ignore(EventGlobals.CollectibleInventoryUpdated)

    def loadCategories(self):
        for catKey in self.cItems:
            category = self.cItems[catKey]
            frameSize = self.categoryList['frameSize']
            # Button to select which category
            categoryItem = DirectButton(
                self.categoryList,
                relief=None,
                text=category.name,
                text_scale=0.06,
                frameSize=(frameSize[0], frameSize[1], -0.05, 0.05),
                frameColor=(1.0, 0.0, 0.0, 1.0),
            )
            categoryItem.setPos(0.0, 0.0, 0.4)
            # Handle clicking and entering this button
            categoryItem.bind(DGG.WITHIN, self.__handleCategoryWithin, extraArgs=[categoryItem])
            categoryItem.bind(DGG.WITHOUT, self.__handleCategoryWithout, extraArgs=[categoryItem])
            categoryItem.bind(DGG.B1CLICK, self.__handleCategoryClicked, extraArgs=[category])
            # Add element to a list for deletion later
            self.categories.append(categoryItem)
            # Add element to our UI List
            self.categoryList.addItem(categoryItem)

    def unloadCategories(self):
        self.categoryList.removeAllItems()
        for categoryItem in self.categories:
            categoryItem.destroy()
        del self.categories[:]
        self.categories = []

    def loadItems(self, category, page):
        self.notify.debug('loadItems(%s, %s)' % (category, page))
        self.currentCat = category
        # Page limits
        if page < 0:
            page = 0
        else:
            pageCount = self.getMaxPages(category)
            if page > pageCount:
                page = pageCount
        self.currentPage = page

        background = TTCardMaker.makeCard('phase_3/maps/gui-circle.png')

        self.itemsHeading['text'] = category.name
        items = category.getOrderedItems(page*self.maxPerPage, (page+1)*self.maxPerPage)
        for index in xrange(0, self.maxPerPage):
            item = None
            if len(items) > index:
                item = items[index]
            itemDialog = self.createItemDialog(item, background, self.itemPositions[index])
            self.items.append(itemDialog)

        self.updatePageInterface(category, page)
        background.removeNode()

    def unloadItems(self):
        for item in self.items:
            item.destroy()
        del self.items[:]
        self.items = []

    def createItemDialog(self, item, background, pos):
        return ItemDialog(self.itemsFrame, item, background, pos, (1.0, 1.0, 1.0, 1.0), self.__handleItemClicked)

    def updatePageInterface(self, category, page):
        pageCount = self.getMaxPages(category)
        if pageCount == 0:
            self.itemsPageNext.hide()
            self.itemsPagePrev.hide()
        if page < pageCount:
            self.itemsPageNext.show()
        if page == pageCount:
            self.itemsPageNext.hide()
        if page > 0:
            self.itemsPagePrev.show()
        if page == 0:
            self.itemsPagePrev.hide()

        self.itemsPageCounter['text'] = TTLocalizer.CollectiblePagePageOfPage % ((page + 1), (pageCount + 1))

    def showPageInterface(self):
        self.itemsPageCounter.show()
        self.itemsPageNext.show()
        self.itemsPagePrev.show()

    def hidePageInterface(self):
        self.itemsPageCounter.hide()
        self.itemsPageNext.hide()
        self.itemsPagePrev.hide()

    def __handleCategoryClicked(self, category, e):
        self.unloadItems()
        self.loadItems(category, 0)
        self.updatePageInterface(category, 0)

    def __handleCategoryWithin(self, categoryItem, e):
        categoryItem['text_bg'] = (0.4, 0.8, 0.4, 1)

    def __handleCategoryWithout(self, categoryItem, e):
        categoryItem['text_bg'] = (0.0, 0.0, 0.0, 0.0)

    def __handleItemClicked(self, item):
        inventory = base.localAvatar.collectibleInventory
        if inventory is None:
            return
        if not inventory.isObtained(item.category, item.id) and item.id != DefaultItems.get(item.category, [-1])[0]:
            return
        if not CollectibleGlobals.getItem(item.category, item.id).isEquippable():
            return
        if inventory.isEquipped(item.category, item.id):
            return

        base.localAvatar.d_requestEquipCollectibleItem(item.category, item.id)

    def __handleNextClicked(self, e=None):
        self.unloadItems()
        self.loadItems(self.currentCat, self.currentPage+1)

    def __handlePrevClicked(self, e=None):
        self.unloadItems()
        self.loadItems(self.currentCat, self.currentPage-1)

    def __handleItemUpdated(self, category):
        if self.currentCat.id == category:
            for itemDialog in self.items:
                itemDialog.update()

    def getMaxPages(self, category):
        return len(category.items)/self.maxPerPage


class CollectibleCategoryItemsDisplay(CategoryItemsDisplay):
    def __init__(self, parent, cItems):
        CategoryItemsDisplay.__init__(self, parent, cItems)

    def createItemDialog(self, item, background, pos):
        return CollectibleItemDialog(self.itemsFrame, item, background, pos, (1.0, 1.0, 1.0, 1.0), self.__handleItemClicked)

    def acceptUpdates(self):
        self.accept(EventGlobals.StatUpdated, self.__handleItemUpdated)

    def ignoreUpdates(self):
        self.ignore(EventGlobals.StatUpdated)

    def __handleItemUpdated(self, category, objective):
        if self.currentCat.id == category:
            for itemDialog in self.items:
                if itemDialog.item.id == objective:
                    itemDialog.update()

    def __handleItemClicked(self, item):
        pass


class ItemDialog(DirectButton):
    StateEmpty = 0
    StateActive = 1
    StateInactive = 2
    StateEquipped = 3

    def __init__(self, parent, item, image, pos, color, command):
        self.parent = parent
        self.item = item
        self.image = image
        self.pos = pos
        self.command = command
        self.color = color
        self.tooltip = None
        self.isEmpty = False

        DirectButton.__init__(self, parent, relief=None, pos=pos)

        self.mainButton = DirectButton(
            self,
            relief=None,
            image=image,
            image_color=color,
            image_scale=(0.0025, 1, 0.0025),
            command=self.__handleClick
        )
        self.mainButton.bind(DGG.WITHIN, self.__handleEnter)
        self.mainButton.bind(DGG.WITHOUT, self.__handleExit)

        if item is not None:
            self.icon = item.buttonIcon
            if self.icon is not None:
                pos = self.icon.getPos()
                self.icon.reparentTo(self.mainButton)
                self.icon.setPos(pos)
            else:
                self.isEmpty = True
        else:
            self.isEmpty = True

        self.updateButtonState()

    def destroy(self):
        self.parent = None
        self.command = None
        if self.mainButton is not None:
            self.mainButton.destroy()
            self.mainButton = None
        DirectButton.destroy(self)

    def setButtonState(self, state):
        if state == self.StateEmpty:
            self.mainButton['state'] = DGG.DISABLED
            self.mainButton['image_color'] = (self.color[0], self.color[1], self.color[2], 0.3)
        elif state == self.StateEquipped:
            self.mainButton['state'] = DGG.NORMAL
            self.mainButton['image_color'] = (0.5, 1.0, 0.5, 1.0)
            self.mainButton['clickSound'] = None
            self.mainButton['rolloverSound'] = None
            self.mainButton.setClickSound()
            self.mainButton.setRolloverSound()
            self.mainButton.bind(DGG.WITHIN, self.showTooltip)
            self.mainButton.bind(DGG.WITHOUT, self.hideTooltip)
        elif state == self.StateInactive:
            self.mainButton['state'] = DGG.NORMAL
            self.mainButton['image_color'] = (self.color[0], self.color[1], self.color[2], 0.3)
            self.mainButton['clickSound'] = None
            self.mainButton['rolloverSound'] = None
            self.mainButton.setClickSound()
            self.mainButton.setRolloverSound()
            self.mainButton.bind(DGG.WITHIN, self.showTooltip)
            self.mainButton.bind(DGG.WITHOUT, self.hideTooltip)
            if self.icon is not None:
                color = self.icon.getColorScale()
                self.icon.setColorScale(color[0], color[1], color[2], 0.3)
        elif state == self.StateActive:
            self.mainButton['state'] = DGG.NORMAL
            self.mainButton['image_color'] = self.color
            self.mainButton['clickSound'] = DGG.getDefaultClickSound()
            self.mainButton['rolloverSound'] = DGG.getDefaultRolloverSound()
            self.mainButton.setClickSound()
            self.mainButton.setRolloverSound()
            self.mainButton.bind(DGG.WITHIN, self.__handleEnter)
            self.mainButton.bind(DGG.WITHOUT, self.__handleExit)
            if self.icon is not None:
                color = self.icon.getColorScale()
                self.icon.setColorScale(color[0], color[1], color[2], 1.0)

    def isEquipped(self):
        inventory = base.localAvatar.collectibleInventory
        if inventory is None:
            return False
        return inventory.isEquipped(self.item.category, self.item.id)

    def isActive(self):
        inventory = base.localAvatar.collectibleInventory
        if inventory is None:
            return False
        return inventory.isObtained(self.item.category, self.item.id) or self.item.id == DefaultItems.get(self.item.category, [-1])[0]

    def update(self):
        self.updateButtonState()

    def updateButtonState(self):
        if self.isEmpty:
            self.setButtonState(self.StateEmpty)
        elif self.isEquipped():
            self.setButtonState(self.StateEquipped)
        elif self.isActive():
            self.setButtonState(self.StateActive)
        else:
            self.setButtonState(self.StateInactive)

    def showTooltip(self, e=None):
        if self.tooltip is not None:
            self.tooltip.destroy()
            self.tooltip = None
        self.tooltip = ItemTooltip(self.mainButton, self.item, (0.0, 0.0, 0.2), 1.0, (1.0, 1.0, 1.0, 0.7))
        self.tooltip.setBin('gui-popup', 0)

    def hideTooltip(self, e=None):
        if self.tooltip is not None:
            self.tooltip.destroy()
            self.tooltip = None

    def __handleClick(self, e=None):
        self.command(self.item)

    def __handleEnter(self, e=None):
        _, _, _, alpha = self.mainButton['image_color']
        self.mainButton['image_color'] = (1, 1, 0.2, alpha)
        self.showTooltip()

    def __handleExit(self, e):
        _, _, _, alpha = self.mainButton['image_color']
        self.mainButton['image_color'] = (1, 1, 1, alpha)
        self.hideTooltip()

    def doNothing(self, e):
        pass


class CollectibleItemDialog(ItemDialog):
    def __init__(self, parent, item, image, pos, color, command):
        ItemDialog.__init__(self, parent, item, image, pos, color, command)

    def update(self):
        ItemDialog.update(self)
        if self.tooltip is not None:
            self.tooltip.updateProgress()

    def showTooltip(self, e=None):
        if self.tooltip is not None:
            self.tooltip.destroy()
            self.tooltip = None
        self.tooltip = CollectibleItemTooltip(self.mainButton, self.item, (0.0, 0.0, 0.2), 1.0, (1.0, 1.0, 1.0, 0.7))
        self.tooltip.setBin('gui-popup', 0)

    def isEquipped(self):
        return False

    def isActive(self):
        obtained = False
        stats = base.localAvatar.stats
        if stats is not None:
            amount = stats.getStatistic(self.item.category, self.item.id)
            if amount >= self.item.goal:
                obtained = True
        return obtained


class ItemTooltip(DirectFrame):
    def __init__(self, parent, item, pos, scale, color):
        self.parent = parent
        self.item = item
        self.pos = pos
        self.scale = scale
        self.color = color

        DirectFrame.__init__(self, parent, relief=None, pos=pos)

        background = TTCardMaker.makeCard('phase_3/maps/curved-gui-square.png')

        self.mainFrame = DirectFrame(
            self,
            relief=None,
            image=background,
            scale=self.scale,
            image_color=self.color,
            image_scale=(0.0004, 0.1, 0.0002)
        )
        self.title = DirectLabel(
            self.mainFrame,
            relief=None,
            text=item.name,
            text_scale=0.0525,
            text_fg=(1.0, 1, 0.0, 1.0),
            text_align=TextNode.ABoxedLeft,
            text_shadow=(0.0, 0.0, 0.0, 1.0),
            text_shadowOffset=(0.06, 0.06),
            pos=(-0.3, 0.0, 0.1)
        )
        self.tooltip = DirectLabel(
            self.mainFrame,
            relief=None,
            text=item.desc,
            text_scale=0.045,
            text_fg=(0.1, 0.1, 0.1, 1.0),
            text_align=TextNode.ABoxedLeft,
            text_wordwrap=14,
            text_shadow=(0.0, 0.0, 0.0, 1.0),
            pos=(-0.3, 0.0, 0.025)
        )
        self.flavorText = DirectLabel(
            self.mainFrame,
            relief=None,
            text=self.item.flavorText,
            text_scale=0.04,
            text_fg=(0.2, 0.6, 0.9, 1.0),
            text_align=TextNode.ABoxedLeft,
            text_shadow=(0.0, 0.0, 0.0, 1.0),
            text_shadowOffset=(0.06, 0.06),
            pos=(-0.3, 0.0, -0.12)
        )
        background.removeNode()

    def destroy(self):
        DirectFrame.destroy(self)

    def setTooltip(self, text):
        self.tooltip['text'] = text

    def setFlavorText(self, text):
        self.flavorText['text'] = text


class CollectibleItemTooltip(ItemTooltip):
    def __init__(self, parent, item, pos, scale, color):
        ItemTooltip.__init__(self, parent, item, pos, scale, color)
        self.updateProgress()

    def getProgressText(self):
        amount = base.localAvatar.stats.getStatistic(self.item.category, self.item.id)
        if amount is None:
            amount = 0
        if amount >= self.item.goal:
            text = TTLocalizer.CollectiblePageObtained
        else:
            text = self.item.flavorText % (amount, self.item.goal)
        return text

    def updateProgress(self):
        self.setFlavorText(self.getProgressText())
