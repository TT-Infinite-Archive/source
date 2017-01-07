from panda3d.core import Vec3
from direct.task.Task import Task
from direct.interval.IntervalGlobal import Sequence
from direct.distributed.ClockDelta import globalClockDelta
from toontown.toon.DistributedNPCToonBase import DistributedNPCToonBase
from toontown.toon import NPCToons
from toontown.chat.ChatGlobals import *
from toontown.minigame import ClerkPurchase
from toontown.toonbase import TTLocalizer, EventGlobals
from toontown.toontowngui.GagSelectGui import GagSelectGui


class DistributedNPCClerk(DistributedNPCToonBase):
    def __init__(self, cr):
        DistributedNPCToonBase.__init__(self, cr)

        self.purchase = None
        self.av = None
        self.timeout = 0

    def disable(self):
        self.ignoreAll()
        taskMgr.remove(self.uniqueName('popupPurchaseGUI'))
        taskMgr.remove(self.uniqueName('lerpCamera'))
        if self.purchase:
            self.purchase.destroy()
            self.purchase = None
        self.av = None
        base.localAvatar.posCamera(0, 0)

        DistributedNPCToonBase.disable(self)

    def handleCollisionSphereEnter(self, collEntry):
        base.cr.playGame.getPlace().fsm.request('purchase')
        self.sendUpdate('avatarEnter', [])

    def __handleUnexpectedExit(self):
        self.notify.warning('Unexpected exit')
        self.av = None

    def resetClerk(self):
        self.ignoreAll()
        taskMgr.remove(self.uniqueName('popupPurchaseGUI'))
        taskMgr.remove(self.uniqueName('lerpCamera'))
        if self.purchase:
            self.purchase.destroy()
            self.purchase = None
        self.clearMat()
        self.startLookAround()
        self.detectAvatars()
        if self.hasLocalToon():
            self.showNametag2d()
            self.freeAvatar()
        return Task.done

    def hasLocalToon(self):
        return self.av.doId == base.localAvatar.doId

    def setMovie(self, mode, npcId, avId, timestamp):
        timeStamp = globalClockDelta.localElapsedTime(timestamp)
        self.timeout = NPCToons.CLERK_COUNTDOWN_TIME - timeStamp
        self.isLocalToon = avId == base.localAvatar.doId
        if mode == NPCToons.PURCHASE_MOVIE_CLEAR:
            return
        if mode == NPCToons.PURCHASE_MOVIE_TIMEOUT:
            taskMgr.remove(self.uniqueName('popupPurchaseGUI'))
            taskMgr.remove(self.uniqueName('lerpCamera'))
            if self.hasLocalToon():
                pass
                # self.ignore(self.purchaseDoneEvent)
            if self.purchase:
                self.purchase.destroy()
                self.purchase = None
            self.setChatAbsolute(TTLocalizer.STOREOWNER_TOOKTOOLONG, CFSpeech | CFTimeout)
            self.resetClerk()
        elif mode == NPCToons.PURCHASE_MOVIE_START:
            if self.isLocalToon:
                self.hideNametag2d()
            self.av = base.cr.doId2do.get(avId)
            if self.av is None:
                self.notify.warning('Avatar %d not found in doId' % avId)
                return
            else:
                self.accept(self.av.uniqueName('disable'), self.__handleUnexpectedExit)
            self.setupAvatars(self.av)
            if self.isLocalToon:
                base.camera.wrtReparentTo(render)
                seq = Sequence((base.camera.posQuatInterval(1, Vec3(-5, 9, self.getHeight() - 0.5), Vec3(-150, -2, 0), other=self, blendType='easeOut', name=self.uniqueName('lerpCamera'))))
                seq.start()
            self.setChatAbsolute(TTLocalizer.STOREOWNER_GREETING, CFSpeech | CFTimeout)
            if self.isLocalToon:
                taskMgr.doMethodLater(1.0, self.popupPurchaseGUI, self.uniqueName('popupPurchaseGUI'))
        elif mode == NPCToons.PURCHASE_MOVIE_COMPLETE:
            self.setChatAbsolute(TTLocalizer.STOREOWNER_GOODBYE, CFSpeech | CFTimeout)
            self.resetClerk()
        elif mode == NPCToons.PURCHASE_MOVIE_NO_MONEY:
            self.setChatAbsolute(TTLocalizer.STOREOWNER_NEEDJELLYBEANS, CFSpeech | CFTimeout)
            self.resetClerk()
        return

    def popupPurchaseGUI(self, task):
        self.setChatAbsolute('', CFSpeech)
        self.purchase = GagSelectGui(base.localAvatar, self.timeout)
        return Task.done

    def __handleUnequipSlot(self, slot):
        pass

    def __handleEquipGag(self, gag):
        pass

    def d_setInventory(self, invString, money, done):
        self.sendUpdate('setInventory', [invString, money, done])
