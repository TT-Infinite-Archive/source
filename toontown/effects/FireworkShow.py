from panda3d.core import NodePath
from direct.interval.IntervalGlobal import *
from toontown.effects import FireworkShowGlobals
from toontown.effects.Firework import Firework
from toontown.toonbase import ToontownGlobals
from toontown.parties import PartyGlobals
fireworkShowTypes = [ToontownGlobals.JULY4_FIREWORKS,
 PartyGlobals.EFireworkShow.SUMMER,
 ToontownGlobals.NEWYEARS_FIREWORKS,
 ToontownGlobals.COMBO_FIREWORKS]

class FireworkShow(NodePath):
    showData = FireworkShowGlobals.showData
    sectionData = FireworkShowGlobals.sectionData
    showMusic = {}

    @classmethod
    def isValidShowType(cls, showType = -1):
        if showType in list(cls.showData.keys()):
            return True
        else:
            return False

    def __init__(self, showType = ToontownGlobals.NEWYEARS_FIREWORKS):
        NodePath.__init__(self, 'FireworkShow')
        self.showType = showType
        self.sectionIvals = []
        self.fireworks = []
        self.delaySectionStart = None
        self.curSection = None
        self.curOffset = 0.0
        return

    def beginSection(self, startIndex, endIndex, offset):
        taskMgr.remove('beginSection' + str(startIndex) + str(endIndex))
        sectionIval = Parallel()
        time = 2.0
        showMusic = self.showMusic.get(self.showType)
        if showMusic:
            base.musicMgr.load(showMusic, looping=False)
            musicOffset = self.getDuration(0, startIndex) - self.getDuration(startIndex, startIndex) + offset
            sectionIval.append(Func(base.musicMgr.request, showMusic, priority=2, looping=False))
            sectionIval.append(Func(base.musicMgr.offsetMusic, musicOffset))
        sectionData = self.showData.get(self.showType)[startIndex:endIndex]
        for fireworkInfo in sectionData:
            typeId = fireworkInfo[0]
            velocity = fireworkInfo[1]
            pos = fireworkInfo[2]
            scale = fireworkInfo[3]
            color1 = fireworkInfo[4]
            color2 = fireworkInfo[5]
            if color2 == -1:
                color2 = color1
            trailDur = fireworkInfo[6]
            delay = fireworkInfo[7]
            firework = Firework(typeId, velocity, scale, color1, color2, trailDur)
            firework.reparentTo(self)
            firework.setPos(pos)
            self.fireworks.append(firework)
            sectionIval.append(Sequence(Wait(time), firework.generateFireworkIval()))
            time += delay

        self.sectionIvals.append(sectionIval)
        self.curSection = sectionIval
        self.curOffset = offset
        self.delaySectionStart = FrameDelayedCall('delaySectionStart', self.startCurSection, frames=24)

    def startCurSection(self):
        self.curSection.start(self.curOffset)

    def begin(self, timestamp):
        time = 0.0
        for section in self.sectionData.get(self.showType):
            startIndex = section[0]
            endIndex = section[1]
            sectionDur = self.getDuration(startIndex, endIndex)
            if timestamp < sectionDur:
                timestamp = max(0.0, timestamp)
                taskMgr.doMethodLater(time, self.beginSection, 'beginSection' + str(startIndex) + str(endIndex), extraArgs=[startIndex, endIndex, timestamp])
                time = time + sectionDur - timestamp
            timestamp -= sectionDur

    def getDuration(self, startIndex = 0, endIndex = None):
        duration = 0.0
        if endIndex == None:
            endIndex = len(self.showData.get(self.showType))
        for firework in self.showData.get(self.showType)[startIndex:endIndex]:
            duration += firework[7]

        return duration

    def isPlaying(self):
        for ival in self.sectionIvals:
            if ival.isPlaying():
                return True

        return False

    def cleanupShow(self):
        if self.delaySectionStart:
            self.delaySectionStart.destroy()
            del self.delaySectionStart
            self.delaySectionStart = None
        showMusic = self.showMusic.get(self.showType)
        if showMusic:
            base.musicMgr.requestFadeOut(showMusic)
        for section in self.sectionData.get(self.showType):
            startIndex = section[0]
            endIndex = section[1]
            taskMgr.remove('beginSection' + str(startIndex) + str(endIndex))

        for ival in self.sectionIvals:
            ival.pause()
            del ival
            ival = None

        self.sectionIvals = []
        for firework in self.fireworks:
            firework.cleanup()
            del firework
            firework = None

        self.fireworks = []
        return
