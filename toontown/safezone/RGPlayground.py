import random

from direct.task.Task import Task

from toontown.safezone import Playground

from toontown.toonbase import ToontownGlobals

class RGPlayground(Playground.Playground):

    def __init__(self, loader, parentFSM, doneEvent):
        Playground.Playground.__init__(self, loader, parentFSM, doneEvent)
        self.cameraSubmerged = -1
        self.toonSubmerged = -1

    def enter(self, requestStatus):
        Playground.Playground.enter(self, requestStatus)

        taskMgr.doMethodLater(1, self.__birds, 'rg-birds')
        base.camLens.setNearFar(ToontownGlobals.ResistanceGroundsCameraNear, ToontownGlobals.ResistanceGroundsCameraFar)

    def exit(self):
        Playground.Playground.exit(self)
        if self.cameraSubmerged:
            self.__emergeCamera()

        taskMgr.remove('rg-check-toon-underwater')
        taskMgr.remove('rg-check-cam-underwater')
        taskMgr.remove('rg-birds')
        base.camLens.setNearFar(ToontownGlobals.DefaultCameraNear, ToontownGlobals.DefaultCameraFar)

    def __birds(self, task):
        base.playSfx(random.choice(self.loader.birdSound))
        time = random.random() * 20.0 + 1
        taskMgr.doMethodLater(time, self.__birds, 'rg-birds')
        return Task.done

    def enterStart(self):
        self.cameraSubmerged = 0
        self.toonSubmerged = 0
        taskMgr.add(self.__checkToonUnderwater, 'rg-check-toon-underwater')
        taskMgr.add(self.__checkCameraUnderwater, 'rg-check-cam-underwater')

    def enterDoorIn(self, requestStatus):
        Playground.Playground.enterDoorIn(self, requestStatus)
        taskMgr.add(self.__checkToonUnderwater, 'rg-check-toon-underwater')

    def enterDoorOut(self):
        Playground.Playground.enterDoorOut(self)
        taskMgr.remove('rg-check-toon-underwater')

    def __submergeCamera(self):
        if self.cameraSubmerged == 1:
            return
        self.loader.hood.setUnderwaterFog()
        base.playSfx(self.loader.underwaterSound, looping=1, volume=0.8)
        taskMgr.remove('rg-birds')
        self.cameraSubmerged = 1
        self.walkStateData.setSwimSoundAudible(1)

    def __emergeCamera(self):
        if self.cameraSubmerged == 0:
            return
        self.loader.hood.setNoFog()
        self.loader.underwaterSound.stop()
        taskMgr.add(self.__birds, 'rg-birds')
        self.cameraSubmerged = 0
        self.walkStateData.setSwimSoundAudible(0)

    def __submergeToon(self):
        if self.toonSubmerged == 1:
            return
        base.playSfx(self.loader.submergeSound)
        if base.config.GetBool('disable-flying-glitch') == 0:
            self.fsm.request('walk')
        self.walkStateData.fsm.request('swimming', [self.loader.swimSound])
        pos = base.localAvatar.getPos(render)
        base.localAvatar.d_playSplashEffect(pos[0], pos[1], 1.675)
        self.toonSubmerged = 1

    def __emergeToon(self):
        if self.toonSubmerged == 0:
            return
        self.walkStateData.fsm.request('walking')
        self.toonSubmerged = 0

    def enterTeleportIn(self, requestStatus):
        self.toonSubmerged = -1
        taskMgr.remove('rg-check-toon-underwater')
        Playground.Playground.enterTeleportIn(self, requestStatus)

    def teleportInDone(self):
        self.toonSubmerged = -1
        taskMgr.add(self.__checkToonUnderwater, 'rg-check-toon-underwater')
        Playground.Playground.teleportInDone(self)

    def __checkCameraUnderwater(self, task):
        if base.camera.getZ(render) < -3:
            self.__submergeCamera()
        else:
            self.__emergeCamera()
        return Task.cont

    def __checkToonUnderwater(self, task):
        if base.localAvatar.getZ() < -4:
            self.__submergeToon()
        else:
            self.__emergeToon()
        return Task.cont
