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
        self.mpButtons3 = []

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
            text="Single Player",
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

        self.kaldronNetworkButton = MATShuffleButton(
            pos=(0, 0, -0.8),
            text="Kaldron\nNetwork",
            text_pos=(0, 0.02, 0),
            wantArrows=False,
            image_scale=buttonScale,
            image2_scale=buttonScale_clickhover,
            image1_scale=buttonScale_clickhover,
            text_scale=0.08,
            text2_scale=0.085,
            text1_scale=0.085,
            command=lambda: self.request('')
        )
        self.buttons.append(self.kaldronNetworkButton)

        # Load the lock icon image for disabled buttons
        lockImage = TTCardMaker.makeCard('phase_3/maps/lock_icon.png')

        # Lock icon for Multiplayer
        self.lockIcon = DirectButton(
            parent=aspect2d,
            relief=None,
            image=lockImage,
            image_scale=(0.0007, 0.0007, 0.0007),
            pos=(0.35, 0, -0.50),
            suppressMouse=True,
            state=DGG.DISABLED
        )

        self.lockIcon.hide()

        # Lock icon for the Kaldron Interactive Network
        self.lockIcon2 = DirectButton(
            parent=aspect2d,
            relief=None,
            image=lockImage,
            image_scale=(0.0007, 0.0007, 0.0007),
            pos=(0.35, 0, -0.80),
            suppressMouse=True,
            state=DGG.DISABLED
        )

        self.lockIcon2.hide()

        # Functionality for enabling and disabling the Multiplayer button
        self.multiPlayerButton['state'] = DGG.DISABLED
        self.multiPlayerButton.setColorScale(CGray)

        if base.wantMultiplayer:
            self.lockIcon.destroy()
            self.multiPlayerButton['state'] = DGG.NORMAL
            self.multiPlayerButton.setColorScale(CDefault)

        # Functionality for enabling and disabling the Kaldron Interactive Network button
        self.kaldronNetworkButton['state'] = DGG.DISABLED
        self.kaldronNetworkButton.setColorScale(CGray)

        if base.wantKaldronNetwork:
            self.lockIcon2.destroy()
            self.kaldronNetworkButton['state'] = DGG.NORMAL
            self.kaldronNetworkButton.setColorScale(CDefault)

        # Single Player Menu Buttons
        self.spLocalButton = MATShuffleButton(
            pos=(0, 0, -0.30),
            text="Local Play",
            wantArrows=False,
            image_scale=buttonScale,
            image2_scale=buttonScale_clickhover,
            image1_scale=buttonScale_clickhover,
            text_scale=0.09,
            text2_scale=0.095,
            text1_scale=0.095,
            command=lambda: self.request('SinglePlayerLocal')
        )
        self.spButtons.append(self.spLocalButton)

        self.spMods = MATShuffleButton(
            pos=(0, 0, -0.60),
            text="Mods",
            wantArrows=False,
            image_scale=buttonScale2,
            image2_scale=buttonScale2_clickhover,
            image1_scale=buttonScale2_clickhover,
            text_scale=0.09,
            text2_scale=0.095,
            text1_scale=0.095,
            command=lambda: self.request('Mods')
        )
        self.spButtons.append(self.spMods)

        # Multiplayer Menu Buttons
        self.mpCustomPlay = MATShuffleButton(
            pos=(0, 0, -0.30),
            text="Custom Play",
            wantArrows=False,
            image_scale=buttonScale,
            image2_scale=buttonScale_clickhover,
            image1_scale=buttonScale_clickhover,
            text_scale=0.082,
            text2_scale=0.087,
            text1_scale=0.087,
            command=lambda: self.request('MultiplayerCP')
        )

        self.mpButtons.append(self.mpCustomPlay)

        self.mpMods = MATShuffleButton(
            pos=(0, 0, -0.60),
            text="Mods",
            wantArrows=False,
            image_scale=buttonScale2,
            image2_scale=buttonScale2_clickhover,
            image1_scale=buttonScale2_clickhover,
            text_scale=0.09,
            text2_scale=0.095,
            text1_scale=0.095,
            command=lambda: self.request('Mods')
        )
        self.mpButtons.append(self.mpMods)

        # Multiplayer Menu Buttons: Join/Host
        self.mpCPJoin = MATShuffleButton(
            pos=(-0.5, 0, -0.45),
            text="Join",
            wantArrows=False,
            image_scale=buttonScale,
            image2_scale=buttonScale_clickhover,
            image1_scale=buttonScale_clickhover,
            text_scale=0.09,
            text2_scale=0.095,
            text1_scale=0.095,
            command=lambda: self.request('MultiplayerCPJoin')
        )
        self.mpButtons2.append(self.mpCPJoin)

        self.mpCPHost = MATShuffleButton(
            pos=(0.5, 0, -0.45),
            text="Host",
            wantArrows=False,
            image_scale=buttonScale,
            image2_scale=buttonScale_clickhover,
            image1_scale=buttonScale_clickhover,
            text_scale=0.09,
            text2_scale=0.095,
            text1_scale=0.095,
            command=lambda: self.request('MultiplayerCPHost')
        )
        self.mpButtons2.append(self.mpCPHost)

        # Multiplayer Menu Buttons: Join Menu
        self.mpCPConnect = MATShuffleButton(
            pos=(0, 0, -0.75),
            text="Connect",
            wantArrows=False,
            image_scale=buttonScale,
            image2_scale=buttonScale_clickhover,
            image1_scale=buttonScale_clickhover,
            text_scale=0.09,
            text2_scale=0.095,
            text1_scale=0.10,
            command=lambda: self.request('MultiplayerCPConnect')
        )
        self.mpButtons3.append(self.mpCPConnect)

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
            pos=(-1.65, 0, -0.935), command=lambda: self.request('Multiplayer'))

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
            pos=(-1.65, 0, -0.935), command=lambda: self.request('MultiplayerCP'))

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

        self.background.show()
        self.logo.show()
        if not base.wantMultiplayer:
            self.lockIcon.show()
        if not base.wantKaldronNetwork:
            self.lockIcon2.show()
        for button in self.buttons:
            button.show()

    def exitIdle(self):
        self.background.hide()
        for button in self.buttons:
            button.hide()
        if not base.wantMultiplayer:
            self.lockIcon.hide()
        if not base.wantKaldronNetwork:
            self.lockIcon2.hide()

    def enterSinglePlayer(self):
        self.background.show()
        self.backButton.show()
        self.quitButton.show()
        base.isSinglePlayer = True
        base.isHosting = False
        for spButton in self.spButtons:
            spButton.show()

        lockImage = TTCardMaker.makeCard('phase_3/maps/lock_icon.png')

        self.lockIcon3 = DirectButton(
            parent=aspect2d,
            relief=None,
            image=lockImage,
            image_scale=(0.00045, 0.00045, 0.00045),
            pos=(0.246, 0, -0.60),
            suppressMouse=True,
            state=DGG.DISABLED
        )
        lockImage.removeNode()

        self.spMods['state'] = DGG.DISABLED
        self.spMods.setColorScale(CGray)

        if base.wantMods:
            self.lockIcon3.destroy()
            self.spMods['state'] = DGG.NORMAL
            self.spMods.setColorScale(CDefault)

    def exitSinglePlayer(self):
        self.background.hide()
        self.backButton.hide()
        for spButton in self.spButtons:
            spButton.hide()
        if not base.wantMods:
            self.lockIcon3.hide()

    def enterSinglePlayerLocal(self):
        OTPLocalizer.SpeedChatStaticText[30500] = "I'm currently playing local play on Toontown Infinite!"
        OTPLocalizer.SpeedChatStaticText[30502] = "Are you enjoying my livestream?"
        OTPLocalizer.SpeedChatStaticText[30503] = 'Hello, viewers! Thanks for watching my livestream!'
        OTPLocalizer.SpeedChatStaticText[30506] = 'I wonder when those tunnels will open...'
        OTPLocalizer.SpeedChatStaticText[
            30512] = 'I can report bugs on the Toontown Infinite Discord server in the #bug-reports text channel.'
        self.__startGameSession(True)

    def enterMultiplayerCPHost(self):
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
        self.quitButton.show()
        base.isSinglePlayer = False
        for mpButton in self.mpButtons:
            mpButton.show()

        lockImage = TTCardMaker.makeCard('phase_3/maps/lock_icon.png')

        self.lockIcon4 = DirectButton(
            parent=aspect2d,
            relief=None,
            image=lockImage,
            image_scale=(0.00045, 0.00045, 0.00045),
            pos=(0.246, 0, -0.60),
            suppressMouse=True,
            state=DGG.DISABLED
        )
        lockImage.removeNode()

        self.mpMods['state'] = DGG.DISABLED
        self.mpMods.setColorScale(CGray)

        if base.wantMods:
            self.lockIcon4.destroy()
            self.mpMods['state'] = DGG.NORMAL
            self.mpMods.setColorScale(CDefault)

    def exitMultiplayer(self):
        self.background.hide()
        self.backButton.hide()
        for mpButton in self.mpButtons:
            mpButton.hide()
        if not base.wantMods:
            self.lockIcon4.hide()

    def enterMultiplayerCP(self):
        self.background.show()
        self.backButton2.show()
        self.quitButton.show()
        for mpButton2 in self.mpButtons2:
            mpButton2.show()

    def exitMultiplayerCP(self):
        self.background.hide()
        self.backButton2.hide()
        for mpButton2 in self.mpButtons2:
            mpButton2.hide()

    def enterMultiplayerCPJoin(self):
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

        for mpButton3 in self.mpButtons3:
            mpButton3.show()

    def exitMultiplayerCPJoin(self):
        self.background.hide()
        self.backButton3.hide()
        self.ipInput.hide()
        self.__disableIPEntry()
        for mpButton3 in self.mpButtons3:
            mpButton3.hide()

    def __submitIP(self, input=None):
        if input is None:
            input = self.ipInput.get()
        self.ipInput['focus'] = 1
        if input == '':
            return
        messenger.send('wakeup')
        self.request('MultiplayerCPConnect')

    def enterMultiplayerCPConnect(self):
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

        for spButton in self.spButtons:
            spButton.hide()

        for mpButton in self.mpButtons:
            mpButton.hide()

        for mpButton2 in self.mpButtons2:
            mpButton2.hide()

        for mpButton3 in self.mpButtons3:
            mpButton3.hide()

    def __handleQuit(self):
        cleanupDialog('globalDialog')
        base.cr.loginFSM.request('shutdown')
