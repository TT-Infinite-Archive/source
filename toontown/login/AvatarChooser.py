import math
import random

from panda3d.core import ConfigVariableInt, DecalEffect, ModelPool, NodePath, TextEncoder, TextNode, TexturePool
from panda3d.core import PlaneNode, Point3, TransparencyAttrib, Vec3, Vec4
from direct.fsm import ClassicFSM, State, StateData
from direct.gui.DirectGui import *
from direct.gui.DirectGuiGlobals import NO_FADE_SORT_INDEX
from direct.gui.OnscreenImage import OnscreenImage
from direct.interval.IntervalGlobal import EventInterval, Func, LerpFunc, LerpHprInterval, LerpPosInterval, Parallel, Sequence

from toontown.estate import HouseGlobals
from toontown.hood import SkyUtil
from toontown.launcher import DownloadForceAcknowledge
from toontown.mainmenu import MainMenuGlobals
from toontown.makeatoon.MakeAToonGUI import MATFrame, MATShuffleButton
from toontown.shtiker.OptionsTabPage import OptionsTabPage
from toontown.toon.Toon import Toon
from toontown.toon.ToonDNA import ToonDNA
from toontown.toonbase import SettingsGlobals, ToontownClientGlobals, ToontownGlobals, TTLocalizer
from toontown.toontowngui import TTDialog

MAX_AVATARS = 6
ChoiceOrder = (1, 3, 4, 5, 0, 2)
CameraPoints = (
    (-69.20, -71.84, 7.16, 330.95, 5.19, 0),
    (79.74, -36.51, 2.68, 185.71, 4.09, 0),
    (-48.66, -93.12, 5.28, 135.00, 0, 0),
    (90.87, -4.09, 10.57, 52.13, 6.71, 0),
    (18.19, 50.72, 2.94, 308.66, 6.71, 0),
    (-7.82, 40.76, 4.93, 90, 6.34, 0))
AvatarPoints = (
    (-64.011, -55.079, 3.980, 167.848, 0, 0),
    (83.914, -47.952, 0.025, -328.349, 0, 0),
    (-59.459, -108.106, 0, -392.763, 0, 0),
    (75.273, 3.147, 8.025, 260.951, 0, 0),
    (28.387, 65.270, 0.027, 511.157, 0, 0),
    (-22.979, 37.503, 2.354, 293.809, 0, 0))
PanDuration = 1.3
PanDelay = 0.2
PanLift = 30.0
PanDip = 20.0
SkyColor = (0.65, 0.82, 0.96, 1)
MovePath = (
    (4.8, 67.4, 4.86), (28.8, 63.6, 0.02), (48.0, 54.0, 0.02), (83.2, 55.6, 0.03), (99.2, 52.4, 0.02),
    (110.4, 38.0, 0.03), (108.8, -0.4, 0), (96.0, -29.2, 0.02), (83.2, -42.0, 0.03), (64.0, -54.8, 1.06),
    (38.4, -61.2, 0.39), (6.4, -59.6, 1.62), (-14.4, -67.6, 0.32), (-25.6, -77.2, 0.02), (-43.2, -88.4, 0.02),
    (-64.0, -91.6, 0.02), (-81.6, -74.0, 0), (-83.2, -54.8, 0.03), (-84.8, -35.6, 0.02), (-80.0, 6.0, 0.02),
    (-75.2, 28.4, 0), (-64.0, 44.4, 0.03), (-36.8, 65.2, 0.03), (-16.0, 68.4, 0.09))
MovePathEntries = (17, 8, 15, 6, 1, 23)
MoveCenter = (12, -12)
MoveRunSpeed = 35.0
MoveMaxDuration = 6.0
MoveBlendIn = 1.0
MoveBlendOut = 1.3
ChaseDistance = 30.0
ChaseHeight = 38.0
BUTTON_PROPERTIES = {
    'wantArrows': False,
    'image_scale': (-0.8, 0.6, 0.6),
    'image1_scale': (-0.84, 0.63, 0.63),
    'image2_scale': (-0.84, 0.63, 0.63)
}
PreloadModels = (
    'phase_5.5/models/estate/terrain.bam',
    'phase_3.5/models/props/TT_sky.bam',
    'phase_5.5/models/estate/houseA.bam',
    'phase_3.5/models/modules/doors_practical.bam'
)


def preload():
    print('Preloading the Pick-A-Toon scene...')

    for modelPath in PreloadModels:
        preloader.loadModel(modelPath)


