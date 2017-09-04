import random

from direct.fsm.FSM import FSM
from direct.gui.DirectGui import *
from direct.interval.FunctionInterval import Func, Wait
from direct.interval.IntervalGlobal import LerpScaleInterval
from direct.interval.MetaInterval import Parallel
from direct.interval.MetaInterval import Sequence
from direct.task.Task import Task
from pandac.PandaModules import *

from toontown.mainmenu import MainMenuGlobals
from toontown.mainmenu.HomeScreen import HomeScreen
from toontown.mainmenu.HostScreen import HostScreen
from toontown.mainmenu.HostStartScreen import HostStartScreen
from toontown.mainmenu.JoinScreen import JoinScreen
from toontown.mainmenu.LoginOrSignUpScreen import LoginOrSignUpScreen
from toontown.mainmenu.LoginScreen import LoginScreen
from toontown.mainmenu.PlayScreen import PlayScreen
from toontown.mainmenu.SignUpScreen import SignUpScreen
from toontown.makeatoon.MakeAToonGUI import MATShuffleButton
from toontown.shtiker.OptionsTabPage import OptionsTabPage
from toontown.suit.Suit import Suit
from toontown.suit.SuitDNA import SuitDNA
from toontown.toon.Toon import Toon
from toontown.toon.ToonDNA import ToonDNA
from toontown.toonbase import ServerSettingsGlobals
from toontown.util.PlacerTool3D import PlacerTool3D
from toontown.toonbase import ToontownGlobals


