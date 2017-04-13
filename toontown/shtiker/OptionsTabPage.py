from panda3d.core import TextNode, Vec4, loadPrcFileData, WindowProperties

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.gui.DirectGui import DirectFrame, DirectButton, DGG

from otp.speedchat import SpeedChat, SCColorScheme, SCStaticTextTerminal

from toontown.shtiker import OptionsPageGlobals, ControlRemapDialog
from toontown.toontowngui import TTLabel, TTClickableLabel, TTButton, TTCheckBox, TTSlider, TTDialog, \
    TTRadioButton, TTRadioGroup
from toontown.toontowngui.TTArrow import TTArrow
from toontown.toonbase import ToontownGlobals, TTLocalizer, EventGlobals, SettingsGlobals, ColorGlobals
from toontown.util.PlacerTool3D import PlacerTool3D


class OptionsTabPage(DirectFrame):
    notify = directNotify.newCategory('OptionsTabPage')
    DisplaySettingsTaskName = 'save-display-settings'
    DisplaySettingsDelay = 60
    ChangeDisplaySettings = base.config.GetBool('change-display-settings', 1)
    ChangeDisplayAPI = base.config.GetBool('change-display-api', 0)
    VideoState = 0
    SoundState = 1
    GameplayState = 2
    SocialState = 3

    def __init__(self, parent=aspect2d):
        DirectFrame.__init__(self, parent=parent, relief=None, pos=(0.0, 0.0, 0.0), scale=(1.0, 1.0, 1.0))

        self._parent = parent
        self.currentSizeIndex = None
        self.displaySettingsChanged = 0
        self.displaySettingsSize = (None, None)
        self.displaySettingsFullscreen = None
        self.displaySettingsApi = None
        self.displaySettingsApiChanged = 0
        self.displaySettings = None
        self.customControlDialog = None

        self.speed_chat_scale = 0.055

        self.warning = None
        self.videoDialog = None
        self.hasAvatar = True
        if not hasattr(base, 'localAvatar'):
            self.hasAvatar = False
        self.load()

    def destroy(self):
        self._parent = None
        self.ignoreAll()
        taskMgr.remove('testResolution-task')
        taskMgr.remove('revertResolution-task')
        DirectFrame.destroy(self)

    def load(self):
        rightXBase = -0.4
        rightYBase = 0.4
        leftXBase = 0.05
        textRowHeight = 0.1
        row = 0

        leftFrameGeom = loader.loadModel('phase_3/models/gui/tt_m_gui_ups_panelBg')

        self.leftFrame = DirectFrame(
            parent=self, relief=None, pos=(-0.5, 0.0, 0.0), frameSize=(-0.3, 0.4, -0.5, 0.5), geom=leftFrameGeom,
            geom_scale=(0.75, 0.75, 0.75),
            geom_pos=(0.05, 0, 0.2)
        )
        self.rightFrame = DirectFrame(
            parent=self, relief=None, pos=(0.5, 0.0, 0.0), frameSize=(-0.4, 0.3, -0.5, 0.5)
        )

        self.videoButton = TTClickableLabel.TTClickableLabel(
            self.leftFrame,
            text=TTLocalizer.OptionsPageVideo,
            pos=(leftXBase, 0.0, 0.35),
            command=self.setOptionsState,
            extraArgs=[self.VideoState]
        )
        self.soundButton = TTClickableLabel.TTClickableLabel(
            self.leftFrame,
            text=TTLocalizer.OptionsPageSound,
            pos=(leftXBase, 0.0, 0.24),
            command=self.setOptionsState,
            extraArgs=[self.SoundState]
        )
        self.gameplayButton = TTClickableLabel.TTClickableLabel(
            self.leftFrame,
            text=TTLocalizer.OptionsPageGameplay,
            pos=(leftXBase, 0.0, 0.13),
            command=self.setOptionsState,
            extraArgs=[self.GameplayState]
        )
        self.socialButton = TTClickableLabel.TTClickableLabel(
            self.leftFrame,
            text=TTLocalizer.OptionsPageSocial,
            pos=(leftXBase, 0.0, 0.02),
            command=self.setOptionsState,
            extraArgs=[self.SocialState]
        )

        # -- Video
        self.videoTitle = TTLabel.TTLabel(
            parent=self.rightFrame,
            text_size=TTLabel.TTLabel.MediumSize,
            pos=(-0.40, 0, rightYBase + 0.1),
            text=TTLocalizer.OptionsPageVideo
        )
        self.screenSizes = list(ToontownGlobals.CommonDisplayResolutions[base.calcRatio])
        self.resIndex = self.getResIndex()
        self.resolutionLabel = TTLabel.TTLabel(parent=self.rightFrame, text=TTLocalizer.DisplaySettingsResolution, pos=(-0.33, 0, 0.35))
        self.resolutionValueLabel = TTLabel.TTLabel(
            parent=self.rightFrame,
            text='%s x %s' % tuple(self.screenSizes[self.resIndex]),
            pos=(0.12, 0, 0.35)
        )
        self.resolutionLeftArrow = TTArrow(
            parent=self.rightFrame,
            orientation=TTArrow.OrientationLeft,
            pos=(-0.11, 0, 0.36),
            command=self.__handleLeftResolutionClicked,
            extraArgs=[]
        )
        self.resolutionRightArrow = TTArrow(
            parent=self.rightFrame,
            orientation=TTArrow.OrientationRight,
            pos=(0.34, 0, 0.36),
            command=self.__handleRightResolutionClicked,
            extraArgs=[]
        )
        self.__updateResolutionArrows()
        self.fullscreenLabel = TTLabel.TTLabel(
            parent=self.rightFrame,
            text=TTLocalizer.OptionsPageFullscreen,
            text_align=TextNode.ALeft,
            pos=(-0.45, 0, 0.21)
        )
        self.windowLabel = TTLabel.TTLabel(
            parent=self.rightFrame,
            text=TTLocalizer.OptionsPageWindow,
            text_align=TextNode.ALeft,
            pos=(-0.45, 0, 0.10)
        )
        isFullscreen = settings.get(SettingsGlobals.Fullscreen, False)
        self.fullscreenRadio = TTRadioButton.TTRadioButton(
            parent=self.rightFrame, selected=isFullscreen, value='fullscreen', pos=(-0.11, 0, 0.22)
        )
        self.windowRadio = TTRadioButton.TTRadioButton(
            parent=self.rightFrame, selected=not isFullscreen, value='window', pos=(-0.11, 0, 0.12))
        self.windowSizeRG = TTRadioGroup.TTRadioGroup(buttons=[self.fullscreenRadio, self.windowRadio], command=self.__handleFullscreenRadioClicked)
        self.applyVideoButton = TTButton.TTButton(
            parent=self.rightFrame, text=TTLocalizer.OptionsPageApply, pos=(-0.31, 0, -0.02), disable=True, command=self.__applyVideoChanges)

        self.vsyncLabel = TTLabel.TTLabel(
            parent=self.rightFrame,
            pos=(-0.36, 0.0, -0.28),
            text_align=TextNode.ALeft,
            text=TTLocalizer.OptionsPageVSync,
        )
        self.vsyncCheckBox = TTCheckBox.TTCheckBox(
            parent=self.rightFrame,
            pos=(-0.42, 0, -0.27),
            checked=settings.get(SettingsGlobals.VSync, False),
            command=self.__doToggleVSync
        )
        self.vsyncRequiresRestartLabel = TTLabel.TTLabel(
            parent=self.rightFrame,
            pos=(-0.2, 0.0, -0.29),
            text_align=TextNode.ALeft,
            text_fg=ColorGlobals.CRed,
            text='*'
        )
        self.changedVsync = False
        self.showFpsLabel = TTLabel.TTLabel(
            parent=self.rightFrame,
            pos=(-0.36, 0.0, -0.17),
            text_align=TextNode.ALeft,
            text=TTLocalizer.OptionsPageShowFps,
        )
        self.showFpsCheckBox = TTCheckBox.TTCheckBox(
            parent=self.rightFrame,
            pos=(-0.42, 0, -0.16),
            checked=settings.get(SettingsGlobals.ShowFps, False),
            command=self.__doToggleShowFps
        )
        self.animationSmoothingLabel = TTLabel.TTLabel(
            parent=self.rightFrame,
            pos=(-0.36, 0.0, -0.39),
            text_align=TextNode.ALeft,
            text=TTLocalizer.OptionsPageAnimationSmoothing
        )
        self.animationSmoothingCheckBox = TTCheckBox.TTCheckBox(
            parent=self.rightFrame,
            pos=(-0.42, 0, -0.38),
            checked=settings.get(SettingsGlobals.AnimationSmoothing, True),
            command=self.__doToggleAnimationSmoothing
        )
        self.animationSmoothingRequiresRestartLabel = TTLabel.TTLabel(
            parent=self.rightFrame,
            pos=(0.12, 0.0, -0.4),
            text_align=TextNode.ALeft,
            text_fg=ColorGlobals.CRed,
            text='*'
        )
        self.changedAnimationSmoothing = False
        self.requiresRestartLabel = TTLabel.TTLabel(
            parent=self.rightFrame,
            pos=(-0.04, 0.0, -0.57),
            text_align=TextNode.ALeft,
            text_fg=ColorGlobals.CRed,
            text='* %s' % TTLocalizer.OptionsPageRequiresRestart
        )
        self.requiresRestart = False
        self.animationSmoothingRequiresRestartLabel.hide()
        self.vsyncRequiresRestartLabel.hide()
        self.requiresRestartLabel.hide()

        # -- Sound

        # Volume
        self.volumeTitle = TTLabel.TTLabel(
            parent=self.rightFrame,
            text_size=TTLabel.TTLabel.MediumSize,
            pos=(rightXBase + 0.02, 0, rightYBase + 0.1),
            text=TTLocalizer.OptionsPageSound
        )

        # Music
        row = 0
        self.musicLabel = TTLabel.TTLabel(
            parent=self.rightFrame,
            pos=(rightXBase, 0, rightYBase - 0.0125 - textRowHeight * row),
            text_align=TextNode.ALeft,
            text=TTLocalizer.OptionsPageEnableMusic,
        )
        self.musicCheckBox = TTCheckBox.TTCheckBox(
            parent=self.rightFrame,
            pos=(rightXBase - 0.05, 0, rightYBase - textRowHeight * row),
            checked=base.musicActive,
            command=self.__doToggleMusic
        )
        self.musicSlider = TTSlider.TTSlider(
            parent=self.rightFrame,
            value=self.getMusicVolume(),
            pos=(-0.1, 0, rightYBase - textRowHeight * row - 0.07),
            enabled=base.musicActive,
            command=self.setMusicVolume
        )

        # Sound
        row += 1.5
        self.soundLabel = TTLabel.TTLabel(
            parent=self.rightFrame,
            pos=(rightXBase, 0, rightYBase - 0.0125 - textRowHeight * row),
            text=TTLocalizer.OptionsPageSound,
            text_align=TextNode.ALeft,
        )
        self.soundCheckBox = TTCheckBox.TTCheckBox(
            parent=self.rightFrame,
            pos=(rightXBase - 0.05, 0, rightYBase - textRowHeight * row),
            checked=base.sfxActive,
            command=self.__doToggleSfx
        )
        self.soundSlider = TTSlider.TTSlider(
            parent=self.rightFrame,
            value=self.getSoundVolume(),
            pos=(-0.1, 0, rightYBase - textRowHeight * row - 0.07),
            enabled=base.sfxActive,
            command=self.setSoundVolume
        )
        
        # Classic Music
        row += 1.5
        self.classicMusicLabel = TTLabel.TTLabel(
            parent=self.rightFrame,
            pos=(rightXBase, 0, rightYBase - 0.0125 - textRowHeight * row),
            text=TTLocalizer.OptionsPageClassicMusic,
            text_align=TextNode.ALeft,
        )
        self.classicMusicCheckBox = TTCheckBox.TTCheckBox(
            parent=self.rightFrame,
            pos=(rightXBase - 0.05, 0, rightYBase - textRowHeight * row),
            checked=base.wantClassicMusic,
            command=self.__doToggleClassicMusic
        )

        # -- Social
        row = 0

        # - Chat
        self.chatTitle = TTLabel.TTLabel(
            parent=self.rightFrame,
            text_size=TTLabel.TTLabel.MediumSize,
            pos=(rightXBase - 0.02, 0, rightYBase + 0.1),
            text=TTLocalizer.OptionsPageChat
        )
        if self.hasAvatar:
            # Whisper Settings
            self.whispersLabel = TTLabel.TTLabel(
                parent=self.rightFrame,
                pos=(rightXBase, 0, rightYBase - 0.0125 - textRowHeight * row),
                text=TTLocalizer.OptionsPageAcceptingWhispers,
                text_align=TextNode.ALeft
            )
            self.whispersCheckBox = TTCheckBox.TTCheckBox(
                parent=self.rightFrame,
                pos=(rightXBase - 0.05, 0, rightYBase - textRowHeight * row),
                checked=base.localAvatar.wantWhispers,
                command=self.__doToggleWantWhispers
            )
            row += 0.75
            self.whispersAnyoneLabel = TTLabel.TTLabel(
                parent=self.rightFrame,
                pos=(rightXBase + 0.05, 0, rightYBase - 0.0125 - textRowHeight * row),
                text=TTLocalizer.OptionsPageFromStrangers,
                text_align=TextNode.ALeft,
                text_size=TTLabel.TTLabel.SmallSize
            )
            self.whispersAnyoneCheckBox = TTCheckBox.TTCheckBox(
                parent=self.rightFrame, pos=(rightXBase, 0, rightYBase - textRowHeight * row),
                disable=not base.localAvatar.wantWhispers,
                checked=base.localAvatar.wantNonFriendWhispers,
                command=self.__doToggleWantNonFriendWhispers
            )
            row += 0.75
            self.whispersFriendsLabel = TTLabel.TTLabel(
                parent=self.rightFrame,
                pos=(rightXBase + 0.05, 0, rightYBase - 0.0125 - textRowHeight * row),
                text=TTLocalizer.OptionsPageFromFriends,
                text_align=TextNode.ALeft,
                text_size=TTLabel.TTLabel.SmallSize
            )
            self.whispersFriendsCheckBox = TTCheckBox.TTCheckBox(
                parent=self.rightFrame, pos=(rightXBase, 0, rightYBase - textRowHeight * row),
                disable=not base.localAvatar.wantWhispers,
                checked=base.localAvatar.wantFriendWhispers,
                command=self.__doToggleWantFriendWhispers
            )
            row += 1
            self.speedChatStyleLabel = TTLabel.TTLabel(
                parent=self.rightFrame,
                pos=(rightXBase, 0, rightYBase - 0.0125 - textRowHeight * row),
                text=TTLocalizer.OptionsPageSpeedChatStyleLabel,
                text_align=TextNode.ALeft
            )
            row += 1
    
            self.speedChatStyleLeftArrow = TTArrow(
                parent=self,
                orientation=TTArrow.OrientationLeft,
                pos=(0.25, 0, rightYBase - textRowHeight * row),
                command=self.__doSpeedChatStyleLeft)
            self.speedChatStyleRightArrow = TTArrow(
                parent=self,
                orientation=TTArrow.OrientationRight,
                pos=(0.65, 0, rightYBase - textRowHeight * row),
                command=self.__doSpeedChatStyleRight
            )
            self.speedChatStyleText = SpeedChat.SpeedChat(
                name='OptionsPageStyleText',
                structure=[2000],
                backgroundModelName='phase_3/models/gui/ChatPanel',
                guiModelName='phase_3.5/models/gui/speedChatGui'
            )
            self.speedChatStyleText.setScale(self.speed_chat_scale)
            self.speedChatStyleText.setPos(0.37, 0, rightYBase - textRowHeight * row + 0.03)
            self.speedChatStyleText.reparentTo(self, DGG.FOREGROUND_SORT_INDEX)
    
            row += 2
            # - Friends
            self.friendsTitle = TTLabel.TTLabel(
                parent=self.rightFrame,
                text_size=TTLabel.TTLabel.MediumSize,
                pos=(rightXBase - 0.08, 0, rightYBase - 0.0125 - textRowHeight * row),
                text=TTLocalizer.OptionsPageFriends,
                text_align=TextNode.ALeft
            )
            row += 1
            self.acceptingFriendsLabel = TTLabel.TTLabel(
                parent=self.rightFrame,
                pos=(rightXBase + 0.05, 0, rightYBase - 0.0125 - textRowHeight * row),
                text=TTLocalizer.OptionsPageAcceptingFriends,
                text_align=TextNode.ALeft
            )
            self.acceptingFriendsCheckBox = TTCheckBox.TTCheckBox(
                parent=self.rightFrame,
                pos=(rightXBase - 0.05, 0, rightYBase - textRowHeight * row),
                checked=base.localAvatar.wantFriends,
                command=self.__doToggleWantFriends
            )
    
            if (base.isSinglePlayer or base.isHosting):
                text = TTLocalizer.OptionsDisconnect
            else:
                text = TTLocalizer.OptionsLeaveServer
            self.exitButton = TTButton.TTButton(
                parent=self,
                buttonScale=1.15,
                text=text,
                pos=(-0.45, 0, -0.53),
                command=self.__handleExitServerShowWithConfirm
            )
            self.toonselectButton = TTButton.TTButton(
                parent=self,
                buttonScale=1.15,
                text=TTLocalizer.OptionsReturnToToonSelect,
                pos=(-0.45, 0, -0.33),
                command=self.__handleExitToToonSelectShowWithConfirm
            )

        # -- Gameplay

        row = 0
        # - Controls
        self.controlsTitle = TTLabel.TTLabel(
            parent=self.rightFrame,
            text_size=TTLabel.TTLabel.MediumSize,
            pos=(rightXBase - 0.08, 0, rightYBase + 0.1),
            text=TTLocalizer.OptionsPageControls,
            text_align=TextNode.ALeft
        )

        # Custom Controls
        self.wantCustomControlsLabel = TTLabel.TTLabel(
            parent=self.rightFrame,
            text_size=TTLabel.TTLabel.NormalSize,
            text=TTLocalizer.OptionsPageCustomControls,
            text_align=TextNode.ALeft,
            pos=(rightXBase, 0, rightYBase - 0.0125 - textRowHeight * row)
        )
        self.wantCustomControls = TTCheckBox.TTCheckBox(
            parent=self.rightFrame,
            pos=(rightXBase - 0.05, 0, rightYBase - textRowHeight * row),
            checked=base.wantCustomControls,
            command=self.__doToggleWantCustomControls
        )
        row += 1
        self.configureControlsButton = TTButton.TTButton(
            parent=self.rightFrame,
            text=TTLocalizer.OptionsPageConfigure,
            pos=(rightXBase + 0.2, 0.0, rightYBase - textRowHeight * row),
            disable=not base.wantCustomControls,
            command=self.__openKeyRemapDialog
        )
        self.setOptionsState(self.VideoState)

    def enter(self):
        self.show()
        taskMgr.remove(self.DisplaySettingsTaskName)
        self.settingsChanged = 0
        self.speedChatStyleText.enter()
        self.speedChatStyleIndex = base.localAvatar.getSpeedChatStyleIndex()
        self.updateSpeedChatStyle()
        if self._parent.book.safeMode:
            self.exitButton.hide()
            self.toonselectButton.hide()
        else:
            self.exitButton.show()
            self.toonselectButton.show()

    def exit(self):
        self.ignore('confirmDone')
        self.hide()
        if self.hasAvatar:
            self.speedChatStyleText.exit()
        if self.displaySettingsChanged:
            taskMgr.doMethodLater(
                self.DisplaySettingsDelay,
                self.writeDisplaySettings,
                self.DisplaySettingsTaskName
            )

    def unload(self):
        self.writeDisplaySettings()
        taskMgr.remove(self.DisplaySettingsTaskName)
        if self.displaySettings is not None:
            self.ignore(self.displaySettings.doneEvent)
            self.displaySettings.unload()
        self.displaySettings = None
        if self.hasAvatar:
            self.exitButton.destroy()
            self.toonselectButton.destroy()
            del self.exitButton
            del self.toonselectButton
            self.speedChatStyleText.exit()
            self.speedChatStyleText.destroy()
            del self.speedChatStyleText
        self.currentSizeIndex = None
        self.leftFrame.destroy()
        self.rightFrame.destroy()

    def setOptionsState(self, state):
        messenger.send(EventGlobals.WakeUp)
        self.videoButton.setActive(0)
        self.soundButton.setActive(0)
        self.gameplayButton.setActive(0)
        self.socialButton.setActive(0)
        self.hideVideoGui()
        self.hideSoundGui()
        self.hideGameplayGui()
        self.hideSocialGui()

        if state == self.VideoState:
            self.videoButton.setActive(1)
            self.showVideoGui()
        elif state == self.SoundState:
            self.soundButton.setActive(1)
            self.showSoundGui()
        elif state == self.GameplayState:
            self.gameplayButton.setActive(1)
            self.showGameplayGui()
        elif state == self.SocialState:
            self.socialButton.setActive(1)
            self.showSocialGui()

    def showVideoGui(self):
        self.videoTitle.show()
        self.resolutionLabel.show()
        self.resolutionLeftArrow.show()
        self.resolutionRightArrow.show()
        self.resolutionValueLabel.show()
        self.fullscreenLabel.show()
        self.windowSizeRG.show()
        self.applyVideoButton.show()
        self.windowLabel.show()
        self.showFpsCheckBox.show()
        self.vsyncCheckBox.show()
        self.showFpsLabel.show()
        self.vsyncLabel.show()
        self.animationSmoothingLabel.show()
        self.animationSmoothingCheckBox.show()
        if self.changedVsync:
            self.vsyncRequiresRestartLabel.show()
        if self.changedAnimationSmoothing:
            self.animationSmoothingRequiresRestartLabel.show()
        if self.requiresRestart:
            self.requiresRestartLabel.show()

    def hideVideoGui(self):
        self.videoTitle.hide()
        self.resolutionLabel.hide()
        self.resolutionLeftArrow.hide()
        self.resolutionRightArrow.hide()
        self.resolutionValueLabel.hide()
        self.fullscreenLabel.hide()
        self.windowSizeRG.hide()
        self.windowLabel.hide()
        self.applyVideoButton.hide()
        self.showFpsCheckBox.hide()
        self.vsyncCheckBox.hide()
        self.showFpsLabel.hide()
        self.vsyncLabel.hide()
        self.animationSmoothingLabel.hide()
        self.animationSmoothingCheckBox.hide()
        self.requiresRestartLabel.hide()
        self.vsyncRequiresRestartLabel.hide()
        self.animationSmoothingRequiresRestartLabel.hide()

    def showSoundGui(self):
        self.volumeTitle.show()
        self.musicCheckBox.show()
        self.musicLabel.show()
        self.musicSlider.show()
        self.soundCheckBox.show()
        self.soundLabel.show()
        self.soundSlider.show()
        self.classicMusicCheckBox.show()
        self.classicMusicLabel.show()

    def hideSoundGui(self):
        self.volumeTitle.hide()
        self.musicCheckBox.hide()
        self.musicLabel.hide()
        self.musicSlider.hide()
        self.soundCheckBox.hide()
        self.soundLabel.hide()
        self.soundSlider.hide()
        self.classicMusicCheckBox.hide()
        self.classicMusicLabel.hide()
        
    def showGameplayGui(self):
        self.controlsTitle.show()
        self.wantCustomControlsLabel.show()
        self.wantCustomControls.show()
        self.configureControlsButton.show()

    def hideGameplayGui(self):
        self.controlsTitle.hide()
        self.wantCustomControlsLabel.hide()
        self.wantCustomControls.hide()
        self.configureControlsButton.hide()

    def showSocialGui(self):
        rightXBase = -0.4
        rightYBase = 0.4
        self.chatTitle.show()
        if not self.hasAvatar:
            self.chatTitle['text'] = "You need to be in game to access these settings!"
            self.chatTitle.setPos(0, 0, rightYBase + 0.1)
        if self.hasAvatar:
            self.friendsTitle.show()
            self.whispersCheckBox.show()
            self.whispersLabel.show()
            self.whispersAnyoneCheckBox.show()
            self.whispersAnyoneLabel.show()
            self.whispersFriendsCheckBox.show()
            self.whispersFriendsLabel.show()
            self.acceptingFriendsLabel.show()
            self.acceptingFriendsCheckBox.show()
            self.speedChatStyleLabel.show()
            self.speedChatStyleLeftArrow.show()
            self.speedChatStyleRightArrow.show()
            self.speedChatStyleText.show()

    def hideSocialGui(self):
        self.chatTitle.hide()
        if self.hasAvatar:
            self.friendsTitle.hide()
            self.whispersCheckBox.hide()
            self.whispersLabel.hide()
            self.whispersAnyoneCheckBox.hide()
            self.whispersAnyoneLabel.hide()
            self.whispersFriendsCheckBox.hide()
            self.whispersFriendsLabel.hide()
            self.acceptingFriendsLabel.hide()
            self.acceptingFriendsCheckBox.hide()
            self.speedChatStyleLabel.hide()
            self.speedChatStyleLeftArrow.hide()
            self.speedChatStyleRightArrow.hide()
            self.speedChatStyleText.hide()

    def getMusicVolume(self):
        # We want it as a value between 0-100
        return settings.get(SettingsGlobals.MusicVolume, 1) * 100

    def setMusicVolume(self, volume=None):
        messenger.send(EventGlobals.WakeUp)
        if volume is None:
            volume = self.musicSlider.getValue()
        else:
            self.musicSlider.setValue(volume)
        # We store it as a value between 0 - 1
        base.musicManager.setVolume(volume/100)
        settings[SettingsGlobals.MusicVolume] = volume/100

    def getSoundVolume(self):
        # We want it as a value between 0-100
        return settings.get(SettingsGlobals.SoundVolume, 1) * 100

    def setSoundVolume(self, volume=None):
        messenger.send(EventGlobals.WakeUp)
        if volume is None:
            volume = self.soundSlider.getValue()
        else:
            self.soundSlider.setValue(volume)
        base.setSfxVolume(volume/100)
        settings[SettingsGlobals.SoundVolume] = volume/100

    def __doToggleMusic(self):
        messenger.send(EventGlobals.WakeUp)
        if base.musicActive:
            base.enableMusic(0)
            settings[SettingsGlobals.Music] = False
            self.musicSlider.disable()
        else:
            base.enableMusic(1)
            settings[SettingsGlobals.Music] = True
            self.musicSlider.enable()
            
    def __doToggleClassicMusic(self):
        messenger.send(EventGlobals.WakeUp)
        if base.wantClassicMusic:
            settings[SettingsGlobals.ClassicMusic] = False
            base.wantClassicMusic = False
        else:
            settings[SettingsGlobals.ClassicMusic] = True
            base.wantClassicMusic = True

    def __doToggleVSync(self):
        messenger.send(EventGlobals.WakeUp)
        flag = not settings.get(SettingsGlobals.VSync, False)
        settings[SettingsGlobals.VSync] = flag
        self.vsyncRequiresRestartLabel.show()
        self.requiresRestartLabel.show()
        self.requiresRestart = True
        self.changedVsync = True

    def __doToggleShowFps(self):
        messenger.send(EventGlobals.WakeUp)
        if settings.get(SettingsGlobals.ShowFps, False):
            settings[SettingsGlobals.ShowFps] = False
            base.setFrameRateMeter(False)
        else:
            settings[SettingsGlobals.ShowFps] = True
            base.setFrameRateMeter(True)

    def __doToggleAnimationSmoothing(self):
        messenger.send(EventGlobals.WakeUp)
        flag = not settings.get(SettingsGlobals.AnimationSmoothing, True)
        settings[SettingsGlobals.AnimationSmoothing] = flag
        self.animationSmoothingRequiresRestartLabel.show()
        self.requiresRestartLabel.show()
        self.requiresRestart = True
        self.changedAnimationSmoothing = True

    def __doToggleSfx(self):
        messenger.send(EventGlobals.WakeUp)
        if base.sfxActive:
            base.enableSoundEffects(0)
            settings[SettingsGlobals.Sound] = False
            self.soundSlider.disable()
        else:
            base.enableSoundEffects(1)
            settings[SettingsGlobals.Sound] = True
            self.soundSlider.enable()

    def __doToggleWantFriends(self):
        messenger.send(EventGlobals.WakeUp)
        wantFriends = settings.get(SettingsGlobals.WantFriends, {})
        if base.localAvatar.wantFriends:
            base.localAvatar.wantFriends = 0
            wantFriends[str(base.localAvatar.doId)] = False
        else:
            base.localAvatar.wantFriends = 1
            wantFriends[str(base.localAvatar.doId)] = True
        settings[SettingsGlobals.WantFriends] = wantFriends

    def __doToggleWantWhispers(self):
        messenger.send(EventGlobals.WakeUp)
        wantWhispers = settings.get(SettingsGlobals.WantWhispers, {})
        if base.localAvatar.wantWhispers:
            base.localAvatar.wantWhispers = False
            wantWhispers[str(base.localAvatar.doId)] = False
            self.whispersAnyoneCheckBox.disable()
            self.whispersFriendsCheckBox.disable()
        else:
            base.localAvatar.wantWhispers = True
            wantWhispers[str(base.localAvatar.doId)] = True
            self.whispersAnyoneCheckBox.enable()
            self.whispersFriendsCheckBox.enable()
        settings[SettingsGlobals.WantWhispers] = wantWhispers

    def __doToggleWantNonFriendWhispers(self):
        messenger.send(EventGlobals.WakeUp)
        wantNonFriendWhispers = settings.get(SettingsGlobals.WantNonFriendWhispers, {})
        if base.localAvatar.wantNonFriendWhispers:
            base.localAvatar.wantNonFriendWhispers = 0
            wantNonFriendWhispers[str(base.localAvatar.doId)] = False
        else:
            base.localAvatar.wantNonFriendWhispers = 1
            wantNonFriendWhispers[str(base.localAvatar.doId)] = True
        settings[SettingsGlobals.WantNonFriendWhispers] = wantNonFriendWhispers

    def __doToggleWantFriendWhispers(self):
        messenger.send(EventGlobals.WakeUp)
        wantFriendWhispers = settings.get(SettingsGlobals.WantFriendWhispers, {})
        if base.localAvatar.wantFriendWhispers:
            base.localAvatar.wantFriendWhispers = False
            wantFriendWhispers[str(base.localAvatar.doId)] = False
        else:
            base.localAvatar.wantFriendWhispers = True
            wantFriendWhispers[str(base.localAvatar.doId)] = True
        settings[SettingsGlobals.WantFriendWhispers] = wantFriendWhispers

    def __doToggleWantCustomControls(self):
        messenger.send(EventGlobals.WakeUp)
        if base.wantCustomControls:
            base.wantCustomControls = settings[SettingsGlobals.WantCustomControls] = False
            self.configureControlsButton.disable()
        else:
            base.wantCustomControls = settings[SettingsGlobals.WantCustomControls] = True
            self.configureControlsButton.enable()

        base.reloadControls()
        if self.hasAvatar:
            base.localAvatar.controlManager.reload()
            base.localAvatar.chatMgr.reloadWASD()
            base.localAvatar.controlManager.disable()

    def __doSpeedChatStyleLeft(self):
        if self.speedChatStyleIndex > 0:
            self.speedChatStyleIndex = self.speedChatStyleIndex - 1
            self.updateSpeedChatStyle()

    def __doSpeedChatStyleRight(self):
        if self.speedChatStyleIndex < len(OptionsPageGlobals.speedChatStyles) - 1:
            self.speedChatStyleIndex = self.speedChatStyleIndex + 1
            self.updateSpeedChatStyle()

    def __openKeyRemapDialog(self):
        if base.wantCustomControls:
            self.customControlDialog = ControlRemapDialog.ControlRemap()

    def __applyVideoChanges(self):
        # Set fullscreen changes
        fullscreen = False
        if self.windowSizeRG.selectedButton.value == 'fullscreen':
            fullscreen = True

        # Set resolution changes
        res = self.screenSizes[self.resIndex]

        # Reload graphics pipe
        wp = WindowProperties()
        wp.setSize(res[0], res[1])
        wp.setFullscreen(fullscreen)
        base.win.requestProperties(wp)
        # Test the resolution and ask the user if they want to keep it
        taskMgr.doMethodLater(0.1, self.testResolution, 'testResolution-task', extraArgs=[res])
        # Revert after 15 seconds of inactivity
        taskMgr.doMethodLater(15, self.revertResolution, 'revertResolution-task', extraArgs=[])
        # Disable apply video so, no need now
        self.applyVideoButton.disable()

    def __videoOptionsChanged(self):
        self.applyVideoButton.enable()

    def revertResolution(self):
        if self.videoDialog:
            self.videoDialog.cleanup()
            self.videoDialog = None
        wp = WindowProperties()
        wp.setFullscreen(settings['fullscreen'])
        res = settings['res']
        wp.setSize(res[0], res[1])
        base.win.requestProperties(wp)
        # Re-enable apply video button because we didn't apply changes
        self.applyVideoButton.enable()

    def testResolution(self, res):
        # Tests if the resolution code ran
        rejectedProperties = base.win.getRejectedProperties()
        failed = False
        if rejectedProperties.hasSize():
            self.notify.warning('Failed to set properties, invalid resolution')
            failed = True
        if rejectedProperties.getFullscreen():
            self.notify.warning('Failed to set fullscreen mode')
            failed = True
        base.win.clearRejectedProperties()
        if failed:
            if self.warning:
                self.warning.cleanup()
            self.warning = TTDialog.TTGlobalDialog(
                style=TTDialog.Acknowledge,
                doneEvent='confirmWarning',
                message='Failed to set new display mode: Invalid settings for monitor size.'
            )
            self.accept('confirmWarning', self.__handleWarningDone)
            self.applyVideoButton.enable()
            if taskMgr.hasTaskNamed('revertResolution-task'):
                taskMgr.remove('revertResolution-task')
                self.revertResolution()
        else:
            if self.videoDialog:
                self.videoDialog.cleaup()
            self.videoDialog = TTDialog.TTGlobalDialog(
                style=TTDialog.TwoChoice,
                doneEvent='confirmVideo',
                message='Do you want to keep these settings? If you don\'t they will revert in (15) seconds.'
            )
            self.accept('confirmVideo', self.__handleVideoConfirmDone)

    def __handleVideoConfirmDone(self, e=None):
        status = self.videoDialog.doneStatus
        self.ignore('confirmVideo')
        self.videoDialog.cleanup()
        self.videoDialog = None

        if status == 'ok':
            # Save the settings
            settings['fullscreen'] = self.windowSizeRG.selectedButton.value == 'fullscreen'
            settings['res'] = self.screenSizes[self.resIndex]
            if taskMgr.hasTaskNamed('revertResolution-task'):
                taskMgr.remove('revertResolution-task')
        else:
            print('cancelled change to window')
            # Make the revert task trigger now
            if taskMgr.hasTaskNamed('revertResolution-task'):
                taskMgr.remove('revertResolution-task')
                self.revertResolution()

    def __handleWarningDone(self, e=None):
        self.ignore('warningDone')
        self.warning.cleanup()
        self.warning = None

    def __updateResolutionArrows(self):
        if self.resIndex == 0:
            self.resolutionLeftArrow['state'] = DGG.DISABLED
        else:
            self.resolutionLeftArrow['state'] = DGG.NORMAL
        if self.resIndex + 1 >= len(self.screenSizes):
            self.resolutionRightArrow['state'] = DGG.DISABLED
        else:
            self.resolutionRightArrow['state'] = DGG.NORMAL

    def __handleLeftResolutionClicked(self):
        messenger.send(EventGlobals.WakeUp)
        if self.resIndex == 0:
            return
        else:
            self.resIndex -= 1

        self.__updateResolutionArrows()
        self.__videoOptionsChanged()
        self.resolutionValueLabel['text'] = '%s x %s' % tuple(self.screenSizes[self.resIndex])

    def __handleRightResolutionClicked(self):
        messenger.send(EventGlobals.WakeUp)
        if self.resIndex + 1 >= len(self.screenSizes):
            return
        else:
            self.resIndex += 1
        self.__updateResolutionArrows()
        self.__videoOptionsChanged()
        self.resolutionValueLabel['text'] = '%s x %s' % tuple(self.screenSizes[self.resIndex])

    def __handleFullscreenRadioClicked(self, value):
        messenger.send(EventGlobals.WakeUp)
        self.__videoOptionsChanged()

    def getResIndex(self):
        res = tuple(settings.get(SettingsGlobals.Resolution, base.getSmallestResolution()))
        if res not in self.screenSizes:
            # The player's resolution is not in our screen sizes, this means they changed it to be something
            # incompatible or our res detection couldn't find a resolution for their native ratio so we have invalid
            # values for our self.screenSizes...
            newRes = base.getSmallestResolution()
            # Getting the new smallest resolution above will adapt
            # base.calcRatio, so we must get a new set of
            # screenSizes
            self.screenSizes = list(ToontownGlobals.CommonDisplayResolutions[base.calcRatio])
            if res not in self.screenSizes:
                # Our resolution is STILL not in these screen sizes, the user must be involved with this confusion
                # so we will reset their res to the smallest resolution
                res = newRes
        return self.screenSizes.index(res)

    def updateSpeedChatStyle(self):
        nameKey, arrowColor, rolloverColor, frameColor = OptionsPageGlobals.speedChatStyles[self.speedChatStyleIndex]
        newSCColorScheme = SCColorScheme.SCColorScheme(
            arrowColor=arrowColor,
            rolloverColor=rolloverColor,
            frameColor=frameColor
        )
        self.speedChatStyleText.setColorScheme(newSCColorScheme)
        self.speedChatStyleText.clearMenu()
        colorName = SCStaticTextTerminal.SCStaticTextTerminal(nameKey)
        self.speedChatStyleText.append(colorName)
        self.speedChatStyleText.finalize()
        self.speedChatStyleText.setPos(
            0.445 -
            self.speedChatStyleText.getWidth() *
            self.speed_chat_scale /
            2,
            0,
            self.speedChatStyleText.getPos()[2])
        if self.speedChatStyleIndex > 0:
            self.speedChatStyleLeftArrow.enable()
        else:
            self.speedChatStyleLeftArrow.disable()
        if self.speedChatStyleIndex < len(OptionsPageGlobals.speedChatStyles) - 1:
            self.speedChatStyleRightArrow.enable()
        else:
            self.speedChatStyleRightArrow.disable()
        base.localAvatar.b_setSpeedChatStyleIndex(self.speedChatStyleIndex)

    def writeDisplaySettings(self, task=None):
        if not self.displaySettingsChanged:
            return
        taskMgr.remove(self.DisplaySettingsTaskName)
        settings['res'] = (self.displaySettingsSize[0], self.displaySettingsSize[1])
        settings['fullscreen'] = self.displaySettingsFullscreen

    def __handleExitServerShowWithConfirm(self):
        if base.isHosting:
            message = TTLocalizer.OptionsPageExitConfirmMultiplayerHost
        else:
            message = TTLocalizer.OptionsPageExitConfirmMultiplayer
        if base.isSinglePlayer:
            message = TTLocalizer.OptionsPageExitConfirmSingleplayer
        self.confirm = TTDialog.TTGlobalDialog(
            doneEvent='confirmDone',
            message=message,
            style=TTDialog.TwoChoice
        )
        self.confirm.show()
        self._parent.doneStatus = {'mode': 'exit',
                                  'exitTo': 'disconnect'}
        self.accept('confirmDone', self.__handleConfirm)

    def __handleExitToToonSelectShowWithConfirm(self):
        self.confirm = TTDialog.TTGlobalDialog(
            doneEvent='confirmDone',
            message=TTLocalizer.OptionsPagePickAToonConfirm,
            style=TTDialog.TwoChoice)
        self.confirm.show()
        self._parent.doneStatus = {'mode': 'exit',
                                  'exitTo': 'closeShard'}
        self.accept('confirmDone', self.__handleConfirm)

    def __handleConfirm(self):
        status = self.confirm.doneStatus
        self.ignore('confirmDone')
        self.confirm.cleanup()
        del self.confirm
        if status == 'ok':
            base.cr._userLoggingOut = True
            messenger.send(self._parent.doneEvent)

    def __back(self):
        status = self.confirm.doneStatus
        self.ignore('confirmDone')
        self.confirm.cleanup()
        del self.confirm
        if status == 'ok':
            base.cr._userLoggingOut = True
            messenger.send(self._parent.doneEvent)
            base.cr.loginFSM.request('homeScreen')
            base.cr.mainMenu.LocalSinglePlayerStart.demand('Off')