def unload():
    for modelPath in PreloadModels:
        preloader.unloadModel(modelPath)


def smoothstep(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def getRouteLength(points):
    return sum((b - a).length() for a, b in zip(points, points[1:]))


def copyModel(modelPath, parent):
    model = preloader.getModel(modelPath)
    if model is None:
        model = loader.loadModel(modelPath)
        model.reparentTo(parent)
        return model
    return model.copyTo(parent)


class AvatarChooser(StateData.StateData):
    lastChoiceIndex = None
    handingOff = None
    teleportInAvatarId = 0
    fadeInOnEnter = False

    def __init__(self, avatarList, parentFSM, doneEvent):
        StateData.StateData.__init__(self, doneEvent)
        self.choice = None
        self.choiceIndex = AvatarChooser.lastChoiceIndex
        self.movingFrom = None
        self.panIval = None
        self.teleportIval = None
        self.teleportInIval = None
        self.moveIval = None
        base.isLoggingOut = None
        self.avatarList = avatarList
        self.position2avatar = [None] * MAX_AVATARS
        self.teleportInPosition = None
        for av in avatarList:
            self.position2avatar[av.position] = av
            if av.id == AvatarChooser.teleportInAvatarId:
                self.teleportInPosition = av.position
                self.choiceIndex = ChoiceOrder.index(av.position)
        AvatarChooser.teleportInAvatarId = 0
        if self.choiceIndex is None:
            self.choiceIndex = self.__getDefaultChoiceIndex()
        self.fsm = ClassicFSM.ClassicFSM('AvatarChooser',
                                         [State.State('Choose', self.enterChoose, self.exitChoose, ['CheckDownload']),
                                          State.State('CheckDownload', self.enterCheckDownload, self.exitCheckDownload,
                                                      ['Choose'])], 'Choose', 'Choose')
        self.fsm.enterInitialState()
        self.parentState = parentFSM.getCurrentState()
        self.parentState.addChild(self.fsm)
        self.exitPending = False
        self.unloadPending = False
        self.optionsScreen = None
        self.deleteFrame = None

    def __getDefaultChoiceIndex(self):
        lastToon = settings.get(SettingsGlobals.LastToon)
        for av in self.avatarList:
            if av.id == lastToon:
                return ChoiceOrder.index(av.position)
        for index, position in enumerate(ChoiceOrder):
            if self.position2avatar[position]:
                return index
        return 0

    def enter(self):
        if not self.isLoaded:
            self.load()
        base.disableMouse()
        base.setBackgroundColor(*SkyColor)
        base.camLens.setMinFov(ToontownGlobals.DefaultCameraFov / (4. / 3.))
        camera.reparentTo(render)
        self.scene.reparentTo(render)
        SkyUtil.startCloudSky(self)
        self.title.reparentTo(aspect2d)
        self.buttons.reparentTo(base.a2dBottomCenter)
        self.__setInputEnabled(True)
        self.__setChoiceIndex(self.choiceIndex, pan=False)
        if AvatarChooser.fadeInOnEnter:
            AvatarChooser.fadeInOnEnter = False
            base.transitions.fadeIn(0.5)
        if self.teleportInPosition is not None:
            self.__teleportIn(self.toons[self.teleportInPosition])
            self.teleportInPosition = None
        choice = ConfigVariableInt('auto-avatar-choice', -1).getValue()
        if 0 <= choice < MAX_AVATARS and self.position2avatar[choice]:
            self.choice = choice
            self.__handleDone('chose')

    def exit(self):
        if self.isLoaded == 0:
            return None
        if AvatarChooser.handingOff is self:
            self.exitPending = True
            return None
        self.ignoreAll()
        self.__stopPan()
        taskMgr.remove('skyTrack')
        self.sky.reparentTo(hidden)
        self.scene.detachNode()
        self.title.reparentTo(hidden)
        self.buttons.reparentTo(hidden)
        self.__hideOptions()

    def skyTrack(self, task):
        return SkyUtil.cloudSkyTrack(task)

    def load(self):
        if self.isLoaded:
            return None

        self.scene = NodePath('pickAToon')
        terrain = copyModel('phase_5.5/models/estate/terrain.bam', self.scene)
        path = terrain.find('**/Path')
        path.setTransparency(TransparencyAttrib.MBinary, 1)
        path.setBin('ground', 10, 1)
        self.sky = copyModel('phase_3.5/models/props/TT_sky.bam', hidden)

        doors = copyModel('phase_3.5/models/modules/doors_practical.bam', hidden)
        self.houses = []
        for position in range(MAX_AVATARS):
            house = copyModel('phase_5.5/models/estate/houseA.bam', self.scene)
            house.setPosHpr(*HouseGlobals.houseDrops[position])
            self.__setupHouse(house, position, doors)
            self.houses.append(house)
        doors.removeNode()

        self.toons = {}
        for av in self.avatarList:
            toon = Toon()
            toon.setDNA(ToonDNA(av.dna))
            toon.setHat(*av.hat)
            toon.setGlasses(*av.glasses)
            toon.setBackpack(*av.backpack)
            toon.setShoes(*av.shoes)
            toon.useLOD(1000)
            toon.setBlend(frameBlend=settings[SettingsGlobals.AnimationSmoothing])
            toon.setPosHpr(*AvatarPoints[av.position])
            toon.reparentTo(self.scene)
            toon.loop('neutral')
            toon.startBlink()
            toon.startLookAround()
            self.toons[av.position] = toon
            if av.name:
                self.__setupHouseName(self.houses[av.position], av)

        self.title = OnscreenText(
            TTLocalizer.AvatarChooserPickAToon, scale=TTLocalizer.ACtitle,
            parent=hidden, font=ToontownGlobals.getSignFont(),
            fg=(1, 0.9, 0.1, 1), shadow=(0, 0, 0, 1), pos=(0.0, 0.82))

        self.buttons = hidden.attachNewNode('pickAToonButtons')
        self.optionsButton = MATShuffleButton(
            parent=self.buttons, text=TTLocalizer.OptionsPageTitle, pos=(-0.95, 0, 0.15),
            command=self.__showOptions, **BUTTON_PROPERTIES)
        self.moveButton = MATShuffleButton(
            parent=self.buttons, text=TTLocalizer.AvatarChooserMove, pos=(-0.53, 0, 0.15),
            command=self.__handleMove, **BUTTON_PROPERTIES)
        self.nameButton = MATShuffleButton(
            parent=self.buttons, text=TTLocalizer.AvatarChooserNameYourToon, pos=(0, 0, 0.29),
            command=self.__handleDone, extraArgs=['nameIt'], **BUTTON_PROPERTIES)
        self.choiceFrame = MATFrame(parent=self.buttons, pos=(0, 0, 0.15), arrowcommand=self.__cycleChoice)
        self.choiceButton = MATShuffleButton(
            parent=self.choiceFrame, wantArrows=False, text=TTLocalizer.AvatarChooserPlay,
            command=self.__handleChoice)
        self.statusText = DirectLabel(
            parent=self.buttons, relief=None, pos=(0, 0, 0.27), text='',
            text_scale=0.07, text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1),
            text_font=ToontownClientGlobals.getToonFont())
        self.deleteButton = MATShuffleButton(
            parent=self.buttons, text=TTLocalizer.AvatarChoiceDelete, pos=(0.53, 0, 0.15),
            command=self.__handleDelete, **BUTTON_PROPERTIES)
        self.quitButton = MATShuffleButton(
            parent=self.buttons, text=TTLocalizer.AvatarChooserQuit, pos=(0.95, 0, 0.15),
            command=self.__handleQuit, **BUTTON_PROPERTIES)

        self.isLoaded = 1

    def __setupHouse(self, house, position, doors):
        color = HouseGlobals.houseColors[position]
        dark = (color[0] * 0.8, color[1] * 0.8, color[2] * 0.8, 1)
        for wall, wallColor in (('back', color), ('front', color), ('right', dark), ('left', dark)):
            wallNP = house.find('**/*' + wall)
            if not wallNP.isEmpty():
                wallNP.setColor(wallColor[0], wallColor[1], wallColor[2], 1)
        attic = house.find('**/attic')
        if not attic.isEmpty():
            attic.setColor(*HouseGlobals.atticWood, 1)
        for chimney in house.findAllMatches('**/chim*'):
            chimney.setColor(*HouseGlobals.houseColors2[position], 1)
        house.find('**/mat').setColor(0.4, 0.357, 0.259, 1.0)

        door_origin = house.find('**/door_origin')
        door_origin.setHpr(90, 0, 0)
        door_origin.setScale(0.6, 0.6, 0.8)
        door_origin.setPos(door_origin, 0.5, 0, 0.0)
        doorNP = doors.find('**/door_double_round_ur').copyTo(door_origin)
        doorColor = Vec4(*HouseGlobals.stairWood, 1)
        doorNP.setPosHprScale(door_origin, (0, 0, 0), (0, 0, 0), (1, 1, 1))
        doorNP.setColor(doorColor, 0)
        leftHole = doorNP.find('door_*_hole_left')
        rightHole = doorNP.find('door_*_hole_right')
        leftDoor = doorNP.find('door_*_left')
        rightDoor = doorNP.find('door_*_right')
        doorFlat = doorNP.find('door_*_flat')
        leftHole.wrtReparentTo(doorFlat, 0)
        rightHole.wrtReparentTo(doorFlat, 0)
        doorFlat.setEffect(DecalEffect.make())
        rightDoor.wrtReparentTo(door_origin, 0)
        leftDoor.wrtReparentTo(door_origin, 0)
        rightDoor.setColor(doorColor, 0)
        leftDoor.setColor(doorColor, 0)
        leftHole.setColor((0, 0, 0, 1), 0)
        rightHole.setColor((0, 0, 0, 1), 0)
        doorNP.flattenMedium()

    def __setupHouseName(self, house, av):
        houseName = TTLocalizer.AvatarsHouse % TTLocalizer.GetPossesive(av.name)
        randomGenerator = random.Random()
        randomGenerator.seed(av.id)
        color = HouseGlobals.houseColors[av.position]

        nameText = self.__makeHouseText(
            houseName, (randomGenerator.random(), randomGenerator.random(), randomGenerator.random(), 1), 16.0)
        sign_origin = house.find('**/sign_origin')
        pos = sign_origin.getPos()
        sign_origin.setPosHpr(pos[0], pos[1], pos[2] + 0.15 * (nameText.getHeight() - 2), 90, 0, 0)
        namePlate = sign_origin.attachNewNode(nameText)
        namePlate.setDepthWrite(0)
        namePlate.setPos(0, -0.05, 0)
        namePlate.setScale(min(1.0, 16.0 / nameText.getWidth()))

        matText = self.__makeHouseText(houseName, (color[0], color[1], color[2], 1), 10.0)
        mat_origin = house.find('**/mat_origin')
        pos = mat_origin.getPos()
        mat_origin.setPosHpr(pos[0] - 0.15 * (matText.getHeight() - 2), pos[1], pos[2], 90, -90, 0)
        floorMat = mat_origin.attachNewNode(matText)
        floorMat.setDepthWrite(0)
        floorMat.setPos(0, -0.025, 0)
        floorMat.setScale(0.45 * min(1.0, 8.0 / matText.getWidth()))

    def __makeHouseText(self, text, color, wordwrap):
        textNode = TextNode('houseText')
        textNode.setTextColor(*color)
        textNode.setAlign(TextNode.ACenter)
        textNode.setFont(ToontownClientGlobals.getBuildingNametagFont())
        textNode.setShadowColor(0, 0, 0, 1)
        textNode.setBin('fixed')
        if TTLocalizer.BuildingNametagShadow:
            textNode.setShadow(*TTLocalizer.BuildingNametagShadow)
        textNode.setWordwrap(wordwrap)
        textNode.setText(text)
        return textNode

    def unload(self):
        if self.isLoaded == 0:
            return None
        if AvatarChooser.handingOff is self:
            self.unloadPending = True
            return None
        cleanupDialog('globalDialog')
        self.__cleanupDelete()
        self.__stopPan()
        self.panIval = None
        if self.optionsScreen:
            self.optionsScreen.destroy()
            self.optionsBackground.removeNode()
            self.optionsBackButton.destroy()
            self.optionsScreen = None
        for ival in (self.teleportIval, self.teleportInIval, self.moveIval):
            if ival:
                ival.pause()
        self.teleportIval = None
        self.teleportInIval = None
        self.moveIval = None
        for toon in self.toons.values():
            toon.stopBlink()
            toon.stopLookAroundNow()
            toon.delete()
        del self.toons
        del self.houses
        self.scene.removeNode()
        del self.scene
        self.sky.removeNode()
        del self.sky
        self.title.removeNode()
        del self.title
        for button in (self.optionsButton, self.moveButton, self.nameButton, self.choiceButton, self.choiceFrame,
                       self.statusText, self.deleteButton, self.quitButton):
            button.destroy()
        self.buttons.removeNode()
        del self.buttons
        unload()
        del self.avatarList
        del self.position2avatar
        self.parentState.removeChild(self.fsm)
        del self.parentState
        del self.fsm
        self.ignoreAll()
        self.isLoaded = 0
        ModelPool.garbageCollect()
        TexturePool.garbageCollect()
        base.setBackgroundColor(ToontownGlobals.DefaultBackgroundColor)

    def __setInputEnabled(self, enabled):
        if enabled:
            self.accept('arrow_left', self.__cycleChoice, [-1])
            self.accept('arrow_right', self.__cycleChoice, [1])
            self.buttons.show()
        else:
            self.ignore('arrow_left')
            self.ignore('arrow_right')
            self.buttons.hide()

    def __cycleChoice(self, direction):
        self.__setChoiceIndex((self.choiceIndex + direction) % MAX_AVATARS)

    def __setChoiceIndex(self, choiceIndex, pan=True):
        self.choiceIndex = choiceIndex
        AvatarChooser.lastChoiceIndex = choiceIndex
        self.choice = ChoiceOrder[choiceIndex]
        if pan:
            taskMgr.remove('pickAToonPan')
            taskMgr.doMethodLater(PanDelay, self.__panCameraTask, 'pickAToonPan')
        else:
            self.__stopPan()
            self.panPosition = self.choice
            camera.setPosHpr(*CameraPoints[self.choice])
        av = self.position2avatar[self.choice]
        status = ''
        self.nameButton.hide()
        self.choiceButton['text_scale'] = TTLocalizer.SBshuffleBtn
        if self.movingFrom is not None:
            if self.choice == self.movingFrom:
                self.choiceButton['state'] = DGG.DISABLED
            else:
                self.choiceButton['state'] = DGG.NORMAL
            if av is None:
                self.choiceButton['text'] = TTLocalizer.AvatarChooserMoveHere
                self.choiceButton['text_scale'] = TTLocalizer.ACmoveHereButton
            else:
                self.choiceButton['text'] = TTLocalizer.AvatarChooserSwap
        elif av is None:
            self.choiceButton['text'] = TTLocalizer.AvatarChooserCreate
            self.moveButton['state'] = DGG.DISABLED
            self.deleteButton['state'] = DGG.DISABLED
        else:
            self.choiceButton['text'] = TTLocalizer.AvatarChooserPlay
            self.moveButton['state'] = DGG.NORMAL
            self.deleteButton['state'] = DGG.NORMAL
            if av.wantName != '':
                status = TTLocalizer.AvatarChoiceNameReview
            elif av.approvedName != '':
                status = TTLocalizer.AvatarChoiceNameApproved
            elif av.rejectedName != '':
                status = TTLocalizer.AvatarChoiceNameRejected
            elif av.allowedName:
                self.nameButton.show()
        self.statusText['text'] = status.replace('\n', ' ')

    def __stopPan(self):
        taskMgr.remove('pickAToonPan')
        if self.panIval:
            self.panIval.pause()

    def __panCameraTask(self, task):
        if self.panIval and self.panIval.isPlaying():
            task.delayTime = 0.1
            return task.again
        if self.panPosition != self.choice:
            self.__panCamera(self.choice)
        return task.done

    def __panCamera(self, position):
        start = CameraPoints[self.panPosition]
        end = CameraPoints[position]
        delta = [e - s for s, e in zip(start, end)]
        delta[3] = (delta[3] + 180) % 360 - 180
        self.panPosition = position
        self.panIval = LerpFunc(self.__panCameraStep, duration=PanDuration, extraArgs=[start, delta])
        self.panIval.start()

    def __panCameraStep(self, t, start, delta):
        # Rise above the rooftops before crossing the estate, and settle back down at the other house.
        travel = smoothstep((t - 0.2) / 0.6)
        lift = smoothstep(t / 0.25) * smoothstep((1 - t) / 0.25)
        x, y, z, h, p, r = [s + d * travel for s, d in zip(start, delta)]
        camera.setPosHpr(x, y, z + PanLift * lift, h, p - PanDip * lift, r)

    def getChoice(self):
        return self.choice

    def __handleMove(self):
        moving = self.movingFrom is None
        self.movingFrom = self.choice if moving else None
        self.title.setText(TTLocalizer.AvatarChooserMoveTitle if moving else TTLocalizer.AvatarChooserPickAToon)
        self.moveButton['text'] = TTLocalizer.lCancel if moving else TTLocalizer.AvatarChooserMove
        self.choiceButton['state'] = DGG.NORMAL
        for button in (self.optionsButton, self.deleteButton, self.quitButton):
            if moving:
                button.hide()
            else:
                button.show()
        self.__setChoiceIndex(self.choiceIndex, pan=False)

    def __handleChoice(self):
        if self.movingFrom is not None:
            self.__moveToons(self.movingFrom, self.choice)
        elif self.position2avatar[self.choice] is None:
            self.__handleDone('create')
        else:
            self.__teleportOut()

    def __getMoveRoute(self, source, target):
        start, end = MovePathEntries[source], MovePathEntries[target]
        routes = []
        for step in (1, -1):
            indices = [start]
            while indices[-1] != end:
                indices.append((indices[-1] + step) % len(MovePath))
            points = [Point3(*AvatarPoints[source][:3])] + [Point3(*MovePath[i]) for i in indices]
            routes.append(points + [Point3(*AvatarPoints[target][:3])])
        return min(routes, key=getRouteLength)

    def __getRunTrack(self, toon, source, target, duration):
        points = self.__getMoveRoute(source, target)
        speed = getRouteLength(points) / duration
        track = Sequence(Func(toon.stopLookAroundNow), Func(toon.setPlayRate, speed / ToontownGlobals.ToonForwardSpeed, 'run'),
                         Func(toon.loop, 'run'))
        for a, b in zip(points, points[1:]):
            delta = b - a
            if delta.length() > 0.01:
                track.append(Func(toon.setH, math.degrees(math.atan2(-delta[0], delta[1]))))
                track.append(LerpPosInterval(toon, delta.length() / speed, b))
        track.append(Func(toon.setPlayRate, 1, 'run'))
        track.append(Func(toon.loop, 'neutral'))
        endH = AvatarPoints[target][3]
        track.append(Func(lambda: toon.setH(endH + (toon.getH() - endH + 180) % 360 - 180)))
        track.append(LerpHprInterval(toon, 0.5, (endH, 0, 0)))
        track.append(Func(toon.startLookAround))
        return track

    def __moveToons(self, source, target):
        self.__setInputEnabled(False)
        self.__stopPan()
        runs = [(source, target)]
        if self.position2avatar[target]:
            runs.append((target, source))
        duration = min(MoveMaxDuration, getRouteLength(self.__getMoveRoute(source, target)) / MoveRunSpeed)
        self.moveToon = self.toons[source]
        self.moveStart = (camera.getPos(), camera.getHpr())
        self.moveEnd = (Point3(*CameraPoints[target][:3]), Vec3(*CameraPoints[target][3:]))
        self.moveDuration = duration
        self.moveIval = Sequence(
            Parallel(LerpFunc(self.__moveCameraStep, duration=duration + MoveBlendOut, toData=duration + MoveBlendOut),
                     *[self.__getRunTrack(self.toons[a], a, b, duration) for a, b in runs]),
            Func(self.__sendMove, source, target))
        self.moveIval.start()

    def __getChasePose(self):
        pos = self.moveToon.getPos()
        inward = Vec3(MoveCenter[0] - pos[0], MoveCenter[1] - pos[1], 0)
        inward.normalize()
        camPos = pos + inward * ChaseDistance + Vec3(0, 0, ChaseHeight)
        delta = pos + Vec3(0, 0, 2) - camPos
        return camPos, Vec3(math.degrees(math.atan2(-delta[0], delta[1])),
                            math.degrees(math.atan2(delta[2], delta.getXy().length())), 0)

    def __moveCameraStep(self, elapsed):
        # Blend from the old house's view into a chase above the running toon, then down to the new house.
        chasePos, chaseHpr = self.__getChasePose()
        if elapsed < self.moveDuration:
            weight = smoothstep(elapsed / MoveBlendIn)
            fromPos, fromHpr = self.moveStart
        else:
            weight = 1 - smoothstep((elapsed - self.moveDuration) / MoveBlendOut)
            fromPos, fromHpr = self.moveEnd
        hpr = [f + ((c - f + 180) % 360 - 180) * weight for f, c in zip(fromHpr, chaseHpr)]
        camera.setPosHpr(fromPos + (chasePos - fromPos) * weight, Vec3(*hpr))

    def __sendMove(self, source, target):
        self.choice = source
        settings[SettingsGlobals.LastToon] = self.position2avatar[source].id
        self.doneStatus = {'mode': 'move', 'index': target}
        AvatarChooser.fadeInOnEnter = True
        base.transitions.fadeOut(0.5, finishIval=EventInterval(self.doneEvent, [self.doneStatus]))

    def __teleportIn(self, toon):
        self.__setInputEnabled(False)
        toon.stopLookAroundNow()
        toon.pose('teleport', toon.getNumFrames('teleport') - 1)
        toon.getGeomNode().hide()
        toon.dropShadow.hide()
        self.teleportInIval = Sequence(toon.getTeleportInTrack(), Func(self.__finishTeleportIn, toon))
        self.teleportInIval.start()
        base.transitions.irisIn(0.4)

    def __finishTeleportIn(self, toon):
        self.teleportInIval = None
        toon.loop('neutral')
        toon.startLookAround()
        self.__setInputEnabled(True)

    def __teleportOut(self):
        av = self.position2avatar[self.choice]
        if av.approvedName != '' or av.rejectedName != '':
            self.__handleDone('chose')
            return
        self.__setInputEnabled(False)
        self.__stopPan()
        self.panPosition = self.choice
        camera.setPosHpr(*CameraPoints[self.choice])
        self.title.hide()
        toon = self.toons[self.choice]
        toon.stopLookAroundNow()
        toon.getGeomNode().setClipPlane(toon.attachNewNode(PlaneNode('holeClip')))
        self.teleportIval = Sequence(toon.getTeleportOutTrack(), Func(toon.hide), Func(self.__handleTeleportDone))
        self.teleportIval.start()

        # Keep the scene up until the teleport is over; the game holds on to the chosen toon until then.
        AvatarChooser.handingOff = self
        self.__handleDone('chose')

    def __handleTeleportDone(self):
        self.teleportIval = None
        base.transitions.irisOut(0.4, finishIval=Func(self.__finishHandoff))

    def __finishHandoff(self):
        AvatarChooser.handingOff = None
        if self.exitPending:
            self.exit()
        if self.unloadPending:
            self.unload()
        messenger.send('pickAToonTeleportDone')

    def __handleDone(self, mode):
        cleanupDialog('globalDialog')
        self.doneStatus = {'mode': mode}
        if mode == 'chose':
            settings[SettingsGlobals.LastToon] = self.position2avatar[self.choice].id
        if mode == 'delete':
            messenger.send(self.doneEvent, [self.doneStatus])
        else:
            self.fsm.request('CheckDownload')

    def __handleQuit(self):
        cleanupDialog('globalDialog')
        self.doneStatus = {'mode': 'exit'}
        messenger.send(self.doneEvent, [self.doneStatus])

    def __showOptions(self):
        if self.optionsScreen is None:
            self.optionsBackground = render2d.attachNewNode('optionsBackground')
            OnscreenImage(parent=self.optionsBackground, image='phase_3.5/maps/blueprint.png')
            self.optionsBackground.setTransparency(TransparencyAttrib.MAlpha)
            self.optionsBackground.setBin('background', 0)
            self.optionsScreen = OptionsTabPage()
            self.optionsBackButton = DirectButton(
                parent=base.a2dBottomLeft, pos=(0.12, 0, 0.10), command=self.__hideOptions,
                **MainMenuGlobals.MINIATURE_BACK_BUTTON)
        self.optionsBackground.show()
        self.optionsScreen.show()
        self.optionsBackButton.show()
        self.title.hide()
        self.buttons.hide()

    def __hideOptions(self):
        if self.optionsScreen is None:
            return
        self.optionsBackground.hide()
        self.optionsScreen.hide()
        self.optionsBackButton.hide()
        self.title.show()
        self.buttons.show()

    def __handleDelete(self):
        av = self.position2avatar[self.choice]
        cleanupDialog('globalDialog')
        if av.guildId != 0:
            self.reject = TTDialog.TTGlobalDialog(
                doneEvent='rejectDone', message=TTLocalizer.AvatarChoiceDeleteRejectGuild % av.name,
                style=TTDialog.Acknowledge)
            self.reject.show()
            self.acceptOnce('rejectDone', self.__handleRejectDone)
            return
        deleteText = TTLocalizer.AvatarChoiceDeleteConfirmText % {
            'name': av.name,
            'confirm': TTLocalizer.AvatarChoiceDeleteConfirmUserTypes}
        if self.deleteFrame is None:
            buttons = loader.loadModel('phase_3/models/gui/dialog_box_buttons_gui')
            nameBalloon = loader.loadModel('phase_3/models/props/chatbox_input')
            okButtonImage = (buttons.find('**/ChtBx_OKBtn_UP'), buttons.find('**/ChtBx_OKBtn_DN'),
                             buttons.find('**/ChtBx_OKBtn_Rllvr'))
            cancelButtonImage = (buttons.find('**/CloseBtn_UP'), buttons.find('**/CloseBtn_DN'),
                                 buttons.find('**/CloseBtn_Rllvr'))
            self.deleteFrame = DirectFrame(
                pos=(0.0, 0.1, 0.2), parent=aspect2dp, relief=None, image=DGG.getDefaultDialogGeom(),
                image_color=ToontownGlobals.GlobalDialogColor, image_scale=(1.4, 1.0, 1.0), text=deleteText,
                text_wordwrap=19, text_scale=TTLocalizer.ACdeleteWithPasswordFrame, text_pos=(0, 0.25),
                textMayChange=1, sortOrder=NO_FADE_SORT_INDEX)
            self.deleteEntry = DirectEntry(
                parent=self.deleteFrame, relief=None, image=nameBalloon, image1_color=(0.8, 0.8, 0.8, 1.0),
                scale=0.064, pos=(-0.3, 0.0, -0.2), width=10, numLines=1, focus=1, cursorKeys=1,
                command=self.__handleDeleteConfirmOK)
            DirectButton(
                parent=self.deleteFrame, image=okButtonImage, relief=None,
                text=TTLocalizer.AvatarChoiceDeletePasswordOK, text_scale=0.05, text_pos=(0.0, -0.1),
                textMayChange=0, pos=(-0.22, 0.0, -0.35), command=self.__handleDeleteConfirmOK)
            DirectLabel(
                parent=self.deleteFrame, relief=None, pos=(0, 0, 0.35),
                text=TTLocalizer.AvatarChoiceDeletePasswordTitle, textMayChange=0, text_scale=0.08)
            DirectButton(
                parent=self.deleteFrame, image=cancelButtonImage, relief=None,
                text=TTLocalizer.AvatarChoiceDeletePasswordCancel, text_scale=0.05, text_pos=(0.0, -0.1),
                textMayChange=1, pos=(0.2, 0.0, -0.35), command=self.__handleDeleteCancel)
            buttons.removeNode()
            nameBalloon.removeNode()
        else:
            self.deleteFrame['text'] = deleteText
            self.deleteEntry['focus'] = 1
            self.deleteEntry.enterText('')
        base.transitions.fadeScreen(0.5)
        self.deleteFrame.show()

    def __handleRejectDone(self):
        self.reject.cleanup()
        del self.reject

    def __handleDeleteConfirmOK(self, *args):
        if TextEncoder.lower(self.deleteEntry.get()) == TextEncoder.lower(TTLocalizer.AvatarChoiceDeleteConfirmUserTypes):
            self.deleteFrame.hide()
            base.transitions.noTransitions()
            self.__handleDone('delete')
        else:
            self.deleteFrame['text'] = TTLocalizer.AvatarChoiceDeleteWrongConfirm % {
                'name': self.position2avatar[self.choice].name,
                'confirm': TTLocalizer.AvatarChoiceDeleteConfirmUserTypes}
            self.deleteEntry['focus'] = 1
            self.deleteEntry.enterText('')

    def __handleDeleteCancel(self):
        self.deleteFrame.hide()
        base.transitions.noTransitions()

    def __cleanupDelete(self):
        if self.deleteFrame is not None:
            self.deleteFrame.destroy()
            self.deleteFrame = None
            base.transitions.noTransitions()

    def enterChoose(self):
        pass

    def exitChoose(self):
        pass

    def enterCheckDownload(self):
        av = self.position2avatar[self.choice]
        lastHoodId = av.lastHoodId if av else 0
        self.accept('downloadAck-response', self.__handleDownloadAck)
        self.downloadAck = DownloadForceAcknowledge.DownloadForceAcknowledge('downloadAck-response')
        self.downloadAck.enter(lastHoodId)

    def exitCheckDownload(self):
        self.downloadAck.exit()
        self.downloadAck = None
        self.ignore('downloadAck-response')

    def __handleDownloadAck(self, doneStatus):
        if doneStatus['mode'] == 'complete' and AvatarChooser.handingOff is self:
            messenger.send(self.doneEvent, [self.doneStatus])
        elif doneStatus['mode'] == 'complete':
            base.transitions.fadeOut(finishIval=EventInterval(self.doneEvent, [self.doneStatus]))
        else:
            self.fsm.request('Choose')
            self.__resetTeleport()

    def __resetTeleport(self):
        if not self.teleportIval:
            return
        self.teleportIval.pause()
        self.teleportIval = None
        AvatarChooser.handingOff = None
        self.title.show()
        toon = self.toons[self.choice]
        toon.getGeomNode().clearClipPlane()
        toon.find('holeClip').removeNode()
        toon.show()
        toon.loop('neutral')
        toon.startLookAround()
        self.__setInputEnabled(True)
