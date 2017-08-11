import os
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator
from direct.fsm.FSM import FSM
from direct.gui.DirectGui import *
from direct.gui import DirectGuiGlobals
from direct.interval.IntervalGlobal import LerpScaleInterval
from direct.interval.IntervalGlobal import Sequence
from pandac.PandaModules import *

from otp.otpbase import OTPLocalizer
from toontown.makeatoon.MakeAToonGUI import MATShuffleButton, MATArrow
from toontown.serverbrowser.BookmarkManager import BookmarkManager
from toontown.shtiker.OptionsTabPage import OptionsTabPage
from toontown.toonbase import TTLocalizer
from toontown.toonbase import ToontownGlobals, ServerSettingsGlobals
from toontown.toonbase.ColorGlobals import CGray, CDefault
from toontown.toontowngui import TTDialog, TTTooltip, TTLabel, TTCheckBox
from toontown.toontowngui.LocalServerStart import LocalServerStart
from toontown.util import PlacerTool3D
from toontown.util import TTCardMaker
from panda3d.core import TransparencyAttrib, Vec4, TextNode
import sys
from direct.interval.IntervalGlobal import Func, Sequence, Wait, Parallel
from direct.interval.LerpInterval import LerpPosInterval
from toontown.toon import NPCToons
from toontown.toon import Toon
from toontown.toon import ToonDNA
from toontown.suit import Suit
from toontown.suit import SuitDNA
from direct.task.Task import Task
from toontown.ai.NewsManager import NewsManager
import random


# Start Sky
def cloudSkyTrack(task):
    task.h += globalClock.getDt() * 0.25
    if task.cloud1.isEmpty() or task.cloud2.isEmpty():
        notify.warning("Couldn't find clouds!")
        return Task.done

    task.cloud1.setH(task.h)
    task.cloud2.setH(-task.h * 0.8)
    return Task.cont

