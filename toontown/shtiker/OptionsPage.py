from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.gui.DirectGui import *
from direct.showbase import PythonUtil
from direct.task import Task
from pandac.PandaModules import *

import DisplaySettingsDialog
import ShtikerPage
from otp.speedchat import SCColorScheme
from otp.speedchat import SCStaticTextTerminal
from otp.speedchat import SpeedChat
from toontown.shtiker.OptionsPageGUI import OptionTab, OptionButton, OptionLabel
from toontown.shtiker import ControlRemapDialog
from toontown.toonbase import TTLocalizer, EventGlobals, SettingsGlobals
from toontown.toontowngui import TTDialog, TTCheckBox, TTButton, TTSlider, TTLabel, TTClickableLabel


speedChatStyles = (
    (
        2000,
        (200 / 255.0, 60 / 255.0, 229 / 255.0),
        (200 / 255.0, 135 / 255.0, 255 / 255.0),
        (220 / 255.0, 195 / 255.0, 229 / 255.0)
    ),
    (
        2012,
        (142 / 255.0, 151 / 255.0, 230 / 255.0),
        (173 / 255.0, 180 / 255.0, 237 / 255.0),
        (220 / 255.0, 195 / 255.0, 229 / 255.0)
    ),
    (
        2001,
        (0 / 255.0, 0 / 255.0, 255 / 255.0),
        (140 / 255.0, 150 / 255.0, 235 / 255.0),
        (201 / 255.0, 215 / 255.0, 255 / 255.0)
    ),
    (
        2010,
        (0 / 255.0, 119 / 255.0, 190 / 255.0),
        (53 / 255.0, 180 / 255.0, 255 / 255.0),
        (201 / 255.0, 215 / 255.0, 255 / 255.0)
    ),
    (
        2014,
        (0 / 255.0, 64 / 255.0, 128 / 255.0),
        (0 / 255.0, 64 / 255.0, 128 / 255.0),
        (201 / 255.0, 215 / 255.0, 255 / 255.0)
    ),
    (
        2002,
        (90 / 255.0, 175 / 255.0, 225 / 255.0),
        (120 / 255.0, 215 / 255.0, 255 / 255.0),
        (208 / 255.0, 230 / 255.0, 250 / 255.0)
    ),
    (
        2003,
        (130 / 255.0, 235 / 255.0, 235 / 255.0),
        (120 / 255.0, 225 / 255.0, 225 / 255.0),
        (234 / 255.0, 255 / 255.0, 255 / 255.0)
    ),
    (
        2004,
        (0 / 255.0, 200 / 255.0, 70 / 255.0),
        (0 / 255.0, 200 / 255.0, 80 / 255.0),
        (204 / 255.0, 255 / 255.0, 204 / 255.0)
    ),
    (
        2015,
        (13 / 255.0, 255 / 255.0, 100 / 255.0),
        (64 / 255.0, 255 / 255.0, 131 / 255.0),
        (204 / 255.0, 255 / 255.0, 204 / 255.0)
    ),
    (
        2005,
        (235 / 255.0, 230 / 255.0, 0 / 255.0),
        (255 / 255.0, 250 / 255.0, 100 / 255.0),
        (255 / 255.0, 250 / 255.0, 204 / 255.0)
    ),
    (
        2006,
        (255 / 255.0, 153 / 255.0, 0 / 255.0),
        (229 / 255.0, 147 / 255.0, 0 / 255.0),
        (255 / 255.0, 234 / 255.0, 204 / 255.0)
    ),
    (
        2011,
        (255 / 255.0, 177 / 255.0, 62 / 255.0),
        (255 / 255.0, 200 / 255.0, 117 / 255.0),
        (255 / 255.0, 234 / 255.0, 204 / 255.0)
    ),
    (
        2007,
        (255 / 255.0, 0 / 255.0, 50 / 255.0),
        (229 / 255.0, 0 / 255.0, 50 / 255.0),
        (255 / 255.0, 204 / 255.0, 204 / 255.0)
    ),
    (
        2013,
        (130 / 255.0, 0 / 255.0, 26 / 255.0),
        (179 / 255.0, 0 / 255.0, 50 / 255.0),
        (255 / 255.0, 204 / 255.0, 204 / 255.0)
    ),
    (
        2016,
        (176 / 255.0, 35 / 255.0, 0 / 255.0),
        (240 / 255.0, 48 / 255.0, 0 / 255.0),
        (255 / 255.0, 204 / 255.0, 204 / 255.0)
    ),
    (
        2008,
        (255 / 255.0, 153 / 255.0, 193 / 255.0),
        (240 / 255.0, 157 / 255.0, 192 / 255.0),
        (255 / 255.0, 215 / 255.0, 238 / 255.0)
    ),
    (
        2009,
        (170 / 255.0, 120 / 255.0, 20 / 255.0),
        (165 / 255.0, 120 / 255.0, 50 / 255.0),
        (210 / 255.0, 200 / 255.0, 180 / 255.0)
    )
)
PageMode = PythonUtil.Enum('Options, Codes')


