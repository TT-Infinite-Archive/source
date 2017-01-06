from toontown.battle.DistributedBattleWaiters import DistributedBattleWaiters

import random
from pandac.PandaModules import VBase3, Point3, Vec4
from direct.interval.IntervalGlobal import Sequence, Func, Parallel, Track, Wait, SoundInterval, LerpColorScaleInterval
from toontown.battle import DistributedBattleFinal, SuitBattleGlobals
from toontown.chat.ChatGlobals import CFSpeech, CFTimeout
from toontown.suit import SuitTimings
from toontown.toonbase import ToontownGlobals

class DistributedBattleVault(DistributedBattleWaiters):

    def announceGenerate(self):
        DistributedBattleFinal.DistributedBattleFinal.announceGenerate(self)
        # self.moveSuitsToInitialPos()

    def doInitialFlyDown(self):
        self.showSuitsFalling(self.suits, 0, self.uniqueName('initial-FlyDown'), self.flyDownDone)

    def flyDownDone(self):
        print 'flyDownDone'

    def showSuitsFalling(self, suits, ts, name, callback):
        if self.bossCog == None:
            return
        suitTrack = Parallel()
        delay = 0
        for suit in suits:
            failSound = loader.loadSfx('phase_11/audio/sfx/LB_laser_beam_on_2.ogg')
            suit.makeVirtual(healthColored=True)
            suit.setState('Battle')
            if suit.dna.dept == 'l':
                suit.reparentTo(self.bossCog)
                suit.setPos(0, 0, 0)
            if suit in self.joiningSuits:
                i = len(self.pendingSuits) + self.joiningSuits.index(suit)
                destPos, h = self.suitPendingPoints[i]
                destHpr = VBase3(h, 0, 0)
            else:
                destPos, destHpr = self.getActorPosHpr(suit, self.suits)
            startPos = destPos + Point3(0, 0, SuitTimings.fromSky * ToontownGlobals.SuitWalkSpeed)
            self.notify.debug('startPos for %s = %s' % (suit, startPos))
            suit.reparentTo(hidden)
            suit.setPos(startPos)
            suit.headsUp(self)
            flyIval = suit.beginSupaFlyMove(destPos, True, 'flyIn')
            taunt = SuitBattleGlobals.getFaceoffTaunt(suit.getStyleName(), suit.doId)
            soundTrack = SoundInterval(failSound, node=suit, volume=0.8)
            suitTrack.append(
                Track(
                    (delay,
                     Sequence(
                         Parallel(
                             flyIval,
                             Sequence(
                                 Wait(2.6),
                                 Func(suit.reparentTo, self),
                                 Parallel(
                                     soundTrack,
                                     suit.scaleInterval(0.6, (1, 1, 1), startScale=(0.01, 0.01, 0.01), blendType='easeIn'),
                                     # suit.posInterval(0.5,
                                     #                 (suit.getX(), suit.getY(), suit.getZ()),
                                     #                 (suit.getX(), suit.getY(), suit.getZ() + 3.5),
                                     #                 blendType='easeInOut'),
                                     LerpColorScaleInterval(suit, 0.75, Vec4(1, 1, 1, 1),
                                                           startColorScale=Vec4(1, 1, 1, 0), blendType='easeIn'),
                                     Sequence(Wait(0.62), Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout)),
                                 ),
                             )
                         ),
                         Func(suit.loop, 'neutral'),
                     )
                     )
                )
            )
            delay += 1.1

        if self.hasLocalToon():
            base.camera.reparentTo(self)
            if random.choice([0, 1]):
                base.camera.setPosHpr(20, -4, 7, 60, 0, 0)
            else:
                base.camera.setPosHpr(-20, -4, 7, -60, 0, 0)
        done = Func(callback)
        track = Sequence(suitTrack, done, name=name)
        track.start(ts)
        self.storeInterval(track, name)
        return
