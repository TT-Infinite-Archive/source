from pandac.PandaModules import *
from direct.fsm.FSM import FSM
from direct.gui.DirectGui import OnscreenImage, DGG, DirectButton
from direct.showbase.DirectObject import DirectObject
from otp.otpbase import OTPLocalizer

from toontown.makeatoon.MakeAToonGUI import MATShuffleButton
from toontown.toonbase.ColorGlobals import CGray, CDefault
from toontown.toonbase import TTLocalizer, ToontownGlobals
from toontown.toontowngui.SinglePlayerMenu import SinglePlayerMenu
from toontown.util import TTCardMaker


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
        self.mpButtons = []
        self.spButtons = []
        buttonScale = (-1.1, 1.1, 1.1)  # (-0.9, 0.9, 0.9)

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

        """
        self.emptyButton = MATShuffleButton(pos=(0, 0, -0.6), text="Empty",
                                                 wantArrows=False,
                                                 image_scale=buttonScale, image2_scale=buttonScale,
                                                 image1_scale=buttonScale, text_scale=0.07,
                                                 command=lambda: self.request('Empty'))
        self.buttons.append(self.emptyButton)

        self.emptyButton = MATShuffleButton(pos=(0, 0, -0.85), text="Empty",
                                              wantArrows=False,
                                              image_scale=buttonScale, image2_scale=buttonScale,
                                              image1_scale=buttonScale, text_scale=0.07)
        self.buttons.append(self.emptyButton)
        """

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
        OTPLocalizer.SpeedChatStaticText[30500] = 'Welcome to Toontown Infinite!'

        self.hide()
        self.backgroundNodePath.show()

        self.singlePlayerMenu = SinglePlayerMenu(self)
        self.singlePlayerMenu.request('Start')

    """
    def enterEmptyButton(self):
        self.backgroundNodePath.show()
        for emButton in self.empButtons:
            emButton.show()

    def exitEmptyButton(self):
        self.backgroundNodePath.hide()
        for emButton in self.emButtons:
            emButton.hide()

    def enterEmpty(self):
        base.cr.loginFSM.request('chooseAvatar', [base.cr.avList])

    def exitEmpty(self):
        pass

    def enterEmpty(self):
        pass
    """

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

        for mpButton in self.mpButtons:
            mpButton.hide()

    def __handleQuit(self):
        cleanupDialog('globalDialog')
        self.doneStatus = {'mode': 'exit'}
        messenger.send(self.doneEvent, [self.doneStatus])
