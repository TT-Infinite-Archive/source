from direct.directnotify import DirectNotifyGlobal
from direct.distributed import ClockDelta
from direct.distributed import DistributedObject
from direct.fsm import ClassicFSM
from direct.fsm import State
from direct.interval.IntervalGlobal import *
from pandac.PandaModules import *
import random

import DistributedToon
import NPCToons
from toontown.nametag import NametagGlobals
from toontown.quest import QuestChoiceGui
from toontown.quest import QuestParser
from toontown.quest import Quests
from toontown.toonbase import ToontownGlobals, ColorGlobals
from toontown.makeatoon.MakeAToonGUI import MATShuffleButton
from direct.gui.OnscreenText import OnscreenText
import sys


class DistributedNPCToonBase(DistributedToon.DistributedToon):
    def __init__(self, cr):
        try:
            self.DistributedNPCToon_initialized
        except:
            self.DistributedNPCToon_initialized = 1
            DistributedToon.DistributedToon.__init__(self, cr)
            self.__initCollisions()
            self.setPickable(0)
            self.setPlayerType(NametagGlobals.CCNonPlayer)
        self.interactable = True # Some NPC's shouldn't be interactable, like the scientists in toon hall, so we disable it for those

    def disable(self):
        self.ignore('enter' + self.cSphereNode.getName())
        DistributedToon.DistributedToon.disable(self)

    def delete(self):
        try:
            self.DistributedNPCToon_deleted
        except:
            self.DistributedNPCToon_deleted = 1
            self.__deleteCollisions()
            DistributedToon.DistributedToon.delete(self)

    def generate(self):
        DistributedToon.DistributedToon.generate(self)
        self.cSphereNode.setName(self.uniqueName('NPCToon'))
        self.detectAvatars()
        self.setParent(ToontownGlobals.SPRender)
        self.startLookAround()

    def generateToon(self):
        self.setLODs()
        self.generateToonLegs()
        self.generateToonHead()
        self.generateToonTorso()
        self.generateToonColor()
        self.parentToonParts()
        self.rescaleToon()
        self.resetHeight()
        self.rightHands = []
        self.leftHands = []
        self.headParts = []
        self.hipsParts = []
        self.torsoParts = []
        self.legsParts = []
        self.__bookActors = []
        self.__holeActors = []

    def announceGenerate(self):
        self.initToonState()
        DistributedToon.DistributedToon.announceGenerate(self)

    def initToonState(self):
        self.setAnimState('neutral', 0.9, None, None)
        npcOrigin = render.find('**/npc_origin_' + str(self.posIndex))
        if not npcOrigin.isEmpty():
            self.reparentTo(npcOrigin)
            self.initPos()

    def initPos(self):
        self.clearMat()

    def wantsSmoothing(self):
        return 0

    def detectAvatars(self):
        if self.interactable:
            self.accept('enter' + self.cSphereNode.getName(), self.promptInteraction)

    def ignoreAvatars(self):
        self.ignore('enter' + self.cSphereNode.getName())

    def getCollSphereRadius(self):
        return 3.25

    def __initCollisions(self):
        self.cSphere = CollisionTube(0.0, 1.0, 0.0, 0.0, 1.0, 5.0, self.getCollSphereRadius())
        self.cSphere.setTangible(0)
        self.cSphereNode = CollisionNode('cSphereNode')
        self.cSphereNode.addSolid(self.cSphere)
        self.cSphereNodePath = self.attachNewNode(self.cSphereNode)
        self.cSphereNodePath.hide()
        self.cSphereNode.setCollideMask(ToontownGlobals.WallBitmask)

    def __deleteCollisions(self):
        self.ignore(base.INTERACT_KEY)
        if hasattr(self, "colorSeq") and self.colorSeq:
            self.colorSeq.finish()
        if hasattr(self, "enterText"):
            self.enterText.removeNode()
            del self.enterText
        del self.cSphere
        del self.cSphereNode
        self.cSphereNodePath.removeNode()
        del self.cSphereNodePath

    def handleCollisionSphereEnter(self, collEntry):
        pass

    def setupAvatars(self, av):
        self.ignoreAvatars()
        av.headsUp(self, 0, 0, 0)
        self.headsUp(av, 0, 0, 0)
        av.stopLookAround()
        av.lerpLookAt(Point3(-0.5, 4, 0), time = 0.5)
        self.stopLookAround()
        self.lerpLookAt(Point3(av.getPos(self)), time = 0.5)

    def b_setPageNumber(self, paragraph, pageNumber):
        self.setPageNumber(paragraph, pageNumber)
        self.d_setPageNumber(paragraph, pageNumber)

    def d_setPageNumber(self, paragraph, pageNumber):
        timestamp = ClockDelta.globalClockDelta.getFrameNetworkTime()
        self.sendUpdate('setPageNumber', [paragraph, pageNumber, timestamp])

    def freeAvatar(self):
        base.localAvatar.posCamera(0, 0)
        base.cr.playGame.getPlace().setState('walk')

    def setPositionIndex(self, posIndex):
        self.posIndex = posIndex

    def wantGroupTracker(self): # Override so we don't use this
        pass

    def promptInteraction(self, collEntry):
        if base.wantNpcInteract:
            self.accept('exit' + self.cSphereNode.getName(), self.handleCollisionSphereExit)
            self.accept('stickerBookEntered', self.handleCollisionSphereExit, [collEntry])
            self.accept(base.INTERACT_KEY, self.interact, [collEntry])
            if hasattr(self, "name"):
                text = ("Press %s to interact with %s" % (base.INTERACT_KEY.upper(), self.name))
            else:
                text = ("Press %s to interact" % base.INTERACT_KEY.upper())
            if sys.platform == 'android':
                self.enterText = MATShuffleButton(relief = None, parent = base.a2dBottomCenter, text = ("Tap to interact"), text_style = 3, text_scale = .07, text_pos = (0, -0.02), text_fg = (1, 0.9, 0.1, 1), scale = 1.5, pos = (0.0, 0.0, 0.5), command = self.interact, extraArgs = [collEntry])
            else:
                self.enterText = OnscreenText(text, style = 3, scale = .07, parent = base.a2dBottomCenter, fg = (ColorGlobals.CDefault), pos = (0.0, 0.45))
            self.enterText.setColorScale(VBase4(1, 1, 1, 0))
            self.colorSeq = Sequence(
                LerpColorScaleInterval(self.enterText, .4, VBase4(1, 1, 1, 1), blendType = 'easeInOut'),
                LerpColorScaleInterval(self.enterText, .4, VBase4(.8, .8, .8, .8), blendType = 'easeInOut')).loop()
        else:
            self.handleCollisionSphereEnter(collEntry)

    def interact(self, collEntry):
        self.ignore(base.INTERACT_KEY)
        if hasattr(self, "colorSeq") and self.colorSeq:
            self.colorSeq.finish()
        if hasattr(self, "enterText"):
            self.enterText.removeNode()
            del self.enterText

        self.handleCollisionSphereEnter(collEntry)

    def handleCollisionSphereExit(self, collEntry):
        self.ignore(base.INTERACT_KEY)
        if hasattr(self, "colorSeq") and self.colorSeq:
            self.colorSeq.finish()
        if hasattr(self, "enterText"):
            self.enterText.removeNode()
            del self.enterText