class MainMenu(DirectFrame, FSM):
    notify = directNotify.newCategory('MainMenu')

    def __init__(self):
        DirectFrame.__init__(self, parent=base.aspect2d)
        FSM.__init__(self, 'MainMenu')

        self.loginOrSignUpScreen = LoginOrSignUpScreen(self)
        self.loginOrSignUpScreen.hide()
        self.loginScreen = LoginScreen(self)
        self.loginScreen.hide()
        self.signUpScreen = SignUpScreen(self)
        self.signUpScreen.hide()
        self.homeScreen = HomeScreen(self)
        self.homeScreen.hide()
        self.playScreen = PlayScreen(self)
        self.playScreen.hide()
        self.hostScreen = HostScreen(self)
        self.hostScreen.hide()
        self.joinScreen = JoinScreen(self)
        self.joinScreen.hide()
        self.optionsScreen = OptionsTabPage()
        self.optionsScreen.hide()
        self.hostStartScreen = HostStartScreen(self)
        self.hostStartScreen.hide()

        self.mainMenuElements = []
        self.createRandomSuitSequence = None
        self.createRandomSuitSequence2 = None
        self.createRandomSuitSequence3 = None

        if ToontownGlobals.HALLOWEEN_PROPS in base.clientHolidayIdList:
            ToontownGlobals.getNametagFont(10)
        else:
            ToontownGlobals.getMinnieFont()

        self.background = OnscreenImage(
            parent=render2d, image='phase_3/maps/menu_bg_clouds.jpg', pos=(0, 0, 0))
        self.background.setBin('background', 0)
        self.background.setScale(render2d, Vec3(1))
        self.mainMenuElements.append(self.background)

        self.logo = OnscreenImage(
            parent=base.a2dTopCenter,
            image='phase_3/maps/toontown_infinite_logo.png',
            scale=(0.8, 0.35, 0.45), pos=(0, 0, -0.6)
        )
        self.logo.setTransparency(TransparencyAttrib.MAlpha)
        self.mainMenuElements.append(self.logo)

        self.logoScaleTrack = Sequence(
            LerpScaleInterval(self.logo, 4, Vec3(0.725, 0.35, 0.40), Vec3(0.70, 0.35, 0.385),
                              blendType='easeInOut'),
            LerpScaleInterval(self.logo, 4, Vec3(0.70, 0.35, 0.385), Vec3(0.725, 0.35, 0.40),
                              blendType='easeInOut')
        )
        self.logoScaleTrack.loop()
        self.bottomLeftButton = MATShuffleButton(
            parent=base.a2dBottomLeft,
            pos=(0.4, 0, 0.2),
            text="Options",
            **MainMenuGlobals.BUTTON_PROPERTIES_2
        )
        self.mainMenuElements.append(self.bottomLeftButton)

        self.quitButton = MATShuffleButton(
            parent=base.a2dBottomRight,
            pos=(-0.4, 0, .2),
            text="Quit",
            command=self.__handleQuit,
            **MainMenuGlobals.BUTTON_PROPERTIES_2
        )
        self.mainMenuElements.append(self.quitButton)

        for elements in self.mainMenuElements:
            elements.hide()

        self.environment = NodePath('mainMenu-environment')
        self.environment.reparentTo(hidden)

        self.flyDownSfx = loader.loadSfx('phase_5/audio/sfx/ENC_propeller_in.ogg')
        self.flyDownSfx.setVolume(0)

    def destroy(self):
        if self.createRandomSuitSequence is not None:
            self.createRandomSuitSequence.finish()
            self.createRandomSuitSequence = None
        if self.createRandomSuitSequence2 is not None:
            self.createRandomSuitSequence2.finish()
            self.createRandomSuitSequence2 = None
        if self.createRandomSuitSequence3 is not None:
            self.createRandomSuitSequence3.finish()
            self.createRandomSuitSequence3 = None
        if self.logoScaleTrack is not None:
            self.logoScaleTrack.finish()
            self.logoScaleTrack = None
        self.environment.removeNode()
        self.hostScreen.destroyAvScreen()
        self.joinScreen.destroy()
        base.camLens.setMinFov(ToontownGlobals.DefaultCameraFov/(4./3.))
        for element in self.mainMenuElements:
            element.destroy()
        DirectFrame.destroy(self)

    def load(self):
        self.loadArea()
        self.initializeRandomActors()
        self.initializeSky()

    def loadArea(self):
        self.loopyLane = loader.loadModel('phase_4/models/neighborhoods/toontown_central_2200')
        self.loopyLane.setPosHpr(34, -12, 0, 5, 0, 0)
        self.loopyLane.reparentTo(self.environment)
        self.loopyLane.find('**/door_double_curved_ur_flat').removeNode()

    def initializeRandomActors(self):
        self.randomToon = Toon()
        self.toonDNA = ToonDNA()
        self.toonDNA.newToonRandom(gender=random.choice(('m', 'f')))
        self.randomToon.setDNA(self.toonDNA)
        self.randomToon.reparentTo(self.environment)
        self.randomToon.setPosHpr(-444, -107, 0.025, 52, 0, 0)
        self.randomToon.useLOD(1000)

        self.randomToon2 = Toon()
        self.toonDNA2 = ToonDNA()
        self.toonDNA2.newToonRandom(gender=random.choice(('m', 'f')))
        self.randomToon2.setDNA(self.toonDNA2)
        self.randomToon2.reparentTo(self.environment)
        self.randomToon2.setPosHpr(-329, -200.5, 0.025, 95, 0, 0)
        self.randomToon2.useLOD(1000)

        self.randomToon.play('bored')
        self.randomToon2.play('bored')
        self.randomToon.setBlend(frameBlend = settings['animation-smoothing'])
        self.randomToon2.setBlend(frameBlend = settings['animation-smoothing'])

        self.createRandomSuitSequence = Sequence(
            Func(self.createRandomSuit),
            Wait(40),
            Func(self.killRandomSuit)
        )
        self.createRandomSuitSequence.loop()

        self.createRandomSuitSequence2 = Sequence(
            Func(self.createRandomSuit2),
            Wait(63),
            Func(self.killRandomSuit2)
        )
        self.createRandomSuitSequence2.loop()

        self.createRandomSuitSequence3 = Sequence(
            Func(self.createRandomSuit3),
            Wait(73),
            Func(self.killRandomSuit3)
        )
        self.createRandomSuitSequence3.loop()

    def createRandomSuit(self):
        self.randomSuit = Suit()
        self.suitDNA = SuitDNA()
        self.suitDNA.newSuitRandom()
        self.randomSuit.setDNA(self.suitDNA)
        self.randomSuit.reparentTo(self.environment)
        self.randomSuit.setDisplayName('')
        self.randomSuit.setPickable(0)
        self.randomSuit.setH(90)
        self.randomSuit.loop('walk')

        self.landingSuitPosInterval = self.randomSuit.posInterval(
            1, (-417.5, -129, 3), startPos=(-417.5, -129, 10)
        )

        self.landingSuitPosInterval2 = self.randomSuit.posInterval(
            1, (-417.5, -129, -0.475), startPos=(-417.5, -129, 3)
        )

        self.landingSuitPosInterval3 = self.randomSuit.posInterval(
            8, (-447.5, -129, -0.47), startPos=(-417.5, -129, -0.475)
        )

        self.landingSuitInterval = Sequence(
            Parallel(
                Func(self.flyDownSfx.play),
                Wait(1),
                Func(self.randomSuit.pose, 'landing', 0),
                self.landingSuitPosInterval),
            Parallel(
                Func(self.randomSuit.play, 'landing'),
                self.landingSuitPosInterval2),
            Wait(2.2),
             Parallel(
                Func(self.randomSuit.loop, 'walk'),
                self.landingSuitPosInterval3),
        )
        self.landingSuitInterval.start()

    def createRandomSuit2(self):
        self.randomSuit2 = Suit()
        self.suitDNA2 = SuitDNA()
        self.suitDNA2.newSuitRandom()
        self.randomSuit2.setDNA(self.suitDNA2)
        self.randomSuit2.reparentTo(self.environment)
        self.randomSuit2.setPos(-344, -159, -0.475)
        self.randomSuit2.setDisplayName('')
        self.randomSuit2.setPickable(0)
        self.randomSuit2.setH(190)
        self.randomSuit2.loop('walk')

        self.suitPosInterval = self.randomSuit2.posInterval(
            16, (-348, -212, -0.475), startPos=(-348, -159, -0.475)
        )

        self.suitHprInterval = self.randomSuit2.hprInterval(
            0.5, (90, 0, 0), startHpr=(190, 0, 0)
        )

        self.suitPosInterval2 = self.randomSuit2.posInterval(
            16, (-404, -215, -0.475), startPos=(-348, -212, -0.475)
        )

        self.suitHprInterval2 = self.randomSuit2.hprInterval(
            0.5, (0, 0, 0), startHpr=(90, 0, 0)
        )

        self.suitPosInterval3 = self.randomSuit2.posInterval(
            22, (-413.5, -129, -0.475), startPos=(-404, -215, -0.475)
        )

        self.suitHprInterval3 = self.randomSuit2.hprInterval(
            0.5, (90, 0, 0), startHpr=(0, 0, 0)
        )

        self.suitPosInterval4 = self.randomSuit2.posInterval(
            8, (-447.5, -129, -0.47), startPos=(-413.5, -129, -0.475)
        )

        self.suitInterval2 = Sequence(
            self.suitPosInterval,
            Parallel(
                self.suitHprInterval,
                self.suitPosInterval2),
            Parallel(
                self.suitHprInterval2,
                self.suitPosInterval3),
            Parallel(
                self.suitHprInterval3,
                self.suitPosInterval4)
        )
        self.suitInterval2.start()
        # from toontown.util.PlacerTool3D import PlacerTool3D
        # PlacerTool3D(self.randomSuit2, increment=1)
        # self.randomSuit2.setPosHpr(-404, -219, -0.475, 90, 0, 0)

    def createRandomSuit3(self):
        self.randomSuit3 = Suit()
        self.suitDNA3 = SuitDNA()
        self.suitDNA3.newSuitRandom()
        self.randomSuit3.setDNA(self.suitDNA3)
        self.randomSuit3.reparentTo(self.environment)
        self.randomSuit3.setPos(-344, -159, -0.475)
        self.randomSuit3.setDisplayName('')
        self.randomSuit3.setPickable(0)
        self.randomSuit3.setH(190)
        self.randomSuit3.loop('walk')

        self.suitPosInterval = self.randomSuit3.posInterval(
            16, (-348, -212, -0.475), startPos=(-348, -159, -0.475)
        )

        self.suitHprInterval = self.randomSuit3.hprInterval(
            0.5, (90, 0, 0), startHpr=(190, 0, 0)
        )

        self.suitPosInterval2 = self.randomSuit3.posInterval(
            16, (-404, -215, -0.475), startPos=(-348, -212, -0.475)
        )

        self.suitHprInterval2 = self.randomSuit3.hprInterval(
            0.5, (0, 0, 0), startHpr=(90, 0, 0)
        )

        self.suitPosInterval3 = self.randomSuit3.posInterval(
            22, (-413.5, -129, -0.475), startPos=(-404, -215, -0.475)
        )

        self.suitHprInterval3 = self.randomSuit3.hprInterval(
            0.5, (90, 0, 0), startHpr=(0, 0, 0)
        )

        self.suitPosInterval4 = self.randomSuit3.posInterval(
            8, (-447.5, -129, -0.47), startPos=(-413.5, -129, -0.475)
        )

        self.suitInterval3 = Sequence(
            Wait(10),
            self.suitPosInterval,
            Parallel(
                self.suitHprInterval,
                self.suitPosInterval2),
            Parallel(
                self.suitHprInterval2,
                self.suitPosInterval3),
            Parallel(
                self.suitHprInterval3,
                self.suitPosInterval4)
        )
        self.suitInterval3.start()

    def killRandomSuit(self):
        self.randomSuit.cleanup()
        self.randomSuit.removeNode()

    def killRandomSuit2(self):
        self.randomSuit2.cleanup()
        self.randomSuit2.removeNode()

    def killRandomSuit3(self):
        self.randomSuit3.cleanup()
        self.randomSuit3.removeNode()

    def initializeSky(self):
        def cloudSkyTrack(task):
            task.h += globalClock.getDt() * 0.25
            if task.cloud1.isEmpty() or task.cloud2.isEmpty():
                notify.warning("Couldn't find clouds!")
                return task.done

            task.cloud1.setH(task.h)
            task.cloud2.setH(-task.h * 0.8)
            return task.cont

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
        self.sky.reparentTo(self.environment)
        self.sky.setPos(-444, -107, 0)
        ce = CompassEffect.make(NodePath(), effects)
        self.sky.node().setEffect(ce)

        self.skyTrackTask = Task(cloudSkyTrack)
        self.skyTrackTask.h = 0
        self.skyTrackTask.cloud1 = self.sky.find('**/cloud1')
        self.skyTrackTask.cloud2 = self.sky.find('**/cloud2')

        if not self.skyTrackTask.cloud1.isEmpty() and not self.skyTrackTask.cloud2.isEmpty():
            taskMgr.add(self.skyTrackTask, 'skyTrack')

    def enterOff(self):
        if self.optionsScreen is not None:
            self.optionsScreen.unload()
            self.optionsScreen = None

    def exitOff(self):
        base.camera.setPosHpr(-454.5, -96, 2.7, 215, 0, 0)
        base.camLens.setFov(30)

    def enterLoginOrSignUpScreen(self):
        self.show()
        self.loginOrSignUpScreen.show()

        for element in self.mainMenuElements:
            element.show()

        self.bottomLeftButton['command'] = lambda: self.request('Options')
        self.bottomLeftButton['text'] = "Options"

        if (base.cr.music is None) and base.musicManagerIsValid:
            base.cr.music = base.musicManager.getSound('phase_3/audio/bgm/tti_main_menu_theme.ogg')
            if base.cr.music is not None:
                base.cr.music.setLoop(1)
                base.cr.music.setVolume(0.9)
                base.cr.music.play()

    def exitLoginOrSignUpScreen(self):
        self.loginOrSignUpScreen.hide()

    def enterLoginScreen(self):
        self.loginScreen.show()
        self.bottomLeftButton['command'] = lambda: self.request('LoginOrSignUpScreen')
        self.bottomLeftButton['text'] = "Back"

    def exitLoginScreen(self):
        self.loginScreen.hide()

    def enterSignUpScreen(self):
        self.signUpScreen.show()
        self.logo.hide()
        self.bottomLeftButton['command'] = lambda: self.request('LoginOrSignUpScreen')
        self.bottomLeftButton['text'] = "Back"

    def exitSignUpScreen(self):
        self.signUpScreen.hide()
        self.logo.show()

    def enterHomeScreen(self):
        self.homeScreen.show()
        self.playScreen.hide()
        self.flyDownSfx.setVolume(0)
        self.environment.reparentTo(hidden)

        for elements in self.mainMenuElements:
            elements.show()

        self.bottomLeftButton['command'] = lambda: self.request('Options2')
        self.bottomLeftButton['text'] = "Options"

    def exitHomeScreen(self):
        self.homeScreen.hide()

        for elements in self.mainMenuElements:
            elements.hide()

    def enterPlayScreen(self):
        self.playScreen.enter()
        self.playScreen.show()
        self.flyDownSfx.setVolume(1)

        for element in self.mainMenuElements:
            element.hide()

        self.environment.reparentTo(render)

        Sequence(
                 Func(self.randomToon.play, 'wave'),
                 Wait(self.randomToon.getDuration('wave')),
                 Func(self.randomToon.play, 'bored'),
                 Wait(2.9),
                 Func(self.randomToon.pingpong, 'bored', fromFrame = 70, toFrame = 130)
                 ).start()
        
        self.randomToon2.pingpong('bored', fromFrame=70, toFrame=130)

    def exitPlayScreen(self):
        self.playScreen.exit()

        for element in self.mainMenuElements:
            element.show()

    def enterHostScreen(self):
        self.playScreen.exit()
        self.hostScreen.enter()
        self.hostScreen.show()

        def hideRandomSuitsTask(task):
            self.randomSuit2.hide()
            self.randomSuit3.hide()

        taskMgr.doMethodLater(4, hideRandomSuitsTask, 'hideRandomSuit2')

        for elements in self.mainMenuElements:
            elements.hide()

    def exitHostScreen(self):
        self.hostScreen.hide()
        self.hostScreen.exit()

        for elements in self.mainMenuElements:
            elements.show()

    def enterJoinScreen(self):
        self.joinScreen.enter()
        self.joinScreen.show()
        self.flyDownSfx.setVolume(0)

        for elements in self.mainMenuElements:
            elements.hide()

    def exitJoinScreen(self):
        self.joinScreen.exit()
        self.joinScreen.hide()
        self.flyDownSfx.setVolume(1)

        for elements in self.mainMenuElements:
            elements.show()

    def enterOptions(self):
        self.optionsScreen.show()
        self.background.show()
        self.bottomLeftButton.show()
        self.bottomLeftButton['command'] = lambda: self.request('LoginOrSignUpScreen')
        self.bottomLeftButton['text'] = "Back"
        self.logo.hide()

    def exitOptions(self):
        self.optionsScreen.hide()
        self.background.hide()
        self.bottomLeftButton.hide()
        self.bottomLeftButton['command'] = lambda: self.request('Options')
        self.bottomLeftButton['text'] = "Options"
        self.logo.show()

    def enterOptions2(self):
        self.optionsScreen.show()
        self.background.show()
        self.bottomLeftButton.show()
        self.bottomLeftButton['command'] = lambda: self.request('HomeScreen')
        self.bottomLeftButton['text'] = "Back"
        self.logo.hide()

    def exitOptions2(self):
        self.optionsScreen.hide()
        self.background.hide()
        self.bottomLeftButton.hide()
        self.bottomLeftButton['command'] = lambda: self.request('Options')
        self.bottomLeftButton['text'] = "Options"
        self.logo.show()

    def enterLoggingIn(self):
        pass

        # Do login magic here:

        # If login is accepted,  request the Home Screen

    def enterLoggingOut(self):
        pass

        # Do logout magic here:

        # If user logs out, request Idle

    def enterStartHost(self):
        self.hostScreen.exit()
        self.hostStartScreen.enter()
        self.hostStartScreen.show()
        self.randomSuit2.hide()
        self.randomSuit3.hide()
        for elements in self.mainMenuElements:
            elements.hide()

    def exitStartHost(self):
        self.hostStartScreen.hide()
        self.randomSuit2.show()
        self.randomSuit3.show()
        for elements in self.mainMenuElements:
            elements.show()

    def enterHostScreenAfterFail(self):
        self.hostStartScreen.hide()
        self.randomSuit2.hide()
        self.randomSuit3.hide()
        self.hostStartScreen.exitBackToHostScreen()
        self.hostScreen.enterAfterFail()
        self.hostScreen.show()
        for elements in self.mainMenuElements:
            elements.hide()

    def exitHostScreenAfterFail(self):
        self.randomSuit2.show()
        self.randomSuit3.show()

    def enterEnterServer(self):
        pass

    def __handleQuit(self):
        cleanupDialog('globalDialog')
        base.cr.loginFSM.request('shutdown')
