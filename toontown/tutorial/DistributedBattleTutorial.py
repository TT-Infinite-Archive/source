from panda3d.core import Point3, VBase3
from direct.interval.IntervalGlobal import Sequence, Func, Wait, Parallel
from toontown.battle import DistributedBattle, SuitBattleGlobals
from toontown.battle.BattleBase import BATTLE_SMALL_VALUE, FACEOFF_TAUNT_T, FACEOFF_LOOK_AT_PROP_T
from toontown.distributed import DelayDelete
from direct.directnotify import DirectNotifyGlobal
from toontown.util import PlacerTool3D
from toontown.nametag import NametagGlobals
from otp.avatar import Emote
from toontown.chat.ChatGlobals import CFSpeech, CFTimeout
import random


class DistributedBattleTutorial(DistributedBattle.DistributedBattle):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedBattleTutorial')

    def generate(self):
        DistributedBattle.DistributedBattle.generate(self)
        self.accept('islands-loaded', self.__handleIslandsLoaded)

    def disable(self):
        self.ignore('islands-loaded')
        DistributedBattle.DistributedBattle.disable(self)

    def setPosition(self, x, y, z):
        pos = Point3(x, y, z)
        self.setPos(base.cr.playGame.hood.loader.islands[1], pos)
        PlacerTool3D.PlacerTool3D(self)

    def startTimer(self, ts = 0):
        self.townBattle.timer.hide()

    def playReward(self, ts):
        self.movie.playTutorialReward(ts, self.uniqueName('reward'), self.handleRewardDone)

    def __handleIslandsLoaded(self, e=None):
        self.reparentTo(base.cr.playGame.hood.loader.islands[1])

    def handleRewardDone(self):
        DistributedBattle.DistributedBattle.handleRewardDone(self)

    def enterFaceOff(self, ts):
        self.notify.debug('enterFaceOff()')
        self.delayDeleteMembers()
        if len(self.toons) > 0 and base.localAvatar == self.toons[0]:
            Emote.globalEmote.disableAll(self.toons[0], 'dbattle, enterFaceOff')
        self.__faceOff(ts, self.faceOffName, self.__handleFaceOffDone)
        if self.interactiveProp:
            self.interactiveProp.gotoFaceoff()

    def __handleFaceOffDone(self):
        print('faceoff done')
        self.notify.debug('FaceOff done')
        if len(self.toons) > 0 and base.localAvatar == self.toons[0]:
            self.d_faceOffDone(base.localAvatar.doId)

    def __faceOff(self, ts, name, callback):
        print('faceoff in distributed tutorial')
        if len(self.suits) == 0:
            self.notify.warning('__faceOff(): no suits.')
            return
        if len(self.toons) == 0:
            self.notify.warning('__faceOff(): no toons.')
            return
        suit = self.suits[0]
        point = self.suitPoints[0][0]
        suitPos = point[0]
        suitHpr = VBase3(point[1], 0.0, 0.0)
        toon = self.toons[0]
        point = self.toonPoints[0][0]
        toonPos = point[0]
        toonHpr = VBase3(point[1], 0.0, 0.0)
        p = toon.getPos(self)
        toon.setPos(self, p[0], p[1], 0.0)
        toon.setShadowHeight(0)
        suit.setState('Battle')
        suitTrack = Sequence()
        toonTrack = Sequence()
        suitTrack.append(Func(suit.loop, 'neutral'))
        suitTrack.append(Func(suit.headsUp, toon))
        taunt = SuitBattleGlobals.getFaceoffTaunt(suit.getStyleName(), suit.doId)
        suitTrack.append(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
        toonTrack.append(Func(toon.loop, 'neutral'))
        toonTrack.append(Func(toon.headsUp, suit))
        suitHeight = suit.getHeight()
        suitOffsetPnt = Point3(0, 0, suitHeight)
        delay = FACEOFF_TAUNT_T
        if self.hasLocalToon():
            MidTauntCamHeight = suitHeight * 0.66
            MidTauntCamHeightLim = suitHeight - 1.8
            if MidTauntCamHeight < MidTauntCamHeightLim:
                MidTauntCamHeight = MidTauntCamHeightLim
            TauntCamY = 16
            TauntCamX = random.choice((-5, 5))
            TauntCamHeight = random.choice((MidTauntCamHeight, 1, 11))
            camTrack = Sequence()
            camTrack.append(Func(base.camera.wrtReparentTo, suit))
            camTrack.append(Func(base.camLens.setMinFov, self.camFOFov/(4./3.)))
            camTrack.append(Func(base.camera.setPos, TauntCamX, TauntCamY, TauntCamHeight))
            camTrack.append(Func(base.camera.lookAt, suit, suitOffsetPnt))
            camTrack.append(Wait(delay))
            camTrack.append(Func(base.camLens.setMinFov, self.camFov/(4./3.)))
            camTrack.append(Func(base.camera.wrtReparentTo, self))
            camTrack.append(Func(base.camera.setPos, self.camFOPos))
            camTrack.append(Func(base.camera.lookAt, suit.getPos(self)))
            if self.interactiveProp:
                camTrack.append(Func(base.camera.lookAt, self.interactiveProp.node.getPos(self)))
                camTrack.append(Wait(FACEOFF_LOOK_AT_PROP_T))
        suitTrack.append(Wait(delay))
        toonTrack.append(Wait(delay))
        suitTrack.append(Func(suit.clearChat))
        suitTrack.append(Func(suit.setPos, self, suitPos))
        suitTrack.append(Func(suit.setHpr, self, suitHpr))
        toonTrack.append(Func(toon.setPos, self, toonPos))
        toonTrack.append(Func(toon.setHpr, self, toonHpr))
        mtrack = Parallel(suitTrack, toonTrack)
        if self.hasLocalToon():
            NametagGlobals.setWant2dNametags(False)
            mtrack = Parallel(mtrack, camTrack)
        done = Func(callback)
        track = Sequence(mtrack, done, name=name)
        track.delayDeletes = [DelayDelete.DelayDelete(toon, '__faceOff'), DelayDelete.DelayDelete(suit, '__faceOff')]
        track.start(ts)
        self.storeInterval(track, name)
