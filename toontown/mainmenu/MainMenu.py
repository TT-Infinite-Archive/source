from panda3d.core import CompassEffect, NodePath, TransparencyAttrib, Vec4
import random

from direct.fsm.FSM import FSM
from direct.gui.DirectGui import *
from direct.task.Task import Task

from toontown.mainmenu.HomeScreen import HomeScreen
from toontown.mainmenu.HostScreen import HostScreen
from toontown.mainmenu.HostStartScreen import HostStartScreen
from toontown.mainmenu.JoinScreen import JoinScreen
from toontown.mainmenu.PlayScreen import PlayScreen
from toontown.toon.Toon import Toon
from toontown.toon.ToonDNA import ToonDNA
from toontown.toonbase import ToontownGlobals


class MainMenu(DirectFrame, FSM):
    notify = directNotify.newCategory('MainMenu')

    def __init__(self):
        DirectFrame.__init__(self, parent=base.aspect2d)
        FSM.__init__(self, 'MainMenu')

        base.setBackgroundColor(Vec4(0, 0, 0, 0))

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

        base.hostFailed = None

        if ToontownGlobals.HALLOWEEN_PROPS in base.clientHolidayIdList:
            ToontownGlobals.getNametagFont(10)
        else:
            ToontownGlobals.getMinnieFont()

        self.environment = NodePath('mainMenu-environment')
        self.environment.reparentTo(hidden)

    def destroy(self):
        self.environment.removeNode()
        self.hostScreen.destroyAvScreen()
        self.joinScreen.destroyModels()
        base.camLens.setMinFov(ToontownGlobals.DefaultCameraFov/(4./3.))
        base.setAspectRatio(0)
        DirectFrame.destroy(self)

    def load(self):
        self.loadStreet()
        self.loadRandomToons()
        self.initializeSky()
        base.setAspectRatio(16./8.5)

    def loadStreet(self):
        self.loopyLane = loader.loadModel('phase_4/models/neighborhoods/toontown_central_2200')
        self.loopyLane.setPosHpr(34, -12, 0, 5, 0, 0)
        self.loopyLane.reparentTo(self.environment)
        self.loopyLane.find('**/door_double_curved_ur_flat').removeNode()

        self.doorAbyss = loader.loadModel('phase_4/models/modules/doors_practical_abyss')
        self.doorAbyss.setPosHpr(-392.20, -246.90, 4, 185, 0, 0)
        self.doorAbyss.reparentTo(self.environment)

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

        self.randomToon.pingpong('bored', fromFrame=70, toFrame=130)
        self.randomToon2.pingpong('bored', fromFrame=70, toFrame=130)
        self.randomToon.setBlend(frameBlend = settings['animation-smoothing'])
        self.randomToon2.setBlend(frameBlend = settings['animation-smoothing'])


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

    def enterPlayScreen(self):
        self.playScreen.enter()
        self.playScreen.show()

    def exitPlayScreen(self):
        self.playScreen.exit()

    def enterHostScreen(self):
        self.hostScreen.enter()
        self.hostScreen.show()

    def exitHostScreen(self):
        self.hostScreen.hide()
        self.hostScreen.exit()

    def enterJoinScreen(self):
        self.joinScreen.enter()
        self.joinScreen.show()

    def exitJoinScreen(self):
        self.joinScreen.exit()
        self.joinScreen.hide()

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
        self.hostStartScreen.enter()
        self.hostStartScreen.show()

    def exitStartHost(self):
        self.hostStartScreen.hide()

    def __handleQuit(self):
        cleanupDialog('globalDialog')
        base.cr.loginFSM.request('shutdown')