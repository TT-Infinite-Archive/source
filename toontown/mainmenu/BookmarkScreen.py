self.bookmarkInfoDialog = None
# Load Bookmarks file
self.bookmarkMgr = BookmarkManager()

def enterBookmarks(self):
    gui = loader.loadModel('phase_3.5/models/gui/friendslist_gui')

    if not hasattr(self, 'bookmarksList'):
        self.bookmarksList = DirectScrolledList(parent=self,
                                                decButton_pos=(0, 0, 0.9),
                                                decButton_image=(gui.find('**/FndsLst_ScrollUp'),
                                                                 gui.find('**/FndsLst_ScrollDN'),
                                                                 gui.find('**/FndsLst_ScrollUp_Rllvr'),
                                                                 gui.find('**/FndsLst_ScrollUp')),
                                                decButton_relief=None,
                                                decButton_scale=(1.5, 1.5, 1.5),

                                                incButton_pos=(0, 0, -0.9),
                                                incButton_image=(gui.find('**/FndsLst_ScrollUp'),
                                                                 gui.find('**/FndsLst_ScrollDN'),
                                                                 gui.find('**/FndsLst_ScrollUp_Rllvr'),
                                                                 gui.find('**/FndsLst_ScrollUp')),
                                                incButton_relief=None,
                                                incButton_scale=(1.5, 1.5, -1.5),

                                                items=[],
                                                numItemsVisible=16,
                                                forceHeight=.096,
                                                itemFrame_frameSize=(-.6, .6, -1.5, .1),
                                                itemFrame_pos=(0, 0, .7),
                                                itemFrame_frameColor=(0.85, 0.95, 1, 1)
                                                )
        self.bookmarksList.setPos(0.8, 0, 0)
    self.bookmarksList.show()
    self.makeBookmarksButtons()
    self.logo.hide()
    self.background['image'] = 'phase_3.5/maps/big_book.jpg'


