import copy

from direct.interval.IntervalGlobal import *
from direct.showbase import DirectObject

import BattleExperience
import GagMovies
import MovieSuitAttacks
import MovieToonVictory
import MovieUtil
import PlayByPlayText
import RewardPanel
from SuitBattleGlobals import *
from toontown.chat.ChatGlobals import *
from toontown.data import Gag
from toontown.distributed import DelayDelete
from toontown.nametag import NametagGlobals
from toontown.toonbase import ToontownGlobals
from toontown.toonbase.ToontownBattleGlobals import *
from toontown.toontowngui import TTDialog
from toontown.util.Queue import Queue

camPos = Point3(14, 0, 10)
camHpr = Vec3(89, -30, 0)
randomBattleTimestamp = base.config.GetBool('random-battle-timestamp', 0)

class Movie(DirectObject.DirectObject):
    notify = DirectNotifyGlobal.directNotify.newCategory('Movie')

    def __init__(self, battle):
        DirectObject.DirectObject.__init__(self)
        self.battle = battle
        self.track = None
        self.tmaQueue = Queue()
        self.smaQueue = Queue()
        self.rewardPanel = None
        self.rewardCallback = None
        self.playByPlayText = PlayByPlayText.PlayByPlayText()
        self.playByPlayText.hide()
        self.renderProps = []
        self.hasBeenReset = 0
        self.reset()
        self.rewardHasBeenReset = 0
        self.resetReward()

    def cleanup(self):
        self.reset()
        self.resetReward()
        self.battle = None
        if self.playByPlayText != None:
            self.playByPlayText.cleanup()
        self.playByPlayText = None
        if self.rewardPanel != None:
            self.rewardPanel.cleanup()
        self.rewardPanel = None
        self.rewardCallback = None
        return

    def needRestoreColor(self):
        self.restoreColor = 1

    def clearRestoreColor(self):
        self.restoreColor = 0

    def needRestoreHips(self):
        self.restoreHips = 1

    def clearRestoreHips(self):
        self.restoreHips = 0

    def needRestoreHeadScale(self):
        self.restoreHeadScale = 1

    def clearRestoreHeadScale(self):
        self.restoreHeadScale = 0

    def needRestoreToonScale(self):
        self.restoreToonScale = 1

    def clearRestoreToonScale(self):
        self.restoreToonScale = 0

    def needRestoreParticleEffect(self, effect):
        self.specialParticleEffects.append(effect)

    def clearRestoreParticleEffect(self, effect):
        if self.specialParticleEffects.count(effect) > 0:
            self.specialParticleEffects.remove(effect)

    def needRestoreRenderProp(self, prop):
        self.renderProps.append(prop)

    def clearRenderProp(self, prop):
        if self.renderProps.count(prop) > 0:
            self.renderProps.remove(prop)

    def restore(self):
        return
        for toon in self.battle.activeToons:
            toon.loop('neutral')
            origPos, origHpr = self.battle.getActorPosHpr(toon)
            toon.setPosHpr(self.battle, origPos, origHpr)
            hands = toon.getRightHands()[:]
            hands += toon.getLeftHands()
            for hand in hands:
                props = hand.getChildren()
                for prop in props:
                    if prop.getName() != 'book':
                        MovieUtil.removeProp(prop)

            if self.restoreColor == 1:
                headParts = toon.getHeadParts()
                torsoParts = toon.getTorsoParts()
                legsParts = toon.getLegsParts()
                partsList = [headParts, torsoParts, legsParts]
                for parts in partsList:
                    for partNum in xrange(0, parts.getNumPaths()):
                        nextPart = parts.getPath(partNum)
                        nextPart.clearColorScale()
                        nextPart.clearTransparency()

            if self.restoreHips == 1:
                parts = toon.getHipsParts()
                for partNum in xrange(0, parts.getNumPaths()):
                    nextPart = parts.getPath(partNum)
                    props = nextPart.getChildren()
                    for prop in props:
                        if prop.getName() == 'redtape-tube.egg':
                            MovieUtil.removeProp(prop)

            if self.restoreHeadScale == 1:
                headScale = ToontownGlobals.toonHeadScales[toon.style.getAnimal()]
                for lod in toon.getLODNames():
                    toon.getPart('head', lod).setScale(headScale)

            if self.restoreToonScale == 1:
                toon.setScale(1)
            headParts = toon.getHeadParts()
            for partNum in xrange(0, headParts.getNumPaths()):
                part = headParts.getPath(partNum)
                part.setHpr(0, 0, 0)
                part.setPos(0, 0, 0)

            arms = toon.findAllMatches('**/arms')
            sleeves = toon.findAllMatches('**/sleeves')
            hands = toon.findAllMatches('**/hands')
            for partNum in xrange(0, arms.getNumPaths()):
                armPart = arms.getPath(partNum)
                sleevePart = sleeves.getPath(partNum)
                handsPart = hands.getPath(partNum)
                armPart.setHpr(0, 0, 0)
                sleevePart.setHpr(0, 0, 0)
                handsPart.setHpr(0, 0, 0)

        for suit in self.battle.activeSuits:
            if suit._Actor__animControlDict != None:
                suit.loop('neutral')
                suit.battleTrapIsFresh = 0
                origPos, origHpr = self.battle.getActorPosHpr(suit)
                suit.setPosHpr(self.battle, origPos, origHpr)
                hands = [suit.getRightHand(), suit.getLeftHand()]
                for hand in hands:
                    props = hand.getChildren()
                    for prop in props:
                        MovieUtil.removeProp(prop)

        for effect in self.specialParticleEffects:
            if effect != None:
                effect.cleanup()

        self.specialParticleEffects = []
        for prop in self.renderProps:
            MovieUtil.removeProp(prop)

        self.renderProps = []
        return

    def _deleteTrack(self):
        if self.track:
            DelayDelete.cleanupDelayDeletes(self.track)
            self.track = None
        return

    def resetReward(self, finish = 0):
        if self.rewardHasBeenReset == 1:
            return
        self.rewardHasBeenReset = 1
        self.stop()
        self._deleteTrack()
        if finish == 1:
            self.restore()
        self.toonRewardDicts = []
        if self.rewardPanel != None:
            self.rewardPanel.destroy()
        self.rewardPanel = None
        return

    def play(self, ts, callback):
        self.hasBeenReset = 0
        self.tmaQueue.reset()
        self.smaQueue.reset()
        for tma in self.battle.toonMovieAttacks:
            # Queue up attacks
            self.tmaQueue.enqueue(tma)
        for sma in self.battle.suitMovieAttacks:
            # Queue up attacks
            self.smaQueue.enqueue(sma)

        self.playNextAttack(callback)

    def playNextAttack(self, callback):
        # Get the next attack and play the movie for it
        # If there are no attacks just end the movie
        if self.tmaQueue.empty() and self.smaQueue.empty():
            callback()
        elif not self.tmaQueue.empty():
            tma = self.tmaQueue.dequeue()
            self.track = Sequence()
            movieFunc = GagMovies.GagToMovieFunc.get(tma.attackId)
            if movieFunc:
                self.track.append(movieFunc(self.battle, tma))
            else:
                self.notify.warning('Gag %s has no movie defined!' % tma.attackId)
            self.track.append(Func(self.playDeadSuits, callback))
            self.track.start()
        else:
            sma = self.smaQueue.dequeue()
            self.track = Sequence()
            self.track.append(Func(self.playNextAttack, callback))
            self.track.start()

    def playDeadSuits(self, callback):
        # Play cogs dying in the event any of them died
        self.track = Sequence()
        deathTrack = Parallel()
        for suit in self.battle.activeSuits:
            if suit.getHp() <= 0:
                deathTrack.append(MovieUtil.suitDeath(suit, self.battle))
        self.track.append(deathTrack)
        self.track.append(Func(self.playNextAttack, callback))
        self.track.start()

    def reset(self):
        self.finish()
        self.track = None

    def finish(self):
        if self.track is not None:
            self.track.finish()

    def playReward(self, ts, name, callback, noSkip = False):
        self.rewardHasBeenReset = 0
        ptrack = Sequence()
        camtrack = Sequence()
        self.rewardPanel = RewardPanel.RewardPanel(name)
        self.rewardPanel.hide()
        victory, camVictory, skipper = MovieToonVictory.doToonVictory(self.battle.localToonActive(), self.battle.activeToons, self.toonRewardIds, self.toonRewardDicts, self.deathList, self.rewardPanel, 1, self.uberList, self.helpfulToonsList, noSkip=noSkip)
        if victory:
            skipper.setIvals((ptrack, camtrack), ptrack.getDuration())
            ptrack.append(victory)
            camtrack.append(camVictory)
        ptrack.append(Func(callback))
        self._deleteTrack()
        self.track = Sequence(ptrack, name='movie-reward-track-%d' % self.battle.doId)
        if self.battle.localToonActive():
            self.track = Parallel(self.track, camtrack, name='movie-reward-track-with-cam-%d' % self.battle.doId)
        self.track.delayDeletes = []
        for t in self.battle.activeToons:
            self.track.delayDeletes.append(DelayDelete.DelayDelete(t, 'Movie.playReward'))

        skipper.setIvals((self.track,), 0.0)
        skipper.setBattle(self.battle)
        self.track.start(ts)
        return None

    def playTutorialReward(self, ts, name, callback):
        self.rewardHasBeenReset = 0
        self.rewardPanel = RewardPanel.RewardPanel(name)
        self.rewardCallback = callback
        self.questList = self.rewardPanel.getQuestIntervalList(base.localAvatar, [0, 1, 1, 0], [base.localAvatar], base.localAvatar.quests[0], [], [base.localAvatar.getDoId()])
        base.camera.setPosHpr(0, 8, base.localAvatar.getHeight() * 0.66, 179, 15, 0)
        self.playTutorialReward_1()

    def playTutorialReward_1(self):
        self.tutRewardDialog_1 = TTDialog.TTDialog(text=TTLocalizer.MovieTutorialReward1, command=self.playTutorialReward_2, style=TTDialog.Acknowledge, fadeScreen=None, pos=(0.65, 0, 0.5), scale=0.8)
        self.tutRewardDialog_1.hide()
        self._deleteTrack()
        self.track = Sequence(name='tutorial-reward-1')
        self.track.append(Func(self.rewardPanel.initGagFrame, base.localAvatar, [0,
         0,
         0,
         0,
         0,
         0,
         0], [0,
         0,
         0,
         0], noSkip=True))
        self.track += self.rewardPanel.getTrackIntervalList(base.localAvatar, THROW_TRACK, 0, 1, 0)
        self.track.append(Func(self.tutRewardDialog_1.show))
        self.track.start()
        return

    def playTutorialReward_2(self, value):
        self.tutRewardDialog_1.cleanup()
        self.tutRewardDialog_2 = TTDialog.TTDialog(text=TTLocalizer.MovieTutorialReward2, command=self.playTutorialReward_3, style=TTDialog.Acknowledge, fadeScreen=None, pos=(0.65, 0, 0.5), scale=0.8)
        self.tutRewardDialog_2.hide()
        self._deleteTrack()
        self.track = Sequence(name='tutorial-reward-2')
        self.track.append(Wait(1.0))
        self.track += self.rewardPanel.getTrackIntervalList(base.localAvatar, SQUIRT_TRACK, 0, 1, 0)
        self.track.append(Func(self.tutRewardDialog_2.show))
        self.track.start()
        return

    def playTutorialReward_3(self, value):
        self.tutRewardDialog_2.cleanup()
        from toontown.toon import Toon
        from toontown.toon import ToonDNA

        def doneChat1(page, elapsed = 0):
            self.track2.start()

        def doneChat2(elapsed):
            self.track2.pause()
            self.track3.start()

        def uniqueName(hook):
            return 'TutorialTom-' + hook

        self.tutorialTom = Toon.Toon()
        dna = ToonDNA.ToonDNA()
        dnaList = ('dls', 'ms', 'm', 'm', 7, 0, 7, 7, 2, 6, 2, 6, 2, 16)
        dna.newToonFromProperties(*dnaList)
        self.tutorialTom.setDNA(dna)
        self.tutorialTom.setName(TTLocalizer.NPCToonNames[20000])
        self.tutorialTom.setPickable(0)
        self.tutorialTom.setPlayerType(NametagGlobals.CCNonPlayer)
        self.tutorialTom.uniqueName = uniqueName
        if base.config.GetString('language', 'english') == 'japanese':
            self.tomDialogue03 = loader.loadSfx('phase_3.5/audio/dial/CC_tom_movie_tutorial_reward01.ogg')
            self.tomDialogue04 = loader.loadSfx('phase_3.5/audio/dial/CC_tom_movie_tutorial_reward02.ogg')
            self.tomDialogue05 = loader.loadSfx('phase_3.5/audio/dial/CC_tom_movie_tutorial_reward03.ogg')
            self.musicVolume = base.config.GetFloat('tutorial-music-volume', 0.5)
        else:
            self.tomDialogue03 = None
            self.tomDialogue04 = None
            self.tomDialogue05 = None
            self.musicVolume = 0.9
        music = base.cr.playGame.place.loader.battleMusic
        if self.questList:
            self.track1 = Sequence(Wait(1.0), Func(self.rewardPanel.initQuestFrame, base.localAvatar, copy.deepcopy(base.localAvatar.quests)), Wait(1.0), Sequence(*self.questList), Wait(1.0), Func(self.rewardPanel.hide), Func(base.camera.setPosHpr, render, 34, 19.88, 3.48, -90, -2.36, 0), Func(base.localAvatar.animFSM.request, 'neutral'), Func(base.localAvatar.setPosHpr, 40.31, 22.0, -0.47, 150.0, 360.0, 0.0), Wait(0.5), Func(self.tutorialTom.reparentTo, render), Func(self.tutorialTom.show), Func(self.tutorialTom.setPosHpr, 40.29, 17.9, -0.47, 11.31, 0.0, 0.07), Func(self.tutorialTom.animFSM.request, 'TeleportIn'), Wait(1.517), Func(self.tutorialTom.animFSM.request, 'neutral'), Func(self.acceptOnce, self.tutorialTom.uniqueName('doneChatPage'), doneChat1), Func(self.tutorialTom.addActive), Func(music.setVolume, self.musicVolume), Func(self.tutorialTom.setLocalPageChat, TTLocalizer.MovieTutorialReward3, 0, None, [self.tomDialogue03]), name='tutorial-reward-3a')
            self.track2 = Sequence(Func(self.acceptOnce, self.tutorialTom.uniqueName('doneChatPage'), doneChat2), Func(self.tutorialTom.setLocalPageChat, TTLocalizer.MovieTutorialReward4, 1, None, [self.tomDialogue04]), Func(self.tutorialTom.setPlayRate, 1.5, 'right-hand-start'), Func(self.tutorialTom.play, 'right-hand-start'), Wait(self.tutorialTom.getDuration('right-hand-start') / 1.5), Func(self.tutorialTom.loop, 'right-hand'), name='tutorial-reward-3b')
            self.track3 = Parallel(Sequence(Func(self.tutorialTom.setPlayRate, -1.8, 'right-hand-start'), Func(self.tutorialTom.play, 'right-hand-start'), Wait(self.tutorialTom.getDuration('right-hand-start') / 1.8), Func(self.tutorialTom.animFSM.request, 'neutral'), name='tutorial-reward-3ca'), Sequence(Wait(0.5), Func(self.tutorialTom.setChatAbsolute, TTLocalizer.MovieTutorialReward5, CFSpeech | CFTimeout, self.tomDialogue05), Wait(1.0), Func(self.tutorialTom.animFSM.request, 'TeleportOut'), Wait(self.tutorialTom.getDuration('teleport')), Wait(1.0), Func(self.playTutorialReward_4, 0), name='tutorial-reward-3cb'), name='tutorial-reward-3c')
            self.track1.start()
        else:
            self.playTutorialReward_4(0)
        return

    def playTutorialReward_4(self, value):
        base.localAvatar.setH(270)
        self.tutorialTom.removeActive()
        self.tutorialTom.delete()
        self.questList = None
        self.rewardCallback()
        return

    def stop(self):
        if self.track:
            self.track.finish()
            self._deleteTrack()
        if hasattr(self, 'track1'):
            self.track1.finish()
            self.track1 = None
        if hasattr(self, 'track2'):
            self.track2.finish()
            self.track2 = None
        if hasattr(self, 'track3'):
            self.track3.finish()
            self.track3 = None
        if self.rewardPanel:
            self.rewardPanel.hide()
        if self.playByPlayText:
            self.playByPlayText.hide()
        return

    def genRewardDicts(self, id0, origExp0, earnedExp0, origQuests0, items0, missedItems0, origMerits0, merits0, parts0, id1, origExp1, earnedExp1, origQuests1, items1, missedItems1, origMerits1, merits1, parts1, id2, origExp2, earnedExp2, origQuests2, items2, missedItems2, origMerits2, merits2, parts2, id3, origExp3, earnedExp3, origQuests3, items3, missedItems3, origMerits3, merits3, parts3, deathList, uberList, helpfulToonsList):
        self.deathList = deathList
        self.helpfulToonsList = helpfulToonsList
        entries = ((id0,
          origExp0,
          earnedExp0,
          origQuests0,
          items0,
          missedItems0,
          origMerits0,
          merits0,
          parts0),
         (id1,
          origExp1,
          earnedExp1,
          origQuests1,
          items1,
          missedItems1,
          origMerits1,
          merits1,
          parts1),
         (id2,
          origExp2,
          earnedExp2,
          origQuests2,
          items2,
          missedItems2,
          origMerits2,
          merits2,
          parts2),
         (id3,
          origExp3,
          earnedExp3,
          origQuests3,
          items3,
          missedItems3,
          origMerits3,
          merits3,
          parts3))
        self.toonRewardDicts = BattleExperience.genRewardDicts(entries)
        self.toonRewardIds = [id0,
         id1,
         id2,
         id3]
        self.uberList = uberList

    def genAttackDicts(self, toons, suits, toonAttacks, suitAttacks):
        if self.track and self.track.isPlaying():
            self.notify.warning('genAttackDicts() - track is playing!')
        self.__genToonAttacks(toonAttacks)
        self.__genSuitAttacks(suitAttacks)

    def __genToonAttacks(self, toonAttacks):
        for ta in toonAttacks:
            tma = BattleAttack.MovieAttack()
            tma.fromList(ta)
            self.toonMovieAttacks.append(tma)

    def __findToonAttack(self, type):
        tp = []
        for tma in self.toonMovieAttacks:
            if tma.attackId == PASS:
                continue
            attack = Gag.Gags.get(tma.attackId)
            if attack is None:
                continue
            elif attack.targetsAlly() and type == HEAL:
                tp.append(tma)
        return tp

    def __genSuitAttacks(self, suitMovieAttacks):
        for sma in suitMovieAttacks:
            suitMovieAttack = BattleAttack.MovieAttack()
            suitMovieAttack.fromList(sma)
            self.suitMovieAttacks.append(suitMovieAttack)

    def __doSuitAttacks(self):
        if base.config.GetBool('want-suit-anims', 1):
            track = Sequence(name='suit-attacks')
            camTrack = Sequence(name='suit-attacks-cam')
            #isLocalToonSad = False
            for sma in self.suitMovieAttacks:
                ival, camIval = MovieSuitAttacks.doSuitAttack(sma)
                if ival:
                    track.append(ival)
                    camTrack.append(camIval)
                '''
                targetField = sma.get('target')
                if targetField is None:
                    continue
                if sma['group'] == ATK_TGT_GROUP:
                    for target in targetField:
                        if target['died'] and target['toon'].doId == base.localAvatar.doId:
                            isLocalToonSad = True

                elif sma['group'] == ATK_TGT_SINGLE:
                    if targetField['died'] and targetField['toon'].doId == base.localAvatar.doId:
                        isLocalToonSad = True
                if isLocalToonSad:
                    break
                '''

            if len(track) == 0:
                return (None, None)
            return (track, camTrack)
        else:
            return (None, None)
