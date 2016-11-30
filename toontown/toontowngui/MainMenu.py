from direct.fsm.FSM import FSM
from direct.showbase.DirectObject import DirectObject
from otp.otpbase import OTPLocalizer

from toontown.makeatoon.MakeAToonGUI import MATShuffleButton
from toontown.toonbase.ColorGlobals import CGray, CDefault
from toontown.toontowngui.SinglePlayerMenu import SinglePlayerMenu
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

        self.singlePlayerMenu = None
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

        buttonScale = (-1.1, 1.1, 1.1)
        buttonScale2 = (-1.4, 1.5, 1.5)# (-0.9, 0.9, 0.9)

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
            command=lambda: self.request('MultiPlayer')
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
            command=lambda: self.request('MultiPlayer')
        )

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
        self.spButtons.append(self.spOnlineButton)
        self.spButtons.append(self.spLocalButton)
        
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
        lockImage.removeNode()

        self.spOnlineButton['state'] = DGG.DISABLED
        self.spOnlineButton.setColorScale(CGray)

        if base.wantKaldronNetwork:
            self.lockIcon.destroy()
            self.spOnlineButton['state'] = DGG.NORMAL
            self.spOnlineButton.setColorScale(CDefault)

    def exitSinglePlayer(self):
        self.backgroundNodePath.hide()
        self.backButton.hide()
        if not base.wantKaldronNetwork:
            self.lockIcon2.hide()
        for spButton in self.spButtons:
            spButton.hide()

    def enterSinglePlayerLocal(self):

        OTPLocalizer.SpeedChatStaticText[30500] = 'Welcome to Toontown Infinite!'
        OTPLocalizer.SpeedChatStaticText[30506] = 'I wonder when those tunnels will open.'
        OTPLocalizer.SpeedChatStaticText[30512] = 'I can report bugs in the Kaldron Interactive Discord channel.'

        self.hide()
        self.backgroundNodePath.show()

        self.singlePlayerMenu = SinglePlayerMenu(self)
        self.singlePlayerMenu.request('Start')

    def enterOff(self):
        self.hide()

    def destroySPMenu(self):
        if self.singlePlayerMenu:
            self.singlePlayerMenu.removeNode()
            self.singlePlayerMenu = None

    def hide(self):
        self.destroySPMenu()
        self.backgroundNodePath.hide()
        for button in self.buttons:
            button.hide()

        for spButton in self.spButtons:
            spButton.hide()

        for mpButton in self.mpButtons:
            mpButton.hide()

    def __handleQuit(self):
        cleanupDialog('globalDialog')
        self.doneStatus = {'mode': 'exit'}
        messenger.send(self.doneEvent, [self.doneStatus])
