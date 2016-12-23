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


class MainMenu(DirectObject, FSM):
    notify = directNotify.newCategory('MainMenu')

    def __init__(self):
        DirectObject.__init__(self)
        FSM.__init__(self, 'MainMenu')

        self.localSinglePlayerStart = None
        self.backgroundNodePath = render2d.attachNewNode('background', 0)
        self.backgroundNodePath.hide()

        self.backgroundModel = loader.loadModel('phase_3/models/gui/loading-background.bam')
        self.backgroundModel.reparentTo(self.backgroundNodePath)
        self.backgroundNodePath.find('**/fg').removeNode()
        self.backgroundNodePath.setScale(1, 1, 1)

        self.logo = OnscreenImage(
            parent=self.backgroundNodePath, 
            image='phase_3/maps/toontown-logo.png',
            scale=(0.38, 0.63, 0.33), pos=(0, 0, 0.38)
        )
        self.logo.setTransparency(TransparencyAttrib.MAlpha)

        self.buttons = []
        self.spButtons = []
        self.mpButtons = []
        self.mpButtons2 = []
        self.mpButtons3 = []

        buttonScale = (-1.1, 1.1, 1.1) # (-0.9, 0.9, 0.9)
        buttonScale2 = (-1.4, 1.5, 1.5)
        buttonScale3 = (-0.8, 0.8, 0.8)

        self.singlePlayerButton = MATShuffleButton(
            pos=(0, 0, -0.25),  # (0, 0, -0.1),
            text="Single Player",
            wantArrows=False,
            image_scale=buttonScale, 
            image2_scale=buttonScale,
            image1_scale=buttonScale, 
            text_scale=0.082, # text_scale=0.07
            command=lambda: self.request('SinglePlayer')
        )
        self.buttons.append(self.singlePlayerButton)

        self.multiPlayerButton = MATShuffleButton(
            pos=(0, 0, -0.6), 
            text="Multiplayer",
            wantArrows=False,
            image_scale=buttonScale, 
            image2_scale=buttonScale,
            image1_scale=buttonScale,
            text_scale=0.09,
            command=lambda: self.request('Multiplayer')
        )
        self.buttons.append(self.multiPlayerButton)

        self.spOnlineButton = MATShuffleButton(
            pos=(0, 0, -0.25),
            text="Kaldron\nNetwork",
            text_pos=(0,0.02,0),
            wantArrows=False,
            image_scale=buttonScale2,
            image2_scale=buttonScale2,
            image1_scale=buttonScale2,
            text_scale=0.10,
            command=lambda: self.request('')
        )
        self.spButtons.append(self.spOnlineButton)

        self.mpOnlineButton = MATShuffleButton(
            pos=(0, 0, -0.25),
            text="Kaldron\nNetwork",
            text_pos=(0,0.02,0),
            wantArrows=False,
            image_scale=buttonScale2,
            image2_scale=buttonScale2,
            image1_scale=buttonScale2,
            text_scale=0.10,
            command=lambda: self.request('')
        )
        self.mpButtons.append(self.mpOnlineButton)

        self.spLocalButton = MATShuffleButton(
            pos=(0, 0, -0.65),
            text="Local Play",
            wantArrows=False,
            image_scale=buttonScale,
            image2_scale=buttonScale,
            image1_scale=buttonScale,
            text_scale=0.09,
            command=lambda: self.request('SinglePlayerLocal')
        )
        self.spButtons.append(self.spLocalButton)

        self.mpCustomPlay = MATShuffleButton(
            pos=(0, 0, -0.65),
            text="Custom Play",
            wantArrows=False,
            image_scale=buttonScale,
            image2_scale=buttonScale,
            image1_scale=buttonScale,
            text_scale=0.082,
            command=lambda: self.request('MultiplayerCP')
        )

        self.mpButtons.append(self.mpCustomPlay)

        self.spMods = MATShuffleButton(
            pos=(0, 0, -0.87),
            text="Mods",
            wantArrows=False,
            image_scale=buttonScale3,
            image2_scale=buttonScale3,
            image1_scale=buttonScale3,
            text_scale=0.09,
            command=lambda: self.request('Mods')
        )
        self.spButtons.append(self.spMods)

        self.mpMods = MATShuffleButton(
            pos=(0, 0, -0.87),
            text="Mods",
            wantArrows=False,
            image_scale=buttonScale3,
            image2_scale=buttonScale3,
            image1_scale=buttonScale3,
            text_scale=0.09,
            command=lambda: self.request('Mods')
        )
        self.mpButtons.append(self.mpMods)

        self.mpCPJoin = MATShuffleButton(
            pos=(-0.5, 0, -0.45),
            text="Join",
            wantArrows=False,
            image_scale=buttonScale,
            image2_scale=buttonScale,
            image1_scale=buttonScale,
            text_scale=0.09,
            command=lambda: self.request('MultiplayerCPJoin')
        )
        self.mpButtons2.append(self.mpCPJoin)

        self.mpCPHost = MATShuffleButton(
            pos=(0.5, 0, -0.45),
            text="Host",
            wantArrows=False,
            image_scale=buttonScale,
            image2_scale=buttonScale,
            image1_scale=buttonScale,
            text_scale=0.09,
            command=lambda: self.request('MultiplayerCPHost')
        )
        self.mpButtons2.append(self.mpCPHost)

        self.mpCPConnect = MATShuffleButton(
            pos=(0, 0, -0.75),
            text="Connect",
            wantArrows=False,
            image_scale=buttonScale,
            image2_scale=buttonScale,
            image1_scale=buttonScale,
            text_scale=0.09,
            command=lambda: self.request('MultiplayerCPConnect')
        )
        self.mpButtons3.append(self.mpCPConnect)
        
        lockImage = TTCardMaker.makeCard('phase_3/maps/lock_icon.png')
        
        self.lockIcon = DirectButton(
            parent=aspect2d,
            relief=None,
            image=lockImage,
            image_scale=(0.0007, 0.0007, 0.0007),
            pos=(0.35, 0, -0.58),
            suppressMouse=True,
            state=DGG.DISABLED
        )
        lockImage.removeNode()

        self.lockIcon.hide()
        self.multiPlayerButton['state'] = DGG.DISABLED
        self.multiPlayerButton.setColorScale(CGray)

        if base.wantMultiplayer:
            self.lockIcon.destroy()
            self.multiPlayerButton['state'] = DGG.NORMAL
            self.multiPlayerButton.setColorScale(CDefault)

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
            pos=(-0.25, 0, 0.075), command=self.__handleQuit)
        self.quitButton.reparentTo(base.a2dBottomRight)
        self.buttons.append(self.quitButton)

        self.hide()

        gui = loader.loadModel('phase_3/models/gui/pick_a_toon_gui.bam')
        quitHover = gui.find('**/QuitBtn_RLVR')

        self.backButton = DirectButton(
            image=(quitHover, quitHover, quitHover), relief=None,
            text=TTLocalizer.OptionsGoBack,
            text_font=ToontownGlobals.getSignFont(),
            text_fg=(0.977, 0.816, 0.133, 1),
            text_pos=TTLocalizer.ACquitButtonPos,
            text_scale=TTLocalizer.ACbackButton, image_scale=1,
            image1_scale=1.05, image2_scale=1.05, scale=1.05,
            pos=(0.25, 0, 0.075), command=lambda: self.request('Idle'))

        self.backButton.hide()
        self.backButton.reparentTo(base.a2dBottomLeft)

        self.backButton2 = DirectButton(
            image=(quitHover, quitHover, quitHover), relief=None,
            text=TTLocalizer.OptionsGoBack,
            text_font=ToontownGlobals.getSignFont(),
            text_fg=(0.977, 0.816, 0.133, 1),
            text_pos=TTLocalizer.ACquitButtonPos,
            text_scale=TTLocalizer.ACbackButton, image_scale=1,
            image1_scale=1.05, image2_scale=1.05, scale=1.05,
            pos=(0.25, 0, 0.075), command=lambda: self.request('Multiplayer'))

        self.backButton2.hide()
        self.backButton2.reparentTo(base.a2dBottomLeft)

        self.backButton3 = DirectButton(
            image=(quitHover, quitHover, quitHover), relief=None,
            text=TTLocalizer.OptionsGoBack,
            text_font=ToontownGlobals.getSignFont(),
            text_fg=(0.977, 0.816, 0.133, 1),
            text_pos=TTLocalizer.ACquitButtonPos,
            text_scale=TTLocalizer.ACbackButton, image_scale=1,
            image1_scale=1.05, image2_scale=1.05, scale=1.05,
            pos=(0.25, 0, 0.075), command=lambda: self.request('MultiplayerCP'))

        self.backButton3.hide()
        self.backButton3.reparentTo(base.a2dBottomLeft)

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

        self.backgroundNodePath.show()
        if not base.wantMultiplayer:
            self.lockIcon.show()
        for button in self.buttons:
          button.show()

    def exitIdle(self):
        self.backgroundNodePath.hide()
        if not base.wantMultiplayer:
            self.lockIcon.hide()
        for button in self.buttons:
            button.hide()

    def enterSinglePlayer(self):
        self.backgroundNodePath.show()
        self.backButton.show()
        self.quitButton.show()
        base.isSinglePlayer = True
        for spButton in self.spButtons:
            spButton.show()

        lockImage = TTCardMaker.makeCard('phase_3/maps/lock_icon.png')

        self.lockIcon2 = DirectButton(
            parent=aspect2d,
            relief=None,
            image=lockImage,
            image_scale=(0.0009, 0.0009, 0.0009),
            pos=(0.44, 0, -0.23),
            suppressMouse=True,
            state=DGG.DISABLED
        )
        self.lockIcon3 = DirectButton(
            parent=aspect2d,
            relief=None,
            image=lockImage,
            image_scale=(0.00045, 0.00045, 0.00045),
            pos=(0.246, 0, -0.86),
            suppressMouse=True,
            state=DGG.DISABLED
        )
        lockImage.removeNode()

        self.spOnlineButton['state'] = DGG.DISABLED
        self.spOnlineButton.setColorScale(CGray)

        self.spMods['state'] = DGG.DISABLED
        self.spMods.setColorScale(CGray)

        if base.wantKaldronNetwork:
            self.lockIcon2.destroy()
            self.spOnlineButton['state'] = DGG.NORMAL
            self.spOnlineButton.setColorScale(CDefault)

        if base.wantMods:
            self.lockIcon3.destroy()
            self.spMods['state'] = DGG.NORMAL
            self.spMods.setColorScale(CDefault)

    def exitSinglePlayer(self):
        self.backgroundNodePath.hide()
        self.backButton.hide()
        if not base.wantKaldronNetwork:
            self.lockIcon2.hide()
        if not base.wantMods:
            self.lockIcon3.hide()
        for spButton in self.spButtons:
            spButton.hide()

    def enterSinglePlayerLocal(self):
        OTPLocalizer.SpeedChatStaticText[30500] = "I'm currently playing offline local play on Toontown Infinite!"
        OTPLocalizer.SpeedChatStaticText[30502] = "Are you enjoying my livestream?"
        OTPLocalizer.SpeedChatStaticText[30503] = 'Hello, viewers! Thanks for watching my livestream!'
        OTPLocalizer.SpeedChatStaticText[30506] = 'I wonder when those tunnels will open.'
        OTPLocalizer.SpeedChatStaticText[30512] = 'I can report bugs in the Kaldron Interactive Discord channel.'
        self.__startSinglePlayer(True)
    
    def enterMultiplayerCPHost(self):
        self.__startSinglePlayer(False)
    
    def __startSinglePlayer(self, singlePlayer):
        self.hide()
        self.backgroundNodePath.show()

        self.LocalSinglePlayerStart = LocalSinglePlayerStart(self, singlePlayer)
        self.LocalSinglePlayerStart.request('Start')

    def enterMultiplayer(self):
        self.backgroundNodePath.show()
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
            image_scale=(0.0009, 0.0009, 0.0009),
            pos=(0.44, 0, -0.23),
            suppressMouse=True,
            state=DGG.DISABLED
        )
        self.lockIcon5 = DirectButton(
            parent=aspect2d,
            relief=None,
            image=lockImage,
            image_scale=(0.00045, 0.00045, 0.00045),
            pos=(0.246, 0, -0.86),
            suppressMouse=True,
            state=DGG.DISABLED
        )
        lockImage.removeNode()

        self.mpOnlineButton['state'] = DGG.DISABLED
        self.mpOnlineButton.setColorScale(CGray)

        self.mpMods['state'] = DGG.DISABLED
        self.mpMods.setColorScale(CGray)

        if base.wantKaldronNetwork:
            self.lockIcon4.destroy()
            self.spOnlineButton['state'] = DGG.NORMAL
            self.spOnlineButton.setColorScale(CDefault)

        if base.wantMods:
            self.lockIcon5.destroy()
            self.spOnlineButton['state'] = DGG.NORMAL
            self.spOnlineButton.setColorScale(CDefault)

    def exitMultiplayer(self):
        self.backgroundNodePath.hide()
        self.backButton.hide()
        if not base.wantKaldronNetwork:
            self.lockIcon4.hide()
        if not base.wantMods:
            self.lockIcon5.hide()
        for mpButton in self.mpButtons:
            mpButton.hide()

    def enterMultiplayerCP(self):
        self.backgroundNodePath.show()
        self.backButton2.show()
        self.quitButton.show()
        for mpButton2 in self.mpButtons2:
            mpButton2.show()

    def exitMultiplayerCP(self):
        self.backgroundNodePath.hide()
        self.backButton2.hide()
        for mpButton2 in self.mpButtons2:
            mpButton2.hide()

    def enterMultiplayerCPJoin(self):
        self.backgroundNodePath.show()
        self.backButton3.show()
        self.quitButton.show()
        for mpButton3 in self.mpButtons3:
            mpButton3.show()

    def exitMultiplayerCPJoin(self):
        self.backgroundNodePath.hide()
        self.backButton3.hide()
        for mpButton3 in self.mpButtons3:
            mpButton3.hide()

    def enterOff(self):
        self.hide()

    def destroySPLocalStart(self):
        if self.localSinglePlayerStart:
            self.localSinglePlayerStart.removeNode()

    def hide(self):
        self.destroySPLocalStart()
        self.backgroundNodePath.hide()
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
        self.doneStatus = {'mode': 'exit'}
        messenger.send(self.doneEvent, [self.doneStatus])
