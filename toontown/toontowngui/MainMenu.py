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
from toontown.makeatoon.MakeAToonGUI import MATShuffleButton
from toontown.serverbrowser.BookmarkManager import BookmarkManager
from toontown.shtiker.OptionsTabPage import OptionsTabPage
from toontown.toonbase import TTLocalizer
from toontown.toonbase import ToontownGlobals
from toontown.toonbase.ColorGlobals import CGray, CDefault
from toontown.toontowngui import TTDialog, TTTooltip, TTLabel, TTCheckBox
from toontown.toontowngui.LocalServerStart import LocalServerStart
from toontown.util import PlacerTool3D
from toontown.util import TTCardMaker
from panda3d.core import TransparencyAttrib, Vec4, TextNode
import sys
from direct.interval.LerpInterval import LerpPosInterval

class MainMenu(DirectFrame, FSM):
    notify = directNotify.newCategory('MainMenu')

    def __init__(self):
        DirectFrame.__init__(self)
        FSM.__init__(self, 'MainMenu')

        self.logoScaleTrack = None
        self.localServerStart = None

        self.idleLabels = []
        self.signInLabels = []
        self.signUpLabels = []

        self.buttonsIdle = []
        self.buttonsHomeScreen = [] 
        self.buttonsSignIn = []
        self.buttonsSignUp = []
        self.buttonsLogIn = []

        self.loadElements()
        self.loadEnviroments()

        self.optionsScreen = OptionsTabPage()
        self.optionsScreen.hide()

    def loadElements(self):
        buttonScale = (-1.1, 1.1, 1.1)
        buttonScale_clickhover = (-1.2, 1.2, 1.2)

        self.label = DirectLabel(relief=None, text='', text_fg=(1, 1, 1, 1),
                                 text_font=ToontownGlobals.getToonFont(), text_scale=0.1, text_wordwrap=25,
                                 pos=(0, 0, -0.13))

        self.label2 = DirectLabel(relief=None, text='', text_fg=(1, 1, 1, 1),
                                  text_font=ToontownGlobals.getToonFont(), text_scale=0.05, text_wordwrap=25,
                                  pos=(0, 0, -0.23))

        self.label3 = DirectLabel(relief=None, text='', text_fg=(1, 1, 1, 1),
                                  text_font=ToontownGlobals.getToonFont(), text_scale=0.05, text_wordwrap=25,
                                  pos=(0, 0, -0.31))

        self.label4 = DirectLabel(relief=None, text='', text_fg=(1, 1, 1, 1),
                                  text_font=ToontownGlobals.getToonFont(), text_scale=0.1, text_wordwrap=25,
                                  pos=(0, 0, -0.18))

        self.label5 = DirectLabel(relief=None, text='', text_fg=(1, 1, 1, 1),
                                  text_font=ToontownGlobals.getToonFont(), text_scale=0.1, text_wordwrap=25,
                                  pos=(0, 0, -0.48))

        self.label6 = DirectLabel(relief=None, text='', text_fg=(1, 1, 1, 1),
                                  text_font=ToontownGlobals.getToonFont(), text_scale=0.1, text_wordwrap=25,
                                  pos=(0, 0, 0.62))

        self.label7 = DirectLabel(relief=None, text='', text_fg=(1, 1, 1, 1),
                                  text_font=ToontownGlobals.getToonFont(), text_scale=0.1, text_wordwrap=25,
                                  pos=(0, 0, 0.32))

        self.label8 = DirectLabel(relief=None, text='', text_fg=(1, 1, 1, 1),
                                  text_font=ToontownGlobals.getToonFont(), text_scale=0.1, text_wordwrap=25,
                                  pos=(0, 0, 0.03))

        self.label9 = DirectLabel(relief=None, text='', text_fg=(1, 1, 1, 1),
                                  text_font=ToontownGlobals.getToonFont(), text_scale=0.1, text_wordwrap=25,
                                  pos=(0, 0, -0.28))

        self.label10 = DirectLabel(relief=None, text='', text_fg=(1, 1, 1, 1),
                                   text_font=ToontownGlobals.getToonFont(), text_scale=0.09, text_wordwrap=25,
                                   pos=(0, 0, -0.54))

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
        self.label.reparentTo(aspect2d)
        self.label2['text'] = TTLocalizer.LogIn
        self.label2.reparentTo(aspect2d)
        self.label3['text'] = TTLocalizer.SignUp
        self.label3.reparentTo(aspect2d)
        self.label4['text'] = TTLocalizer.Username
        self.label4.reparentTo(aspect2d)
        self.label5['text'] = TTLocalizer.Password
        self.label5.reparentTo(aspect2d)
        self.label6['text'] = TTLocalizer.Username
        self.label6.reparentTo(aspect2d)
        self.label7['text'] = TTLocalizer.Password
        self.label7.reparentTo(aspect2d)
        self.label8['text'] = TTLocalizer.Birthday
        self.label8.reparentTo(aspect2d)
        self.label9['text'] = TTLocalizer.Email
        self.label9.reparentTo(aspect2d)
        self.label10['text'] = TTLocalizer.Warning
        self.label10.reparentTo(aspect2d)

        for label in self.idleLabels:
            label.hide()

        for label in self.signInLabels:
            label.hide()

        for label in self.signUpLabels:
            label.hide()

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

        # Load the Toontown Infinite logo
        offset = -0.04

        self.logo = OnscreenImage(
            parent=base.aspect2d,
            image='phase_3/maps/toontown_infinite_logo.png',
            scale=(0.8, 0.35, 0.45), pos=(offset, 0, 0.40)
        )
        self.logo.setTransparency(TransparencyAttrib.MAlpha)

        if self.logoScaleTrack is not None:
            self.logoScaleTrack.finish()
            self.logoScaleTrack = None

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
            text_scale=0.082,
            text2_scale=0.087,
            text1_scale=0.087,
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
        self.buttonsIdle.append(self.optionsButton)

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
            command=lambda: self.request('StartHost')
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

        self.optionsButton2 = MATShuffleButton(
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
            command=lambda: self.request('Options2')
        )
        self.buttonsHomeScreen.append(self.optionsButton2)

        self.connectButton = DirectButton(
            parent=base.a2dTopLeft,
            relief=None,
            pos=(.35, 0, -0.3),
            text="Connect",
            text_scale=0.082,
            text2_scale=0.087,
            text1_scale=0.087,
            text_style=3,
            command=lambda: self.request('Singleplayer')
        )
        self.connectButton.hide()

        self.serverBrowserButton = DirectButton(
            parent=base.a2dTopLeft,
            relief=None,
            pos=(.35, 0, -0.3),
            text="Server Browser",
            text_scale=0.082,
            text2_scale=0.087,
            text1_scale=0.087,
            text_style=3,
            command=lambda: self.request('Singleplayer')
        )
        self.serverBrowserButton.hide()

        # Log In button for the login screen
        self.logInButton2 = MATShuffleButton(
            pos=(0, 0, -0.8),
            text="Log In",
            wantArrows=False,
            image_scale=buttonScale,
            image2_scale=buttonScale_clickhover,
            image1_scale=buttonScale_clickhover,
            text_scale=0.082,
            text2_scale=0.087,
            text1_scale=0.087,
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

        self.hide()

        self.bookmarkInfoDialog = None

        # Load Bookmarks file
        self.bookmarkMgr = BookmarkManager()

        # Host Screen
        self.host_StartServer = MATShuffleButton(
            pos=(0, 0, -0.8),
            text="Host",
            wantArrows=False,
            image_scale=buttonScale,
            image2_scale=buttonScale_clickhover,
            image1_scale=buttonScale_clickhover,
            text_scale=0.10,
            text2_scale=0.105,
            text1_scale=0.105,
            command=lambda: self.request('StartHost')
        )
        self.host_ShowInBrowserLabel = TTLabel.TTLabel(
            pos=(-.55, 0, -.11),
            text="Show In Server Browser",
            text_align=TextNode.ALeft,
        )
        self.host_ShowInBrowserBox = TTCheckBox.TTCheckBox(
            pos=(-.6, 0, -.1),
            checked=False
        )

        self.host_CheatsLabel = TTLabel.TTLabel(
            pos=(-.55, 0, -.21),
            text="Cheats",
            text_align=TextNode.ALeft,
        )
        self.host_CheatsBox = TTCheckBox.TTCheckBox(
            pos=(-.6, 0, -.2),
            checked=True
        )

        self.host_ShowInBrowserBox.disable()
        self.host_CheatsBox.disable()

        self.hostButtons = []
        self.hostButtons.append(self.host_StartServer)
        self.hostButtons.append(self.host_ShowInBrowserLabel)
        self.hostButtons.append(self.host_ShowInBrowserBox)
        self.hostButtons.append(self.host_CheatsBox)
        self.hostButtons.append(self.host_CheatsLabel)

        for button in self.hostButtons:
            button.hide()

    def loadEnviroments(self):
        self.toontownCentral = loader.loadModel('phase_4/models/neighborhoods/toontown_central_sz.bam')
        self.toontownCentral.reparentTo(hidden)

    def unloadEnviroments(self):
        self.toontownCentral.removeNode()
        del self.toontownCentral

    def enterIdle(self):
        if (base.cr.music is None) and base.musicManagerIsValid:
            base.cr.music = base.musicManager.getSound('phase_3/audio/bgm/tti_main_menu_theme.ogg')
            if base.cr.music is not None:
                base.cr.music.setLoop(1)
                base.cr.music.setVolume(0.9)
                base.cr.music.play()

        # if sys.platform == 'android':
            # for button2 in self.buttonsIdle2:
                    # button2.hide()
        # else:
            # for button2 in self.buttonsIdle2:
                    # button2.show()
        # if not base.wantMultiplayer:
            # self.lockIconMP.show()
        # if not sys.platform == 'android':
            # if not base.wantMods:
                # self.lockIconMods.show()
        for button in self.buttonsIdle:
            button.show()

        self.background.show()
        self.logo.show()
        self.quitButton.show()

        for label in self.idleLabels:
            label.show()

    def exitIdle(self):
        # if not sys.platform == 'android':
            # for button2 in self.buttonsIdle2:
                    # button2.hide()
        # if not base.wantMultiplayer:
            # self.lockIconMP.hide()
        # if not sys.platform == 'android':
            # if not base.wantMods:
                # self.lockIconMods.hide()
        self.quitButton.hide()

        for button in self.buttonsIdle:
            button.hide()
        for label in self.idleLabels:
            label.hide()

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

        # If login is accepted then request the Home Screen

    def enterLoggingOut(self):
        pass

        # Do logout magic here:

        # If user is logging out request Idle

    def enterHomeScreen(self):
        for button2 in self.buttonsHomeScreen:
            button2.show()
        # if not base.wantMultiplayer:
            # self.lockIconMP.show()
        # if not base.wantMods:
            # self.lockIconMods.show()
        self.background.show()
        self.logo.show()
        self.quitButton.show()
        self.optionsButton2.show()
        self.modsButton.show()

    def exitHomeScreen(self):
        for button2 in self.buttonsHomeScreen:
            button2.hide()
        self.optionsButton2.hide()
        self.modsButton.hide()
        # if not base.wantMultiplayer:
            # self.lockIconMP.hide()
        # if not base.wantMods:
            # self.lockIconMods.hide()
    
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

    def enterHost(self):
        self.host_StartServer.show()

        # Load the ip input bar
        self.host_ServerNameInput = DirectEntry(
            parent=aspect2d,
            relief=DGG.GROOVE,
            scale=0.1,
            pos=(0, 0, -0.45),
            borderWidth=(0.05, 0.05),
            frameColor=((1, 1, 1, 0),
                        (1, 1, 1, 0),
                        (0.5, 0.5, 0.5, 0)),
            image = "phase_3/maps/input_box.png",
            image_scale = (4.6, 0, 1),
            image_pos = (0, 0, .2),
            state=DGG.DISABLED,
            text_align=TextNode.ACenter,
            text_scale=TTLocalizer.OPCodesInputTextScale,
            width=15.5,
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
        self.host_ServerNameInput.setTransparency(1)
        self.host_ServerNameInput.hide()
        self.host_ServerNameInputLabel = TTLabel.TTLabel(
            pos=(0, 0, -.3),
            text="Server Settings Coming Soon",#"Server Name in browser",
            text_align=TextNode.ACenter,
        )
    
    def exitHost(self):
        for button in self.hostButtons:
            button.hide()
        if hasattr(self, 'host_ServerNameInput'):
            self.host_ServerNameInput.destroy()
            del self.host_ServerNameInput
            self.host_ServerNameInputLabel.destroy()
            del self.host_ServerNameInputLabel
    
    def enterStartHost(self):
        base.isHosting = True
        base.isSinglePlayer = None
        self.__startGameSession(False)

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

        for label in self.labels:
            label.hide()

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

    def destroySPLocalStart(self):
        if self.localServerStart:
            self.localServerStart.removeNode()

    def hide(self):
        self.destroySPLocalStart()

        self.background.hide()
        self.logo.hide()

        for button in self.buttonsIdle:
            button.hide()

        for button in self.buttonsHomeScreen:
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

    def unload(self):
        print 'unload'
        if self.optionsScreen is not None:
            self.optionsScreen.unload()
            self.optionsScreen = None

        if self.optionsScreen2 is not None:
            self.optionsScreen2.unload()
            self.optionsScreen2 = None

    def __handleQuit(self):
        cleanupDialog('globalDialog')
        base.cr.loginFSM.request('shutdown')

    def showTooltip(self, text, event):
        self.currentTooltip = TTTooltip.TTTooltip(description = text)
        
    def killTooltip(self, event):
        if hasattr(self, 'currentTooltip'):
            self.currentTooltip.destroy()