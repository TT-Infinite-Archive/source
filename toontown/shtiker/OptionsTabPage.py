from panda3d.core import TextNode, WindowProperties

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.gui.DirectGui import DirectFrame, DirectScrolledFrame, DGG

from otp.speedchat import SpeedChat, SCColorScheme, SCStaticTextTerminal

from toontown.shtiker import OptionsPageGlobals, ControlRemapDialog
from toontown.shtiker.OptionsPageGlobals import ECategory, ERowKind
from toontown.toontowngui import TTLabel, TTButton, TTDialog
from toontown.toontowngui.TTOptionRow import TTButtonRow, TTChoiceRow, TTOptionHeading, TTSliderRow, TTToggleRow
from toontown.toontowngui.TTTabBar import TTTabBar
from toontown.toonbase import ToontownGlobals, TTLocalizer, EventGlobals, SettingsGlobals, ColorGlobals
from toontown.toonbase import ToontownClientGlobals


class OptionsTabPage(DirectFrame):
    notify = directNotify.newCategory('OptionsTabPage')
    PaneLeft = -0.82
    PaneRight = 0.84
    CanvasRight = 0.72
    PaneTop = 0.52
    PaneBottom = -0.54
    RowTop = -0.06
    TabsZ = 0.64
    ButtonsZ = -0.62
    TrackWidth = 0.012
    ThumbWidth = 0.045
    ThumbLength = 0.15

    def __init__(self, parent = aspect2d, wantTabs = True):
        DirectFrame.__init__(self, parent = parent, relief = None, pos = (0.0, 0.0, 0.0), scale = (1.0, 1.0, 1.0))

        self._parent = parent
        self.wantTabs = wantTabs
        self.tabBar = None
        self.state = None
        self.customControlDialog = None

        self.speed_chat_scale = 0.055

        self.warning = None
        self.videoDialog = None
        self.confirm = None
        self.requiresRestart = False
        self.hasAvatar = hasattr(base, 'localAvatar')
        self.panes = {}
        self.rows = {}
        self.load()

    def destroy(self):
        self._parent = None
        self.ignoreAll()
        taskMgr.remove('testResolution-task')
        taskMgr.remove('revertResolution-task')
        DirectFrame.destroy(self)

    def load(self):
        if self.wantTabs:
            self.tabBar = TTTabBar(
                self,
                tabs = OptionsPageGlobals.Categories,
                pos = (0, 0, self.TabsZ),
                command = self.setOptionsState
            )

        self.requiresRestartLabel = TTLabel.TTLabel(
            parent = self,
            pos = (self.PaneLeft, 0.0, self.PaneBottom - 0.06),
            text_align = TextNode.ALeft,
            text_fg = ColorGlobals.CRed,
            text_size = TTLabel.TTLabel.SmallSize,
            text = '* %s' % TTLocalizer.OptionsPageRequiresRestart
        )
        self.requiresRestartLabel.hide()

        self.__loadVideoPane()
        self.__loadSoundPane()
        self.__loadGameplayPane()
        self.__loadSocialPane()

        self.setOptionsState(ECategory.VIDEO)

    # -- Panes

    def __makePane(self):
        # A thin track like the volume sliders', with a handle made from the
        # yellow button art turned on its side.
        buttonGui = loader.loadModel('phase_3/models/gui/quit_button')
        thumb = [buttonGui.find('**/QuitBtn_%s' % state) for state in ('UP', 'DN', 'RLVR', 'UP')]
        low, high = thumb[0].getTightBounds()

        pane = DirectScrolledFrame(
            parent = self,
            relief = None,
            frameSize = (self.PaneLeft, self.PaneRight, self.PaneBottom, self.PaneTop),
            canvasSize = (self.PaneLeft, self.CanvasRight, 0, 0),
            manageScrollBars = True,
            autoHideScrollBars = True,
            scrollBarWidth = self.TrackWidth,
            horizontalScroll_relief = None,
            verticalScroll_relief = DGG.FLAT,
            verticalScroll_frameColor = ColorGlobals.CToontownBlue,
            verticalScroll_manageButtons = False,
            verticalScroll_resizeThumb = False,
            verticalScroll_thumb_relief = None,
            verticalScroll_thumb_frameSize = (-self.ThumbWidth / 2, self.ThumbWidth / 2,
                                              -self.ThumbLength / 2, self.ThumbLength / 2),
            verticalScroll_thumb_image = tuple(thumb),
            verticalScroll_thumb_image_hpr = (0, 0, 90),
            verticalScroll_thumb_image_scale = (self.ThumbLength / (high[0] - low[0]), 1,
                                                self.ThumbWidth / (high[2] - low[2]))
        )
        pane.verticalScroll.incButton.hide()
        pane.verticalScroll.decButton.hide()
        buttonGui.removeNode()
        return pane

    def __fitPane(self, pane, bottom):
        pane['canvasSize'] = (self.PaneLeft, self.CanvasRight,
                              min(bottom, self.PaneBottom - self.PaneTop), 0)

    def __addRows(self, pane, options, z):
        rows = {}
        for option in options:
            if not option.isAvailable():
                continue
            row = self.__makeRow(pane.getCanvas(), option)
            row.setPos(0, 0, z)
            z -= row.Height
            if option.key is not None:
                rows[option.key] = row
        return rows, z

    def __makeRow(self, canvas, option):
        if option.kind == ERowKind.HEADING:
            return TTOptionHeading(canvas, text = option.label)

        if option.kind == ERowKind.CHOICE:
            return TTChoiceRow(
                canvas,
                text = option.label,
                values = option.values,
                valueLabels = option.valueLabels,
                value = option.getValue(),
                requiresRestart = option.requiresRestart,
                command = lambda value, o = option: self.__optionChanged(o, value)
            )

        if option.kind == ERowKind.SLIDER:
            # Volumes are stored 0-1 and shown 0-100.
            return TTSliderRow(
                canvas,
                text = option.label,
                value = option.getValue() * 100,
                command = lambda value, o = option: self.__optionChanged(o, value / 100)
            )

        return TTToggleRow(
            canvas,
            text = option.label,
            checked = option.getValue(),
            requiresRestart = option.requiresRestart,
            command = lambda value, o = option: self.__optionChanged(o, value)
        )

    def __optionChanged(self, option, value):
        messenger.send(EventGlobals.WakeUp)
        option.setValue(value)

        if option.requiresRestart:
            self.requiresRestart = True
            self.requiresRestartLabel.show()

        self.__sideEffects(option.key, value)

    def __sideEffects(self, key, value):
        if key == SettingsGlobals.Music:
            self.__setEnabled(self.rows.get(SettingsGlobals.MusicVolume), value)
        elif key == SettingsGlobals.Sound:
            self.__setEnabled(self.rows.get(SettingsGlobals.SoundVolume), value)
        elif key == SettingsGlobals.WantCustomControls:
            base.wantCustomControls = value
            self.__setEnabled(self.configureControlsRow, value)
            base.reloadControls()
            if self.hasAvatar:
                base.localAvatar.controlManager.reload()
                base.localAvatar.chatMgr.reloadWASD()
                base.localAvatar.controlManager.disable()
            messenger.send('controlsRemapped')

    def __setEnabled(self, row, enabled):
        if row is None:
            return
        if enabled:
            row.enable()
        else:
            row.disable()

    # -- Video

    def __loadVideoPane(self):
        pane = self.panes[ECategory.VIDEO] = self.__makePane()
        canvas = pane.getCanvas()
        z = self.RowTop

        base.getSmallestResolution()
        self.screenSizes = list(ToontownClientGlobals.CommonDisplayResolutions[base.calcRatio])

        displayHeading = TTOptionHeading(canvas, text = TTLocalizer.OptionsPageDisplay)
        displayHeading.setPos(0, 0, z)
        z -= displayHeading.Height

        self.displayModeRow = TTChoiceRow(
            canvas,
            text = TTLocalizer.OptionsPageDisplayMode,
            values = (False, True),
            valueLabels = TTLocalizer.OptionsPageDisplayModeValues,
            value = settings.get(SettingsGlobals.Fullscreen, False),
            command = self.__videoOptionsChanged
        )
        self.displayModeRow.setPos(0, 0, z)
        z -= self.displayModeRow.Height

        self.resolutionRow = TTChoiceRow(
            canvas,
            text = TTLocalizer.OptionsPageResolutionLabel,
            command = self.__videoOptionsChanged
        )
        self.resolutionRow.setValues(self.screenSizes, ['%s x %s' % tuple(size) for size in self.screenSizes],
                                     tuple(settings.get(SettingsGlobals.Resolution, ())))
        self.resolutionRow.setPos(0, 0, z)
        z -= self.resolutionRow.Height

        self.applyVideoRow = TTButtonRow(
            canvas,
            buttonText = TTLocalizer.OptionsPageApply,
            disable = True,
            command = self.__applyVideoChanges
        )
        self.applyVideoRow.setPos(0, 0, z)
        z -= self.applyVideoRow.Height

        rows, z = self.__addRows(pane, OptionsPageGlobals.VideoOptions, z)
        self.rows.update(rows)
        self.__fitPane(pane, z)

    # -- Sound

    def __loadSoundPane(self):
        pane = self.panes[ECategory.SOUND] = self.__makePane()
        rows, z = self.__addRows(pane, OptionsPageGlobals.SoundOptions, self.RowTop)
        self.rows.update(rows)
        self.__fitPane(pane, z)

        self.__setEnabled(self.rows.get(SettingsGlobals.MusicVolume), base.musicActive)
        self.__setEnabled(self.rows.get(SettingsGlobals.SoundVolume), base.sfxActive)

    # -- Gameplay

    def __loadGameplayPane(self):
        pane = self.panes[ECategory.GAMEPLAY] = self.__makePane()
        canvas = pane.getCanvas()

        heading = TTOptionHeading(canvas, text = TTLocalizer.OptionsPageControls)
        heading.setPos(0, 0, self.RowTop)
        z = self.RowTop - heading.Height

        rows, z = self.__addRows(pane, OptionsPageGlobals.CustomControlsOptions, z)
        self.rows.update(rows)

        self.configureControlsRow = TTButtonRow(
            canvas,
            buttonText = TTLocalizer.OptionsPageConfigure,
            disable = not base.wantCustomControls,
            command = self.__openKeyRemapDialog
        )
        self.configureControlsRow.setPos(0, 0, z)
        z -= self.configureControlsRow.Height

        rows, z = self.__addRows(pane, OptionsPageGlobals.InteractionOptions, z)
        self.rows.update(rows)

        self.__fitPane(pane, z)

    # -- Social

    def __loadSocialPane(self):
        pane = self.panes[ECategory.SOCIAL] = self.__makePane()
        canvas = pane.getCanvas()
        z = self.RowTop

        if not self.hasAvatar:
            self.noAvatarLabel = TTLabel.TTLabel(
                parent = canvas,
                text = TTLocalizer.OptionsPageNeedsAvatar,
                text_wordwrap = 15,
                pos = (-0.08, 0, z - 0.1)
            )
            self.exitButton = None
            self.toonselectButton = None
            self.__fitPane(pane, z - 0.3)
            return

        chatHeading = TTOptionHeading(canvas, text = TTLocalizer.OptionsPageChat)
        chatHeading.setPos(0, 0, z)
        z -= chatHeading.Height

        self.whispersRow = TTToggleRow(
            canvas,
            text = TTLocalizer.OptionsPageAcceptingWhispers,
            checked = base.localAvatar.wantWhispers,
            command = self.__doToggleWantWhispers
        )
        self.whispersRow.setPos(0, 0, z)
        z -= self.whispersRow.Height

        self.whispersAnyoneRow = TTToggleRow(
            canvas,
            text = TTLocalizer.OptionsPageFromStrangers,
            checked = base.localAvatar.wantNonFriendWhispers,
            disable = not base.localAvatar.wantWhispers,
            command = self.__doToggleWantNonFriendWhispers
        )
        self.whispersAnyoneRow.setPos(0, 0, z)
        z -= self.whispersAnyoneRow.Height

        self.whispersFriendsRow = TTToggleRow(
            canvas,
            text = TTLocalizer.OptionsPageFromFriends,
            checked = base.localAvatar.wantFriendWhispers,
            disable = not base.localAvatar.wantWhispers,
            command = self.__doToggleWantFriendWhispers
        )
        self.whispersFriendsRow.setPos(0, 0, z)
        z -= self.whispersFriendsRow.Height

        self.speedChatStyleRow = TTChoiceRow(
            canvas,
            text = TTLocalizer.OptionsPageSpeedChatStyleLabel,
            values = list(range(len(OptionsPageGlobals.speedChatStyles))),
            valueLabels = [''] * len(OptionsPageGlobals.speedChatStyles),
            value = 0,
            command = self.__setSpeedChatStyle
        )
        self.speedChatStyleRow.setPos(0, 0, z)
        self.speedChatStyleRow.valueLabel.hide()
        self.speedChatZ = z + 0.04
        z -= self.speedChatStyleRow.Height

        self.speedChatStyleText = SpeedChat.SpeedChat(
            name = 'OptionsPageStyleText',
            structure = [2000],
            backgroundModelName = 'phase_3/models/gui/ChatPanel',
            guiModelName = 'phase_3.5/models/gui/speedChatGui'
        )
        self.speedChatStyleText.setScale(self.speed_chat_scale)
        self.speedChatStyleText.reparentTo(canvas, DGG.FOREGROUND_SORT_INDEX)

        friendsHeading = TTOptionHeading(canvas, text = TTLocalizer.OptionsPageFriends)
        friendsHeading.setPos(0, 0, z)
        z -= friendsHeading.Height

        self.acceptingFriendsRow = TTToggleRow(
            canvas,
            text = TTLocalizer.OptionsPageAcceptingFriends,
            checked = base.localAvatar.wantFriends,
            command = self.__doToggleWantFriends
        )
        self.acceptingFriendsRow.setPos(0, 0, z)
        z -= self.acceptingFriendsRow.Height

        self.__fitPane(pane, z)

        if base.cr.isProductionServer():
            self.exitButton = TTButton.TTButton(
                parent = self,
                buttonScale = 1.15,
                text = TTLocalizer.OptionsPageExitToontown,
                pos = (0, 0, self.ButtonsZ),
                command = self.__handleExitToToonSelectShowWithConfirm
            )
            self.toonselectButton = None
        else:
            if base.isHosting or base.wantSinglePlayer:
                text = TTLocalizer.OptionsDisconnect
            else:
                text = TTLocalizer.OptionsLeaveServer
            self.exitButton = TTButton.TTButton(
                parent = self,
                buttonScale = 1.15,
                text = text,
                pos = (0.28, 0, self.ButtonsZ),
                command = self.__handleExitServerShowWithConfirm
            )
            self.toonselectButton = TTButton.TTButton(
                parent = self,
                buttonScale = 1.15,
                text = TTLocalizer.OptionsReturnToToonSelect,
                pos = (-0.28, 0, self.ButtonsZ),
                command = self.__handleExitToToonSelectShowWithConfirm
            )

    # -- State

    def enter(self):
        self.show()

        if self.hasAvatar:
            self.speedChatStyleText.enter()
            self.speedChatStyleIndex = base.localAvatar.getSpeedChatStyleIndex()
            self.speedChatStyleRow.setValue(self.speedChatStyleIndex)
            self.updateSpeedChatStyle()

        self.__updateExitButtons()

    def exit(self):
        self.ignore('confirmDone')
        self.hide()
        if self.hasAvatar:
            self.speedChatStyleText.exit()

    def unload(self):
        if self.hasAvatar:
            self.speedChatStyleText.exit()
            self.speedChatStyleText.destroy()
            del self.speedChatStyleText

        for button in (self.exitButton, self.toonselectButton):
            if button is not None:
                button.destroy()
        self.exitButton = None
        self.toonselectButton = None

        for pane in self.panes.values():
            pane.destroy()
        self.panes = {}
        self.rows = {}

        if self.tabBar is not None:
            self.tabBar.destroy()
            self.tabBar = None

    def __updateExitButtons(self):
        if not self.hasAvatar or self.exitButton is None:
            return

        safeMode = getattr(getattr(self._parent, 'book', None), 'safeMode', False)
        visible = self.state == ECategory.SOCIAL and not safeMode
        for button in (self.exitButton, self.toonselectButton):
            if button is None:
                continue
            if visible:
                button.show()
            else:
                button.hide()

    def setOptionsState(self, state):
        messenger.send(EventGlobals.WakeUp)
        self.state = state

        for key, pane in self.panes.items():
            if key == state:
                pane.show()
            else:
                pane.hide()

        if self.tabBar is not None:
            self.tabBar.setActive(state)

        if state == ECategory.VIDEO and self.requiresRestart:
            self.requiresRestartLabel.show()
        else:
            self.requiresRestartLabel.hide()

        self.__updateExitButtons()

    # -- Social handlers

    def __doToggleWantWhispers(self, value):
        messenger.send(EventGlobals.WakeUp)
        wantWhispers = settings.get(SettingsGlobals.WantWhispers, {})
        base.localAvatar.wantWhispers = value
        wantWhispers[str(base.localAvatar.doId)] = value
        settings[SettingsGlobals.WantWhispers] = wantWhispers
        self.__setEnabled(self.whispersAnyoneRow, value)
        self.__setEnabled(self.whispersFriendsRow, value)

    def __doToggleWantNonFriendWhispers(self, value):
        messenger.send(EventGlobals.WakeUp)
        wantNonFriendWhispers = settings.get(SettingsGlobals.WantNonFriendWhispers, {})
        base.localAvatar.wantNonFriendWhispers = value
        wantNonFriendWhispers[str(base.localAvatar.doId)] = value
        settings[SettingsGlobals.WantNonFriendWhispers] = wantNonFriendWhispers

    def __doToggleWantFriendWhispers(self, value):
        messenger.send(EventGlobals.WakeUp)
        wantFriendWhispers = settings.get(SettingsGlobals.WantFriendWhispers, {})
        base.localAvatar.wantFriendWhispers = value
        wantFriendWhispers[str(base.localAvatar.doId)] = value
        settings[SettingsGlobals.WantFriendWhispers] = wantFriendWhispers

    def __doToggleWantFriends(self, value):
        messenger.send(EventGlobals.WakeUp)
        wantFriends = settings.get(SettingsGlobals.WantFriends, {})
        base.localAvatar.wantFriends = value
        wantFriends[str(base.localAvatar.doId)] = value
        settings[SettingsGlobals.WantFriends] = wantFriends

    def __setSpeedChatStyle(self, index):
        self.speedChatStyleIndex = index
        self.updateSpeedChatStyle()

    def updateSpeedChatStyle(self):
        nameKey, arrowColor, rolloverColor, frameColor = OptionsPageGlobals.speedChatStyles[self.speedChatStyleIndex]
        newSCColorScheme = SCColorScheme.SCColorScheme(
            arrowColor = arrowColor,
            rolloverColor = rolloverColor,
            frameColor = frameColor
        )
        self.speedChatStyleText.setColorScheme(newSCColorScheme)
        self.speedChatStyleText.clearMenu()
        colorName = SCStaticTextTerminal.SCStaticTextTerminal(nameKey)
        self.speedChatStyleText.append(colorName)
        self.speedChatStyleText.finalize()
        self.speedChatStyleText.setPos(
            TTChoiceRow.ValueX - self.speedChatStyleText.getWidth() * self.speed_chat_scale / 2,
            0,
            self.speedChatZ
        )
        base.localAvatar.b_setSpeedChatStyleIndex(self.speedChatStyleIndex)

    def __openKeyRemapDialog(self):
        if base.wantCustomControls:
            self.customControlDialog = ControlRemapDialog.ControlRemap()

    # -- Display mode and resolution

    def __videoOptionsChanged(self, value = None):
        messenger.send(EventGlobals.WakeUp)
        self.applyVideoRow.enable()

    def __applyVideoChanges(self):
        fullscreen = self.displayModeRow.getValue()
        res = self.resolutionRow.getValue()

        wp = WindowProperties()
        wp.setSize(res[0], res[1])
        wp.setFullscreen(fullscreen)
        base.win.requestProperties(wp)
        # Test the resolution and ask the user if they want to keep it
        taskMgr.doMethodLater(0.1, self.testResolution, 'testResolution-task', extraArgs = [res])
        # Revert after 15 seconds of inactivity
        taskMgr.doMethodLater(15, self.revertResolution, 'revertResolution-task', extraArgs = [])
        self.applyVideoRow.disable()

    def revertResolution(self):
        if self.videoDialog:
            self.videoDialog.cleanup()
            self.videoDialog = None
        wp = WindowProperties()
        wp.setFullscreen(settings[SettingsGlobals.Fullscreen])
        res = settings[SettingsGlobals.Resolution]
        wp.setSize(res[0], res[1])
        base.win.requestProperties(wp)
        self.applyVideoRow.enable()

    def testResolution(self, res):
        rejectedProperties = base.win.getRejectedProperties()
        failed = False
        if rejectedProperties.hasSize():
            self.notify.warning('Failed to set properties, invalid resolution')
            failed = True
        if rejectedProperties.hasFullscreen():
            self.notify.warning('Failed to set fullscreen mode')
            failed = True
        base.win.clearRejectedProperties()
        if failed:
            if self.warning:
                self.warning.cleanup()
            self.warning = TTDialog.TTGlobalDialog(
                style = TTDialog.Acknowledge,
                doneEvent = 'confirmWarning',
                message = TTLocalizer.OptionsPageDisplayFailed
            )
            self.accept('confirmWarning', self.__handleWarningDone)
            self.applyVideoRow.enable()
            if taskMgr.hasTaskNamed('revertResolution-task'):
                taskMgr.remove('revertResolution-task')
                self.revertResolution()
        else:
            if self.videoDialog:
                self.videoDialog.cleanup()
            self.videoDialog = TTDialog.TTGlobalDialog(
                style = TTDialog.TwoChoice,
                doneEvent = 'confirmVideo',
                message = TTLocalizer.OptionsPageKeepDisplay
            )
            self.accept('confirmVideo', self.__handleVideoConfirmDone)

    def __handleVideoConfirmDone(self, e = None):
        status = self.videoDialog.doneStatus
        self.ignore('confirmVideo')
        self.videoDialog.cleanup()
        self.videoDialog = None

        if status == 'ok':
            settings[SettingsGlobals.Fullscreen] = self.displayModeRow.getValue()
            settings[SettingsGlobals.Resolution] = self.resolutionRow.getValue()
            if taskMgr.hasTaskNamed('revertResolution-task'):
                taskMgr.remove('revertResolution-task')
        else:
            if taskMgr.hasTaskNamed('revertResolution-task'):
                taskMgr.remove('revertResolution-task')
                self.revertResolution()

    def __handleWarningDone(self, e = None):
        self.ignore('confirmWarning')
        self.warning.cleanup()
        self.warning = None

    # -- Leaving

    def __handleExitServerShowWithConfirm(self):
        if base.isHosting:
            message = TTLocalizer.LeaveServerHost
        else:
            message = TTLocalizer.LeaveServer
        if base.wantSinglePlayer:
            message = TTLocalizer.LeaveServerHostSP
        self.confirm = TTDialog.TTGlobalDialog(
            doneEvent = 'confirmDone',
            message = message,
            style = TTDialog.TwoChoice
        )
        self.confirm.show()
        self._parent.doneStatus = {'mode': 'exit', 'exitTo': 'disconnect'}
        self.accept('confirmDone', self.__handleConfirm)

    def __handleExitToToonSelectShowWithConfirm(self):
        if base.cr.isProductionServer():
            # Live calls this button Exit Toontown, so it asks the way it used to.
            message = TTLocalizer.OptionsPageExitConfirm
        else:
            message = TTLocalizer.PickAToonConfirm
        self.confirm = TTDialog.TTGlobalDialog(
            doneEvent = 'confirmDone',
            message = message,
            style = TTDialog.TwoChoice)
        self.confirm.show()
        self._parent.doneStatus = {'mode': 'exit', 'exitTo': 'closeShard'}
        self.accept('confirmDone', self.__handleConfirm)

    def __handleConfirm(self):
        status = self.confirm.doneStatus
        self.ignore('confirmDone')
        self.confirm.cleanup()
        self.confirm = None
        if status == 'ok':
            base.cr._userLoggingOut = True
            messenger.send(self._parent.doneEvent)
