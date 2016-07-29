from direct.fsm.FSM import FSM
from direct.gui.DirectGui import OnscreenImage, OnscreenText, DirectButton
from direct.showbase.DirectObject import DirectObject
from direct.interval.IntervalGlobal import *
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import TTLocalizer
from panda3d.core import Vec3, Vec4
from toontown.battle import BattleParticles
from direct.interval.IntervalGlobal import *
from panda3d.core import Point3
from direct.actor.Actor import Actor

class BossyBusinessMenu(DirectObject, FSM):
    def __init__(self):
        self.bgm = None
        self.title = None
        self.sceneNp = None
        #self.sellbotHQ = None
        self.cashbotHQ = None
        self.vaultLobby = None
        self.midVault = None
        self.endVault = None
        #self.lawbotHQ = None
        #self.bossbotHQ = None
        self.skyBoxLoop = None
        self.rain = None
        self.rainRender = None

    def load(self):
        self.sceneNp = render.attachNewNode('BossyBusinessBackground')

        # Sellbot HQ
        #self.sellbotHQ = loader.loadModel('phase_9/models/cogHQ/SellbotHQExterior.bam')

        # Cashbot HQ
        self.cashbotHQ = loader.loadModel('phase_10/models/cogHQ/CashBotShippingStation.bam')
        self.vaultLobby = loader.loadModel('phase_10/models/cogHQ/VaultLobby.bam')
        self.midVault = loader.loadModel('phase_10/models/cogHQ/MidVault.bam')
        self.endVault = loader.loadModel('phase_10/models/cogHQ/EndVault.bam')

        # Lawbot HQ
        #self.lawbotbotHQ = loader.loadModel('phase_12/models/bossbotHQ/CogGolfCourtyard.bam')

        # Bossbot HQ
        #self.bossbotHQ = loader.loadModel('phase_12/models/bossbotHQ/CogGolfCourtyard.bam')
        #self.fieldOffice = loader.loadModel('phase_5/models/cogdominium/tt_m_ara_crg_penthouse.bam')

        self.bgm = loader.loadMusic('phase_7/audio/bgm/bossy_business_menu_bgm.ogg')

        # Sellbot HQ, Bossbot HQ ONLY
        self.wind = loader.loadSfx('phase_9/audio/sfx/CHQ_FACT_whistling_wind.ogg')

        self.title = OnscreenText(text="Bossy Business", scale=0.2, font=ToontownGlobals.getSuitFont(),
                                  pos=(0.0, 0.0, 1.0), fg=Vec4(1, 1, 1, 1))
        self.title.hide()

        gui = loader.loadModel('phase_3/models/gui/pick_a_toon_gui.bam')
        quitHover = gui.find('**/QuitBtn_RLVR')
        self.backButton = DirectButton(
            image=(quitHover, quitHover, quitHover), relief=None,
            text=TTLocalizer.OptionsGoBack,
            text_font=ToontownGlobals.getSignFont(),
            text_fg=(0.977, 0.816, 0.133, 1),
            text_scale=TTLocalizer.AClogoutButton, text_pos=(0, -0.035),
            pos=(0.15, 0, 0.05), image_scale=1.15, image1_scale=1.15,
            image2_scale=1.18, scale=0.5,
            command=lambda: base.mainMenu.request('Idle'))
        self.backButton.reparentTo(base.a2dBottomLeft)

        # Actors
        self.cfo = Actor({"head": "phase_10/models/char/cashbotBoss-head-zero.bam",
                          "torso": "phase_10/models/char/cashbotBoss-torso-zero.bam",
                          "legs": "phase_9/models/char/bossCog-legs-zero.bam"},
                         # Animations
                         {"head": {"walk": "phase_9/models/char/bossCog-head-Bb_neutral.bam",
                                   "run": "phase_9/models/char/bossCog-head-Bb_neutral.bam"},
                          "torso": {"walk": "phase_9/models/char/bossCog-torso-Bb_neutral.bam",
                                    "run": "phase_9/models/char/bossCog-torso-Bb_neutral.bam"},
                          "legs": {"walk": "phase_9/models/char/bossCog-legs-Bb_neutral.bam",
                                   "run": "phase_9/models/char/bossCog-legs-Bb_neutral.bam"}
                          })

        self.cfo.attach("head", "torso", "joint34")
        self.cfo.attach("torso", "legs", "joint_legs")
        self.cfo.reparentTo(render)
        tread = loader.loadModel("phase_9/models/char/bossCog-treads.bam")
        rear = self.cfo.find('**/joint_axle')
        tread.reparentTo(rear)
        self.cfo.setPos(119.63, -229.80, 0)
        self.cfo.loop("walk")
        self.cfo.setHpr(270, 0, 0)

        # Attemping to close his front and rear doors, but no luck
        # self.cfo.find('**/joint_doorFront').setHpr(0, 0, -80)
        # self.cfo.find('**/joint_doorRear').setHpr(0, 0, -80)

        # Sellbot Boss Camera Angles
        # base.camera.setPos(-75.95, -218.55, 2.02)
        # base.camera.setHpr(336.80, 9.46, 0)

        # Cashbot C.F.O. Scene
        # Selecting the Cashbot Vault will begin playing this scene
        base.camera.setHpr(349.70, 12.09, 0)

        # Vault Lobby Entrance
        cashbotCamInterval = base.camera.posInterval(20,
                                                     Point3(93.84, 348.56, 39.96),
                                                     startPos=Point3(85.95, 140.59, -16.40))

        # Vault Lobby Interior
        cashbotCamInterval2 = base.camera.posInterval(20,
                                                     Point3(116.34, -30.19, 91.26),
                                                     startPos=Point3(116.34, -214.43, 39.86))

        # MidVault
        cashbotCamInterval3 = base.camera.posInterval(25,
                                                     Point3(84.21, -225.84, 18.07),
                                                     startPos=Point3(55.89, -224.37, 12.97))

        # MidVault2
        cashbotCamInterval4 = base.camera.posInterval(20,
                                                     Point3(101.38, -202.19, 17.17),
                                                     startPos=Point3(102.04, -204.08, 2.98))

        # EndVault
        cashbotCamInterval5 = base.camera.posInterval(25,
                                                      Point3(108.54, -291.60, 21.88),
                                                      startPos=Point3(57.65, -269.95, 30.75)) #hpr 232.82 348.69 0

        # EndVault2
        cashbotCamInterval6 = base.camera.posInterval(30,
                                                      Point3(101.09, -344.12, 5.58),
                                                      startPos=Point3(116.51,-363.15, 5.58)) #hpr 321.01 2.76 0

        # Movie
        self.vaultLobby.hide()
        self.midVault.hide()
        self.endVault.hide()
        self.cfo.hide()
        self.midVault.setPos(0, -222, -70.7)
        self.endVault.setPos(84, -201, -6)
        self.cashCamPace = Sequence(Func(base.transitions.fadeIn), # <--- This transition currently doesn't work until the first loop occurs
                                    cashbotCamInterval, Func(base.transitions.fadeOut), Wait(1),
                                    Parallel(
                                        Func(base.transitions.fadeIn),
                                        Func(base.camera.setHpr, (0, 8.13, 0)),
                                        Func(self.cashbotHQ.hide),
                                        Func(self.vaultLobby.show)),
                                    cashbotCamInterval2, Func(base.transitions.fadeOut), Wait(1),
                                    Parallel(
                                        Func(base.transitions.fadeIn),
                                        Func(self.midVault.show),
                                        Func(self.vaultLobby.hide),
                                        Func(self.cfo.show),
                                        Func(base.camera.setHpr, (260.54, 0, 0))),
                                    cashbotCamInterval3, Func(base.transitions.fadeOut), Wait(1),
                                    Parallel(
                                        Func(base.transitions.fadeIn),
                                        Func(base.camera.setHpr, (206.57, 0, 0))),
                                    cashbotCamInterval4, Func(base.transitions.fadeOut), Wait(1),
                                    Parallel(
                                        Func(base.transitions.fadeIn),
                                        Func(self.cfo.hide),
                                        Func(self.midVault.hide),
                                        Func(self.endVault.show),
                                        Func(base.camera.setHpr, (232.82, 348.69, 0))),
                                    cashbotCamInterval5, Func(base.transitions.fadeOut), Wait(1),
                                    Parallel(
                                        Func(base.transitions.fadeIn),
                                        Func(base.camera.setHpr, (321.01, 2.76, 0))),
                                    cashbotCamInterval6, Func(base.transitions.fadeOut), Wait(1),
                                    Parallel(
                                        Func(self.endVault.hide),
                                        Func(self.cashbotHQ.show),
                                        Func(base.camera.setHpr, (349.70, 12.09, 0))),
                                    name="cashCamPace")
        self.cashCamPace.loop()
        # END

    def startRain(self):
        self.rain = BattleParticles.loadParticleFile('raindisk.ptf')
        self.rain.setPos(0, 0, 20)
        self.rainRender = render.attachNewNode('rainRender')
        self.rainRender.setDepthWrite(0)
        self.rainRender.setBin('fixed', 1)
        self.rain.start(camera, self.rainRender)

    def stopRain(self):
        if self.rain:
            self.rain.cleanup()

    def unload(self):
        del self.rain
        del self.rainRender

    def exit(self):
        self.stopRain()

    def show(self):
        #self.sellbotHQ.reparentTo(self.sceneNp)
        self.cashbotHQ.reparentTo(self.sceneNp)
        self.vaultLobby.reparentTo(self.sceneNp)
        self.midVault.reparentTo(self.sceneNp)
        self.endVault.reparentTo(self.sceneNp)
        #self.bossbotHQ.reparentTo(self.sceneNp)
        self.title.show()

        #skyBox = self.bossbotHQ.find("**/*SkyBox")
        #self.skyBoxLoop = skyBox.hprInterval(200, Vec3(360, 0, 0))
        #self.skyBoxLoop.loop()

        Sequence(
            Func(base.transitions.fadeIn),
            LerpPosInterval(nodePath=self.title, duration=2.4, pos=(0.0, 0.0, 0.7))
        ).start()
        self.bgm.setLoop(1)
        self.bgm.play()
        self.wind.setVolume(0.5)
        self.wind.setLoop(1)
        self.wind.play()
        self.startRain()

    def hide(self):
        pass

    """
    # Field Office Scene

    base.camera.setHpr(80.91, 0, 0)
    mainCamInterval = base.camera.posInterval(20,
                                              Point3(-4.90, -1.79, 5.20),
                                              startPos=Point3(18.38, -4.82, 6.51))

    mainCamInterval2 = base.camera.posInterval(25,
                                                  Point3(-2.18, -2.16, 3.56),
                                                  startPos=Point3(-2.18, 18.67, 3.56))
    # Movie
    self.mainCamPace = Sequence(Func(base.transitions.fadeIn, 3),
                                mainCamInterval, Func(base.transitions.fadeOut), Wait(3),
                                Parallel
                                (Func(base.transitions.fadeIn),
                                    mainCamInterval2,
                                    Func(base.camera.setHpr, (315, 0, 0))), Wait(3),
                                Func(base.camera.setHpr, (80.91, 0, 0)),
                                name="mainCamPace")
    self.mainCamPace.loop()
    # END
    """