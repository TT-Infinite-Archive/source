from direct.interval.IntervalGlobal import *
from toontown.chat.ChatGlobals import CFSpeech, CFTimeout
from toontown.toonbase import ToontownGlobals
from panda3d.core import Vec3, Quat, headsUp
from direct.gui.DirectGui import DirectLabel

ALL = -1


def getHeadsUpHpr(fromPos, toPos):
    quat = Quat()
    headsUp(quat, toPos - fromPos, Vec3.up())
    hpr = quat.getHpr()
    return Vec3(hpr[0] % 360, hpr[1] % 360, hpr[2] % 360)


class CutsceneHandler:
    SHOW = []
    HIDE = []

    def __init__(self, assets, parent):
        self.assets = assets
        self.parent = parent
        self.sequence = self.getSequence()
        self.subtitle = DirectLabel(relief=None, text='', text_scale=0.1, text_wordwrap=20,
                                    text_font=ToontownGlobals.getSuitFont(), text_fg=(1, 1, 1, 1),
                                    text_shadow=(0, 0, 0, 1), pos=(0, 0, 0.75))
        self.image = None
        self.music = None

    def getSequence(self):
        return Sequence()

    def load(self):
        pass

    def start(self, ts=0):
        if self.SHOW == ALL:
            self.showProps()
            self.showActors()
        elif self.HIDE == ALL:
            self.hideProps()
            self.hideActors()
        else:
            for name, prop in self.assets.propPool.items():
                if name in self.SHOW:
                    prop.reparentTo(self.parent)
                if name in self.HIDE:
                    prop.reparentTo(hidden)

            for name, actor in self.assets.actorPool.items():
                if name in self.SHOW:
                    actor.reparentTo(self.parent)
                    actor.addActive()
                if name in self.HIDE:
                    actor.reparentTo(hidden)
                    actor.removeActive()

        if self.sequence:
            self.sequence.start(ts)

    def stop(self):
        if self.sequence:
            self.sequence.finish()

    def pause(self):
        if self.sequence:
            self.sequence.pause()

    def cleanup(self):
        self.deleteImage()
        self.deleteSubtitle()

    def getActors(self):
        return self.assets.actorPool.values()

    def getProps(self):
        return self.assets.propPool.values()

    def hideActors(self):
        for actor in self.getActors():
            if actor:
                actor.hide()
                actor.removeActive()

    def showActors(self):
        for actor in self.getActors():
            if actor:
                actor.show()
                actor.addActive()

    def deleteActors(self):
        for actor in self.getActors():
            if actor:
                actor.delete()

    def clearActorChats(self):
        for actor in self.getActors():
            if actor:
                actor.clearChat()

    def deleteImage(self):
        if self.image:
            self.image.removeNode()
            self.image = None

    def deleteSubtitle(self):
        if self.subtitle:
            self.subtitle.destroy()
            self.subtitle = None

    def hideProps(self):
        for prop in self.getProps():
            prop.hide()

    def showProps(self):
        for prop in self.getProps():
            prop.show()

    def deleteProps(self):
        for prop in self.getProps():
            prop.removeNode()

    def say(self, actor, chat, duration=0, dialogue=None):
        return Sequence(Func(actor.setChatAbsolute, chat, CFSpeech | CFTimeout, dialogue), Wait(duration))

    def walkTo(self, actor, position):
        distance = (actor.getPos().getXy() - position.getXy()).length()
        duration = distance / ToontownGlobals.ToonForwardSlowSpeed
        posInterval = LerpPosInterval(actor, duration, position)
        return Parallel(
            ActorInterval(actor, 'walk', duration),
            posInterval
        )

    def runTo(self, actor, position):
        distance = actor.getDistance(position)
        duration = distance / ToontownGlobals.ToonForwardSpeed
        posInterval = LerpPosInterval(actor, duration, position)
        return Parallel(
            ActorInterval(actor, 'run', duration),
            posInterval
        )

    def __loopSuit(self, actor, animation):
        actor.suit.loop(animation)

    def makeLoopInterval(self, actor, animation, suit):
        if suit:
            return Func(self.__loopSuit, actor, animation)
        return Func(actor.loop, animation)

    def turn(self, actor, h, delay=0, suit=False):
        duration = abs(h / ToontownGlobals.ToonRotateSpeed)
        return Sequence(
            Wait(delay),
            self.makeLoopInterval(actor, 'walk', suit),
            actor.hprInterval(duration, (h, 0, 0)),
            self.makeLoopInterval(actor, 'neutral', suit)
        )

    def playMusic(self, name, looping, volume):
        return Func(base.playMusic, self.assets.musicPool.get(name), looping, 1, volume)

    def makePoof(self, actor, scale, func, *args):
        makePoof(actor, scale, func, args)

    def setSubtitleText(self, text):
        self.subtitle['text'] = text

    def loopSuit(self, actor, animation):
        actor.suit.loop(animation)

    def poseSuit(self, actor, animation, frame):
        actor.suit.pose(animation, frame)

    def playSuitStart(self, actor, animation, startFrame=0):
        actor.suit.play(animation, fromFrame=startFrame)

    def playSuitEnd(self, actor, animation, endFrame=0):
        actor.suit.play(animation, toFrame=endFrame)
