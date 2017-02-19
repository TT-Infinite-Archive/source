from direct.fsm.FSM import FSM
from direct.showbase.DirectObject import DirectObject
from otp.otpbase import OTPLocalizer

from toontown.makeatoon.MakeAToonGUI import MATShuffleButton
from toontown.toonbase.ColorGlobals import CGray, CDefault
from toontown.toontowngui.LocalSinglePlayerStart import LocalSinglePlayerStart
from toontown.util import TTCardMaker

from pandac.PandaModules import *
from toontown.toonbase import ToontownGlobals
from direct.gui.DirectGui import *
from toontown.toonbase import TTLocalizer
from direct.interval.IntervalGlobal import Sequence
from direct.interval.IntervalGlobal import LerpScaleInterval
from toontown.toontowngui import TTDialog


class MainMenu(DirectObject, FSM):
    notify = directNotify.newCategory('MainMenu')

    def __init__(self):
        DirectObject.__init__(self)
        FSM.__init__(self, 'MainMenu')

        self.logoScaleTrack = None
        self.localSinglePlayerStart = None

        self.buttons = []
        self.spButtons = []
        self.mpButtons = []
        self.mpButtons2 = []

        buttonScale = (-1.1, 1.1, 1.1)
        buttonScale_clickhover = (-1.2, 1.2, 1.2)


        buttonScale2 = (-0.8, 0.8, 0.8)
        buttonScale2_clickhover = (-0.9, 0.9, 0.9)

        # Load the background image for the Main Menu
        self.background = OnscreenImage(
            parent=base.aspect2d, image='phase_3/maps/loading_bg_clouds.jpg',
            scale=(2, 1, 1), pos=(0, 0, 0))

        # Load the Toontown Infinite logo
        offset = -0.02
        self.logo = OnscreenImage(
            parent=base.aspect2d,
            image='phase_3/maps/toontown_infinite_logo.png',
            scale=(0.75, 0.35, 0.40), pos=(offset, 0, 0.35)
        )
        self.logo.setTransparency(TransparencyAttrib.MAlpha)

        if self.logoScaleTrack is not None:
            self.logoScaleTrack.finish()
            self.logoScaleTrack = None

        # Pulsating animation for the logo
        self.logoScaleTrack = Sequence(
            LerpScaleInterval(self.logo, 4, Vec3(0.75, 0.35, 0.40), Vec3(0.70, 0.35, 0.375),
                              blendType='easeInOut'),
            LerpScaleInterval(self.logo, 4, Vec3(0.70, 0.35, 0.375), Vec3(0.75, 0.35, 0.40),
                              blendType='easeInOut')
        )
        self.logoScaleTrack.loop()

        # Main Menu Buttons
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
            command=lambda: self.request('SinglePlayer')
        )
        self.buttons.append(self.singlePlayerButton)

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
        self.buttons.append(self.multiPlayerButton)

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
        self.buttons.append(self.modsButton)

        # Load the lock icon image for disabled buttons
        lockImage = TTCardMaker.makeCard('phase_3/maps/lock_icon.png')

        # Lock icon for Multiplayer
        self.lockIconMP = DirectButton(
            parent=aspect2d,
            relief=None,
            image=lockImage,
            image_scale=(0.0007, 0.0007, 0.0007),
            pos=(0.35, 0, -0.50),
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
            pos=(0.35, 0, -0.80),
            suppressMouse=True,
            state=DGG.DISABLED
        )

        self.lockIconMods.hide()

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
        self.serverBrowser = MATShuffleButton(
            pos=(0, 0, -0.30),
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

        self.directConnectButton = MATShuffleButton(
            pos=(-0.5, 0, -0.60),
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
            pos=(0.5, 0, -0.60),
            text="Host While\nPlaying",
            text_pos=(0, 0.02, 0),
            wantArrows=False,
            image_scale=buttonScale,
            image2_scale=buttonScale_clickhover,
            image1_scale=buttonScale_clickhover,
            text_scale=0.08,
            text2_scale=0.085,
            text1_scale=0.085,
            command=lambda: self.request('HostMultiplayer')
        )
        self.mpButtons.append(self.hostButton)
        self.mpButtons.append(self.directConnectButton)
        self.mpButtons.append(self.serverBrowser)

        # Multiplayer Menu Buttons: Join Menu
        self.connectButton = MATShuffleButton(
            pos=(0, 0, -0.75),
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
        self.mpButtons2.append(self.connectButton)

        # Quit Button for all the menus
        gui = loader.loadModel('phase_3/models/gui/pick_a_toon_gui.bam')
        quitHover = gui.find('**/QuitBtn_RLVR')
        self.quitButton = DirectButton(
            image=(quitHover, quitHover, quitHover), relief=None,
            text=TTLocalizer.AvatarChooserQuit,
            text_font=ToontownGlobals.getSignFont(),
            text_fg=(0.977, 0.816, 0.133, 1),
            text_pos=TTLocalizer.ACquitButtonPos,
            text_scale=TTLocalizer.ACquitButton, image_scale=1,
            image1_scale=1.05, image2_scale=1.05, scale=1.05,
            pos=(1.65, 0, -0.935), command=self.__handleQuit)
        self.quitButton.reparentTo(base.aspect2d)
        self.buttons.append(self.quitButton)

        gui = loader.loadModel('phase_3/models/gui/pick_a_toon_gui.bam')
        quitHover = gui.find('**/QuitBtn_RLVR')

        # Back Button
        self.backButton = DirectButton(
            image=(quitHover, quitHover, quitHover), relief=None,
            text=TTLocalizer.OptionsGoBack,
            text_font=ToontownGlobals.getSignFont(),
            text_fg=(0.977, 0.816, 0.133, 1),
            text_pos=TTLocalizer.ACquitButtonPos,
            text_scale=TTLocalizer.ACbackButton, image_scale=1,
            image1_scale=1.05, image2_scale=1.05, scale=1.05,
            pos=(-1.65, 0, -0.935), command=lambda: self.request('Idle'))

        self.backButton.hide()
        self.backButton.reparentTo(base.aspect2d)

        # Back Button 2
        self.backButton2 = DirectButton(
            image=(quitHover, quitHover, quitHover), relief=None,
            text=TTLocalizer.OptionsGoBack,
            text_font=ToontownGlobals.getSignFont(),
            text_fg=(0.977, 0.816, 0.133, 1),
            text_pos=TTLocalizer.ACquitButtonPos,
            text_scale=TTLocalizer.ACbackButton, image_scale=1,
            image1_scale=1.05, image2_scale=1.05, scale=1.05,
            pos=(-1.65, 0, -0.935), command=lambda: self.request('Idle'))

        self.backButton2.hide()
        self.backButton2.reparentTo(base.aspect2d)

        # Back Button 3
        self.backButton3 = DirectButton(
            image=(quitHover, quitHover, quitHover), relief=None,
            text=TTLocalizer.OptionsGoBack,
            text_font=ToontownGlobals.getSignFont(),
            text_fg=(0.977, 0.816, 0.133, 1),
            text_pos=TTLocalizer.ACquitButtonPos,
            text_scale=TTLocalizer.ACbackButton, image_scale=1,
            image1_scale=1.05, image2_scale=1.05, scale=1.05,
            pos=(-1.65, 0, -0.935), command=lambda: self.request('Multiplayer'))

        self.backButton3.hide()
        self.backButton3.reparentTo(base.aspect2d)

        self.hide()

    def enterIdle(self):
        if (base.cr.music is None) and base.musicManagerIsValid:
            if ToontownGlobals.HALLOWEEN_PROPS in base.clientHolidayIdList:
                base.cr.music = base.musicManager.getSound('phase_3/audio/bgm/tti_theme_halloween.ogg')
            else:
                base.cr.music = base.musicManager.getSound('phase_3/audio/bgm/tti_theme.ogg')
            if base.cr.music is not None:
                base.cr.music.setLoop(1)
                base.cr.music.setVolume(0.9)
                base.cr.music.play()

        
        OTPLocalizer.SpeedChatStaticText[30500] = "Welcome to the server!"
        OTPLocalizer.SpeedChatStaticText[30502] = "Are you livestreaming?"
        OTPLocalizer.SpeedChatStaticText[30503] = "I'm livestreaming right now!"
        OTPLocalizer.SpeedChatStaticText[30506] = "When do you think those tunnels will open?"
        OTPLocalizer.SpeedChatStaticText[30512] = "You can report bugs on the Toontown Infinite Discord server in the #bug-report text channel."

        self.background.show()
        self.logo.show()
        if not base.wantMultiplayer:
            self.lockIconMP.show()
        if not base.wantMods:
            self.lockIconMods.show()
        for button in self.buttons:
            button.show()

    def exitIdle(self):
        self.background.hide()
        for button in self.buttons:
            button.hide()
        if not base.wantMultiplayer:
            self.lockIconMP.hide()
        if not base.wantMods:
            self.lockIconMods.hide()

    def enterSinglePlayer(self):
        OTPLocalizer.SpeedChatStaticText[30500] = "I'm playing Singleplayer on Toontown Infinite!"
        OTPLocalizer.SpeedChatStaticText[30502] = "Are you enjoying my livestream?"
        OTPLocalizer.SpeedChatStaticText[30503] = 'Hello, viewers! Thanks for watching my livestream!'
        OTPLocalizer.SpeedChatStaticText[30506] = 'I wonder when those tunnels will open...'
        OTPLocalizer.SpeedChatStaticText[30512] = 'I can report bugs on the Toontown Infinite Discord server in the #bug-report text channel.'
        self.__startGameSession(True)
        base.isSinglePlayer = True
        base.isHosting = False

    def enterHostMultiplayer(self):
        base.isHosting = True
        self.__startGameSession(False)

    def __startGameSession(self, singlePlayer):
        self.hide()
        self.background.show()
        self.logo.show()

        self.LocalSinglePlayerStart = LocalSinglePlayerStart(self, singlePlayer)
        self.LocalSinglePlayerStart.request('Start')

    def enterMultiplayer(self):
        self.background.show()
        self.backButton.show()
        base.isSinglePlayer = False
        for mpButton in self.mpButtons:
            mpButton.show()

    def exitMultiplayer(self):
        self.background.hide()
        self.backButton.hide()
        for mpButton in self.mpButtons:
            mpButton.hide()

    def enterDirectConnect(self):
        self.background.show()
        self.backButton3.show()
        self.quitButton.show()

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
        for mpButton2 in self.mpButtons2:
            mpButton2.show()

    def exitDirectConnect(self):
        self.background.hide()
        self.backButton3.hide()
        self.ipInput.hide()
        self.__disableIPEntry()
        for mpButton2 in self.mpButtons2:
            mpButton2.hide()

    def __submitIP(self, input=None):
        if input is None:
            input = self.ipInput.get()
        self.ipInput['focus'] = 1
        if input == '':
            return
        messenger.send('wakeup')
        self.request('StartDirectConnect')

    def enterStartDirectConnect(self):
        base.isHosting = False
        ip = self.ipInput.get()
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
        for button in self.buttons:
            button.hide()

        for mpButton in self.mpButtons:
            mpButton.hide()

        for mpButton2 in self.mpButtons2:
            mpButton2.hide()

    def __handleQuit(self):
        cleanupDialog('globalDialog')
        base.cr.loginFSM.request('shutdown')
