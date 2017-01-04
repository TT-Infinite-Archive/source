from direct.actor import Actor
from direct.distributed.ClockDelta import PartBundle, HideInterval, ShowInterval
from direct.interval.IntervalGlobal import *
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.fsm.FSM import FSM
from panda3d.core import NodePath, Vec4, Point3, LODNode, CollisionSphere, CollisionNode

from toontown.toonbase import ToontownGlobals
import random


class Butterfly(FSM):
    notify = directNotify.newCategory('Butterfly')
    wingTypes = ('wings_1', 'wings_2', 'wings_3', 'wings_4', 'wings_5', 'wings_6')
    yellowColors = (Vec4(1, 1, 1, 1), Vec4(0.2, 0, 1, 1), Vec4(0.8, 0, 1, 1))
    whiteColors = (
        Vec4(0.8, 0, 0.8, 1),
        Vec4(0, 0.8, 0.8, 1),
        Vec4(0.9, 0.4, 0.6, 1),
        Vec4(0.9, 0.4, 0.4, 1),
        Vec4(0.8, 0.5, 0.9, 1),
        Vec4(0.4, 0.1, 0.7, 1))
    paleYellowColors = (
        Vec4(0.8, 0, 0.8, 1),
        Vec4(0.6, 0.6, 0.9, 1),
        Vec4(0.7, 0.6, 0.9, 1),
        Vec4(0.8, 0.6, 0.9, 1),
        Vec4(0.9, 0.6, 0.9, 1),
        Vec4(1, 0.6, 0.9, 1)
    )
    shadowScaleBig = Point3(0.07, 0.07, 0.07)
    shadowScaleSmall = Point3(0.01, 0.01, 0.01)

    def __init__(self, positions):
        FSM.__init__(self, self.uniqueName('ButterflyFSM'))
        self.notify.debug('Initializing %s' % str(positions))
        self.butterfly = None
        self.butterfly2 = None
        self.butterflyNode = None
        self.dropShadow = None
        self.positions = positions
        self.glideWeight = random.random() * 2
        self.curIndex = 0
        self.ival = None
        self.load()
        self.__initCollisions()
        self.request('Landed')

    def load(self):
        if self.butterfly:
            return
        self.butterfly = Actor.Actor()
        self.butterfly.loadModel('phase_4/models/props/SZ_butterfly-mod.bam')
        self.butterfly.loadAnims({
            'flutter': 'phase_4/models/props/SZ_butterfly-flutter.bam',
            'glide': 'phase_4/models/props/SZ_butterfly-glide.bam',
            'land': 'phase_4/models/props/SZ_butterfly-land.bam'
        })
        random.seed(id(self))
        index = random.randint(0, len(self.wingTypes) - 1)
        chosenType = self.wingTypes[index]
        node = self.butterfly.getGeomNode()
        for wType in self.wingTypes:
            wing = node.find('**/' + wType)
            if wType != chosenType:
                wing.removeNode()
            else:
                if index == 0 or index == 1:
                    random.seed(id(self))
                    color = random.choice(self.yellowColors)
                elif index == 2 or index == 3:
                    random.seed(id(self))
                    color = random.choice(self.whiteColors)
                elif index == 4:
                    random.seed(id(self))
                    color = random.choice(self.paleYellowColors)
                else:
                    color = Vec4(1, 1, 1, 1)
                wing.setColor(color)

        self.butterfly2 = Actor.Actor(other=self.butterfly)
        self.butterfly.enableBlend(blendType=PartBundle.BTLinear)
        self.butterfly.loop('flutter')
        self.butterfly.loop('land')
        self.butterfly.loop('glide')
        random.seed(id(self))
        playRate = 0.6 + 0.8 * random.random()
        self.butterfly.setPlayRate(playRate, 'flutter')
        self.butterfly.setPlayRate(playRate, 'land')
        self.butterfly.setPlayRate(playRate, 'glide')
        self.butterfly2.setPlayRate(playRate, 'flutter')
        self.butterfly2.setPlayRate(playRate, 'land')
        self.butterfly2.setPlayRate(playRate, 'glide')
        lodNode = LODNode('butterfly-node')
        lodNode.addSwitch(100, 40)
        lodNode.addSwitch(40, 0)
        self.butterflyNode = NodePath(lodNode)
        self.butterfly2.setH(180.0)
        self.butterfly2.reparentTo(self.butterflyNode)
        self.butterfly.setH(180.0)
        self.butterfly.reparentTo(self.butterflyNode)
        self.dropShadow = loader.loadModel('phase_3/models/props/drop_shadow')
        self.dropShadow.setColor(0, 0, 0, 0.3)
        self.dropShadow.setPos(0, 0.1, -0.05)
        self.dropShadow.setScale(self.shadowScaleBig)
        self.dropShadow.reparentTo(self.butterfly)

    def cleanup(self):
        self.request('Off')
        if self.butterfly:
            self.butterfly.cleanup()
            self.butterfly = None
        if self.butterfly2:
            self.butterfly2.cleanup()
            self.butterfly2 = None
        self.butterflyNode.removeNode()
        self.__deleteCollisions()
        FSM.cleanup(self)

    def uniqueName(self, name):
        return name + '-%d' % id(self)

    def __detectAvatars(self):
        self.accept('enter' + self.cSphereNode.getName(), self.__handleCollisionSphereEnter)

    def __ignoreAvatars(self):
        self.ignore('enter' + self.cSphereNode.getName())

    def __initCollisions(self):
        self.cSphere = CollisionSphere(0.0, 1.0, 0.0, 3.0)
        self.cSphere.setTangible(0)
        self.cSphereNode = CollisionNode(self.uniqueName('cSphereNode'))
        self.cSphereNode.addSolid(self.cSphere)
        self.cSphereNodePath = self.butterflyNode.attachNewNode(self.cSphereNode)
        self.cSphereNodePath.hide()
        self.cSphereNode.setCollideMask(ToontownGlobals.WallBitmask)

    def __deleteCollisions(self):
        del self.cSphere
        del self.cSphereNode
        self.cSphereNodePath.removeNode()
        del self.cSphereNodePath

    def __handleCollisionSphereEnter(self, collEntry):
        self.request('Fly')

    def enterOff(self):
        if self.butterflyNode is not None:
            self.butterflyNode.reparentTo(hidden)

    def exitOff(self):
        if self.butterflyNode is not None:
            self.butterflyNode.reparentTo(render)

    @property
    def nextPos(self):
        return self.positions[self.nextIndex]

    @property
    def nextIndex(self):
        idx = self.curIndex
        if self.positions[-1] == self.positions[idx]:
            idx = 0
        else:
            idx += 1
        return idx

    def enterFly(self):
        self.__ignoreAvatars()
        destPos = self.nextPos
        curPos = self.positions[self.curIndex]
        flyHeight = max(self.positions[self.curIndex][2], destPos[2]) + 2.2
        curPosHigh = Point3(curPos[0], curPos[1], flyHeight)
        destPosHigh = Point3(destPos[0], destPos[1], flyHeight)
        takeoffTime = 1.4
        landTime = 1.4
        moveTime = 1.5 + random.random()
        flyTime = takeoffTime + landTime + moveTime
        self.butterflyNode.setPos(curPos)
        self.dropShadow.show()
        self.dropShadow.setScale(self.shadowScaleBig)
        oldHpr = self.butterflyNode.getHpr()
        self.butterflyNode.headsUp(destPos)
        newHpr = self.butterflyNode.getHpr()
        self.butterflyNode.setHpr(oldHpr)
        takeoffShadowT = 0.2 * takeoffTime
        landShadowT = 0.2 * landTime
        self.butterfly2.loop('flutter')
        self.ival = Sequence(
            Parallel(
                # Fly up
                LerpPosHprInterval(self.butterflyNode, takeoffTime, curPosHigh, newHpr),
                LerpAnimInterval(self.butterfly, takeoffTime, 'land', 'flutter'),
                LerpAnimInterval(self.butterfly, takeoffTime, None, 'glide', startWeight=0, endWeight=self.glideWeight),
                Sequence(
                    LerpScaleInterval(self.dropShadow, takeoffShadowT, self.shadowScaleSmall, startScale=self.shadowScaleBig),
                    HideInterval(self.dropShadow)
                )
            ),
            # Fly to the point above the position
            LerpPosInterval(self.butterflyNode, flyTime, destPosHigh),
            # Land
            Parallel(
                LerpPosInterval(self.butterflyNode, landTime, destPos),
                LerpAnimInterval(self.butterfly, landTime, 'flutter', 'land'),
                LerpAnimInterval(self.butterfly, landTime, None, 'glide', startWeight=self.glideWeight, endWeight=0),
                Sequence(
                    Wait(landTime - landShadowT),
                    ShowInterval(self.dropShadow), LerpScaleInterval(self.dropShadow, landShadowT, self.shadowScaleBig, startScale=self.shadowScaleSmall)
                )
            ),
            name=self.uniqueName('Butterfly')
        )
        self.ival.start()
        taskMgr.doMethodLater(self.ival.getDuration(), self.__handleLandTask, self.uniqueName('toLandTask'))

    def exitFly(self):
        taskMgr.remove(self.uniqueName('toLandTask'))
        if self.ival is not None:
            self.ival.finish()
            self.ival = None

    def enterLanded(self):
        self.__detectAvatars()
        self.curIndex = self.nextIndex
        curPos = self.positions[self.curIndex]
        self.butterflyNode.setPos(curPos)
        self.dropShadow.show()
        self.dropShadow.setScale(self.shadowScaleSmall)
        self.butterfly.setControlEffect('land', 1.0)
        self.butterfly.setControlEffect('flutter', 0.0)
        self.butterfly.setControlEffect('glide', 0.0)
        self.butterfly2.pose('land', random.randrange(self.butterfly2.getNumFrames('land')))
        taskMgr.doMethodLater(random.randint(2, 10), self.__handleFlyTask, self.uniqueName('toFlyTask'))

    def exitLanded(self):
        taskMgr.remove(self.uniqueName('toFlyTask'))
        self.__ignoreAvatars()

    def __handleLandTask(self, task=None):
        self.request('Landed')

    def __handleFlyTask(self, task=None):
        self.request('Fly')