class MainMenu(DirectFrame, FSM):
    notify = directNotify.newCategory('MainMenu')

    def __init__(self):
        DirectFrame.__init__(self)
        FSM.__init__(self, 'MainMenu')

        base.isSinglePlayer = None
        base.isHosting = None

        self.logoScaleTrack = None
        self.localServerStart = None
        self.playFadeSequence = None
        self.suitPosInterval = None
        self.loopyLane = None
        self.buttonSequence = None

        self.randomNPC = None
        self.suit = None
        self.avScreen = None

        self.idleLabels = []
        self.signInLabels = []
        self.signUpLabels = []

        self.buttonsIdle = []
        self.buttonsHomeScreen = []
        self.buttonsPlayScreen = []
        self.buttonsSignIn = []
        self.buttonsSignUp = []
        self.buttonsLogIn = []
        self.hostButtons = []

        self.optionsScreen = OptionsTabPage()
        self.optionsScreen.hide()

        self.loadElements()

    def loadElements(self):
        buttonScale = (-1.1, 1.1, 1.1)
        buttonScale_clickhover = (-1.2, 1.2, 1.2)

        self.label = DirectLabel(relief=None, text='', text_fg=(1, 1, 1, 1),
                                 text_font=ToontownGlobals.getToonFont(), text_scale=0.1, text_wordwrap=25,
                                 pos=(0, 0, -1.13))

        self.label2 = DirectLabel(relief=None, text='', text_fg=(1, 1, 1, 1),
                                  text_font=ToontownGlobals.getToonFont(), text_scale=0.05, text_wordwrap=25,
                                  pos=(0, 0, -1.23))

        self.label3 = DirectLabel(relief=None, text='', text_fg=(1, 1, 1, 1),
                                  text_font=ToontownGlobals.getToonFont(), text_scale=0.05, text_wordwrap=25,
                                  pos=(0, 0, -1.31))

        self.label4 = DirectLabel(relief=None, text='', text_fg=(1, 1, 1, 1),
                                  text_font=ToontownGlobals.getToonFont(), text_scale=0.1, text_wordwrap=25,
                                  pos=(0, 0, -1.18))

        self.label5 = DirectLabel(relief=None, text='', text_fg=(1, 1, 1, 1),
                                  text_font=ToontownGlobals.getToonFont(), text_scale=0.1, text_wordwrap=25,
                                  pos=(0, 0, -1.48))

        self.label6 = DirectLabel(relief=None, text='', text_fg=(1, 1, 1, 1),
                                  text_font=ToontownGlobals.getToonFont(), text_scale=0.1, text_wordwrap=25,
                                  pos=(0, 0, -0.38))

        self.label7 = DirectLabel(relief=None, text='', text_fg=(1, 1, 1, 1),
                                  text_font=ToontownGlobals.getToonFont(), text_scale=0.1, text_wordwrap=25,
                                  pos=(0, 0, -0.68))

        self.label8 = DirectLabel(relief=None, text='', text_fg=(1, 1, 1, 1),
                                  text_font=ToontownGlobals.getToonFont(), text_scale=0.1, text_wordwrap=25,
                                  pos=(0, 0, -0.97))

        self.label9 = DirectLabel(relief=None, text='', text_fg=(1, 1, 1, 1),
                                  text_font=ToontownGlobals.getToonFont(), text_scale=0.1, text_wordwrap=25,
                                  pos=(0, 0, -1.28))

        self.label10 = DirectLabel(relief=None, text='', text_fg=(1, 1, 1, 1),
                                   text_font=ToontownGlobals.getToonFont(), text_scale=0.09, text_wordwrap=25,
                                   pos=(0, 0, -1.54))

        self.label11 = DirectLabel(relief=None, text='', text_fg=(0, 0, 0, 1),
                                   text_font=ToontownGlobals.getToonFont(), text_scale=0.09, text_wordwrap=25,
                                   pos=(-0.55, 0, 0.5))

        self.idleLabels.append(self.label)
        self.idleLabels.append(self.label2)
        self.idleLabels.append(self.label3)
        self.signInLabels.append(self.label4)
        self.signInLabels.append(self.label5)
        self.signUpLabels.append(self.label6)
        self.signUpLabels.append(self.label7)
        self.signUpLabels.append(self.label8)
        self.signUpLabels.append(self.label9)
        self.signUpLabels.append(self.label10)

        self.label['text'] = TTLocalizer.WelcomeMessage
        self.label.reparentTo(base.a2dTopCenter)
        self.label2['text'] = TTLocalizer.LogIn
        self.label2.reparentTo(base.a2dTopCenter)
        self.label3['text'] = TTLocalizer.SignUp
        self.label3.reparentTo(base.a2dTopCenter)
        self.label4['text'] = TTLocalizer.Username
        self.label4.reparentTo(base.a2dTopCenter)
        self.label5['text'] = TTLocalizer.Password
        self.label5.reparentTo(base.a2dTopCenter)
        self.label6['text'] = TTLocalizer.Username
        self.label6.reparentTo(base.a2dTopCenter)
        self.label7['text'] = TTLocalizer.Password
        self.label7.reparentTo(base.a2dTopCenter)
        self.label8['text'] = TTLocalizer.Birthday
        self.label8.reparentTo(base.a2dTopCenter)
        self.label9['text'] = TTLocalizer.Email
        self.label9.reparentTo(base.a2dTopCenter)
        self.label10['text'] = TTLocalizer.Warning
        self.label10.reparentTo(base.a2dTopCenter)
        self.label11['text'] = TTLocalizer.ServerSettings
        self.label11.reparentTo(base.aspect2d)

        for label in self.idleLabels:
            label.hide()

        for label in self.signInLabels:
            label.hide()

        for label in self.signUpLabels:
            label.hide()

        self.label11.hide()

        # Load the background image for the Main Menu
        self.background = OnscreenImage(
            parent=render2d, image='phase_3/maps/menu_bg_clouds.jpg', pos=(0, 0, 0))
        self.background.setBin('background', 0)
        self.background.setScale(render2d, Vec3(1))
        if ToontownGlobals.HALLOWEEN_PROPS in base.clientHolidayIdList:
            font = ToontownGlobals.getNametagFont(10)
        else:
            font = ToontownGlobals.getMinnieFont()
        self.motdLabel = OnscreenText(
            '', parent=hidden, font=font, fg=Vec4(1, 1, 1, 1), scale=0.05,
            align=TextNode.ALeft, wordwrap=25)

        self.logo = OnscreenImage(
            parent=base.a2dTopCenter,
            image='phase_3/maps/toontown_infinite_logo.png',
            scale=(0.8, 0.35, 0.45), pos=(0, 0, -0.6)
        )
        self.logo.setTransparency(TransparencyAttrib.MAlpha)

        # Pulsating animation for the logo
        self.logoScaleTrack = Sequence(
            LerpScaleInterval(self.logo, 4, Vec3(0.725, 0.35, 0.40), Vec3(0.70, 0.35, 0.385),
                              blendType='easeInOut'),
            LerpScaleInterval(self.logo, 4, Vec3(0.70, 0.35, 0.385), Vec3(0.725, 0.35, 0.40),
                              blendType='easeInOut')
        )
        self.logoScaleTrack.loop()

        # Idle
        self.logInButton = MATShuffleButton(
            pos=(0, 0, -0.5),
            text="Log In",
            wantArrows=False,
            image_scale=buttonScale,
            image2_scale=buttonScale_clickhover,
            image1_scale=buttonScale_clickhover,
            text_scale=0.09,
            text2_scale=0.095,
            text1_scale=0.095,
            command=lambda: self.request('SignInScreen')
        )
        self.buttonsIdle.append(self.logInButton)

        self.signUpButton = MATShuffleButton(
            pos=(0, 0, -0.8),
            text="Sign Up",
            wantArrows=False,
            image_scale=buttonScale,
            image2_scale=buttonScale_clickhover,
            image1_scale=buttonScale_clickhover,
            text_scale=0.09,
            text2_scale=0.095,
            text1_scale=0.095,
            command=lambda: self.request('SignUpScreen')
        )
        self.buttonsIdle.append(self.signUpButton)

        self.optionsButton = MATShuffleButton(
            parent=base.a2dBottomLeft,
            pos=(.4, 0, .2),
            text="Options",
            wantArrows=False,
            image_scale=buttonScale,
            image2_scale=buttonScale_clickhover,
            image1_scale=buttonScale_clickhover,
            text_scale=0.10,
            text2_scale=0.105,
            text1_scale=0.105,
            command=lambda: self.request('Options')
        )
        self.optionsButton.hide()

        # Homescreen
        self.singlePlayerButton = MATShuffleButton(
            pos=(0, 0, -0.2),
            text="Play",
            wantArrows=False,
            image_scale=buttonScale,
            image2_scale=buttonScale_clickhover,
            image1_scale=buttonScale_clickhover,
            text_scale=0.10,
            text2_scale=0.105,
            text1_scale=0.105,
            command=lambda: self.request('PlayWait')
        )
        self.buttonsHomeScreen.append(self.singlePlayerButton)

        self.modsButton = MATShuffleButton(
            pos=(0, 0, -0.5),
            text="Mods",
            wantArrows=False,
            image_scale=buttonScale,
            image2_scale=buttonScale_clickhover,
            image1_scale=buttonScale_clickhover,
            text_scale=0.09,
            text2_scale=0.095,
            text1_scale=0.095,
            command=lambda: self.request('Mods')
        )
        self.buttonsHomeScreen.append(self.modsButton)

        self.sighOutButton = MATShuffleButton(
            pos=(0, 0, -0.8),
            text="Sign Out",
            wantArrows=False,
            image_scale=buttonScale,
            image2_scale=buttonScale_clickhover,
            image1_scale=buttonScale_clickhover,
            text_scale=0.10,
            text2_scale=0.105,
            text1_scale=0.105,
            command=lambda: self.request('Idle')
        )
        self.buttonsHomeScreen.append(self.sighOutButton)

        # Log In button for the login screen
        self.logInButton2 = MATShuffleButton(
            pos=(0, 0, -0.8),
            text="Log In",
            wantArrows=False,
            image_scale=buttonScale,
            image2_scale=buttonScale_clickhover,
            image1_scale=buttonScale_clickhover,
            text_scale=0.09,
            text2_scale=0.095,
            text1_scale=0.095,
            command=lambda: self.request('HomeScreen')
        )
        self.buttonsLogIn.append(self.logInButton2)

        # Sign Up button for the login screen
        self.signUpButton2 = MATShuffleButton(
            pos=(0, 0, -0.8),
            text="Sign Up",
            wantArrows=False,
            image_scale=buttonScale,
            image2_scale=buttonScale_clickhover,
            image1_scale=buttonScale_clickhover,
            text_scale=0.09,
            text2_scale=0.095,
            text1_scale=0.095,
            command=lambda: self.request('HomeScreen')
        )
        self.buttonsLogIn.append(self.signUpButton2)

        # Sign Up button for the signup screen
        self.signUpButton3 = MATShuffleButton(
            pos=(-0.5, 0, -0.8),
            text="Sign Up",
            wantArrows=False,
            image_scale=buttonScale,
            image2_scale=buttonScale_clickhover,
            image1_scale=buttonScale_clickhover,
            text_scale=0.09,
            text2_scale=0.095,
            text1_scale=0.095,
            command=lambda: self.request('')
        )
        self.buttonsSignUp.append(self.signUpButton3)

        self.termsButton = MATShuffleButton(
            pos=(0.5, 0, -0.8),
            text="Terms of\n Service",
            text_pos=(0, 0.02, 0),
            wantArrows=False,
            image_scale=buttonScale,
            image2_scale=buttonScale_clickhover,
            image1_scale=buttonScale_clickhover,
            text_scale=0.08,
            text2_scale=0.095,
            text1_scale=0.095,
            command=lambda: self.request('')
        )
        self.buttonsSignUp.append(self.termsButton)

        # Quit Button for all the menus
        gui = loader.loadModel('phase_3/models/gui/pick_a_toon_gui.bam')
        quitHover = gui.find('**/QuitBtn_RLVR')
        self.quitButton = MATShuffleButton(
            parent=base.a2dBottomRight,
            pos=(-0.4, 0, .2),
            text="Quit",
            wantArrows=False,
            image_scale=buttonScale,
            image2_scale=buttonScale_clickhover,
            image1_scale=buttonScale_clickhover,
            text_scale=0.10,
            text2_scale=0.105,
            text1_scale=0.105,
            command=self.__handleQuit
        )
        self.quitButton.hide()

        gui = loader.loadModel('phase_3/models/gui/pick_a_toon_gui.bam')
        quitHover = gui.find('**/QuitBtn_RLVR')
        # Back Button
        self.backButton = MATShuffleButton(
            parent=base.a2dBottomLeft,
            pos=(0.4, 0, 0.2),
            text=TTLocalizer.OptionsGoBack,
            wantArrows=False,
            image_scale=buttonScale,
            image2_scale=buttonScale_clickhover,
            image1_scale=buttonScale_clickhover,
            text_scale=0.10,
            text2_scale=0.105,
            text1_scale=0.105,
            command=lambda: self.request('Idle')
        )
        self.backButton.hide()

        # Back Button 2
        self.backButton2 = MATShuffleButton(
            parent=base.a2dBottomLeft,
            pos=(0.4, 0, 0.2),
            text=TTLocalizer.OptionsGoBack,
            wantArrows=False,
            image_scale=buttonScale,
            image2_scale=buttonScale_clickhover,
            image1_scale=buttonScale_clickhover,
            text_scale=0.10,
            text2_scale=0.105,
            text1_scale=0.105,
            command=lambda: self.request('HomeScreen')
        )
        self.backButton2.hide()

        # Back Button 2
        self.backButton3 = MATShuffleButton(
            text=TTLocalizer.OptionsGoBack,
            wantArrows=False,
            pos=(4, 0, -0.6),
            image_scale=buttonScale,
            image2_scale=buttonScale_clickhover,
            image1_scale=buttonScale_clickhover,
            text_scale=0.10,
            text2_scale=0.105,
            text1_scale=0.105,
            command=lambda: self.request('HomeScreen')
        )
        self.backButton3.hide()

        # Host Screen
        self.hostButton = MATShuffleButton(
            text="Host",
            pos=(4, 0, 0.3),
            wantArrows=False,
            image_scale=buttonScale,
            image2_scale=buttonScale_clickhover,
            image1_scale=buttonScale_clickhover,
            text_scale=0.10,
            text2_scale=0.105,
            text1_scale=0.105,
            command=lambda: self.request('HostScreen')
        )
        self.buttonsPlayScreen.append(self.hostButton)

        self.directConnectButton = MATShuffleButton(
            text="Direct\nConnect",
            pos=(4, 0, 0),
            text_pos=(0, 0.02, 0),
            wantArrows=False,
            image_scale=buttonScale,
            image2_scale=buttonScale_clickhover,
            image1_scale=buttonScale_clickhover,
            text_scale=0.08,
            text2_scale=0.085,
            text1_scale=0.085,
            command=lambda: self.request('DirectConnect')
        )
        self.buttonsPlayScreen.append(self.directConnectButton)

        self.serverBrowserButton = MATShuffleButton(
            text="Server\nBrowser",
            pos=(4, 0, -0.3),
            text_pos=(0, 0.02, 0),
            wantArrows=False,
            image_scale=buttonScale,
            image2_scale=buttonScale_clickhover,
            image1_scale=buttonScale_clickhover,
            text_scale=0.08,
            text2_scale=0.085,
            text1_scale=0.085,
            command=lambda: self.request('DirectConnect')
        )
        self.buttonsPlayScreen.append(self.serverBrowserButton)

        self.startServerButton = MATShuffleButton(
            text="Start",
            pos=(0.84, 0, 0.79),
            wantArrows=False,
            image_scale=buttonScale,
            image2_scale=buttonScale_clickhover,
            image1_scale=buttonScale_clickhover,
            text_scale=0.10,
            text2_scale=0.105,
            text1_scale=0.105,
            command=lambda: self.request('StartHost')
        )

        self.hostWantRacingLabel = TTLabel.TTLabel(
            pos=(-0.9, 0, 0.36),
            text="Racing",
            text_align=TextNode.ALeft,
        )
        self.hostWantRacingBox = TTCheckBox.TTCheckBox(
            pos=(-0.95, 0, 0.37),
            checked=serverSettings[ServerSettingsGlobals.WantRacing],
            command=self.toggleServerSetting, extraArgs=[ServerSettingsGlobals.WantRacing]
        )

        self.hostWantGolfLabel = TTLabel.TTLabel(
            pos=(-0.9, 0, 0.26),
            text="Golf",
            text_align=TextNode.ALeft,
        )
        self.hostWantGolfBox = TTCheckBox.TTCheckBox(
            pos=(-0.95, 0, 0.27),
            checked=serverSettings[ServerSettingsGlobals.WantGolf],
            command=self.toggleServerSetting, extraArgs=[ServerSettingsGlobals.WantGolf]
        )

        self.hostExpMultDec = MATArrow(
            pos=(-0.8, 0, -0.02), command=self.setServerExpMult)

        self.hostExpMultInc = MATArrow(
            pos=(-0.29, 0, -0.02), inverted=True, command=self.setServerExpMult)

        self.hostExpMultLabel = TTLabel.TTLabel(
            pos=(-0.55, 0, -0.04),
            text="EXP Multiplier: %sx" % str(serverSettings[ServerSettingsGlobals.ExpMultiplier]),
            text_align=TextNode.ACenter,
        )

        self.connectButton = MATShuffleButton(
            pos=(-0.35, 0, -0.75),
            text="Connect",
            wantArrows=False,
            image_scale=buttonScale,
            image2_scale=buttonScale_clickhover,
            image1_scale=buttonScale_clickhover,
            text_scale=0.09,
            text2_scale=0.095,
            text1_scale=0.10,
            command=self.__submitIP
        )
        self.connectButton.hide()

        self.addToBookmarksButton = MATShuffleButton(
            pos=(0.35, 0, -0.75),
            text="Bookmark",
            wantArrows=False,
            image_scale=buttonScale,
            image2_scale=buttonScale_clickhover,
            image1_scale=buttonScale_clickhover,
            text_scale=0.09,
            text2_scale=0.095,
            text1_scale=0.10,
            command=self.createBookmark
        )
        self.addToBookmarksButton.hide()

        self.hide()

        self.bookmarkInfoDialog = None

        # Load Bookmarks file
        self.bookmarkMgr = BookmarkManager()

        #self.host_CheatsBox.disable()
        #self.host_ShowInBrowserBox.disable()
        #
        #)
        #    checked=True
        #    pos=(-.6, 0, -.4),
        #self.hostCheatsBox = TTCheckBox.TTCheckBox(
        #)
        #    text_align=TextNode.ALeft,
        #    text="Cheats",
        #self.hostShowInBrowserLabel = TTLabel.TTLabel(
        #    pos=(-.55, 0, -.31),
        #    text="Show In Server Browser",
        #    text_align=TextNode.ALeft,
        #self.hostShowInBrowserBox = TTCheckBox.TTCheckBox(
        #)
        #    pos=(-.6, 0, -.3),
        #    checked=False
        #
        #)
        #self.hostCheatsLabel = TTLabel.TTLabel(
        #    pos=(-.55, 0, -.41),
        self.hostButtons.append(self.startServerButton)
        #self.hostButtons.append(self.host_ShowInBrowserLabel)
        #self.hostButtons.append(self.host_ShowInBrowserBox)
        #self.hostButtons.append(self.host_CheatsBox)
        #self.hostButtons.append(self.host_CheatsLabel)
        self.hostButtons.append(self.hostWantRacingLabel)
        self.hostButtons.append(self.hostWantRacingBox)
        self.hostButtons.append(self.hostWantGolfLabel)
        self.hostButtons.append(self.hostWantGolfBox)
        self.hostButtons.append(self.hostExpMultDec)
        self.hostButtons.append(self.hostExpMultInc)
        self.hostButtons.append(self.hostExpMultLabel)

        for button in self.hostButtons:
            button.hide()

    def enterIdle(self):
        if (base.cr.music is None) and base.musicManagerIsValid:
            base.cr.music = base.musicManager.getSound('phase_3/audio/bgm/tti_main_menu_theme.ogg')
            if base.cr.music is not None:
                base.cr.music.setLoop(1)
                base.cr.music.setVolume(0.9)
                base.cr.music.play()

        for button in self.buttonsIdle:
            button.show()
        for label in self.idleLabels:
            label.show()

        self.optionsButton.show()
        self.background.show()
        self.logo.show()
        self.quitButton.show()

    def exitIdle(self):
        for button in self.buttonsIdle:
            button.hide()
        for label in self.idleLabels:
            label.hide()
        self.optionsButton.hide()

    def enterSignInScreen(self):
        self.backButton.show()
        self.logInButton2.show()

        self.usernameInput = DirectEntry(
            parent=aspect2d,
            relief=DGG.GROOVE,
            scale=0.1,
            pos=(0, 0, -0.60),
            borderWidth=(0.05, 0.05),
            frameColor=((1, 1, 1, 1),
                        (1, 1, 1, 1),
                        (0.5, 0.5, 0.5, 0.5)),
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
        # command=self.__submitUserName)

        self.usernameInput.show()
        self.usernameInput.enterText('')

        self.passwordInput = DirectEntry(
            parent=aspect2d,
            relief=DGG.GROOVE,
            scale=0.1,
            pos=(0, 0, -0.30),
            borderWidth=(0.05, 0.05),
            frameColor=((1, 1, 1, 1),
                        (1, 1, 1, 1),
                        (0.5, 0.5, 0.5, 0.5)),
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
            # command=self.__submitPassWord)

        self.passwordInput.show()
        self.passwordInput.enterText('')

        for label in self.signInLabels:
            label.show()

    def exitSignInScreen(self):
        self.backButton.hide()
        self.logInButton2.hide()
        self.usernameInput.hide()
        self.passwordInput.hide()

        for label in self.signInLabels:
            label.hide()

    def enterSignUpScreen(self):
        self.backButton.show()
        self.signUpButton3.show()
        self.termsButton.show()
        self.logo.hide()

        for label in self.signUpLabels:
            label.show()

        self.monthInput = DirectEntry(
            parent=aspect2d,
            relief=DGG.GROOVE,
            scale=0.1,
            pos=(-0.31, 0, -0.10),
            borderWidth=(0.05, 0.05),
            frameColor=((1, 1, 1, 1),
                        (1, 1, 1, 1),
                        (0.5, 0.5, 0.5, 0.5)),
            state=DGG.NORMAL,
            text_align=TextNode.ACenter,
            text_scale=TTLocalizer.OPCodesInputTextScale,
            width=3,
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
            # command=self.__submitPassword)

        self.monthInput.show()
        self.monthInput.enterText('Month')

        self.dayInput = DirectEntry(
            parent=aspect2d,
            relief=DGG.GROOVE,
            scale=0.1,
            pos=(0, 0, -0.10),
            borderWidth=(0.05, 0.05),
            frameColor=((1, 1, 1, 1),
                        (1, 1, 1, 1),
                        (0.5, 0.5, 0.5, 0.5)),
            state=DGG.NORMAL,
            text_align=TextNode.ACenter,
            text_scale=TTLocalizer.OPCodesInputTextScale,
            width=3,
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
            # command=self.__submitPassword)

        self.dayInput.show()
        self.dayInput.enterText('Day')

        self.yearInput = DirectEntry(
            parent=aspect2d,
            relief=DGG.GROOVE,
            scale=0.1,
            pos=(0.31, 0, -0.10),
            borderWidth=(0.05, 0.05),
            frameColor=((1, 1, 1, 1),
                        (1, 1, 1, 1),
                        (0.5, 0.5, 0.5, 0.5)),
            state=DGG.NORMAL,
            text_align=TextNode.ACenter,
            text_scale=TTLocalizer.OPCodesInputTextScale,
            width=3,
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
            # command=self.__submitPassword)

        self.yearInput.show()
        self.yearInput.enterText('Year')

        self.emailInput = DirectEntry(
            parent=aspect2d,
            relief=DGG.GROOVE,
            scale=0.1,
            pos=(0, 0, -0.40),
            borderWidth=(0.05, 0.05),
            frameColor=((1, 1, 1, 1),
                        (1, 1, 1, 1),
                        (0.5, 0.5, 0.5, 0.5)),
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
        # command=self.__submitPassword)

        self.emailInput.show()
        self.emailInput.enterText('')

        self.passwordInput = DirectEntry(
            parent=aspect2d,
            relief=DGG.GROOVE,
            scale=0.1,
            pos=(0, 0, 0.20),
            borderWidth=(0.05, 0.05),
            frameColor=((1, 1, 1, 1),
                        (1, 1, 1, 1),
                        (0.5, 0.5, 0.5, 0.5)),
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
        # command=self.__submitPassword)

        self.passwordInput.show()
        self.passwordInput.enterText('')

        self.usernameInput = DirectEntry(
            parent=aspect2d,
            relief=DGG.GROOVE,
            scale=0.1,
            pos=(0, 0, 0.50),
            borderWidth=(0.05, 0.05),
            frameColor=((1, 1, 1, 1),
                        (1, 1, 1, 1),
                        (0.5, 0.5, 0.5, 0.5)),
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
        # command=self.__submitUsername)

        self.usernameInput.show()
        self.usernameInput.enterText('')

    def exitSignUpScreen(self):
        self.backButton.hide()
        self.logInButton2.hide()
        self.signUpButton3.hide()
        self.usernameInput.hide()
        self.passwordInput.hide()
        self.monthInput.hide()
        self.dayInput.hide()
        self.yearInput.hide()
        self.emailInput.hide()
        self.termsButton.hide()
        self.logo.show()
        for label in self.signUpLabels:
            label.hide()

    def enterLoggingIn(self):
        pass

        # Do login magic here:

        # If login is accepted,  request the Home Screen

    def enterLoggingOut(self):
        pass

        # Do logout magic here:

        # If user logs out, request Idle

    def enterHomeScreen(self):
        for button in self.buttonsHomeScreen:
            button.show()
        self.background.show()
        self.logo.show()
        self.quitButton.show()
        self.optionsButton.show()
        self.optionsButton['command'] = lambda: self.request('Options2')

    def exitHomeScreen(self):
        for button in self.buttonsHomeScreen:
            button.hide()

        self.optionsButton.hide()
        self.optionsButton['command'] = lambda: self.request('Options')

    def enterOptions(self):
        self.optionsScreen.show()
        self.optionsButton.show()
        self.optionsButton['command'] = lambda: self.request('Idle')
        self.optionsButton['text'] = "Back"
        self.logo.hide()

    def exitOptions(self):
        self.optionsScreen.hide()
        self.optionsButton['command'] = lambda: self.request('Options')
        self.optionsButton['text'] = "Options"
        self.logo.show()

    def enterOptions2(self):
        self.optionsScreen.show()
        self.optionsButton.show()
        self.optionsButton['command'] = lambda: self.request('HomeScreen')
        self.optionsButton['text'] = "Back"
        self.logo.hide()

    def exitOptions2(self):
        self.optionsScreen.hide()
        self.optionsButton['command'] = lambda: self.request('Options')
        self.optionsButton['text'] = "Options"
        self.logo.show()

    def enterSingleplayer(self):
        self.__startGameSession(True)
        base.isSinglePlayer = True
        base.isHosting = False

    def enterPlayWait(self):
        base.transitions.fadeOut(0)
        self.background.hide()
        self.logo.hide()
        self.quitButton.hide()
        Sequence(Wait(0.1), Func(lambda: self.request('PlayScreen'))).start()

    def enterPlayScreen(self):
        base.camLens.setFov(30)

        self.loopyLane = loader.loadModel('phase_4/models/neighborhoods/toontown_central_2200')
        self.loopyLane.setPosHpr(34, -12, 0, 5, 0, 0)
        self.loopyLane.reparentTo(render)

        self.randomNPC = Toon.Toon()
        dna = ToonDNA.ToonDNA()
        dna.newToonRandom(gender=random.choice(('m', 'f')))
        self.randomNPC.setDNA(dna)
        if dna.legs == 's':
            base.camera.setPosHpr(-454.5, -96, 2.6, 215, 0, 0)
        elif dna.legs == 'l':
            base.camera.setPosHpr(-454.5, -96, 3, 215, 0, 0)
        else:
            base.camera.setPosHpr(-454.5, -96, 2.7, 215, 0, 0)
        self.randomNPC.reparentTo(render)
        self.randomNPC.pingpong('bored', fromFrame=70, toFrame=130)
        self.randomNPC.setPosHpr(-444, -107, 0.025, 52, 0, 0)

        self.avScreen = loader.loadModel('phase_5/models/props/av_screen_server_settings.bam')
        self.avScreen.setPosHpr(-329, -196, 0.025, 95, 0, 0)
        self.avScreen.reparentTo(render)
        self.avScreen.setScale(1.3)

        # base.oobe()

        self.suit = Suit.Suit()
        dna = SuitDNA.SuitDNA()
        dna.newSuitRandom()
        self.suit.setDNA(dna)
        self.suit.reparentTo(render)
        self.suit.setDisplayName('')
        self.suit.setPickable(0)
        self.suit.loop('walk')
        # self.suit.pose('landing', 20)
        self.suit.setH(90)

        effects = CompassEffect.PRot | CompassEffect.PZ

        self.sky = loader.loadModel('phase_3.5/models/props/TT_sky')
        self.sky.setTransparency(TransparencyAttrib.MAlpha)
        self.sky.setTag('sky', 'Regular')
        self.sky.setScale(1.0)
        self.sky.setFogOff()
        self.sky.setDepthTest(0)
        self.sky.setDepthWrite(0)
        self.sky.setBin('background', 100)
        self.sky.find('**/Sky').reparentTo(self.sky, -1)
        self.sky.reparentTo(render)
        self.sky.setPos(-444, -107, 0)

        ce = CompassEffect.make(NodePath(), effects)
        self.sky.node().setEffect(ce)

        skyTrackTask = Task(cloudSkyTrack)
        skyTrackTask.h = 0
        skyTrackTask.cloud1 = self.sky.find('**/cloud1')
        skyTrackTask.cloud2 = self.sky.find('**/cloud2')

        if not skyTrackTask.cloud1.isEmpty() and not skyTrackTask.cloud2.isEmpty():
            taskMgr.add(skyTrackTask, 'skyTrack')

        for button in self.buttonsPlayScreen:
            button.show()

        self.backButton3.show()

        buttonPosInterval = LerpPosInterval(self.hostButton, 0.5, Point3(0.35, 0, 0.3), Point3(4, 0, 0.3),
                                            blendType='easeOut')
        buttonPosInterval2 = LerpPosInterval(self.directConnectButton, 0.5, Point3(0.35, 0, 0), Point3(4, 0, 0),
                                             blendType='easeOut')
        buttonPosInterval3 = LerpPosInterval(self.serverBrowserButton, 0.5, Point3(0.35, 0, -0.3), Point3(4, 0, -0.3),
                                             blendType='easeOut')
        buttonPosInterval4 = LerpPosInterval(self.backButton3, 0.5, Point3(0.35, 0, -0.6), Point3(4, 0, -0.6),
                                             blendType='easeOut')

        self.buttonSequence = Sequence(Wait(2), Func(buttonPosInterval.start), Func(buttonPosInterval2.start), Func(buttonPosInterval3.start), Func(buttonPosInterval4.start))
        self.buttonSequence.start()

        self.suitPosInterval = self.suit.posInterval(8, (-447.5, -129, -0.47), startPos=(-417.5, -129, -0.475))
        self.suitPosInterval.loop()

        self.playFadeSequence = Sequence(Wait(2), Func(base.transitions.fadeIn, 1))
        self.playFadeSequence.start()

        base.camera.setPosHpr(-454.5, -96, 2.7, 215, 0, 0)

        PlacerTool3D.PlacerTool3D(camera, increment=5)

    def exitPlayScreen(self):
        self.background.show()
        self.logo.show()
        self.loopyLane.reparentTo(hidden)

        for button in self.buttonsPlayScreen:
            button.hide()

        self.hostButton.setPos(4, 0, 0.3)
        self.directConnectButton.setPos(4, 0, 0)
        self.serverBrowserButton.setPos(4, 0, -0.3)
        self.backButton3.setPos(4, 0, -0.6)
        self.backButton3.hide()

        self.randomNPC.removeNode()
        self.suit.removeNode()
        # base.camera.setPosHpr(0, 0, 0, 0, 0, 0)

    def enterHostScreen(self):
        for button in self.hostButtons:
            button.show()

        self.label11.show()

        self.background.hide()
        self.logo.hide()
        self.loopyLane.reparentTo(render)

        self.cameraPosInterval = camera.posInterval(3, Point3(-449.5, -156, 27), startPos=Point3(-454.5, -96, 2.7))
        self.cameraHprInterval = camera.hprInterval(3, (225, 0, 0), startHpr=(215, 0, 0))
        self.cameraPosInterval2 = camera.posInterval(4, Point3(-359.5, -204, 3.7), startPos=Point3(-449.5, -156, 27))
        self.cameraHprInterval2 = camera.hprInterval(4, (280, 0, 0), startHpr=(225, 0, 0))
        Sequence(Parallel(self.cameraPosInterval, self.cameraHprInterval), Parallel(self.cameraPosInterval2, self.cameraHprInterval2))

    def exitHostScreen(self):
        for button in self.hostButtons:
            button.hide()
        if hasattr(self, 'host_ServerNameInput'):
            self.host_ServerNameInput.destroy()
            del self.host_ServerNameInput
            self.host_ServerNameInputLabel.destroy()
            del self.host_ServerNameInputLabel

    def enterStartHost(self):
        base.isHosting = True
        self.__startGameSession(True)

    def __startGameSession(self, server):
        self.LocalServerStart = LocalServerStart(self, server)
        self.LocalServerStart.request('Start')
        self.quitButton.hide()

    def enterBookmarks(self):
        gui = loader.loadModel('phase_3.5/models/gui/friendslist_gui')

        if not hasattr(self, 'bookmarksList'):
            self.bookmarksList = DirectScrolledList(parent = self,
                decButton_pos= (0, 0, 0.9),
                decButton_image = (gui.find('**/FndsLst_ScrollUp'),
                    gui.find('**/FndsLst_ScrollDN'),
                    gui.find('**/FndsLst_ScrollUp_Rllvr'),
                    gui.find('**/FndsLst_ScrollUp')),
                decButton_relief = None,
                decButton_scale = (1.5, 1.5, 1.5),

                incButton_pos= (0, 0, -0.9),
                incButton_image = (gui.find('**/FndsLst_ScrollUp'),
                    gui.find('**/FndsLst_ScrollDN'),
                    gui.find('**/FndsLst_ScrollUp_Rllvr'),
                    gui.find('**/FndsLst_ScrollUp')),
                incButton_relief = None,
                incButton_scale = (1.5, 1.5, -1.5),


                items = [],
                numItemsVisible = 16,
                forceHeight = .096,
                itemFrame_frameSize = (-.6, .6, -1.5, .1),
                itemFrame_pos = (0, 0, .7),
                itemFrame_frameColor = (0.85, 0.95, 1, 1)
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

    def enterDirectConnect(self):
        # Load the image for the ip input bar for Multiplayer
        cdrGui = loader.loadModel('phase_3.5/models/gui/tt_m_gui_sbk_codeRedemptionGui')

        # Load the ip input bar
        self.ipInput = DirectEntry(
            parent=aspect2d,
            relief=DGG.GROOVE,
            scale=0.1,
            pos=(0, 0, -0.50),
            borderWidth=(0.05, 0.05),
            frameColor=((1, 1, 1, 1),
                        (1, 1, 1, 1),
                        (0.5, 0.5, 0.5, 0.5)),
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
            autoCapitalize=0,
            command=self.__submitIP)

        self.ipInput.show()
        self.__enableIPEntry()
        self.ipInput.enterText('')
        self.ipInput.setTransparency(1)
        self.connectButton.show()
        self.addToBookmarksButton.show()

    def exitDirectConnect(self):
        self.ipInput.hide()
        self.__disableIPEntry()
        self.connectButton.hide()
        self.addToBookmarksButton.hide()

    def __submitIP(self, input=None):
        if input is None:
            input = self.ipInput.get()
            self.ipInput['focus'] = 1

        if input == '':
            return
        self.targetIp = input
        messenger.send('wakeup')
        self.request('StartDirectConnect')

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
                    text_pos=(0, 0), suppressKeys = True, suppressMouse = True
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
            image = "phase_3/maps/input_box.png",
            image_scale = (4.6, 0, 1),
            image_pos = (0, 0, .2),
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
            try: # This wants to crash so i'll do this for now
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
                base.showNotification("Bookmark added! (IP: %s, Name: %s)" %(self.ipInput.get(), self.serverNameInput.get()))
            elif resp == 2:
                base.showNotification("Error: A bookmark for the IP %s already exists!" %self.ipInput.get())
            elif resp == 3:
                base.showNotification("Error: Please specify an IP!")
            else:
                base.showNotification("Error: Unknown error adding bookmark! Please report this to the developers!")

    def deleteFromBookmarks(self, name, address):
        if self.bookmarkInfoDialog:
            self.bookmarkInfoDialog.hide()
        resp = self.bookmarkMgr.removeBookmark(address)
        if resp == 1:
            base.showNotification("Bookmark removed! (IP: %s, Name: %s)" %(address, name))
        elif resp == 2:
            base.showNotification("Error: A bookmark for %s doesn't exist, so it can't be deleted!" %address)
        else:
            base.showNotification("Error: Unknown error removing bookmark! Please report this to the developers!")
        self.makeBookmarksButtons()

    def enterStartDirectConnect(self):
        base.isHosting = False
        if not hasattr(self, 'targetIp'):
            ip = self.ipInput.get()
        else:
            ip = self.targetIp
        if ':' in ip:
            ip, port = ip.split(':')
            try:
                port = int(port)
            except:
                # TODO: Better handle invalid addresses
                port = 7000
            base.connectToServer(ip, port)
        else:
            base.connectToServer(ip)

    def __enableIPEntry(self):
        self.ipInput['state'] = DGG.NORMAL
        self.ipInput['focus'] = 1

    def __disableIPEntry(self):
        self.ipInput['state'] = DGG.DISABLED

    def enterOff(self):
        self.hide()

        if self.logoScaleTrack is not None:
            self.logoScaleTrack.finish()
            self.logoScaleTrack = None

        if self.optionsScreen is not None:
            self.optionsScreen.unload()
            self.optionsScreen = None

        if self.playFadeSequence is not None:
            self.playFadeSequence.finish()
            self.playFadeSequence = None

        if self.playFadeSequence is not None:
            self.playFadeSequence.finish()
            self.playFadeSequence = None

        if self.buttonSequence is not None:
            self.buttonSequence.finish()
            self.buttonSequence = None

        if self.suitPosInterval is not None:
            self.suitPosInterval.finish()
            self.suitPosInterval = None

    def destroyLocalStart(self):
        if self.localServerStart:
            self.localServerStart.removeNode()

    def hide(self):
        self.destroyLocalStart()
        self.unload()

        self.background.hide()
        self.logo.hide()

        for button in self.buttonsIdle:
            button.hide()

        for button in self.buttonsHomeScreen:
            button.hide()

        for button in self.buttonsPlayScreen:
            button.hide()

        for button in self.buttonsLogIn:
            button.hide()

        for button in self.buttonsSignIn:
            button.hide()

        for button in self.buttonsSignUp:
            button.hide()

        for label in self.idleLabels:
            label.hide()

        for label in self.signInLabels:
            label.hide()

        for label in self.signUpLabels:
            label.hide()

        if self.playFadeSequence is not None:
            self.playFadeSequence.finish()
            self.playFadeSequence = None

        if self.playFadeSequence is not None:
            self.playFadeSequence.finish()
            self.playFadeSequence = None

        if self.buttonSequence is not None:
            self.buttonSequence.finish()
            self.buttonSequence = None

        if self.suitPosInterval is not None:
            self.suitPosInterval.finish()
            self.suitPosInterval = None

    def unload(self):
        base.camLens.setMinFov(ToontownGlobals.DefaultCameraFov/(4./3.))
        if self.loopyLane is not None:
            self.loopyLane.removeNode()
            del self.loopyLane
            self.loopyLane = None

        if self.randomNPC is not None:
            self.randomNPC.removeNode()
            del self.randomNPC
            self.randomNPC = None

        if self.suit is not None:
            self.suit.removeNode()
            del self.suit
            self.suit = None

    def __handleQuit(self):
        cleanupDialog('globalDialog')
        base.cr.loginFSM.request('shutdown')

    def showTooltip(self, text, event):
        self.currentTooltip = TTTooltip.TTTooltip(description = text)

    def killTooltip(self, event):
        if hasattr(self, 'currentTooltip'):
            self.currentTooltip.destroy()

    def toggleServerSetting(self, setting):
        if serverSettings.get(setting) == True:
            serverSettings[setting] = False
        else:
            serverSettings[setting] = True

    def setServerExpMult(self, offset):
        value = max(min((serverSettings[ServerSettingsGlobals.ExpMultiplier] + offset), 20), 1)
        serverSettings[ServerSettingsGlobals.ExpMultiplier] = value
        self.hostExpMultLabel['text'] = "EXP Multiplier: %sx" % str(value)