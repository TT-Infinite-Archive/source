import os
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator
from direct.fsm.FSM import FSM
from direct.gui.DirectGui import *
from direct.gui.DirectGui import *
from direct.interval.IntervalGlobal import LerpScaleInterval
from direct.interval.IntervalGlobal import Sequence
from pandac.PandaModules import *

from otp.otpbase import OTPLocalizer
from toontown.makeatoon.MakeAToonGUI import MATShuffleButton
from toontown.shtiker.OptionsTabPage import OptionsTabPage
from toontown.toonbase import TTLocalizer
from toontown.toonbase import ToontownGlobals
from toontown.toonbase.ColorGlobals import CGray, CDefault
from toontown.toontowngui import TTDialog
from toontown.toontowngui.LocalSinglePlayerStart import LocalSinglePlayerStart
from toontown.util import PlacerTool3D
from toontown.util import TTCardMaker


class MainMenu(DirectFrame, FSM):
    notify = directNotify.newCategory('MainMenu')

    def __init__(self):
        DirectFrame.__init__(self)
        FSM.__init__(self, 'MainMenu')

        self.logoScaleTrack = None
        self.localSinglePlayerStart = None

        self.buttons = []
        self.buttons2 = []
        self.mpButtons = []
        self.labels = []

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

        self.label11 = DirectLabel(relief=None, text='', text_fg=(1, 1, 1, 1),
                                 text_font=ToontownGlobals.getToonFont(), text_scale=0.09, text_wordwrap=25,
                                 pos=(0, 0, -0.36))

        self.label12 = DirectLabel(relief=None, text='', text_fg=(1, 1, 1, 1),
                                 text_font=ToontownGlobals.getToonFont(), text_scale=0.12, text_wordwrap=25,
                                 pos=(0, 0, -0.36))

        self.labels.append(self.label)
        self.labels.append(self.label2)
        self.labels.append(self.label3)
        self.labels.append(self.label4)
        self.labels.append(self.label5)
        self.labels.append(self.label6)
        self.labels.append(self.label7)
        self.labels.append(self.label8)
        self.labels.append(self.label9)
        self.labels.append(self.label10)
        self.labels.append(self.label11)
        self.labels.append(self.label12)

        # Load the background image for the Main Menu
        self.background = OnscreenImage(
            parent=render2d, image='phase_3/maps/loading_bg_clouds.jpg', pos=(0, 0, 0))
        self.background.setBin('background', 0)
        self.background.setScale(render2d, Vec3(1))
        
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

        # Main Menu Buttons
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
        self.buttons.append(self.logInButton)

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
        self.buttons.append(self.signUpButton)

        self.singlePlayerButton = MATShuffleButton(
            pos=(0, 0, -0.2),
            text="Singleplayer",
            wantArrows=False,
            image_scale=buttonScale,
            image2_scale=buttonScale_clickhover,
            image1_scale=buttonScale_clickhover,
            text_scale=0.082,
            text2_scale=0.087,
            text1_scale=0.087,
            command=lambda: self.request('Singleplayer')
        )
        self.buttons2.append(self.singlePlayerButton)

        self.multiPlayerButton = MATShuffleButton(
            pos=(0, 0, -0.5),
            text="Multiplayer",
            wantArrows=False,
            image_scale=buttonScale,
            image2_scale=buttonScale_clickhover,
            image1_scale=buttonScale_clickhover,
            text_scale=0.09,
            text2_scale=0.095,
            text1_scale=0.095,
            command=lambda: self.request('Multiplayer')
        )
        self.buttons2.append(self.multiPlayerButton)

        self.modsButton = MATShuffleButton(
            pos=(0, 0, -0.8),
            text="Mods",
            wantArrows=False,
            image_scale=buttonScale,
            image2_scale=buttonScale_clickhover,
            image1_scale=buttonScale_clickhover,
            text_scale=0.10,
            text2_scale=0.105,
            text1_scale=0.105,
            # command=lambda: self.request('Mods')
        )
        self.buttons2.append(self.modsButton)
        
        self.optionsButton = MATShuffleButton(
            parent = base.a2dBottomLeft,
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
        self.buttons2.append(self.optionsButton)

        """
        gui = loader.loadModel('phase_3/models/gui/pick_a_toon_gui.bam')
        quitHover = gui.find('**/QuitBtn_RLVR')
        self.logOutButton = DirectButton(
            image=(quitHover, quitHover, quitHover), relief=None,
            text=TTLocalizer.OptionsPageLogout,
            text_font=ToontownGlobals.getSignFont(),
            text_fg=(0.977, 0.816, 0.133, 1),
            text_pos=TTLocalizer.AClogOutButtonPos,
            text_scale=TTLocalizer.AClogOutButton, image_scale=1,
            image1_scale=1.05, image2_scale=1.05, scale=1.05,
            pos=(-1.65, 0, -0.935), command=lambda: self.request('Idle'))
        self.logOutButton.reparentTo(base.aspect2d)
        self.buttons2.append(self.logOutButton)
        """

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
        self.logInButton2.hide()

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
        self.signUpButton2.hide()

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
        self.signUpButton3.hide()

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
            command=lambda: self.request('HomeScreen')
        )
        self.termsButton.hide()

        for button2 in self.buttons2:
            button2.hide()

        # Load the lock icon image for disabled buttons
        lockImage = TTCardMaker.makeCard('phase_3/maps/lock_icon.png')

        # Lock icon for Multiplayer
        self.lockIconMP = DirectButton(
            parent=aspect2d,
            relief=None,
            image=lockImage,
            image_scale=(0.0007, 0.0007, 0.0007),
            pos=(0.34, 0, -0.48),
            suppressMouse=True,
            state=DGG.DISABLED
        )
        self.lockIconMP.hide()

        # Lock icon for Mods
        self.lockIconMods = DirectButton(
            parent=aspect2d,
            relief=None,
            image=lockImage,
            image_scale=(0.0007, 0.0007, 0.0007),
            pos=(0.34, 0, -0.78),
            suppressMouse=True,
            state=DGG.DISABLED
        )
        self.lockIconMods.hide()

        # Lock icon for the Server Browser
        self.lockIconSB = DirectButton(
            parent=aspect2d,
            relief=None,
            image=lockImage,
            image_scale=(0.0007, 0.0007, 0.0007),
            pos=(0.34, 0, -0.49),
            suppressMouse=True,
            state=DGG.DISABLED
        )
        self.lockIconSB.hide()

        # Functionality for enabling and disabling the Multiplayer button
        self.multiPlayerButton['state'] = DGG.DISABLED
        self.multiPlayerButton.setColorScale(CGray)

        if base.wantMultiplayer:
            self.lockIconMP.destroy()
            self.multiPlayerButton['state'] = DGG.NORMAL
            self.multiPlayerButton.setColorScale(CDefault)

        # Functionality for enabling and disabling the Mods button
        self.modsButton['state'] = DGG.DISABLED
        self.modsButton.setColorScale(CGray)

        if base.wantMods:
            self.lockIconMods.destroy()
            self.modsButton['state'] = DGG.NORMAL
            self.modsButton.setColorScale(CDefault)

        # Multiplayer Menu Buttons
        self.serverBrowserButton = MATShuffleButton(
            pos=(-.35, 0, -0.5),
            text="Server\nBrowser",
            text_pos=(0, 0.02, 0),
            wantArrows=False,
            image_scale=buttonScale,
            image2_scale=buttonScale_clickhover,
            image1_scale=buttonScale_clickhover,
            text_scale=0.08,
            text2_scale=0.085,
            text1_scale=0.085,
            command=lambda: self.request('MultiplayerSB')
        )
        
        self.bookmarksButton = MATShuffleButton(
            pos=(.35, 0, -0.5),
            text="Bookmarked\nServers",
            text_pos=(0, 0.02, 0),
            wantArrows=False,
            image_scale=buttonScale,
            image2_scale=buttonScale_clickhover,
            image1_scale=buttonScale_clickhover,
            text_scale=0.08,
            text2_scale=0.085,
            text1_scale=0.085,
            command=lambda: self.request('Bookmarks')
        )

        self.directConnectButton = MATShuffleButton(
            pos=(-0.35, 0, -0.2),
            text="Direct\nConnect",
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

        self.hostButton = MATShuffleButton(
            pos=(0.35, 0, -0.2),
            text="Host",
            wantArrows=False,
            image_scale=buttonScale,
            image2_scale=buttonScale_clickhover,
            image1_scale=buttonScale_clickhover,
            text_scale=0.10,
            text2_scale=0.105,
            text1_scale=0.105,
            command=lambda: self.request('HostMultiplayer')
        )

        self.helpButton = MATShuffleButton(
            pos=(0, 0, -0.8),
            text="Help",
            wantArrows=False,
            image_scale=buttonScale,
            image2_scale=buttonScale_clickhover,
            image1_scale=buttonScale_clickhover,
            text_scale=0.10,
            text2_scale=0.105,
            text1_scale=0.105,
            command=lambda: self.request('MultiplayerHelp')
        )

        self.label11['text'] = TTLocalizer.EnterAddress
        self.label11.reparentTo(aspect2d)
        self.label11.hide()

        self.mpButtons.append(self.hostButton)
        self.mpButtons.append(self.serverBrowserButton)
        self.mpButtons.append(self.directConnectButton)
        self.mpButtons.append(self.helpButton)
        self.mpButtons.append(self.bookmarksButton)

        # Functionality for enabling and disabling the Server Browser button
        self.serverBrowserButton['state'] = DGG.DISABLED
        self.serverBrowserButton.setColorScale(CGray)

        if base.wantServerBrowser:
            self.lockIconSB.destroy()
            self.serverBrowserButton['state'] = DGG.NORMAL
            self.serverBrowserButton.setColorScale(CDefault)

        # Multiplayer Menu Buttons: Join Menu
        self.connectButton = MATShuffleButton(
            pos=(.35, 0, -0.75),
            text="Connect",
            wantArrows=False,
            image_scale=buttonScale,
            image2_scale=buttonScale_clickhover,
            image1_scale=buttonScale_clickhover,
            text_scale=0.09,
            text2_scale=0.095,
            text1_scale=0.10,
            command=lambda: self.request('StartDirectConnect')
        )
        self.connectButton.hide()
        
        # Multiplayer Menu Buttons: Add current ip to Bookmarks
        self.addToBookmarksButton = MATShuffleButton(
            pos=(-.35, 0, -0.75),
            text_pos=(0, 0.02, 0),
            text="Add To\nBookmarks",
            wantArrows=False,
            image_scale=buttonScale,
            image2_scale=buttonScale_clickhover,
            image1_scale=buttonScale_clickhover,
            text_scale=0.09,
            text2_scale=0.095,
            text1_scale=0.10,
            command=self.addToBookmarks
        )
        self.addToBookmarksButton.hide()

        self.label12['text'] = TTLocalizer.Help
        self.label12.reparentTo(aspect2d)
        self.label12.hide()

        # Quit Button for all the menus
        gui = loader.loadModel('phase_3/models/gui/pick_a_toon_gui.bam')
        quitHover = gui.find('**/QuitBtn_RLVR')
        self.quitButton = MATShuffleButton(
            parent = base.a2dBottomRight,
            pos=(-.4, 0, .2),
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
        self.buttons2.append(self.quitButton)

        gui = loader.loadModel('phase_3/models/gui/pick_a_toon_gui.bam')
        quitHover = gui.find('**/QuitBtn_RLVR')

        # Back Button
        self.backButton = MATShuffleButton(
            parent = base.a2dBottomLeft,
            pos=(.4, 0, .2),
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
            parent = base.a2dBottomLeft,
            pos=(.4, 0, .2),
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

        self.backButton2.hide()

        # Back Button 3
        self.backButton3 = MATShuffleButton(
            parent = base.a2dBottomLeft,
            pos=(.4, 0, .2),
            text=TTLocalizer.OptionsGoBack,
            wantArrows=False,
            image_scale=buttonScale,
            image2_scale=buttonScale_clickhover,
            image1_scale=buttonScale_clickhover,
            text_scale=0.10,
            text2_scale=0.105,
            text1_scale=0.105,
            command=lambda: self.request('Multiplayer')
        )

        self.backButton3.hide()

        self.hide()
        
        # Load Bookmarks file
        self.bookmarks = []
        
        if self.bookmarks == []:
            if not os.path.exists("bookmarks.dat"):
                with open("bookmarks.dat", 'wb') as file:
        
                    data = PyDatagram()
                    data.add_uint8(0)
                    
                    file.write(PyDatagramIterator(data).get_remaining_bytes())
                    
            file = open("bookmarks.dat", 'rb')
            data = file.read()
            file.close()
            
            dg = PyDatagram(data)
            data = PyDatagramIterator(dg)
            
            def getBookmark(index, dgi):
                name = dgi.get_string()
                address = dgi.get_string()
                if address != '':
                    self.bookmarks.append([name, address])
            
            for index in xrange(data.get_uint8()):
                getBookmark(index, data)
            
            print(self.bookmarks)

    def enterIdle(self):
        if (base.cr.music is None) and base.musicManagerIsValid:
            base.cr.music = base.musicManager.getSound('phase_3/audio/bgm/tti_theme.ogg')
            if base.cr.music is not None:
                base.cr.music.setLoop(1)
                base.cr.music.setVolume(0.9)
                base.cr.music.play()
        
        OTPLocalizer.SpeedChatStaticText[30500] = "Welcome to the server!"
        OTPLocalizer.SpeedChatStaticText[30502] = "Are you livestreaming?"
        OTPLocalizer.SpeedChatStaticText[30503] = "I'm livestreaming right now!"
        OTPLocalizer.SpeedChatStaticText[30512] = "You can report bugs on the Toontown Infinite Discord server in the #bug-report text channel."

        for button2 in self.buttons2:
            button2.show()
        if not base.wantMultiplayer:
            self.lockIconMP.show()
        if not base.wantMods:
            self.lockIconMods.show()
        self.background.show()
        self.logo.show()
        self.quitButton.show()

        """
        self.background.show()
        self.logo.show()
        self.quitButton.show()
        for button in self.buttons:
            button.show()

        self.label['text'] = TTLocalizer.WelcomeMessage
        self.label.reparentTo(aspect2d)

        self.label2['text'] = TTLocalizer.LogIn
        self.label2.reparentTo(aspect2d)

        self.label3['text'] = TTLocalizer.SignUp
        self.label3.reparentTo(aspect2d)

        self.label.show()
        self.label2.show()
        self.label3.show()
        """

    def exitIdle(self):
        for button2 in self.buttons2:
            button2.hide()
        if not base.wantMultiplayer:
            self.lockIconMP.hide()
        if not base.wantMods:
            self.lockIconMods.hide()
        self.quitButton.hide()

        """
        for button in self.buttons:
            button.hide()
        self.label.hide()
        self.label2.hide()
        self.label3.hide()
        """

    def enterSignInScreen(self):
        self.backButton.show()
        self.logInButton2.show()

        self.label4['text'] = TTLocalizer.Username
        self.label4.reparentTo(aspect2d)

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

        self.label5['text'] = TTLocalizer.Password
        self.label5.reparentTo(aspect2d)

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
        self.label4.show()
        self.label5.show()

    def exitSignInScreen(self):
        self.backButton.hide()
        self.logInButton2.hide()
        self.usernameInput.hide()
        self.passwordInput.hide()
        self.label4.hide()
        self.label5.hide()

    def enterSignUpScreen(self):
        self.backButton.show()
        self.signUpButton3.show()
        self.label6.show()
        self.label7.show()
        self.label8.show()
        self.label9.show()
        self.label10.show()
        self.termsButton.show()
        self.logo.hide()

        self.label8['text'] = TTLocalizer.Birthday
        self.label8.reparentTo(aspect2d)

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

        self.label9['text'] = TTLocalizer.Email
        self.label9.reparentTo(aspect2d)

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

        self.label7['text'] = TTLocalizer.Password
        self.label7.reparentTo(aspect2d)

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

        self.label6['text'] = TTLocalizer.Username
        self.label6.reparentTo(aspect2d)

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
        # PlacerTool3D.PlacerTool3D(self.usernameInput, increment=0.01)
        self.label10['text'] = TTLocalizer.Warning
        self.label10.reparentTo(aspect2d)

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
        for label in self.labels:
            label.hide()

    def enterLoggingIn(self):
        pass

        # Do login magic here:

        # If login is accepted then request the Home Screen

    def enterLoggingOut(self):
        pass

        # Do logout magic here:

        # If user is logging out request Idle

    """
    def enterHomeScreen(self):
        for button2 in self.buttons2:
            button2.show()
        if not base.wantMultiplayer:
            self.lockIconMP.show()
        if not base.wantMods:
            self.lockIconMods.show()
        self.background.show()
        self.logo.show()
        self.quitButton.show()

    def exitHomeScreen(self):
        for button2 in self.buttons2:
            button2.hide()
        if not base.wantMultiplayer:
            self.lockIconMP.hide()
        if not base.wantMods:
            self.lockIconMods.hide()
    """
    
    def enterOptions(self):
        self.optionsScreen = OptionsTabPage()
        self.optionsScreen.show()
        self.optionsButton.show()
        self.optionsButton['command'] = lambda: self.request('Idle')
        self.optionsButton['text'] = "Back"
        self.logo.hide()
        
    def exitOptions(self):
        if self.optionsScreen is not None:
            self.optionsScreen.unload()
            self.optionsScreen = None
        self.optionsButton['command'] = lambda: self.request('Options')
        self.optionsButton['text'] = "Options"
        self.logo.show()

    def enterSingleplayer(self):
        OTPLocalizer.SpeedChatStaticText[30500] = "I'm playing Singleplayer on Toontown Infinite!"
        OTPLocalizer.SpeedChatStaticText[30502] = "Are you enjoying my livestream?"
        OTPLocalizer.SpeedChatStaticText[30503] = 'Hello, viewers! Thanks for watching my livestream!'
        OTPLocalizer.SpeedChatStaticText[30512] = 'I can report bugs on the Toontown Infinite Discord server in the #bug-report text channel.'
        self.__startGameSession(True)
        base.isSinglePlayer = True
        base.isHosting = False

    def enterHostMultiplayer(self):
        base.isHosting = True
        self.__startGameSession(False)

    def __startGameSession(self, singlePlayer):
        self.LocalSinglePlayerStart = LocalSinglePlayerStart(self, singlePlayer)
        self.LocalSinglePlayerStart.request('Start')
        self.quitButton.hide()

    def enterMultiplayer(self):
        self.backButton2.show()
        base.isSinglePlayer = False
        for mpButton in self.mpButtons:
            mpButton.show()
        if not base.wantServerBrowser:
            self.lockIconSB.show()

    def exitMultiplayer(self):
        self.backButton2.hide()
        for mpButton in self.mpButtons:
            mpButton.hide()
        if not base.wantServerBrowser:
            self.lockIconSB.hide()

    def enterMultiplayerHelp(self):
        self.label12.show()
        self.backButton3.show()

    def exitMultiplayerHelp(self):
        self.label12.hide()
        self.backButton3.hide()
        
    def enterBookmarks(self):
        self.backButton3.show()
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
                itemFrame_frameSize = (-1, 1, -1.5, .1),
                itemFrame_pos = (0, 0, .7),
                itemFrame_frameColor = (0.85, 0.95, 1, 1)
                )
        self.bookmarksList.show()
        self.makeBookmarksButtons()
        self.logo.hide()
         
    def exitBookmarks(self):
        self.backButton3.hide()
        self.bookmarksList.hide()
        self.logo.show()

    def makeBookmarksButtons(self):
        self.bookmarksList.removeAllItems()
        
        trashcanGui = loader.loadModel('phase_3/models/gui/trashcan_gui.bam')
        buttonScale = (-1.1, .6, .6)
        buttonScale_clickhover = (-1.2, .7, .7)
        for bookmark in self.bookmarks:
            name = bookmark[0]
            address = bookmark[1]
            button = DirectButton(
                relief = None,
                text="%s" %(name),
                text_scale = 0.082,
                text2_scale = 0.087,
                text1_scale = 0.087,
                text_fg = (1, 1, 1, 1),
                text_shadow = (0, 0, 0, 1),
                command = self.__submitIP,
                extraArgs = [address])
            
            deleteButton = DirectButton(parent = button,
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
                scale = .2,
                command = self.deleteFromBookmarks,
                extraArgs = [name, address],
                pos = (0, 0, 0))
            deleteButton.reparentTo(button)
            deleteButton.setPos(.9, 0, .03)
                    

            self.bookmarksList.addItem(button)
        
    def enterDirectConnect(self):
        self.backButton3.show()
        self.label11.show()

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
        self.connectButton.show()
        self.addToBookmarksButton.show()

    def exitDirectConnect(self):
        self.backButton3.hide()
        self.ipInput.hide()
        self.label11.hide()
        self.__disableIPEntry()
        self.connectButton.hide()
        self.addToBookmarksButton.hide()

        for label in self.labels:
            label.hide()

    def __submitIP(self, input=None):
        print(input)
        if input is None:
            input = self.ipInput.get()
            self.ipInput['focus'] = 1
        if input == '':
            return
        self.targetIp = input
        messenger.send('wakeup')
        self.request('StartDirectConnect')
        
    def addToBookmarks(self):
        def makeBookmark(name, address, dg):
            dg.add_string(name)
            dg.add_string(address)
            
        if hasattr(self, 'ipInput'):
            if self.ipInput.get() == '':
                return
            name = self.ipInput.get() # TODO: Add custom naming of bookmarks
            address = self.ipInput.get()
            bookmark = [name, address]
            if not bookmark in self.bookmarks:
                self.bookmarks.append(bookmark)
            with open("bookmarks.dat", 'wb') as file:
                dg = PyDatagram()
                dg.add_uint8(len(self.bookmarks))
                for bookmark in self.bookmarks:
                    makeBookmark(bookmark[0], bookmark[1], dg)
                file.write(PyDatagramIterator(dg).getRemainingBytes())
                print(self.bookmarks)
                
    def deleteFromBookmarks(self, name, address):
        data = [name, address]
        self.bookmarks.remove(data)
        self.makeBookmarksButtons()
        self.addToBookmarks()
                
    def enterStartDirectConnect(self):
        base.isHosting = False
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
        if self.localSinglePlayerStart:
            self.localSinglePlayerStart.removeNode()

    def hide(self):
        self.destroySPLocalStart()
        self.background.hide()
        self.logo.hide()
        self.connectButton.hide()
        self.logInButton.hide()
        self.logInButton2.hide()
        self.signUpButton.hide()
        self.signUpButton2.hide()
        self.signUpButton3.hide()

        for button in self.buttons:
            button.hide()

        for button2 in self.buttons2:
            button2.hide()

        for mpButton in self.mpButtons:
            mpButton.hide()

        for label in self.labels:
            label.hide()

    def __handleQuit(self):
        cleanupDialog('globalDialog')
        base.cr.loginFSM.request('shutdown')
