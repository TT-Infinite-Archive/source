from panda3d.core import Vec3, Quat, headsUp

from direct.interval.IntervalGlobal import *

from toontown.chat.ChatGlobals import *
from direct.interval.IntervalGlobal import *
from direct.distributed.DistributedObject import DistributedObject
from direct.fsm.FSM import FSM
from direct.gui.DirectGui import *
from toontown.toonbase import ToontownGlobals, TTLocalizer
from toontown.toon import NPCToons
from toontown.suit import DistributedSuitBase, SuitDNA
from direct.directnotify import DirectNotifyGlobal
from direct.distributed.ClockDelta import globalClockDelta
from toontown.effects.DustCloud import DustCloud
from toontown.battle.BattleProps import globalPropPool
from toontown.battle.MovieSuitAttacks import getSoundTrack
import StormGlobals


class DistributedStormEvent(DistributedObject, FSM):
    notify = DirectNotifyGlobal.directNotify.newCategory("DistributedStormEvent")

    def __init__(self, cr):
        DistributedObject.__init__(self, cr)
        FSM.__init__(self, 'StormFSM')
        self.cr.storm = self
        self.sequence = None
        self.actors = []
        self.props = []
        self.image = None
        self.subtitle = None

        self.loadActors()
        self.loadProps()
    
    def disable(self):
        DistributedObject.disable(self)
        self.request('Off', 0)

    def setState(self, state, time):
        self.request(state, globalClockDelta.localElapsedTime(time))
    
    def getActors(self):
        return self.actors
    
    def getProps(self):
        return self.props
    
    def hideActors(self):
        for actor in self.actors:
            if actor:
                actor.hide()
                actor.removeActive()
    
    def showActors(self):
        for actor in self.actors:
            if actor:
                actor.show()
                actor.addActive()
    
    def deleteActors(self):
        for actor in self.actors:
            if actor:
                actor.delete()
        
        self.actors = []
    
    def clearActorChats(self):
        for actor in self.actors:
            if actor:
                actor.clearChat()
    
    def hideProps(self):
        for prop in self.props:
            prop.hide()
    
    def showProps(self):
        for prop in self.props:
            prop.show()
    
    def deleteProps(self):
        for prop in self.props:
            prop.removeNode()
        
        self.props = []
    
    def pauseSequence(self):
        if self.sequence:
            self.sequence.pause()
            self.sequence = None
    
    def deleteImage(self):
        if self.image:
            self.image.removeNode()
            self.image = None
    
    def deleteSubtitle(self):
        if self.subtitle:
            self.subtitle.destroy()
            self.subtitle = None

    def loadActors(self):
        if self.actors:
            return

        # Prof. Moochtopher
        moochtopher = NPCToons.createLocalNPC(91921)
        moochtopher.initializeBodyCollisions('toon')
        moochtopher.reparentTo(render)
        moochtopher.animFSM.request('ScientistEmcee')
        moochtopher.setPosHpr(85.114, -24.173, 19.785, 50, 0, 0)

        # Give him a clipboard
        rightHand = moochtopher.find('**/rightHand')
        clipBoard = loader.loadModel('phase_4/models/props/tt_m_prp_acs_clipboard')
        clipBoard.reparentTo(rightHand)
        clipBoard.setH(180)
        clipBoard.setPos(0, 0, 0)
        clipBoard.setScale(1)

        # Gideon
        gideon = NPCToons.createLocalNPC(91922)
        gideon.initializeBodyCollisions('toon')
        gideon.reparentTo(render)
        gideon.animFSM.request('neutral')
        gideon.setPosHpr(83.539, -8.610, 4.025, 199.797, 0, 0)

        # Random NPC #1 Soggy Bottom will be killed off
        randomNpc1 = NPCToons.createLocalNPC(5124)
        randomNpc1.initializeBodyCollisions('toon')
        randomNpc1.reparentTo(render)
        randomNpc1.animFSM.request('neutral')
        randomNpc1.setPosHpr(79.216, -10.626, 4.025, 219.058, 0, 0)

        # Random NPC #2
        randomNpc2 = NPCToons.createLocalNPC(2208)
        randomNpc2.initializeBodyCollisions('toon')
        randomNpc2.reparentTo(render)
        randomNpc2.animFSM.request('neutral')
        randomNpc2.setPosHpr(76.664, -14.819, 4.025, 219.058, 0, 0)

        # Allen
        allen = NPCToons.createLocalNPC(91923)
        allen.initializeBodyCollisions('toon')
        allen.reparentTo(render)
        allen.animFSM.request('Sit')
        allen.setPosHpr(77, -22.2, 28, 315, 0, 0)

        # Doctor Surlee
        surlee = NPCToons.createLocalNPC(2019)
        surlee.initializeBodyCollisions('toon')
        surlee.reparentTo(render)
        surlee.animFSM.request('neutral')
        surlee.setPosHpr(74.822, -22.105, 6.051, 258.403, 0, 0)
        surlee.cogLevels = [11, 11, 11, 11]

        # Philip Neuton
        philip = NPCToons.createLocalNPC(91924)
        philip.initializeBodyCollisions('toon')
        philip.reparentTo(render)
        philip.animFSM.request('neutral')
        philip.setPosHpr(97.391, -26.123, 18.840, 42.999, 0, 0)

        # Alternate Philip who is Chairman of the Governaughts
        philipCog = NPCToons.createLocalNPC(91924)
        philipCog.reparentTo(render)
        philipCog.setPosHpr(100.263, -35.361, 24.264, 49.785, 0.0, 0.0)
        philipCog.cogLevels = [14, 14, 14, 14]
        philipCog.putOnSuit('tbc', setDisplayName=False, distributed=True)
        philipCog.nametag.setText('Philip Neuton\nGovernaught Chairman')
        philipCog.setScale(1.2)
        self.__cogTransform(philipCog, 'tbc', (0.05, 0, 0.6))
        
        # Add the actors
        self.actors = [moochtopher, gideon, randomNpc1, randomNpc2, allen, surlee, philip, philipCog]
        self.hideActors()

        # Philip Neuton Governaught Dial

        phasePath = 'phase_4/audio/dial/'
        self.speechExclaim = loader.loadSfx(phasePath + 'av_suit_duck_exclaim.ogg')
        self.speechHowl = loader.loadSfx(phasePath + 'av_suit_duck_howl.ogg')
        self.speechLong = loader.loadSfx(phasePath + 'av_suit_duck_long.ogg')
        self.speechQuestion = loader.loadSfx(phasePath + 'av_suit_duck_question.ogg')
        self.speechShort = loader.loadSfx(phasePath + 'av_suit_duck_short.ogg')
        self.speechTransition = loader.loadSfx(phasePath + 'av_suit_duck_transition.ogg')

    def loadProps(self):
        if self.props:
            return

        # Allen's popcorn cart
        popcornCart = loader.loadModel('phase_5.5/models/estate/popcornCart')
        popcornCart.reparentTo(render)
        popcornCart.setPosHpr(75.5, -26.2, 29.15, 180, 0, 315)

        self.props = [popcornCart]
        self.hideProps()
    
    def loadHat(self, actor, pos=(0, 0, 0), hpr=(0, 0, 0), scale=0.5):
        hat = loader.loadModel('phase_4/models/accessories/tt_m_chr_avt_acc_hat_bowler')
        hat.reparentTo(actor.find('**/__Actor_head'))
        hat.setPos(pos)
        hat.setHpr(hpr)
        hat.setScale(scale)
        actor.hat = hat
    
    def getHeadsUpHpr(self, fromPos, toPos):
        quat = Quat()
        headsUp(quat, toPos - fromPos, Vec3.up())
        hpr = quat.getHpr()
        return Vec3(hpr[0] % 360, hpr[1] % 360, hpr[2] % 360)

    def __makeLoopInterval(self, actor, animation, suit):
        if suit:
            return Func(self.__loopSuit, actor, animation)
        else:
            return Func(actor.loop, animation)
    
    def __makeTurnSequence(self, actor, time, hpr, delay=0, suit=False):
        return Sequence(
            Wait(delay),
            self.__makeLoopInterval(actor, 'walk', suit),
            actor.hprInterval(time, hpr),
            self.__makeLoopInterval(actor, 'neutral', suit)
        )
    
    def __makePoof(self, actor, scale, func, *args):
        cloud = DustCloud(fBillboard=False)
        cloud.setBillboardAxis(2)
        cloud.setZ(3)
        cloud.setScale(scale)
        cloud.createTrack()
        
        return Sequence(
            Func(cloud.reparentTo, render),
            Func(cloud.setPos, actor.getPos(render)),
            Parallel(
                Sequence(
                    Func(actor.hide),
                    Func(func, *args),
                    Wait(0.05),
                    Func(actor.show)
                ),
                cloud.track),
            Func(cloud.destroy)
        )
    
    def __makeImageSequence(self, image, text, sfx, delay=0):
        return Sequence(
            Func(self.__setSubtitleText, ''),
            Wait(0.5),
            Func(base.hideAspect2dMargins),
            Func(self.switchImage, image),
            Wait(0.5),
            Func(base.transitions.irisIn, 0.5),
            Wait(1.5),
            Func(self.__setSubtitleText, text),
            Func(base.playSfx, sfx, volume=0.9),
            self.subtitle.colorScaleInterval(1.5, (1, 1, 1, 1), (1, 1, 1, 0)),
            Wait(delay - 3),
            Func(base.transitions.irisOut, 0.5),
            Wait(0.5)
        )
    
    def __makeEvilEyeMovies(self, cog, targetPos):
        eye = globalPropPool.getProp('evil-eye')
        eyePosHpr = (-0.4, 4.65, 5.01, -155.0, -20.0, 0.0)

        soundTrack = getSoundTrack('SA_evil_eye.ogg', delay=1, node=cog)
        eyeTrack = Sequence(
            Wait(1.06),
            Func(eye.reparentTo, cog),
            Func(eye.setPosHpr, *eyePosHpr),
            eye.scaleInterval(0.63, 11),
            Wait(0.33),
            eye.hprInterval(0.02, (205, 40, 0)),
            Wait(0.77),
            Func(eye.wrtReparentTo, render),
            Parallel(
                eye.hprInterval(1.1, (0, 0, -180)),
                eye.posInterval(1.1, Vec3(targetPos) + Vec3(0, 0, 2.5))
            ),
            Func(eye.removeNode)
        )
        # Thank you Joe and the TTO team
        suitTrack = Sequence(
            Func(self.__playSuitEnd, cog, 'glower', 32),
            Wait(32 / 24.0),
            Func(self.__poseSuit, cog, 'glower', 32),
            Wait(1.11),
            Func(self.__playSuitStart, cog, 'glower', 32),
            Wait(1.41),
            Func(self.__loopSuit, cog, 'neutral')
        )

        return Parallel(soundTrack, eyeTrack, suitTrack)
    
    def __makeDeathAftermatchSequence(self, actor, target, initialTime, walkTime, waitTime, oldHpr, text):
        return Sequence(
            Func(actor.sadEyes),
            Func(actor.blinkEyes),
            self.__makeTurnSequence(actor, walkTime, self.getHeadsUpHpr(actor.getPos(), target.getPos()), initialTime),
            Func(actor.setChatAbsolute, text, CFSpeech | CFTimeout),
            Wait(waitTime),
            self.__makeTurnSequence(actor, walkTime, oldHpr),
            Func(actor.normalEyes),
            Func(actor.blinkEyes),
            Func(actor.clearChat)
        )
    
    def __setSubtitleText(self, text):
        self.subtitle['text'] = text
    
    def __cogTransform(self, toon, cogType, pos):
        toon.putOnSuit(cogType, distributed=True)
        toon.nametag3d.wrtReparentTo(toon.suit.getGeomNode())
        toon.angryEyes()
        toon.blinkEyes()
        self.loadHat(toon, pos=pos)
    
    def __loopSuit(self, actor, animation):
        actor.suit.loop(animation)
    
    def __poseSuit(self, actor, animation, frame):
        actor.suit.pose(animation, frame)
    
    def __playSuitStart(self, actor, animation, startFrame=0):
        actor.suit.play(animation, fromFrame=startFrame)
    
    def __playSuitEnd(self, actor, animation, endFrame=0):
        actor.suit.play(animation, toFrame=endFrame)
    
    def switchImage(self, image):
        self.deleteImage()
        self.image = OnscreenImage(parent=render2d, image=image)

    def enterIdle(self, offset):
        self.pauseSequence()
        self.loadActors()
        self.loadProps()
        self.showActors()
        self.showProps()

        # Music for the cutscene
        StormAmbience = base.loadMusic(StormGlobals.StormAmbience)
        GovernaughtBrawl = base.loadMusic(StormGlobals.GovernaughtBrawl)

        moochtopher, gideon, randomNpc1, randomNpc2, allen, surlee, philip, philipCog = self.actors
        philipCog.removeActive()
        philipCog.hide()
        
        self.subtitle = DirectLabel(relief=None, text='', text_scale=0.1, text_wordwrap=20,
                                    text_font=ToontownGlobals.getSuitFont(), text_fg=(1, 1, 1, 1),
                                    text_shadow=(0, 0, 0, 1), pos=(0, 0, 0.75))

        # Scene 1
        self.currentSequence = Sequence(
            Func(base.playMusic, StormAmbience, looping=0, volume=0.8),
            Func(moochtopher.loop, 'neutral'),
            Func(moochtopher.setChatAbsolute, "Hello Toooons of Toontown!", CFSpeech | CFTimeout),
            Wait(6),
            Func(moochtopher.setChatAbsolute, "My name is Professor Moochtopher, but you might have already known that by my floating nametag.", CFSpeech | CFTimeout),
            Wait(8),
            Func(moochtopher.setChatAbsolute, "I created those to easily identify Toons all across Toontown.", CFSpeech | CFTimeout),
            Wait(7),
            Func(moochtopher.setChatAbsolute, "I couldn't stand those silly stickers you put on your shirt that tells someone your name.", CFSpeech | CFTimeout),
            Wait(8),
            Func(moochtopher.setChatAbsolute, "But I digress!", CFSpeech | CFTimeout),
            Wait(4),
            Func(randomNpc1.setChatAbsolute, "Get on with it!", CFSpeech | CFTimeout),
            Wait(2),
            Func(moochtopher.setChatAbsolute, "I'm here to let you all know that I have this situation under control.", CFSpeech | CFTimeout),
            Wait(8),
            Func(moochtopher.setChatAbsolute, "All the rumors you may have heard about our town being doomed are false.", CFSpeech | CFTimeout),
            Wait(8),
            Func(randomNpc2.setChatAbsolute, "But what about this storm?", CFSpeech | CFTimeout),
            Wait(6),
            Func(randomNpc2.setChatAbsolute, "Why would it return again?", CFSpeech | CFTimeout),
            Wait(6),
            Func(gideon.setChatAbsolute, "It could be a special force telling us that we are in danger.", CFSpeech | CFTimeout),
            Wait(7),
            Func(moochtopher.setChatAbsolute, "Don't get ahead of yourself now, Gideon.", CFSpeech | CFTimeout),
            Wait(5),
            Func(moochtopher.setChatAbsolute, "Disregard everything you heard about this storm potentially threatening us Toons.", CFSpeech | CFTimeout),
            Wait(7),
            Func(moochtopher.setChatAbsolute, "We are safe.", CFSpeech | CFTimeout),
            Wait(3),
            Func(randomNpc2.setChatAbsolute, "It can't be happening for no reason though.", CFSpeech | CFTimeout),
            Wait(4),
            Func(allen.setChatAbsolute, "Why do I have a feeling this monkey is trying to hide something from us?", CFSpeech | CFTimeout),
            Wait(6),
            Func(randomNpc1.setChatAbsolute, "We want answers!", CFSpeech | CFTimeout),
            Wait(3),
            Func(randomNpc1.setChatAbsolute, "Give us the answers!", CFSpeech | CFTimeout),
            Wait(1.5),
            Func(randomNpc2.setChatAbsolute, "Yeah! Tell the truth!", CFSpeech | CFTimeout),
            Wait(4),
            Func(moochtopher.setChatAbsolute, "I wouldn't be up here if I-", CFSpeech | CFTimeout),
            Wait(5),
            Func(moochtopher.clearChat),
            Func(surlee.setChatAbsolute, "Don't listen to him...", CFSpeech | CFTimeout),
            self.__makeTurnSequence(surlee, 1, (308, 0, 0)),
            Parallel(
                self.__makeTurnSequence(randomNpc1, 1, (180, 0, 0)),
                self.__makeTurnSequence(randomNpc2, 1, (180, 0, 0), 0.25),
                self.__makeTurnSequence(gideon, 1, (180, 0, 0), 0.5)
            ),
            Wait(2.5),
            Func(surlee.setChatAbsolute, "He's lying.", CFSpeech | CFTimeout),
            Wait(5),
            Func(moochtopher.setChatAbsolute, "Please don't interrupt me Surlee.", CFSpeech | CFTimeout),
            self.__makeTurnSequence(moochtopher, 1, (90, 0, 0)),
            Wait(5),
            Func(moochtopher.setChatAbsolute, "Let me handle this.", CFSpeech | CFTimeout),
            Wait(3),
            Func(moochtopher.setChatAbsolute, "Each and every one of you are safe from any-", CFSpeech | CFTimeout),
            self.__makeTurnSequence(moochtopher, 1, (50, 0, 0)),
            Wait(5),
            Func(moochtopher.clearChat),
            Func(surlee.setChatAbsolute, "All of you are in this situation because of me.", CFSpeech | CFTimeout),
            Wait(6),
            Func(surlee.setChatAbsolute, "My only intentions were to save my home.", CFSpeech | CFTimeout),
            self.__makeTurnSequence(moochtopher, 1, (90, 0, 0)),
            Wait(4),
            Func(surlee.setChatAbsolute, "The Walt Dimension.", CFSpeech | CFTimeout),
            Wait(3),
            Func(moochtopher.setChatAbsolute, "Surlee. Stop this now.", CFSpeech | CFTimeout),
            Wait(2),
            Func(surlee.setChatAbsolute, "My plan was to stop the Cogs from ever becoming boring business men, however, doing so created a giant rip in the space time continuum!", CFSpeech | CFTimeout),
            Wait(12),
            Func(surlee.setChatAbsolute, "Your world seemed the most interesting to me since I couldn't find my way back to mine.", CFSpeech | CFTimeout),
            Wait(8),
            Func(surlee.setChatAbsolute, "So I entered it.", CFSpeech | CFTimeout),
            Wait(3),
            Func(surlee.setChatAbsolute, "I entered it because it was so different from the others.", CFSpeech | CFTimeout),
            Wait(5),
            Func(surlee.setChatAbsolute, "The Possibilities were Infinite!", CFSpeech | CFTimeout),
            Wait(4),
            Func(moochtopher.setChatAbsolute, "Okay! Enough!", CFSpeech | CFTimeout),
            moochtopher.actorInterval('angry'),
            Func(moochtopher.loop, 'neutral'),
            Wait(3),
            Func(surlee.setChatAbsolute, "And for goodness sake, you Toons need to stop listening to what Professor Moochtopher is telling you.", CFSpeech | CFTimeout),
            Wait(9),
            Func(surlee.setChatAbsolute, "He is only trying to comfort you during these dark times.", CFSpeech | CFTimeout),
            Wait(6),
            Func(surlee.setChatAbsolute, "But the truth is...", CFSpeech | CFTimeout),
            Wait(3),
            Func(surlee.setChatAbsolute, "We are too late now.", CFSpeech | CFTimeout))

        self.currentSequence2 = Sequence(
            Wait(4),
            Func(surlee.setChatAbsolute, "I knew what was going on the first time the storm happened. I just didn't want to scare anyone.", CFSpeech | CFTimeout),
            Wait(8),
            Func(surlee.setChatAbsolute, "The Toon Resistance knows that the storm was a warning too, but they don't actually know what's triggering it.", CFSpeech | CFTimeout),
            Wait(9),
            Func(surlee.setChatAbsolute, "The thing is...", CFSpeech | CFTimeout),
            Wait(4),
            Func(surlee.setChatAbsolute, "I do.", CFSpeech | CFTimeout),
            Wait(3),
            Func(moochtopher.setChatAbsolute, "Zip it Surlee.", CFSpeech | CFTimeout),
            Wait(3),
            Func(surlee.setChatAbsolute, "Because of my arrival, holes were open through time which allows anyone from anywhere to enter and exit freely.", CFSpeech | CFTimeout),
            Wait(9),
            Func(surlee.setChatAbsolute, "Everytime this storm occurs, it's a warning the dome automatically sets off letting the citizens of Toontown know that they are in danger and that dark times lie ahead.", CFSpeech | CFTimeout),
            Wait(12),
            Func(allen.setChatAbsolute, "The dome? What's this monkey talking about?", CFSpeech | CFTimeout),
            Wait(5),
            Func(gideon.setChatAbsolute, "I don't know?", CFSpeech | CFTimeout),
            Wait(3),
            Func(moochtopher.setChatAbsolute, "This is confidential information, Surlee. I'd advise that you stop speaking.", CFSpeech | CFTimeout),
            Wait(6),
            Func(philip.setChatAbsolute, "So you two are hiding something from me that I don't know?", CFSpeech | CFTimeout),
            Wait(6),
            Func(philip.setChatAbsolute, "These crates we are standing on. Are you two lying about those too?", CFSpeech | CFTimeout),
            Wait(6),
            Func(philip.setChatAbsolute, "Because I doubt that they just appeared out of thin air.", CFSpeech | CFTimeout),
            Wait(6),
            Func(surlee.setChatAbsolute, "No- they did. And for a reason too.", CFSpeech | CFTimeout),
            Wait(6),
            Func(surlee.setChatAbsolute, "They were put here for a purpose.", CFSpeech | CFTimeout),
            Wait(6),
            Func(surlee.setChatAbsolute, "A purpose that you will soon learn about.", CFSpeech | CFTimeout),
            Wait(6),
            Func(surlee.setChatAbsolute, "It is time that we accept our fate, open these crates and sign the papers.", CFSpeech | CFTimeout),
            Wait(6),
            Func(surlee.setChatAbsolute, "And if we don't, they are coming.", CFSpeech | CFTimeout),
            Wait(4),
            Func(randomNpc2.setChatAbsolute, "Who is coming?", CFSpeech | CFTimeout),
            randomNpc2.actorInterval('shrug'),
            Func(randomNpc2.loop, 'neutral'),
            Wait(2),
            Func(surlee.setChatAbsolute, "The Govern-", CFSpeech | CFTimeout),
            Wait(1.5),
            Func(surlee.clearChat),
            Func(moochtopher.setChatAbsolute, "ENOUGH! This is preposterous!", CFSpeech | CFTimeout),
            Wait(4),
            Func(surlee.setChatAbsolute, "You see. This is all my fault.", CFSpeech | CFTimeout),
            Wait(5),
            Func(surlee.setChatAbsolute, "It's over. It leaves us at no other choice but to work with them.", CFSpeech | CFTimeout),
            Wait(6),
            Func(randomNpc1.setChatAbsolute, "He better not be thinking what I'm thinking!", CFSpeech | CFTimeout),
            Wait(3),
            Func(surlee.setChatAbsolute, "With my knowledge and determination, I could be an important asset to them!", CFSpeech | CFTimeout),
            surlee.actorInterval('think'),
            Func(surlee.loop, 'neutral'),
            Wait(1),
            Func(allen.setChatAbsolute, "What's this Toon talking about?", CFSpeech | CFTimeout),
            Wait(3),
            Func(surlee.setChatAbsolute, "Your world is just as doomed as Philip's.", CFSpeech | CFTimeout),
            Wait(4),
            Func(randomNpc1.setChatAbsolute, "He's talking about another Philip right?", CFSpeech | CFTimeout),
            Wait(4),
            Func(philip.setChatAbsolute, "Uh. I think so.", CFSpeech | CFTimeout),
            Wait(3),
            Func(randomNpc2.setChatAbsolute, "I'm not familiar with any other scientist named Philip in town.", CFSpeech | CFTimeout),
            Wait(5),
            Func(gideon.setChatAbsolute, "Surlee, you're scaring me...", CFSpeech | CFTimeout),
            Wait(5),
            Func(allen.setChatAbsolute, "Giddy, come on! Don't be scared. He's smart. He knows how to save us all. Don't worry about it!", CFSpeech | CFTimeout),
            Wait(6),
            Func(allen.setChatAbsolute, "Right?", CFSpeech | CFTimeout),
            Wait(4),
            Func(surlee.setChatAbsolute, "I'm sorry Allen.", CFSpeech | CFTimeout),
            Wait(4),
            Func(surlee.setChatAbsolute, "Like myself, Philip made the same mistake.", CFSpeech | CFTimeout),
            Wait(4),
            Func(philip.setChatAbsolute, "Huh?", CFSpeech | CFTimeout),
            Wait(2),
            Func(surlee.setChatAbsolute, "He tried the one thing that could save his world too.", CFSpeech | CFTimeout),
            Wait(5),
            Func(philip.setChatAbsolute, "I didn't do any of this!", CFSpeech | CFTimeout),
            Wait(3),
            Func(surlee.setChatAbsolute, "And failed...", CFSpeech | CFTimeout),
            Wait(7),
            Func(surlee.setChatAbsolute, "He had two options like we all do now.", CFSpeech | CFTimeout),
            Wait(4),
            Func(surlee.setChatAbsolute, "Become sad for an eternity or join the ranks.", CFSpeech | CFTimeout),
            Wait(4),
            Func(surlee.setChatAbsolute, "The choices were there, but he really had none.", CFSpeech | CFTimeout),
            Wait(5),
            Func(surlee.setChatAbsolute, "No Toon ever chooses to be sad.", CFSpeech | CFTimeout),
            Wait(4),
            Func(surlee.setChatAbsolute, "So he found a new way to be happy.", CFSpeech | CFTimeout),
            Wait(5),
            Func(surlee.setChatAbsolute, "And so he became one of them.", CFSpeech | CFTimeout),
            Wait(4),
            Func(philip.setChatAbsolute, "Okay, you're insane Surlee!", CFSpeech | CFTimeout),
            Wait(3),
            Func(randomNpc1.setChatAbsolute, "Why should we even believe what this Toon is saying?", CFSpeech | CFTimeout),
            Wait(5),
            Func(randomNpc2.setChatAbsolute, "I don't believe him!", CFSpeech | CFTimeout),
            Wait(3),
            Func(philip.setChatAbsolute, "I am no traitor! I would never team up with the Cogs!", CFSpeech | CFTimeout),
            Wait(5),
            Func(moochtopher.setChatAbsolute, "Surlee, don't do this! ", CFSpeech | CFTimeout),
            Wait(4),
            Func(moochtopher.setChatAbsolute, "There's another way! I know it!", CFSpeech | CFTimeout),
            Wait(4),
            Func(moochtopher.setChatAbsolute, "Just give me more time and I'll figure this out!", CFSpeech | CFTimeout),
            Wait(4),
            Func(surlee.setChatAbsolute, "There is no more time. They are probably coming now!", CFSpeech | CFTimeout),
            Wait(6),
            Func(gideon.setChatAbsolute, "Philip? Your working with the Cogs?!", CFSpeech | CFTimeout),
            Wait(5),
            Func(philip.setChatAbsolute, "I am most certainly not! That's bogus!", CFSpeech | CFTimeout),
            Wait(3),
            Func(moochtopher.setChatAbsolute, "PLEASE SURLEE! STOP THIS NOW!", CFSpeech | CFTimeout),
            Wait(3),
            Func(gideon.setChatAbsolute, "So you're a traitor Philip?", CFSpeech | CFTimeout),
            Wait(3),
            Func(philip.setChatAbsolute, "No! I'm a loyal citizen to this town like you!", CFSpeech | CFTimeout),
            Wait(4),
            Func(allen.setChatAbsolute, "How dare he help the Cogs?!", CFSpeech | CFTimeout),
            Wait(3),
            Func(moochtopher.setChatAbsolute, "We can work this out Surlee!", CFSpeech | CFTimeout),
            Wait(3),
            Func(gideon.setChatAbsolute, "So were you the one who created the blueprint for that blimp?!", CFSpeech | CFTimeout),
            Wait(5),
            Func(allen.setChatAbsolute, "I'm bored. Does anyone want to ride the Trolley?", CFSpeech | CFTimeout),
            Wait(5),
            Parallel(
                Sequence(
                    Wait(1),
                    Func(moochtopher.setChatAbsolute, 'NO!', CFSpeech | CFTimeout),
                    Func(gideon.setChatAbsolute, 'NO!', CFSpeech | CFTimeout),
                    Func(randomNpc1.setChatAbsolute, 'NO!', CFSpeech | CFTimeout),
                    Func(randomNpc2.setChatAbsolute, 'NO!', CFSpeech | CFTimeout),
                    Func(philip.setChatAbsolute, 'NO!', CFSpeech | CFTimeout),
                ),
                Parallel(
                    self.__makeTurnSequence(moochtopher, 1, (76, 0, 0), 0.25),
                    self.__makeTurnSequence(gideon, 1, (154, 0, 0), 1),
                    self.__makeTurnSequence(randomNpc1, 1, (169, 0, 0), 0.75),
                    self.__makeTurnSequence(randomNpc2, 1, (183, 0, 0), 0.5),
                    self.__makeTurnSequence(philip, 1, (79, 0, 0), 0)
                )
            ),
            Wait(1),
            Func(allen.setChatAbsolute, "No?", CFSpeech | CFTimeout),
            Wait(3),
            Func(allen.setChatAbsolute, "Alright then, jeez.", CFSpeech | CFTimeout),
            Parallel(
                self.__makeTurnSequence(moochtopher, 1, (90, 0, 0), 0.5),
                self.__makeTurnSequence(gideon, 1, (180, 0, 0), 0.75),
                self.__makeTurnSequence(randomNpc1, 1, (180, 0, 0), 0.25),
                self.__makeTurnSequence(randomNpc2, 1, (240, 0, 0), 0),
                self.__makeTurnSequence(philip, 1, (43, 0, 0), 1)
            ),
            Wait(3),
            Func(moochtopher.setChatAbsolute, "You don't want to do this Doctor.", CFSpeech | CFTimeout),
            Wait(6),
            Func(moochtopher.setChatAbsolute, "You are too smart. We will lose.", CFSpeech | CFTimeout),
            Wait(5),
            Func(surlee.setChatAbsolute, "I must Professor.", CFSpeech | CFTimeout),
            Wait(5),
            Func(surlee.setChatAbsolute, "No Toon deserves to be sad. I must find new happiness in life.", CFSpeech | CFTimeout),
            Wait(6),
            Func(surlee.setChatAbsolute, "And you should too.", CFSpeech | CFTimeout),
            Wait(7),
            Func(moochtopher.setChatAbsolute, "I will never surrender!", CFSpeech | CFTimeout),
            Wait(4),
            Func(surlee.setChatAbsolute, "Join the prospects with me.", CFSpeech | CFTimeout),
            Wait(5),
            Func(surlee.setChatAbsolute, "Like Philip did.", CFSpeech | CFTimeout),
            Wait(4),
            Func(surlee.setChatAbsolute, "Together we can continue to be happy...", CFSpeech | CFTimeout),
            Wait(4),
            Func(surlee.setChatAbsolute, "By becoming...", CFSpeech | CFTimeout),
            Wait(3),
            Func(surlee.setChatAbsolute, "Hybrid.", CFSpeech),
            Wait(3),
            Func(philipCog.show),
            Func(philipCog.addActive),
            philipCog.suit.beginSupaFlyMove(Vec3(0, 0, 0), True, 'fromSky', False, True, True),
            Wait(1),
            Parallel(
                self.__makeTurnSequence(philip, 1.25, (200, 0, 0)),
                self.__makeTurnSequence(moochtopher, 1.25, (220, 0, 0), 0.25)
            ),
            Func(philip.setChatAbsolute, "What? Is that me?!", CFSpeech | CFTimeout),
            Wait(1),
            Func(allen.setChatAbsolute, "My head hurts.", CFSpeech | CFTimeout),
            Wait(2),
            Func(gideon.setChatAbsolute, "Oh my...", CFSpeech | CFTimeout),
            Wait(0.5),
            Func(randomNpc1.setChatAbsolute, "HOLEY SMOKES!!!", CFSpeech | CFTimeout),
            Parallel(
                self.__makeTurnSequence(philip, 1.25, (43, 0, 0), 0.25),
                self.__makeTurnSequence(moochtopher, 1.25, (50, 0, 0))
            ),
            Func(moochtopher.setChatAbsolute, "They're here...", CFSpeech | CFTimeout),
            Wait(1.3),
            Func(randomNpc2.setChatAbsolute, "WE ARE DOOOMED!", CFSpeech | CFTimeout),
            Wait(4),
            Func(surlee.setChatAbsolute, "I'm sorry.", CFSpeech | CFTimeout),
            Wait(2),
            self.__makePoof(surlee, 1.3, self.__cogTransform, surlee, 'tbc', (0.05, 0, 0.6)),
            Wait(2),
            Func(self.__loopSuit, surlee, 'walk'),
            surlee.posInterval(1.5, (80.866, -16.983, 4.025)),
            Func(self.__loopSuit, surlee, 'neutral'),
            Wait(0.5),
            self.__makeTurnSequence(surlee, 1, (375, 0, 0), suit=True),
            Wait(2.5),
            Func(allen.setChatAbsolute, "Well. Game over.", CFSpeech | CFTimeout),
            Wait(3),
            Func(allen.setChatAbsolute, "Matters well enjoy the show while I still have some happiness in me.", CFSpeech | CFTimeout),
            Wait(4),
            Func(allen.setChatAbsolute, "At least the views good from up here.", CFSpeech | CFTimeout),
            Wait(4))

        self.currentSequence3 = Sequence(
            Func(philipCog.setChatAbsolute, 'Ha ha!', CFSpeech|CFTimeout, dialogue = self.speechExclaim),
            Wait(4),
            Func(philipCog.setChatAbsolute, "Good show! Good show!", CFSpeech | CFTimeout, dialogue = self.speechExclaim),
            Wait(5),
            Func(philipCog.setChatAbsolute, "Welcome aboard Surlee.", CFSpeech | CFTimeout, dialogue = self.speechShort),
            Wait(5),
            Func(gideon.setChatAbsolute, "I can't believe my eyes.", CFSpeech | CFTimeout),
            Wait(6),
            Func(gideon.setChatAbsolute, "So this duck was behind it all along...", CFSpeech | CFTimeout),
            Wait(4),
            self.__makeTurnSequence(gideon, 1, (67, 0, 0)),
            Wait(1),
            Func(gideon.setChatAbsolute, "The cause of these warnings. The documents. That blueprint.", CFSpeech | CFTimeout),
            Wait(6),
            Func(gideon.setChatAbsolute, "The duck with the plan.", CFSpeech | CFTimeout),
            Wait(6),
            Func(gideon.setChatAbsolute, "The plan to scare everyone all just to get us to sign those papers and join your corporation.", CFSpeech | CFTimeout),
            Wait(7),
            Func(gideon.setChatAbsolute, "And Surlee fell for it...", CFSpeech | CFTimeout),
            Wait(5),
            Func(gideon.setChatAbsolute, "You think for one second that us Toons are just going to just give up?", CFSpeech | CFTimeout),
            Wait(5),
            Func(gideon.setChatAbsolute, "Give up what we do best?", CFSpeech | CFTimeout),
            Wait(5),
            Func(gideon.setChatAbsolute, "Having fun.", CFSpeech | CFTimeout),
            Wait(4),
            Func(gideon.setChatAbsolute, "We'll take on your fight.", CFSpeech | CFTimeout),
            Wait(4),
            Func(gideon.setChatAbsolute, "Throw it all at us.", CFSpeech | CFTimeout),
            Wait(4),
            Func(gideon.setChatAbsolute, "Because we'll fight until the end if we go sad trying.", CFSpeech | CFTimeout),
            Wait(4),
            Func(philipCog.setChatAbsolute, "What an informative speech you gave Toon, but it appears your time is up.", CFSpeech | CFTimeout, dialogue = self.speechLong),
            Wait(6),
            Func(philipCog.setChatAbsolute, "It's my shift now.", CFSpeech | CFTimeout, dialogue = self.speechShort),
            Wait(4),
            Func(philip.setChatAbsolute, "Ah look, another secret.", CFSpeech | CFTimeout),
            Wait(4),
            Func(philip.setChatAbsolute, "I bet you and Surlee knew all about this one too- huh Moochtopher?", CFSpeech | CFTimeout),
            Wait(6),
            Func(moochtopher.setChatAbsolute, "Phil, I'm sorry, but this isn't exactly the right time to bring this up...", CFSpeech | CFTimeout),
            Wait(7),
            Func(philip.setChatAbsolute, "I get it.", CFSpeech | CFTimeout),
            Wait(3),
            Func(philip.setChatAbsolute, "If you would've said that there's another version of me from an alternate reality who is on the front cover of 'Greatest Business Bots of Cog Nation' magazine, I probably wouldn't have believed you.", CFSpeech | CFTimeout),
            Wait(14),
            Func(randomNpc1.setChatAbsolute, "Hmm. I wonder if there is another version of me; not that anyone would really want that though.", CFSpeech | CFTimeout),
            Wait(6),
            Func(philipCog.setChatAbsolute, "You know Toons, I do believe in second chances.", CFSpeech | CFTimeout, dialogue = self.speechLong),
            Wait(6),
            Func(philipCog.setChatAbsolute, "So here.", CFSpeech | CFTimeout, dialogue = self.speechShort),
            Wait(4),
            Func(philipCog.setChatAbsolute, "Open the crates and sign the papers...", CFSpeech | CFTimeout, dialogue = self.speechLong),
            Wait(5),
            Func(philipCog.setChatAbsolute, "Or regret doing so.", CFSpeech | CFTimeout, dialogue = self.speechShort),
            Wait(4),
            Func(philipCog.setChatAbsolute, "If you can't decide...", CFSpeech | CFTimeout, dialogue = self.speechShort),
            Wait(5),
            Func(base.transitions.irisOut, 0.5),
            Wait(1),
            self.__makeImageSequence('phase_4/maps/another_town_2.png', "You better ask this town what they think.", self.speechShort, 6),
            self.__makeImageSequence('phase_4/maps/another_town_1.png', "You wouldn't want your town turning into something like this...\n\x01red\x01Would you?\x02", self.speechQuestion, 7),
            self.__makeImageSequence('phase_4/maps/another_town_3.png', "Now join me... and together we can live \x01skyBlue\x01Better Lives\x02.", self.speechLong, 7),
            Wait(0.5),
            Func(self.deleteSubtitle),
            Func(self.deleteImage),
            Wait(0.5),
            Func(base.transitions.irisIn, 0.5),
            Wait(0.5),
            Func(base.showAspect2dMargins),
            Func(allen.setChatAbsolute, "Uh guys. We better do this.", CFSpeech | CFTimeout),
            Wait(4),
            Func(philipCog.setChatAbsolute, "See. Listen to the bear. He seems bright.", CFSpeech | CFTimeout, dialogue = self.speechLong),
            Wait(4),
            Func(randomNpc1.setChatAbsolute, "Heh.", CFSpeech | CFTimeout),
            Wait(4),
            Func(philipCog.setChatAbsolute, "Did you just...", CFSpeech | CFTimeout, dialogue = self.speechShort),
            Wait(3),
            Func(philipCog.setChatAbsolute, "LAUGH AT ME!", CFSpeech | CFTimeout, dialogue = self.speechExclaim),
            Wait(3.5),
            Func(randomNpc1.setChatAbsolute, "Uh. I'm sorry. He's just- uh. Not exactly the-", CFSpeech | CFTimeout),
            Wait(4),
            Func(philipCog.setChatAbsolute, "SILENCE!", CFSpeech | CFTimeout, dialogue = self.speechExclaim),
            Wait(4),
            Func(philipCog.setChatAbsolute, "YOU SHALL BE DOOMED TO SADNESS FOR AN ETERNITY!", CFSpeech | CFTimeout, dialogue = self.speechHowl),
            Wait(4),
            Func(philipCog.setChatAbsolute, "SURLEE! You know what to do!", CFSpeech | CFTimeout, dialogue = self.speechHowl),
            Wait(4),
            self.__makeTurnSequence(surlee, 0.25, (380, 0, 0), suit=True),
            self.__makeEvilEyeMovies(surlee, randomNpc1.getPos()),
            Func(randomNpc1.setChatAbsolute, "Wait- what no!", CFSpeech | CFTimeout),
            Func(randomNpc1.animFSM.request, 'Died'),
            Wait(1),
            Parallel(
                self.__makeDeathAftermatchSequence(gideon, randomNpc1, 0, 1.5, 4, (67, 0, 0), "What? SOGGY BOTTOM!!!"),
                self.__makeDeathAftermatchSequence(randomNpc2, randomNpc1, 0.75, 1, 5, (240, 0, 0), "Now you've really done it, Governaughts...")
            ),
            Func(randomNpc1.delete),
            Func(philipCog.setChatAbsolute, "TA TA!", CFSpeech | CFTimeout, dialogue = self.speechExclaim),
            Wait(3),
            Func(philipCog.setChatAbsolute, "Now allow me to introduce myself.", CFSpeech | CFTimeout, dialogue = self.speechShort),
            Wait(4),
            Func(base.playMusic, GovernaughtBrawl, looping=1, volume=0.8),
            Func(philipCog.setChatAbsolute, "My name is Philip Neuton--Chairman of the Governaught Corporation.", CFSpeech | CFTimeout, dialogue = self.speechLong),
            Wait(5),
            Func(philipCog.setChatAbsolute, "And without further ado, say hello to a new breed of Cogs--Governaughts!", CFSpeech | CFTimeout, dialogue = self.speechExclaim),
            # Governaught Cogs will now fly down and land all over the Toontown Central Plaza
            Wait(8),
            Func(philipCog.setChatAbsolute, "Any last words?", CFSpeech | CFTimeout, dialogue = self.speechQuestion),
            Wait(3),
            Func(philipCog.setChatAbsolute, "Just kidding.", CFSpeech | CFTimeout, dialogue = self.speechShort),
            Wait(1),
            philipCog.posInterval(0.8, (97.105,  -32.769,  25.647)),
            Wait(0.5),
            Parallel(
                philipCog.posInterval(5, (87.064,  -25.349,  21.443)),
                Func(philipCog.setChatAbsolute, "If it's a war you want...", CFSpeech | CFTimeout, dialogue = self.speechLong)),
            Wait(1),
            Func(philipCog.setChatAbsolute, "Then allow me to declare it.", CFSpeech | CFTimeout, dialogue = self.speechExclaim),
            Wait(0.3),
            # Kick Prof. Moochtopher off the crate and onto the ground
            philipCog.posInterval(0.3, (85.114, -24.173, 19.785)),
            moochtopher.posInterval(0.3, (87.307,  -17.609,  13.189)),
            Func(moochtopher.play, 'FallDown'),
            moochtopher.posInterval(0.3, (88.217,  -7.775,  4.025)),
            Func(moochtopher.play, 'FallDown'),
            Wait(2),
            Func(moochtopher.setChatAbsolute, "Oh my. These Cogs are very different.", CFSpeech | CFTimeout),
            Wait(4),
            Func(moochtopher.setChatAbsolute, "It appears they have new abilities and attributes that can be used in battle.", CFSpeech | CFTimeout),
            Wait(5),
            Func(moochtopher.setChatAbsolute, "When you are fighting them, be careful.", CFSpeech | CFTimeout),
            Wait(3),
            Func(moochtopher.setChatAbsolute, "They aren't the everyday Cogs we are familiar with.", CFSpeech | CFTimeout),
            Wait(4),
            Func(philip.setChatAbsolute, "As you are fighting them, you will learn more about how they work.", CFSpeech | CFTimeout),
            Wait(5),
            Func(philip.setChatAbsolute, "Some of them have even been promoted past level 12.", CFSpeech | CFTimeout),
            Wait(4),
            Func(moochtopher.setChatAbsolute, "It may be tricky, but I believe in all of you.", CFSpeech | CFTimeout),
            Wait(4),
            Func(gideon.setChatAbsolute, "Fortunately, I have some extra gags that we can use during this fight.", CFSpeech | CFTimeout),
            Wait(5),
            Func(gideon.setChatAbsolute, "Here take some; on me!", CFSpeech | CFTimeout),
            Wait(2.5),
            #Use Gag-Up All unite
            Func(allen.setChatAbsolute, "Hey! I can't reach the gags from up here!", CFSpeech | CFTimeout),
            Wait(3.5),
            Func(gideon.setChatAbsolute, "That's too bad Allen. You should've came down when I told you to!", CFSpeech | CFTimeout),
            Wait(4),
            Func(moochtopher.setChatAbsolute, "Fight to your last smirk Toons!", CFSpeech | CFTimeout),
            Wait(4),
            Func(philipCog.setChatAbsolute, "ATTACK!!!", CFSpeech, dialogue = self.speechHowl),
            Wait(10),
            Func(philipCog.clearChat))

        self.sequence = Sequence(self.currentSequence, self.currentSequence2, self.currentSequence3)
        
        if offset >= 2.5:
            self.sequence = Parallel(self.sequence, Sequence(Wait(offset + 0.25), Func(self.clearActorChats)))

        self.sequence.start(min(offset, self.sequence.getDuration()))

    def exitIdle(self):
        self.pauseSequence()
        self.deleteImage()
        self.deleteSubtitle()

    def enterOff(self, offset):
        self.deleteActors()
        self.deleteProps()
