from direct.fsm import ClassicFSM, State
from direct.gui.DirectGui import *
from direct.task.Task import Task
import time

from .DistributedNPCToonBase import *
from toontown.chat.ChatGlobals import *
from toontown.effects import DustCloud
from toontown.nametag.NametagGlobals import *
from toontown.toonbase import TTLocalizer
from toontown.toon import ToonDNA


def getDustCloudIval(toon):
    dustCloud = DustCloud.DustCloud(fBillboard=0)
    dustCloud.setBillboardAxis(2.0)
    dustCloud.setZ(3)
    dustCloud.setScale(0.4)
    dustCloud.createTrack()
    if getattr(toon, 'laffMeter', None):
        toon.laffMeter.color = toon.style.getBlackColor()
    seq = Sequence(Wait(0.5), Func(dustCloud.reparentTo, toon), dustCloud.track, Func(dustCloud.destroy))
    if getattr(toon, 'laffMeter', None):
        seq.append(Func(toon.laffMeter.adjustFace, toon.hp, toon.maxHp))
    return seq


class DistributedNPCYin(DistributedNPCToonBase):
    def __init__(self, cr):
        DistributedNPCToonBase.__init__(self, cr)

        self.pickColorGui = None
        self.pickColorGuiDoneEvent = 'pickColorGuiDone'

        self.nextCollision = 0

        self.fsm = ClassicFSM.ClassicFSM(
            'NPCYin',
            [
                State.State('off', self.enterOff, self.exitOff,
                            ['pickColor', 'trickOrTreatSpeech']),
                State.State('pickColor', self.enterPickColor,
                            self.exitPickColor, ['off', 'trickOrTreatSpeech']),
                State.State('trickOrTreatSpeech', self.enterTrickOrTreatSpeech,
                            self.exitTrickOrTreatSpeech, ['off', 'pickColor'])
            ], 'off', 'off')
        self.fsm.enterInitialState()

        self.title = None
        self.yesButton = None
        self.noButton = None

        self.trickOrTreatSpeech = None

        self.buttonModels = loader.loadModel('phase_3.5/models/gui/inventory_gui')
        self.upButton = self.buttonModels.find('**//InventoryButtonUp')
        self.downButton = self.buttonModels.find('**/InventoryButtonDown')
        self.rolloverButton = self.buttonModels.find('**/InventoryButtonRollover')

    def disable(self):
        self.ignoreAll()

        if self.title:
            self.title.destroy()
            self.title = None

        if self.yesButton:
            self.yesButton.destroy()
            self.yesButton = None

        if self.noButton:
            self.noButton.destroy()
            self.noButton = None

        if self.trickOrTreatSpeech is not None:
            self.trickOrTreatSpeech.finish()
            self.trickOrTreatSpeech = None

        if self.buttonModels:
            self.buttonModels.removeNode()
            self.buttonModels = None

        if self.upButton:
            self.upButton.removeNode()
            self.upButton = None

        if self.downButton:
            self.downButton.removeNode()
            self.downButton = None

        if self.rolloverButton:
            self.rolloverButton.removeNode()
            self.rolloverButton = None

        if self.pickColorGui:
            self.pickColorGui.destroy()
            self.pickColorGui = None

        self.nextCollision = 0

        DistributedNPCToonBase.disable(self)

    def initToonState(self):
        self.setAnimState('neutral', 1.05, None, None)
        if (base.cr.newsManager is not None) and base.cr.newsManager.isHolidayRunning(ToontownGlobals.HALLOWEEN):
            self.setPosHpr(-53.576, -14.410, -1.934, 212.58, 0, 0)

            self.style.topTex = 94
            self.style.sleeveTex = 83
            self.style.botTex = 36
            self.setDNA(self.style)

            for head in self.findAllMatches('**/__Actor_head'):
                for p in head.getChildren():
                    if hasattr(self, 'pumpkins') and (not self.pumpkins.hasPath(p)):
                        p.hide()
                        p.setTag('pumpkin', 'enabled')

            self.setCheesyEffect(ToontownGlobals.CEPumpkin, 0, 0)

            self.trickOrTreatSpeech = Sequence()
            for speechText in TTLocalizer.YinTrickOrTreatHints:
                self.trickOrTreatSpeech.append(Func(self.setChatAbsolute, speechText, CFSpeech))
                self.trickOrTreatSpeech.append(Wait(0.55 * len(speechText.split(' '))))
                self.trickOrTreatSpeech.append(Func(self.clearChat))
                self.trickOrTreatSpeech.append(Wait(6))

            self.fsm.request('trickOrTreatSpeech')
        else:
            self.setPosHpr(101, 15.5, 4, -245, 0, 0)

    def getCollSphereRadius(self):
        return 1.0

    def handleCollisionSphereEnter(self, collEntry):
        self.currentTime = time.time()
        if self.nextCollision <= self.currentTime:
            self.fsm.request('pickColor')
        self.nextCollision = self.currentTime + 2

    def enterOff(self):
        pass

    def exitOff(self):
        pass

    def enterPickColor(self):
        base.cr.playGame.getPlace().setState('stopped')
        taskMgr.doMethodLater(15, self.leave, 'npcSleepTask-%s' % self.doId)
        self.setChatAbsolute('', CFSpeech)
        if base.localAvatar.style.getAnimal() != 'cat':
            self.setChatAbsolute(TTLocalizer.YinNotCat, CFSpeech|CFTimeout)
            if (base.cr.newsManager is not None) and base.cr.newsManager.isHolidayRunning(ToontownGlobals.HALLOWEEN):
                taskMgr.doMethodLater(
                    2, self.fsm.request, 'trickOrTreatSpeechTask',
                    extraArgs=['trickOrTreatSpeech'])
            else:
                self.fsm.request('off')
            base.cr.playGame.getPlace().setState('walk')
        elif ToonDNA.getColorIdFromColorDna(base.localAvatar.style.colorDNA.headColor) == 0x1a:
            self.setChatAbsolute(TTLocalizer.YinAlreadyBlack, CFSpeech|CFTimeout)
            if (base.cr.newsManager is not None) and base.cr.newsManager.isHolidayRunning(ToontownGlobals.HALLOWEEN):
                taskMgr.doMethodLater(
                    2, self.fsm.request, 'trickOrTreatSpeechTask',
                    extraArgs=['trickOrTreatSpeech'])
            else:
                self.fsm.request('off')
            base.cr.playGame.getPlace().setState('walk')
        else:
            self.popupPickColorGUI()

    def exitPickColor(self, task=None):
        taskMgr.remove('npcSleepTask-%s' % self.doId)
        if self.title:
            self.title.destroy()
            self.title = None
        if self.yesButton:
            self.yesButton.destroy()
            self.yesButton = None
        if self.noButton:
            self.noButton.destroy()
            self.noButton = None

        if task is not None:
            return task.done

    def enterTrickOrTreatSpeech(self):
        if self.trickOrTreatSpeech is not None:
            self.trickOrTreatSpeech.loop()

    def exitTrickOrTreatSpeech(self):
        if self.trickOrTreatSpeech is not None:
            self.trickOrTreatSpeech.pause()

    def popupPickColorGUI(self):
        self.setChatAbsolute('', CFSpeech)
        self.setChatAbsolute(TTLocalizer.YinPickColor, CFSpeech)
        base.setCellsActive(base.bottomCells, 0)

        self.title = DirectLabel(
            aspect2d, relief=None, text=TTLocalizer.YinTitle,
            text_pos=(0, 0), text_fg=(1, 0, 0, 1), text_scale=0.09,
            text_font=ToontownGlobals.getSignFont(),
            pos=(0, 0, -0.55), text_shadow=(1, 1, 1, 1))
        self.yesButton = DirectButton(
            relief=None, text=TTLocalizer.lYes,
            text_fg=(1, 1, 0.65, 1), text_pos=(0, -0.23),
            text_scale=0.8, image=(self.upButton, self.downButton, self.rolloverButton),
            image_color=(1, 0, 0, 1), image_scale=(20, 1, 11), pos=(-0.275, 0, -0.75), scale=0.15,
            command=lambda self=self: self.d_requestTransformation())
        self.noButton = DirectButton(
            relief=None, text=TTLocalizer.lNo,
            text_fg=(1, 1, 0.65, 1), text_pos=(0, -0.23),
            text_scale=0.8, image=(self.upButton, self.downButton, self.rolloverButton),
            image_color=(1, 0, 0, 1), image_scale=(20, 1, 11), pos=(0.275, 0, -0.75), scale=0.15,
            command=lambda self=self: self.leave())

    def doTransformation(self, avId):
        av = self.cr.doId2do.get(avId)
        if not av:
            return
        if av.style.getAnimal() != 'cat':
            return
        self.dustCloudIval = getDustCloudIval(av)
        self.dustCloudIval.start()

        self.setChatAbsolute('', CFSpeech)
        self.setChatAbsolute(TTLocalizer.YinEnjoy, CFSpeech|CFTimeout)
        base.setCellsActive(base.bottomCells, 1)

    def d_requestTransformation(self):
        self.sendUpdate('requestTransformation', [])
        if (base.cr.newsManager is not None) and base.cr.newsManager.isHolidayRunning(ToontownGlobals.HALLOWEEN):
            taskMgr.doMethodLater(
                2, self.fsm.request, 'trickOrTreatSpeechTask',
                extraArgs=['trickOrTreatSpeech'])
        else:
            self.fsm.request('off')
        base.cr.playGame.getPlace().setState('walk')

    def leave(self, task=None):
        self.setChatAbsolute('', CFSpeech)
        self.setChatAbsolute(TTLocalizer.YinGoodbye, CFSpeech|CFTimeout)
        if (base.cr.newsManager is not None) and base.cr.newsManager.isHolidayRunning(ToontownGlobals.HALLOWEEN):
            taskMgr.doMethodLater(
                2, self.fsm.request, 'trickOrTreatSpeechTask',
                extraArgs=['trickOrTreatSpeech'])
        else:
            self.fsm.request('off')
        base.cr.playGame.getPlace().setState('walk')
        base.setCellsActive(base.bottomCells, 1)

        if task is not None:
            return task.done

