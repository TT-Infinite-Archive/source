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
from toontown.mainmenu.PlayScreen import PlayScreen
from toontown.makeatoon.MakeAToonGUI import MATShuffleButton
from toontown.suit.Suit import Suit
from toontown.suit.SuitDNA import SuitDNA
from toontown.toon.Toon import Toon
from toontown.toon.ToonDNA import ToonDNA
from toontown.toonbase import ToontownGlobals
from direct.filter.CommonFilters import CommonFilters


class MainMenu(DirectFrame, FSM):
    notify = directNotify.newCategory('MainMenu')

    def __init__(self):
        DirectFrame.__init__(self, parent=base.aspect2d)
        FSM.__init__(self, 'MainMenu')

        self.backgroundNodePath = render2d.attachNewNode('background', 0)
        self.background = OnscreenImage(
            parent=self.backgroundNodePath,
            image='phase_3.5/maps/blueprint.png'
        )
        self.background.setTransparency(TransparencyAttrib.MAlpha)
        self.background.hide()

        self.homeScreen = HomeScreen(self)
        self.homeScreen.hide()
        self.playScreen = PlayScreen(self)
        self.playScreen.hide()
        self.hostScreen = HostScreen(self)
        self.hostScreen.hide()
        self.joinScreen = JoinScreen(self)
        self.joinScreen.hide()
        self.hostStartScreen = HostStartScreen(self)
        self.hostStartScreen.hide()

        self.createRandomSuitSequence = None
        self.createRandomSuitSequence2 = None
        self.createRandomSuitSequence3 = None

        if ToontownGlobals.HALLOWEEN_PROPS in base.clientHolidayIdList:
            ToontownGlobals.getNametagFont(10)
        else:
            ToontownGlobals.getMinnieFont()

        self.environment = NodePath('mainMenu-environment')
        self.environment.reparentTo(hidden)

        # self.suits = NodePath('mainMenu-suits')
        # self.suits.reparentTo(hidden)

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
        self.environment.removeNode()
        self.hostScreen.destroyAvScreen()
        self.joinScreen.destroyModels()
        base.camLens.setMinFov(ToontownGlobals.DefaultCameraFov/(4./3.))
        DirectFrame.destroy(self)

    def load(self):
        self.loadStreet()
        self.loadRandomToons()
        self.generateRandomSuits()
        self.initializeSky()

    def loadStreet(self):
        self.loopyLane = loader.loadModel('phase_4/models/neighborhoods/toontown_central_2200')
        self.loopyLane.setPosHpr(34, -12, 0, 5, 0, 0)
        self.loopyLane.reparentTo(self.environment)
        self.loopyLane.find('**/door_double_curved_ur_flat').removeNode()

    def loadRandomToons(self):
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

    def generateRandomSuits(self):
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

    def exitOff(self):
        base.camera.setPosHpr(-454.5, -96, 2.7, 215, 0, 0)
        base.camLens.setFov(30)

    def enterPlayScreen(self):
        self.playScreen.enter()
        self.playScreen.show()
        self.flyDownSfx.setVolume(1)
        self.environment.reparentTo(render)

        Sequence(
                 Func(self.randomToon.play, 'neutral'),
                 Wait(2),
                 Func(self.randomToon.play, 'wave'),
                 Wait(self.randomToon.getDuration('wave')),
                 Func(self.randomToon.play, 'bored'),
                 Wait(2.9),
                 Func(self.randomToon.pingpong, 'bored', fromFrame = 70, toFrame = 130)
                 ).start()
        
        self.randomToon2.pingpong('bored', fromFrame=70, toFrame=130)

    def exitPlayScreen(self):
        self.playScreen.exit()

    def enterHostScreen(self):
        self.playScreen.exit()
        self.hostScreen.enter()
        self.hostScreen.show()
        # base.oobe()

        def hideRandomSuits(task):
            self.randomSuit2.reparentTo(hidden)
            self.randomSuit3.reparentTo(hidden)

        taskMgr.doMethodLater(4, hideRandomSuits, 'hideRandomSuits')

    def exitHostScreen(self):
        self.randomSuit2.reparentTo(self.environment)
        self.randomSuit3.reparentTo(self.environment)
        self.hostScreen.hide()
        self.hostScreen.exit()
        taskMgr.remove('hideRandomSuits')

    def enterJoinScreen(self):
        self.joinScreen.enter()
        self.joinScreen.show()
        self.flyDownSfx.setVolume(0)

    def exitJoinScreen(self):
        self.joinScreen.exit()
        self.joinScreen.hide()
        self.flyDownSfx.setVolume(1)

    def enterStartDirectConnect(self):
        base.isHosting = False
        if not hasattr(self, 'targetIp'):
            ip = self.joinScreen.ipInput.get()
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

    def enterStartHost(self):
        self.hostScreen.exit()
        self.hostStartScreen.enter()
        self.hostStartScreen.show()
        self.randomSuit2.hide()
        self.randomSuit3.hide()

    def exitStartHost(self):
        self.hostStartScreen.hide()
        self.randomSuit2.show()
        self.randomSuit3.show()

    def enterHostScreenAfterFail(self):
        self.hostStartScreen.hide()
        self.randomSuit2.hide()
        self.randomSuit3.hide()
        self.hostStartScreen.exitBackToHostScreen()
        self.hostScreen.enterAfterFail()
        self.hostScreen.show()

    def exitHostScreenAfterFail(self):
        self.randomSuit2.show()
        self.randomSuit3.show()

    def __handleQuit(self):
        cleanupDialog('globalDialog')
        base.cr.loginFSM.request('shutdown')