def exitBookmarks(self):
    self.bookmarksList.hide()
    if self.bookmarkInfoDialog:
        self.bookmarkInfoDialog.hide()
    self.logo.show()
    self.background['image'] = 'phase_3/maps/loading_bg_clouds.jpg'

    def makeBookmarksButtons(self):
        self.bookmarksList.removeAllItems()
        bookmarks = self.bookmarkMgr.getBookmarks()
        for bookmark in bookmarks:
            address = bookmark
            name = bookmarks.get(address)
            button = DirectButton(
                relief = None,
                text="%s" %(name),
                text_scale = 0.082,
                text2_scale = 0.087,
                text1_scale = 0.087,
                text_fg = (0, 0, 0, 1),
                command = self.showBookmarkInfo,
                extraArgs = [name, address])
            button.bind(DirectGuiGlobals.ENTER, self.showTooltip, extraArgs = ["Name: %s\nAddress: %s" %(name, address)])
            button.bind(DirectGuiGlobals.EXIT, self.killTooltip)

            self.bookmarksList.addItem(button)

    def showBookmarkInfo(self, name, address):
        buttonScale = (-1.1, 1.1, 1.1)
        buttonScale_clickhover = (-1.2, 1.2, 1.2)
        if self.bookmarkInfoDialog:
            self.bookmarkInfoDialog.removeNode()
            self.bookmarkInfoDialog = None
        def done():
            self.bookmarkInfoDialog.hide()
            self.__submitIP(address)

        if not self.bookmarkInfoDialog:

            self.bookmarkInfoDialog = self.attachNewNode('bookmarkInfoDialog')
            self.bookmarkInfoDialog.setPos(-0.8, 0, 0)

            infoTitle = DirectLabel(relief = None, parent = self.bookmarkInfoDialog, pos = (0, 0, 0.5), text_align = TextNode.ACenter, text_font = ToontownGlobals.getToonFont(), text_scale = 0.1, text_wordwrap = 25, text = "Bookmark Information")
            nameLabel = DirectLabel(relief = None, parent = self.bookmarkInfoDialog, pos = (-.5, 0, 0.2), text_fg = (0, 0, 0, 1), text_align = TextNode.ALeft, text_font = ToontownGlobals.getToonFont(), text_scale = 0.06, text_wordwrap = 25, text = "\1candidate_inactive\1Name:\2 %s" %name)
            addressLabel = DirectLabel(relief = None, parent = self.bookmarkInfoDialog, pos = (-.5, 0, 0.1), text_fg = (0, 0, 0, 1), text_align = TextNode.ALeft, text_font = ToontownGlobals.getToonFont(), text_scale = 0.06, text_wordwrap = 25, text = "\1candidate_inactive\1Address:\2 %s" %address)
            connectButton = MATShuffleButton(parent = self.bookmarkInfoDialog, pos=(0, 0, -0.3), text="Connect", wantArrows=False,
            image_scale=buttonScale, image2_scale=buttonScale_clickhover,
            image1_scale=buttonScale_clickhover, text_scale=0.082, text2_scale=0.087,
            text1_scale=0.087, command=done)

            trashcanGui = loader.loadModel('phase_3/models/gui/trashcan_gui.bam')
            deleteButton = DirectButton(parent = self.bookmarkInfoDialog,
                geom = (trashcanGui.find('**/TrashCan_CLSD'),
                    trashcanGui.find('**/TrashCan_OPEN'),
                    trashcanGui.find('**/TrashCan_RLVR')),
                text = ('',
                    TTLocalizer.AvatarChoiceDelete,
                    TTLocalizer.AvatarChoiceDelete,
                    ''),
                text_fg = (1, 1, 1, 1),
                text_shadow = (0, 0, 0, 1),
                text_scale = 0.15,
                text_pos = (0, -0.1),
                relief = None,
                scale = .4,
                command = self.deleteFromBookmarks,
                extraArgs = [name, address],
                pos = (.4, 0, -.3))

            deleteButton.bind(DirectGuiGlobals.ENTER, self.showTooltip, extraArgs = ["This will PERMENANTLY delete this bookmark. This action is not reversable!"])
            deleteButton.bind(DirectGuiGlobals.EXIT, self.killTooltip)

            def createBookmark(self):
                if self.ipInput.get() == '':
                    return

                def done():
                    if self.addToBookmarksDialog.doneStatus == 'ok':
                        self.addToBookmarks()
                    self.addToBookmarksDialog.hide()
                    base.transitions.noFade()

                self.addToBookmarksDialog = TTDialog.TTGlobalDialog(
                    dialogName='AddToBookmarkDialog', doneEvent='addBookmark', style=TTDialog.TwoChoice,
                    text="Choose a name for this bookmark", text_wordwrap=24,
                    text_pos=(0, 0), suppressKeys=True, suppressMouse=True
                )
                base.transitions.fadeScreen(.5)
                scale = self.addToBookmarksDialog.component('image0').getScale()
                scale.setX(((scale[0] * 2.5) / base.getAspectRatio()) * 1.2)
                scale.setZ(scale[2] * 2.5)
                self.addToBookmarksDialog.component('image0').setScale(scale)
                self.addToBookmarksDialog.accept('addBookmark', done)
                self.serverNameInput = DirectEntry(
                    parent=self.addToBookmarksDialog,
                    relief=DGG.GROOVE,
                    scale=0.1,
                    pos=(0, 0, 0.2),
                    borderWidth=(0.05, 0.05),
                    frameColor=((1, 1, 1, 0),
                                (1, 1, 1, 0),
                                (0.5, 0.5, 0.5, 0)),
                    image="phase_3/maps/input_box.png",
                    image_scale=(4.6, 0, 1),
                    image_pos=(0, 0, .2),
                    state=DGG.NORMAL,
                    text_align=TextNode.ACenter,
                    text_scale=TTLocalizer.OPCodesInputTextScale,
                    width=10.5,
                    numLines=1,
                    focus=1,
                    backgroundFocus=0,
                    cursorKeys=1,
                    text_fg=(0,
                             0,
                             0,
                             1),
                    suppressMouse=1,
                    autoCapitalize=0)
                self.serverNameInput.setTransparency(1)

            def addToBookmarks(self):
                if hasattr(self, 'ipInput'):
                    if self.ipInput.get() == '':
                        return
                    try:  # This wants to crash so i'll do this for now
                        if self.serverNameInput.get() == '':
                            if self.ipInput != '':
                                self.name = self.ipInput.get()
                            else:
                                return
                    except:
                        return
                    name = self.serverNameInput.get()
                    address = self.ipInput.get()
                    resp = self.bookmarkMgr.addBookmark(address, name)
                    if resp == 1:
                        base.showNotification(
                            "Bookmark added! (IP: %s, Name: %s)" % (self.ipInput.get(), self.serverNameInput.get()))
                    elif resp == 2:
                        base.showNotification("Error: A bookmark for the IP %s already exists!" % self.ipInput.get())
                    elif resp == 3:
                        base.showNotification("Error: Please specify an IP!")
                    else:
                        base.showNotification(
                            "Error: Unknown error adding bookmark! Please report this to the developers!")

            def deleteFromBookmarks(self, name, address):
                if self.bookmarkInfoDialog:
                    self.bookmarkInfoDialog.hide()
                resp = self.bookmarkMgr.removeBookmark(address)
                if resp == 1:
                    base.showNotification("Bookmark removed! (IP: %s, Name: %s)" % (address, name))
                elif resp == 2:
                    base.showNotification("Error: A bookmark for %s doesn't exist, so it can't be deleted!" % address)
                else:
                    base.showNotification(
                        "Error: Unknown error removing bookmark! Please report this to the developers!")
                self.makeBookmarksButtons()