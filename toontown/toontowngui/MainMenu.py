from direct.fsm.FSM import FSM
from direct.gui.DirectGui import OnscreenImage, OnscreenText, DirectButton
from direct.showbase.DirectObject import DirectObject
from panda3d.core import TransparencyAttrib, Point3, Vec4, Vec3, TextNode
from toontown.toonbase import ToontownGlobals
from toontown.makeatoon.MakeAToonGUI import MATShuffleButton
from otp.otpbase import OTPLocalizer
from toontown.toonbase import TTLocalizer
from toontown.toontowngui.BossyBusinessMenu import BossyBusinessMenu
from direct.interval.IntervalGlobal import *


class MainMenu(DirectObject, FSM):
    notify = directNotify.newCategory('MainMenu')

    def __init__(self):
        DirectObject.__init__(self)
        FSM.__init__(self, 'MainMenu')

        self.backgroundNodePath = render2d.attachNewNode('background', 0)
        self.backgroundNodePath.hide()

        self.backgroundModel = loader.loadModel('phase_3/models/gui/loading-background.bam')
        self.backgroundModel.reparentTo(self.backgroundNodePath)
        self.backgroundNodePath.find('**/fg').removeNode()
        self.backgroundNodePath.setScale(1, 1, 1)

        self.logo = OnscreenImage(
            parent=self.backgroundNodePath, image='phase_3/maps/toontown-logo.png',
            scale=(0.35, 0.60, 0.30), pos=(0, 0, 0.4))
        self.logo.setTransparency(TransparencyAttrib.MAlpha)

        self.buttons = []
        self.mpButtons = []
        self.spButtons = []
        self.optionButtons = []
        buttonScale = (-1.1, 1.1, 1.1)

        self.singlePlayerButton = MATShuffleButton(pos=(0, 0, -0.3),
                                                   text="Single Player",
                                                   wantArrows=False,
                                                   image_scale=buttonScale, image2_scale=buttonScale,
                                                   image1_scale=buttonScale, text_scale=0.09,
                                                   command=lambda: self.request('SinglePlayer'))
        self.buttons.append(self.singlePlayerButton)

        """
        self.multiPlayerButton = MATShuffleButton(pos=(0, 0, -0.35), text="Multiplayer",
                                                  wantArrows=False,
                                                  image_scale=buttonScale, image2_scale=buttonScale,
                                                  image1_scale=buttonScale, text_scale=0.07,
                                                  command=lambda: self.request('MultiPlayer'))
        self.buttons.append(self.multiPlayerButton)


        if config.GetBool('want-multiplayer', True):
            self.bossyBusinessButton = MATShuffleButton(pos=(0, 0, -0.35), text="Bossy Business",
                                                      wantArrows=False,
                                                      image_scale=buttonScale, image2_scale=buttonScale,
                                                      image1_scale=buttonScale, text_scale=0.06,
                                                      command=lambda : self.request('BossyBusiness'))
            self.bossyBusinessButton.setScale(1.5)

            self.bossyBusinessMenu = BossyBusinessMenu()

            self.mpButtons.append(self.bossyBusinessButton)

        self.charSelectButton = MATShuffleButton(pos=(0, 0, -0.6), text="Toon Select",
                                                 wantArrows=False,
                                                 image_scale=buttonScale, image2_scale=buttonScale,
                                                 image1_scale=buttonScale, text_scale=0.07,
                                                 command=lambda: self.request('CharSelect'))
        self.buttons.append(self.charSelectButton)

        self.optionsButton = MATShuffleButton(pos=(0, 0, -0.85), text="Options",
                                              wantArrows=False,
                                              image_scale=buttonScale, image2_scale=buttonScale,
                                              image1_scale=buttonScale, text_scale=0.07)
        self.buttons.append(self.optionsButton)
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
        self.backgroundNodePath.show()
        for button in self.buttons:
          button.show()

    def exitIdle(self):
        self.backgroundNodePath.hide()
        for button in self.buttons:
            button.hide()

    def enterSinglePlayer(self):
        OTPLocalizer.SpeedChatStaticText[30500] = 'Welcome to Toontown Infinite!'
        base.connectToServer('localhost')

    """
    def enterMultiPlayer(self):
        self.backgroundNodePath.show()
        for mpButton in self.mpButtons:
            mpButton.show()

    def exitMultiPlayer(self):
        self.backgroundNodePath.hide()
        for mpButton in self.mpButtons:
            mpButton.hide()

    def enterBossyBusiness(self):
        base.transitions.fadeOut()
        self.bossyBusinessMenu.load()
        self.bossyBusinessMenu.show()

    def enterCharSelect(self):
        base.cr.loginFSM.request('chooseAvatar', [base.cr.avList])

    def exitCharSelect(self):
        pass

    def enterOptions(self):
        pass
    """

    def enterOff(self):
        self.hide()

    def hide(self):
        self.backgroundNodePath.hide()
        for button in self.buttons:
            button.hide()

        for mpButton in self.mpButtons:
            mpButton.hide()

    def __handleQuit(self):
        cleanupDialog('globalDialog')
        self.doneStatus = {'mode': 'exit'}
        messenger.send(self.doneEvent, [self.doneStatus])
