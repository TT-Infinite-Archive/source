from direct.distributed import DistributedSmoothNode
from direct.distributed.DistributedObject import DistributedObject
from direct.distributed.ClockDelta import globalClockDelta
from direct.interval.IntervalGlobal import *

from toontown.battle import BattleProps
from toontown.toonbase import ToontownGlobals
from toontown.suit import SuitTimings
from toontown.suit.SuitDNA import SuitDNA
from toontown.suit.Suit import Suit

from pandac.PandaModules import SmoothMover, Point3, VBase4, Vec3


class DistributedStrikeEnemy(DistributedObject):
    def __init__(self, cr):
        DistributedObject.__init__(self, cr)

        self.type = None
        self.avatar = None
        self.initialPos = None
        self.initialH = None

        self.prop = None

        self.smoother = SmoothMover()
        self.smoother.setSmoothMode(SmoothMover.SMOn)
        self.smoother.setPredictionMode(SmoothMover.PMOn)
        self.smoother.setDelay(DistributedSmoothNode.PredictionLag)

    def announceGenerate(self):
        DistributedObject.announceGenerate(self)

        dna = SuitDNA()
        dna.newSuit(name=self.type)

        self.avatar = Suit()
        self.avatar.setDNA(dna)
        self.avatar.loop('walk')
        self.avatar.setH(self.initialH)
        self.avatar.reparentTo(render)

        self.spawn()

        taskMgr.add(self.__smoothPosition, self.uniqueName('smooth-position'))

    def spawn(self):
        skyPos = Point3(self.initialPos)
        skyPos.setZ(self.initialPos.getZ() + SuitTimings.fromSky * ToontownGlobals.SuitWalkSpeed)

        groundF = 28
        dur = self.avatar.getDuration('landing')
        fr = self.avatar.getFrameRate('landing')
        animTimeInAir = groundF / fr
        impactLength = dur - animTimeInAir
        timeTillLanding = SuitTimings.fromSky - impactLength
        waitTime = timeTillLanding - animTimeInAir

        self.prop = BattleProps.globalPropPool.getProp('propeller')
        propDur = self.prop.getDuration('propeller')
        lastSpinFrame = 8

        fr = self.prop.getFrameRate('propeller')
        spinTime = lastSpinFrame / fr
        openTime = (lastSpinFrame+1) / fr

        lerpPosTrack = Sequence(Func(self.avatar.setH, self.initialH),
                                self.avatar.posInterval(timeTillLanding, self.initialPos, startPos=skyPos),
                                Wait(impactLength))
        fadeInTrack = Sequence(Func(self.avatar.setTransparency, 1),
                               self.avatar.colorScaleInterval(1, colorScale=VBase4(1, 1, 1, 1),
                                                              startColorScale=VBase4(1, 1, 1, 0)),
                               Func(self.avatar.clearColorScale), Func(self.avatar.clearTransparency))
        animTrack = Sequence(Func(self.avatar.pose, 'landing', 0), Wait(waitTime),
                             ActorInterval(self.avatar, 'landing', duration=dur),
                             Func(self.avatar.loop, 'walk'))

        self.attachPropeller()

        propInSound = base.loadSfx('phase_5/audio/sfx/ENC_propeller_in.ogg')
        propTrack = Parallel(SoundInterval(propInSound, duration=waitTime+dur, node=self.avatar),
                             Sequence(
                                 ActorInterval(self.prop, 'propeller', constrainedLoop=1, duration=waitTime+spinTime,
                                               startTime=0.0, endTime=spinTime),
                                 ActorInterval(self.prop, 'propeller', duration=propDur-openTime, startTime=openTime),
                                 Func(self.detachPropeller)))

        Sequence(
            Parallel(lerpPosTrack, fadeInTrack, animTrack, propTrack, name=self.uniqueName('trackName')),
            Func(self.setToInitialPos)
        ).start()

    def attachPropeller(self):
        if self.prop is None:
            self.prop = BattleProps.globalPropPool.getProp('propeller')

        head = self.avatar.find('**/joint_head')
        self.prop.reparentTo(head)

    def detachPropeller(self):
        if self.prop:
            self.prop.cleanup()
            self.prop.removeNode()
            self.prop = None

    def setToInitialPos(self):
        self.smoother.clearPositions(0)
        self.smoother.setPos(self.initialPos)
        self.smoother.setH(self.initialH)
        self.smoother.setPhonyTimestamp()
        self.smoother.markPosition()
        self.smoother.applySmoothPosHpr(self.avatar, self.avatar)
        self.smoother.clearPositions(1)

    def __smoothPosition(self, task):
        self.smoother.computeAndApplySmoothPosHpr(self.avatar, self.avatar)
        return task.cont

    def setType(self, type):
        self.type = type

    def setInitialPos(self, x, y, z, h):
        self.initialPos = Point3(x, y, z)
        self.initialH = h

    def setPosition(self, x, y, z, h, timestamp):
        self.smoother.setPos(x, y, z)
        self.smoother.setH(h)

        now = globalClock.getFrameTime()
        local = globalClockDelta.networkToLocalTime(timestamp, now)

        self.smoother.setTimestamp(local)
        self.smoother.markPosition()