class OptionsPage(ShtikerPage.ShtikerPage):
    notify = directNotify.newCategory('OptionsPage')

    def __init__(self):
        ShtikerPage.ShtikerPage.__init__(self)

        self.optionsTabPage = None
        self.codesTabPage = None
        self.title = None
        self.optionsTab = None
        self.codesTab = None

    def load(self):
        ShtikerPage.ShtikerPage.load(self)

        self.optionsTabPage = OptionsTabPage(self)
        self.optionsTabPage.hide()
        self.codesTabPage = CodesTabPage(self)
        self.codesTabPage.hide()

        self.title = DirectLabel(
            parent=self, relief=None, text=TTLocalizer.OptionsPageTitle,
            text_scale=0.12, pos=(0, 0, 0.61))

        self.optionsTab = OptionTab(
            parent=self, tabType=1, text=TTLocalizer.OptionsPageTitle, text_scale=TTLocalizer.OPoptionsTab,
            text_pos=(0.01, 0.0, 0.0), image_pos=(0.55, 1, -0.91), pos=(-0.4, 0, 0.77),
            command=self.setMode, extraArgs=[PageMode.Options])

        self.codesTab = OptionTab(
            parent=self, text=TTLocalizer.OptionsPageCodesTab, text_scale=TTLocalizer.OPoptionsTab,
            text_pos=(-0.035, 0.0, 0.0), image_pos=(0.12, 1, -0.91), pos=(0.2, 0, 0.77),
            command=self.setMode, extraArgs=[PageMode.Codes])

    def enter(self):
        self.setMode(PageMode.Options, updateAnyways=1)

        ShtikerPage.ShtikerPage.enter(self)

    def exit(self):
        self.optionsTabPage.exit()
        self.codesTabPage.exit()

        ShtikerPage.ShtikerPage.exit(self)

    def unload(self):
        if self.optionsTabPage is not None:
            self.optionsTabPage.unload()
            self.optionsTabPage = None

        if self.codesTabPage is not None:
            self.codesTabPage.unload()
            self.codesTabPage = None

        if self.title is not None:
            self.title.destroy()
            self.title = None

        if self.optionsTab is not None:
            self.optionsTab.destroy()
            self.optionsTab = None

        if self.codesTab is not None:
            self.codesTab.destroy()
            self.codesTab = None

        ShtikerPage.ShtikerPage.unload(self)

    def setMode(self, mode, updateAnyways=0):
        messenger.send('wakeup')

        if not updateAnyways:
            if self.mode == mode:
                return

        self.mode = mode

        if mode == PageMode.Options:
            self.title['text'] = TTLocalizer.OptionsPageTitle
            self.optionsTab['state'] = DGG.DISABLED
            self.optionsTabPage.enter()
            self.codesTab['state'] = DGG.NORMAL
            self.codesTabPage.exit()
        elif mode == PageMode.Codes:
            self.title['text'] = TTLocalizer.CdrPageTitle
            self.optionsTab['state'] = DGG.NORMAL
            self.optionsTabPage.exit()
            self.codesTab['state'] = DGG.DISABLED
            self.codesTabPage.enter()
        else:
            self.notify.warning('Invalid mode for options page %s' % mode)


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

        self.parent = parent
        self.currentSizeIndex = None
        self.displaySettingsChanged = 0
        self.displaySettingsSize = (None, None)
        self.displaySettingsFullscreen = None
        self.displaySettingsApi = None
        self.displaySettingsApiChanged = 0
        self.displaySettings = None
        self.customControlDialog = None

        self.speed_chat_scale = 0.055

        self.load()

    def destroy(self):
        self.parent = None

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
            text='Video',
            pos=(leftXBase, 0.0, 0.35),
            command=self.setOptionsState,
            extraArgs=[self.VideoState]
        )
        self.soundButton = TTClickableLabel.TTClickableLabel(
            self.leftFrame,
            text='Sound',
            pos=(leftXBase, 0.0, 0.24),
            command=self.setOptionsState,
            extraArgs=[self.SoundState]
        )
        self.gameplayButton = TTClickableLabel.TTClickableLabel(
            self.leftFrame,
            text='Gameplay',
            pos=(leftXBase, 0.0, 0.13),
            command=self.setOptionsState,
            extraArgs=[self.GameplayState]
        )
        self.socialButton = TTClickableLabel.TTClickableLabel(
            self.leftFrame,
            text='Social',
            pos=(leftXBase, 0.0, 0.02),
            command=self.setOptionsState,
            extraArgs=[self.SocialState]
        )

        # -- Video

        # Display Button
        # TODO: Bring this stuff from there into this gui
        self.displaySettingsButton = TTButton.TTButton(
            parent=self.rightFrame,
            text=TTLocalizer.OptionsPageChange,
            pos=(-0.1, 0.0, rightYBase + textRowHeight * row),
            command=self.__doDisplaySettings
        )

        # -- Sound

        # Volume
        self.volumeTitle = TTLabel.TTLabel(
            parent=self.rightFrame,
            text_size=TTLabel.TTLabel.MediumSize,
            pos=(rightXBase + 0.02, 0, rightYBase + 0.1),
            text='Volume'
        )

        # Music
        row = 0
        self.musicLabel = TTLabel.TTLabel(
            parent=self.rightFrame,
            pos=(rightXBase, 0, rightYBase - 0.0125 - textRowHeight * row),
            text_align=TextNode.ALeft,
            text='Enable Music',
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
            text='Sound',
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

        # -- Social
        row = 0

        # - Chat
        self.chatTitle = TTLabel.TTLabel(
            parent=self.rightFrame,
            text_size=TTLabel.TTLabel.MediumSize,
            pos=(rightXBase - 0.02, 0, rightYBase + 0.1),
            text='Chat'
        )

        # Whisper Settings
        self.whispersLabel = TTLabel.TTLabel(
            parent=self.rightFrame,
            pos=(rightXBase, 0, rightYBase - 0.0125 - textRowHeight * row),
            text='Accepting Whispers',
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
            text='From Strangers',
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
            text='From Friends',
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

        gui = loader.loadModel('phase_3.5/models/gui/friendslist_gui')
        self.speedChatStyleLeftArrow = DirectButton(
            parent=self,
            relief=None,
            image=(
                gui.find('**/Horiz_Arrow_UP'),
                gui.find('**/Horiz_Arrow_DN'),
                gui.find('**/Horiz_Arrow_Rllvr'),
                gui.find('**/Horiz_Arrow_UP')),
            image3_color=Vec4(1, 1, 1, 0.5),
            scale=(-1.0, 1.0, 1.0),
            pos=(0.25, 0, rightYBase - textRowHeight * row),
            command=self.__doSpeedChatStyleLeft)
        self.speedChatStyleRightArrow = DirectButton(
            parent=self,
            relief=None,
            image=(
                gui.find('**/Horiz_Arrow_UP'),
                gui.find('**/Horiz_Arrow_DN'),
                gui.find('**/Horiz_Arrow_Rllvr'),
                gui.find('**/Horiz_Arrow_UP')),
            image3_color=Vec4(1, 1, 1, 0.5),
            pos=(0.65, 0, rightYBase - textRowHeight * row),
            command=self.__doSpeedChatStyleRight)
        self.speedChatStyleText = SpeedChat.SpeedChat(name='OptionsPageStyleText',
            structure=[2000],
            backgroundModelName='phase_3/models/gui/ChatPanel',
            guiModelName='phase_3.5/models/gui/speedChatGui')
        self.speedChatStyleText.setScale(self.speed_chat_scale)
        self.speedChatStyleText.setPos(0.37, 0, rightYBase - textRowHeight * row + 0.03)
        self.speedChatStyleText.reparentTo(self, DGG.FOREGROUND_SORT_INDEX)

        row += 2
        # - Friends
        self.friendsTitle = TTLabel.TTLabel(
            parent=self.rightFrame,
            text_size=TTLabel.TTLabel.MediumSize,
            pos=(rightXBase - 0.08, 0, rightYBase - 0.0125 - textRowHeight * row),
            text='Friends',
            text_align=TextNode.ALeft
        )
        row += 1
        self.acceptingFriendsLabel = TTLabel.TTLabel(
            parent=self.rightFrame,
            pos=(rightXBase + 0.05, 0, rightYBase - 0.0125 - textRowHeight * row),
            text='Accepting Friends',
            text_align=TextNode.ALeft
        )
        self.acceptingFriendsCheckBox = TTCheckBox.TTCheckBox(
            parent=self.rightFrame,
            pos=(rightXBase - 0.05, 0, rightYBase - textRowHeight * row),
            checked=base.localAvatar.wantFriends,
            command=self.__doToggleWantFriends
        )

        self.exitButton = OptionButton(
            parent=self,
            image_scale=1.15,
            text=TTLocalizer.OptionsDisconnect,
            pos=(-0.45, 0, -0.53), command=self.__handleExitServerShowWithConfirm
        )
        self.toonselectButton = OptionButton(
            parent=self,
            image_scale=1.15,
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
            text='Controls',
            text_align=TextNode.ALeft
        )

        # Custom Controls
        self.wantCustomControlsLabel = TTLabel.TTLabel(
            parent=self.rightFrame,
            text_size=TTLabel.TTLabel.NormalSize,
            text='Custom Controls',
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
            text='Configure',
            pos=(rightXBase + 0.2, 0.0, rightYBase - textRowHeight * row),
            disable=not base.wantCustomControls,
            command=self.__openKeyRemapDialog
        )
        gui.removeNode()

        self.setOptionsState(self.VideoState)

    def enter(self):
        self.show()
        taskMgr.remove(self.DisplaySettingsTaskName)
        self.settingsChanged = 0
        self.speedChatStyleText.enter()
        self.speedChatStyleIndex = base.localAvatar.getSpeedChatStyleIndex()
        self.updateSpeedChatStyle()
        if self.parent.book.safeMode:
            self.exitButton.hide()
            self.toonselectButton.hide()
        else:
            self.exitButton.show()
            self.toonselectButton.show()

    def exit(self):
        self.ignore('confirmDone')
        self.hide()
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
        self.displaySettingsButton.show()

    def hideVideoGui(self):
        self.displaySettingsButton.hide()

    def showSoundGui(self):
        self.volumeTitle.show()
        self.musicCheckBox.show()
        self.musicLabel.show()
        self.musicSlider.show()
        self.soundCheckBox.show()
        self.soundLabel.show()
        self.soundSlider.show()

    def hideSoundGui(self):
        self.volumeTitle.hide()
        self.musicCheckBox.hide()
        self.musicLabel.hide()
        self.musicSlider.hide()
        self.soundCheckBox.hide()
        self.soundLabel.hide()
        self.soundSlider.hide()

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
        self.friendsTitle.show()
        self.chatTitle.show()
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
        self.friendsTitle.hide()
        self.chatTitle.hide()
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
        base.localAvatar.controlManager.reload()
        base.localAvatar.chatMgr.reloadWASD()
        base.localAvatar.controlManager.disable()

    def __doDisplaySettings(self):
        if self.displaySettings is None:
            self.displaySettings = DisplaySettingsDialog.DisplaySettingsDialog()
            self.displaySettings.load()
            self.accept(self.displaySettings.doneEvent, self.__doneDisplaySettings)
        self.displaySettings.enter(self.ChangeDisplaySettings, self.ChangeDisplayAPI)

    def __doneDisplaySettings(self, anyChanged, apiChanged):
        if anyChanged:
            self.__setDisplaySettings()
            properties = base.win.getProperties()
            self.displaySettingsChanged = 1
            self.displaySettingsSize = (properties.getXSize(), properties.getYSize())
            self.displaySettingsFullscreen = properties.getFullscreen()
            self.displaySettingsApi = base.pipe.getInterfaceName()
            self.displaySettingsApiChanged = apiChanged

    def __setDisplaySettings(self):
        properties = base.win.getProperties()
        if properties.getFullscreen():
            screensize = '%s x %s' % (properties.getXSize(), properties.getYSize())
        else:
            screensize = TTLocalizer.OptionsPageDisplayWindowed
        api = base.pipe.getInterfaceName()
        settings = {'screensize': screensize,
                    'api': api}
        if self.ChangeDisplayAPI:
            OptionsPage.notify.debug('change display settings...')
            text = TTLocalizer.OptionsPageDisplaySettings % settings
        else:
            OptionsPage.notify.debug('no change display settings...')
            text = TTLocalizer.OptionsPageDisplaySettingsNoApi % settings
        self.DisplaySettings_Label['text'] = text

    def __doSpeedChatStyleLeft(self):
        if self.speedChatStyleIndex > 0:
            self.speedChatStyleIndex = self.speedChatStyleIndex - 1
            self.updateSpeedChatStyle()

    def __doSpeedChatStyleRight(self):
        if self.speedChatStyleIndex < len(speedChatStyles) - 1:
            self.speedChatStyleIndex = self.speedChatStyleIndex + 1
            self.updateSpeedChatStyle()

    def __openKeyRemapDialog(self):
        if base.wantCustomControls:
            self.customControlDialog = ControlRemapDialog.ControlRemap()

    def updateSpeedChatStyle(self):
        nameKey, arrowColor, rolloverColor, frameColor = speedChatStyles[self.speedChatStyleIndex]
        newSCColorScheme = SCColorScheme.SCColorScheme(
            arrowColor=arrowColor,
            rolloverColor=rolloverColor,
            frameColor=frameColor)
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
            self.speedChatStyleLeftArrow['state'] = DGG.NORMAL
        else:
            self.speedChatStyleLeftArrow['state'] = DGG.DISABLED
        if self.speedChatStyleIndex < len(speedChatStyles) - 1:
            self.speedChatStyleRightArrow['state'] = DGG.NORMAL
        else:
            self.speedChatStyleRightArrow['state'] = DGG.DISABLED
        base.localAvatar.b_setSpeedChatStyleIndex(self.speedChatStyleIndex)

    def writeDisplaySettings(self, task=None):
        if not self.displaySettingsChanged:
            return
        taskMgr.remove(self.DisplaySettingsTaskName)
        settings['res'] = (self.displaySettingsSize[0], self.displaySettingsSize[1])
        settings['fullscreen'] = self.displaySettingsFullscreen
        return Task.done

    def __handleExitServerShowWithConfirm(self):
        self.confirm = TTDialog.TTGlobalDialog(
            doneEvent='confirmDone',
            message=TTLocalizer.OptionsPageExitConfirm,
            style=TTDialog.TwoChoice)
        self.confirm.show()
        self.parent.doneStatus = {'mode': 'exit',
                                  'exitTo': 'closeShard'}
        self.accept('confirmDone', self.__handleConfirm)

    def __handleExitToToonSelectShowWithConfirm(self):
        self.confirm = TTDialog.TTGlobalDialog(
            doneEvent='confirmDone',
            message=TTLocalizer.OptionsPagePickAToonConfirm,
            style=TTDialog.TwoChoice)
        self.confirm.show()
        self.parent.doneStatus = {'mode': 'exit',
                                  'exitTo': 'closeShard'}
        self.accept('confirmDone', self.__back)

    def __handleConfirm(self):
        status = self.confirm.doneStatus
        self.ignore('confirmDone')
        self.confirm.cleanup()
        del self.confirm
        if status == 'ok':
            base.cr._userLoggingOut = True
            messenger.send(self.parent.doneEvent)

    def __back(self):
        status = self.confirm.doneStatus
        self.ignore('confirmDone')
        self.confirm.cleanup()
        del self.confirm
        if status == 'ok':
            base.cr._userLoggingOut = True
            messenger.send(self.parent.doneEvent)

            # TODO: Have this button disconnect you and bring you all the way back to the main menu like the one on the Toon Select screen
            base.cr.loginFSM.request('mainMenu')
            base.cr.mainMenu.singlePlayerMenu.demand('Off')


class CodesTabPage(DirectFrame):
    notify = directNotify.newCategory('CodesTabPage')

    def __init__(self, parent=aspect2d):
        self.parent = parent
        DirectFrame.__init__(
            self, parent=self.parent, relief=None, pos=(
                0.0, 0.0, 0.0), scale=(
                1.0, 1.0, 1.0))
        self.load()
        return

    def destroy(self):
        self.parent = None
        DirectFrame.destroy(self)
        return

    def load(self):
        cdrGui = loader.loadModel('phase_3.5/models/gui/tt_m_gui_sbk_codeRedemptionGui')
        instructionGui = cdrGui.find('**/tt_t_gui_sbk_cdrPresent')
        flippyGui = cdrGui.find('**/tt_t_gui_sbk_cdrFlippy')
        codeBoxGui = cdrGui.find('**/tt_t_gui_sbk_cdrCodeBox')
        self.resultPanelSuccessGui = cdrGui.find('**/tt_t_gui_sbk_cdrResultPanel_success')
        self.resultPanelFailureGui = cdrGui.find('**/tt_t_gui_sbk_cdrResultPanel_failure')
        self.resultPanelErrorGui = cdrGui.find('**/tt_t_gui_sbk_cdrResultPanel_error')
        self.successSfx = base.loadSfx('phase_3.5/audio/sfx/tt_s_gui_sbk_cdrSuccess.ogg')
        self.failureSfx = base.loadSfx('phase_3.5/audio/sfx/tt_s_gui_sbk_cdrFailure.ogg')
        self.instructionPanel = DirectFrame(parent=self,
                                            relief=None,
                                            image=instructionGui,
                                            image_scale=0.8,
                                            text=TTLocalizer.CdrInstructions,
                                            text_pos=TTLocalizer.OPCodesInstructionPanelTextPos,
                                            text_align=TextNode.ACenter,
                                            text_scale=TTLocalizer.OPCodesResultPanelTextScale,
                                            text_wordwrap=TTLocalizer.OPCodesInstructionPanelTextWordWrap,
                                            pos=(-0.429,
                                                 0,
                                                 -0.05))
        self.codeBox = DirectFrame(parent=self, relief=None, image=codeBoxGui, pos=(0.433, 0, 0.35))
        self.flippyFrame = DirectFrame(
            parent=self, relief=None, image=flippyGui, pos=(
                0.44, 0, -0.353))
        self.codeInput = DirectEntry(parent=self.codeBox,
                                     relief=DGG.GROOVE,
                                     scale=0.08,
                                     pos=(-0.33,
                                          0,
                                          -0.006),
                                     borderWidth=(0.05,
                                                  0.05),
                                     frameColor=((1,
                                                  1,
                                                  1,
                                                  1),
                                                 (1,
                                                  1,
                                                  1,
                                                  1),
                                                 (0.5,
                                                  0.5,
                                                  0.5,
                                                  0.5)),
                                     state=DGG.NORMAL,
                                     text_align=TextNode.ALeft,
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
                                     autoCapitalize=0,
                                     command=self.__submitCode)
        submitButtonGui = loader.loadModel('phase_3/models/gui/quit_button')
        self.submitButton = DirectButton(
            parent=self,
            relief=None,
            image=(
                submitButtonGui.find('**/QuitBtn_UP'),
                submitButtonGui.find('**/QuitBtn_DN'),
                submitButtonGui.find('**/QuitBtn_RLVR'),
                submitButtonGui.find('**/QuitBtn_UP')),
            image3_color=Vec4(
                0.5,
                0.5,
                0.5,
                0.5),
            image_scale=1.15,
            state=DGG.NORMAL,
            text=TTLocalizer.NameShopSubmitButton,
            text_scale=TTLocalizer.OPCodesSubmitTextScale,
            text_align=TextNode.ACenter,
            text_pos=TTLocalizer.OPCodesSubmitTextPos,
            text3_fg=(
                0.5,
                0.5,
                0.5,
                0.75),
            textMayChange=0,
            pos=(
                0.45,
                0.0,
                0.0896),
            command=self.__submitCode)
        self.resultPanel = DirectFrame(parent=self,
                                       relief=None,
                                       image=self.resultPanelSuccessGui,
                                       text='',
                                       text_pos=TTLocalizer.OPCodesResultPanelTextPos,
                                       text_align=TextNode.ACenter,
                                       text_scale=TTLocalizer.OPCodesResultPanelTextScale,
                                       text_wordwrap=TTLocalizer.OPCodesResultPanelTextWordWrap,
                                       pos=(-0.42,
                                            0,
                                            -0.0567))
        self.resultPanel.hide()
        closeButtonGui = loader.loadModel('phase_3/models/gui/dialog_box_buttons_gui')
        self.closeButton = DirectButton(
            parent=self.resultPanel,
            pos=(
                0.296,
                0,
                -0.466),
            relief=None,
            state=DGG.NORMAL,
            image=(
                closeButtonGui.find('**/CloseBtn_UP'),
                closeButtonGui.find('**/CloseBtn_DN'),
                closeButtonGui.find('**/CloseBtn_Rllvr')),
            image_scale=(
                1,
                1,
                1),
            command=self.__hideResultPanel)
        closeButtonGui.removeNode()
        cdrGui.removeNode()
        submitButtonGui.removeNode()
        return

    def enter(self):
        self.show()
        localAvatar.chatMgr.fsm.request('otherDialog')
        self.codeInput['focus'] = 1
        self.codeInput.enterText('')
        self.__enableCodeEntry()

    def exit(self):
        self.resultPanel.hide()
        self.hide()
        localAvatar.chatMgr.fsm.request('mainMenu')

    def unload(self):
        self.instructionPanel.destroy()
        self.instructionPanel = None
        self.codeBox.destroy()
        self.codeBox = None
        self.flippyFrame.destroy()
        self.flippyFrame = None
        self.codeInput.destroy()
        self.codeInput = None
        self.submitButton.destroy()
        self.submitButton = None
        self.resultPanel.destroy()
        self.resultPanel = None
        self.closeButton.destroy()
        self.closeButton = None
        del self.successSfx
        del self.failureSfx
        return

    def __submitCode(self, input=None):
        if input is None:
            input = self.codeInput.get()
        self.codeInput['focus'] = 1
        if input == '':
            return
        messenger.send('wakeup')
        if hasattr(base, 'codeRedemptionMgr'):
            base.codeRedemptionMgr.redeemCode(input, self.__getCodeResult)
        self.codeInput.enterText('')
        self.__disableCodeEntry()
        return

    def __getCodeResult(self, result, awardMgrResult):
        self.notify.debug('result = %s' % result)
        self.notify.debug('awardMgrResult = %s' % awardMgrResult)
        self.__enableCodeEntry()
        if result == 0:
            self.resultPanel['image'] = self.resultPanelSuccessGui
            self.resultPanel['text'] = TTLocalizer.CdrResultSuccess
        elif result == 1 or result == 3:
            self.resultPanel['image'] = self.resultPanelFailureGui
            self.resultPanel['text'] = TTLocalizer.CdrResultInvalidCode
        elif result == 2:
            self.resultPanel['image'] = self.resultPanelFailureGui
            self.resultPanel['text'] = TTLocalizer.CdrResultExpiredCode
        elif result == 4:
            self.resultPanel['image'] = self.resultPanelErrorGui
            if awardMgrResult == 0:
                self.resultPanel['text'] = TTLocalizer.CdrResultSuccess
            elif awardMgrResult == 1 or awardMgrResult == 2 or awardMgrResult == 15 or awardMgrResult == 16:
                self.resultPanel['text'] = TTLocalizer.CdrResultUnknownError
            elif awardMgrResult == 3 or awardMgrResult == 4:
                self.resultPanel['text'] = TTLocalizer.CdrResultMailboxFull
            elif awardMgrResult == 5 or awardMgrResult == 10:
                self.resultPanel['text'] = TTLocalizer.CdrResultAlreadyInMailbox
            elif awardMgrResult == 6 or awardMgrResult == 7 or awardMgrResult == 11:
                self.resultPanel['text'] = TTLocalizer.CdrResultAlreadyInQueue
            elif awardMgrResult == 8:
                self.resultPanel['text'] = TTLocalizer.CdrResultAlreadyInCloset
            elif awardMgrResult == 9:
                self.resultPanel['text'] = TTLocalizer.CdrResultAlreadyBeingWorn
            elif awardMgrResult == 12 or awardMgrResult == 13 or awardMgrResult == 14:
                self.resultPanel['text'] = TTLocalizer.CdrResultAlreadyReceived
        elif result == 5:
            self.resultPanel['text'] = TTLocalizer.CdrResultTooManyFails
            self.__disableCodeEntry()
        elif result == 6:
            self.resultPanel['text'] = TTLocalizer.CdrResultServiceUnavailable
            self.__disableCodeEntry()
        if result == 0:
            self.successSfx.play()
        else:
            self.failureSfx.play()
        self.resultPanel.show()

    def __hideResultPanel(self):
        self.resultPanel.hide()

    def __disableCodeEntry(self):
        self.codeInput['state'] = DGG.DISABLED
        self.submitButton['state'] = DGG.DISABLED

    def __enableCodeEntry(self):
        self.codeInput['state'] = DGG.NORMAL
        self.codeInput['focus'] = 1
        self.submitButton['state'] = DGG.NORMAL