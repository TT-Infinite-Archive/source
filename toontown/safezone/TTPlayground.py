from pandac.PandaModules import Vec3, Point3

from direct.interval.IntervalGlobal import *
from direct.task.Task import Task

from toontown.chat.ChatGlobals import *
from toontown.classicchars import CCharPaths
from toontown.safezone import Playground
from toontown.suit import Suit, SuitDNA
from toontown.toon import Toon, ToonDNA
from toontown.toonbase import TTLocalizer

from toontown.nametag.NametagGroup import *
from panda3d.core import *
from toontown.toonbase import ToontownGlobals

import random


class TTPlayground(Playground.Playground):
    def __init__(self, loader, parentFSM, doneEvent):
        Playground.Playground.__init__(self, loader, parentFSM, doneEvent)

        self.skyBoxLoop = None

    def enter(self, requestStatus):
        Playground.Playground.enter(self, requestStatus)
        taskMgr.doMethodLater(1, self.__birds, 'TT-birds')

        if base.cr.newsManager.isStormEnabled():
            self.loadStormProps()

    def loadStormProps(self):
        # Storm: No birds.
        taskMgr.remove('TT-birds')

        # Storm: Documents.
        self.documents = loader.loadModel('phase_11/models/lawbotHQ/LB_evidence.bam')
        self.documents.reparentTo(render)
        self.documents.setPos(90, -14, 4.025)
        self.documents.setHpr(-305, 0, 0)
        self.documents.setScale(40)

        self.crate = loader.loadModel('phase_9/models/cogHQ/woodCrateB.bam')
        self.crate.reparentTo(render)
        self.crate.setPos(43.44, -27.84, 5.44)
        self.crate.setHpr(170.54, 0, 33.69)
        self.crate.setScale(1)

        self.crate2 = loader.loadModel('phase_9/models/cogHQ/woodCrateB.bam')
        self.crate2.reparentTo(render)
        self.crate2.setPos(-38, -71, 0.025)
        self.crate2.setHpr(24, 0, 0)
        self.crate2.setScale(1)

        self.crate3 = loader.loadModel('phase_9/models/cogHQ/woodCrateB.bam')
        self.crate3.reparentTo(render)
        self.crate3.setPos(99.162, -34.474, 18.739)
        self.crate3.setScale(1)

        self.crate4 = loader.loadModel('phase_9/models/cogHQ/woodCrateB.bam')
        self.crate4.reparentTo(render)
        self.crate4.setPos(45.625, 16.459, 4.025)
        self.crate4.setHpr(107, 0, 0)
        self.crate4.setScale(1)

        self.crate5 = loader.loadModel('phase_9/models/cogHQ/woodCrateB.bam')
        self.crate5.reparentTo(render)
        self.crate5.setPos(87.74,  -25.83,  4.03)
        self.crate5.setHpr(20.00, 0, 0)
        self.crate5.setScale(1.57)

        self.crate6 = loader.loadModel('phase_9/models/cogHQ/woodCrateB.bam')
        self.crate6.reparentTo(render)
        self.crate6.setPos(86.93,  -26.01,  12.61)
        self.crate6.setHpr(0, 0, 0)
        self.crate6.setScale(1.30)

        self.woodpiece = loader.loadModel('phase_4/models/modules/wood_piece.bam')
        self.woodpiece.reparentTo(render)
        self.woodpiece.setPos(130.59,  -50.05,  -31.59)
        self.woodpiece.setHpr(45.34, 328.39, 0)
        self.woodpiece.setScale(1.8,2,1.8)

        self.cab_ground = loader.loadModel('phase_11/models/lawbotHQ/LB_filing_cabB.bam')
        self.cab_ground.reparentTo(render)
        self.cab_ground.setPos(110.739, -16.757, 4.025)
        self.cab_ground.setHpr(272, 0, 0)
        self.cab_ground.setScale(1)

        self.pstacks = loader.loadModel('phase_11/models/lawbotHQ/LB_paper_big_stacks2.bam')
        self.pstacks.reparentTo(render)
        self.pstacks.setPos(99, -34, 4.025)
        self.pstacks.setHpr(-306, 0, 0)
        self.pstacks.setScale(1.3)

        self.whirlwind = loader.loadModel('phase_5/models/cogdominium/tt_m_ara_cfg_whirlwind.bam')
        self.whirlwind.reparentTo(render)
        self.whirlwind.setPos(140, -41, 4)
        self.whirlwind.setHpr(1461, 0, 0)
        self.whirlwind.setScale(1.1)

        # Moving the tornado
        whirlPosInterval1 = LerpPosInterval(self.whirlwind,
                                               duration=12,
                                               pos=Point3(140, -41, 4),
                                               startPos=Point3(155.594,  1.093, 4),
                                               blendType='easeInOut')

        whirlPosInterval2 = LerpPosInterval(self.whirlwind,
                                            duration=12,
                                            pos=Point3(171.831, -122.539, 4),
                                            startPos=Point3(140, -41, 4),
                                            blendType='easeInOut')

        whirlPosInterval3 = LerpPosInterval(self.whirlwind,
                                            duration=12,
                                            pos=Point3(189.243, -38.862, 4),
                                            startPos=Point3(171.831, -122.539, 4),
                                            blendType='easeInOut')

        whirlPosInterval4 = LerpPosInterval(self.whirlwind,
                                            duration=12,
                                            pos=Point3(155.594,  1.093, 4),
                                            startPos=Point3(189.243, -38.862, 4),
                                            blendType='easeInOut')

        self.whirlTrack = self.whirlwind.hprInterval(2, Vec3(360, 0, 0))
        self.whirlTrack.loop()
        self.whirlPace = Sequence(whirlPosInterval1,
                                  whirlPosInterval2,
                                  whirlPosInterval3,
                                  whirlPosInterval4,
                                  name="whirlPace")

        self.whirlPace.loop()

        self.crate7 = loader.loadModel('phase_9/models/cogHQ/woodCrateB.bam')
        self.crate7.reparentTo(self.whirlwind)
        self.crate7.setPos(0,5,40)
        self.crate7.setHpr(34, -12, 3)
        self.crate7.setScale(1)

        flyingCratePosInterval1 = LerpPosInterval(self.crate7,
                                               duration=2,
                                               pos=Point3(0,3,35),
                                               startPos=Point3(0,3,50),
                                               blendType='easeInOut')

        flyingCratePosInterval2 = LerpPosInterval(self.crate7,
                                               duration=2,
                                               pos=Point3(0,3,35),
                                               startPos=Point3(0,3,35),
                                               blendType='easeInOut')

        flyingCratePosInterval3 = LerpPosInterval(self.crate7,
                                               duration=2,
                                               pos=Point3(0,3,50),
                                               startPos=Point3(0,3,35),
                                               blendType='easeInOut')

        self.flyingCrateTrack = self.crate7.hprInterval(2, Vec3(360, 0, 0))
        self.flyingCrateTrack.loop()
        self.flyingCratePace = Sequence(flyingCratePosInterval1,
                                  flyingCratePosInterval2,
                                  flyingCratePosInterval3,
                                  name="flyingCratePace")
        self.flyingCratePace.loop()

        self.cab = loader.loadModel('phase_11/models/lawbotHQ/LB_filing_cabB.bam')
        self.cab.reparentTo(self.whirlwind)
        self.cab.setPos(0, 5, 10)
        self.cab.setHpr(4, 8, 25)
        self.cab.setScale(1)

        cabPosInterval1 = LerpPosInterval(self.cab,
                                               duration=1,
                                               pos=Point3(0,2,22),
                                               startPos=Point3(0,2,28),
                                               blendType='easeInOut')

        cabPosInterval2 = LerpPosInterval(self.cab,
                                               duration=1,
                                               pos=Point3(0,2,23),
                                               startPos=Point3(0,2,22),
                                               blendType='easeInOut')

        cabPosInterval3 = LerpPosInterval(self.cab,
                                               duration=1,
                                               pos=Point3(0,2,28),
                                               startPos=Point3(0,2,23),
                                               blendType='easeInOut')

        self.cabTrack = self.cab.hprInterval(2, Vec3(360, 0, 0))
        self.cabTrack.loop()
        self.cabPace = Sequence(cabPosInterval1,
                                  cabPosInterval2,
                                  cabPosInterval3,
                                  name="cabPace")
        self.cabPace.loop()

        self.whirlwind2 = loader.loadModel('phase_5/models/cogdominium/tt_m_ara_cfg_whirlwind.bam')
        self.whirlwind2.reparentTo(render)
        self.whirlwind2.setScale(1, 1, 0.5)

        # Moving the second tornado
        whirl2PosInterval1 = LerpPosInterval(self.whirlwind2,
                                            duration=6,
                                            pos=Point3(-148.088,  66.016,  0.525),
                                            startPos=Point3(-162.982,  37.736,  0.525),
                                            blendType='easeInOut')

        whirl2PosInterval2 = LerpPosInterval(self.whirlwind2,
                                            duration=6,
                                            pos=Point3(-121.603,  94.245,  0.525),
                                            startPos=Point3(-148.088,  66.016,  0.525),
                                            blendType='easeInOut')

        whirl2PosInterval3 = LerpPosInterval(self.whirlwind2,
                                            duration=6,
                                            pos=Point3(-88.334,  111.066,  0.525),
                                            startPos=Point3(-121.603,  94.245,  0.525),
                                            blendType='easeInOut')

        whirl2PosInterval4 = LerpPosInterval(self.whirlwind2,
                                            duration=6,
                                            pos=Point3(-108.957,  132.262,  0.525),
                                            startPos=Point3(-88.334,  111.066,  0.525),
                                            blendType='easeInOut')

        whirl2PosInterval5 = LerpPosInterval(self.whirlwind2,
                                            duration=6,
                                            pos=Point3(-144.679,  93.690,  0.525),
                                            startPos=Point3(-108.957,  132.262,  0.525),
                                            blendType='easeInOut')

        whirl2PosInterval6 = LerpPosInterval(self.whirlwind2,
                                            duration=6,
                                            pos=Point3(-166.587,  44.754,  0.525),
                                            startPos=Point3(-144.679,  93.690,  0.525),
                                            blendType='easeInOut')

        whirl2PosInterval7 = LerpPosInterval(self.whirlwind2,
                                            duration=6,
                                            pos=Point3(-162.982,  37.736,  0.525),
                                            startPos=Point3(-166.587,  44.754,  0.525),
                                            blendType='easeInOut')

        self.whirlTrack2 = self.whirlwind2.hprInterval(1, Vec3(360, 0, 0))
        self.whirlTrack2.loop()
        self.whirlPace2 = Sequence(whirl2PosInterval1,
                                  whirl2PosInterval2,
                                  whirl2PosInterval3,
                                  whirl2PosInterval4,
                                  whirl2PosInterval5,
                                  whirl2PosInterval6,
                                  whirl2PosInterval7,
                                  name="whirl2Pace")
        self.whirlPace2.loop()

        # Storm: Sky box loop.
        self.skyBoxLoop = self.loader.hood.sky.hprInterval(100, Vec3(-360, 0, 0))
        self.skyBoxLoop.loop()

        # Collision Sphere around the area where the cutscene is
        self.cutsceneSite = render.attachNewNode('cutsceneSite')
        cn = CollisionNode('cutsceneSphere')
        cn.setIntoCollideMask(ToontownGlobals.WallBitmask)
        self.cutsceneSphere = self.cutsceneSite.attachNewNode(cn)
        self.cutsceneSphere.setPos(86.812, -14.687, 4.025)
        cs = CollisionSphere(0, 0, 0, 16)
        cs.setTangible(1)
        self.cutsceneSphere.node().addSolid(cs)
        self.cutsceneSphere.hide()

    def unloadStormProps(self):
        self.documents.removeNode()
        del self.documents

        self.crate.removeNode()
        del self.crate

        self.crate2.removeNode()
        del self.crate2

        self.crate3.removeNode()
        del self.crate3

        self.crate4.removeNode()
        del self.crate4

        self.crate5.removeNode()
        del self.crate5

        self.crate6.removeNode()
        del self.crate6

        self.crate7.removeNode()
        del self.crate7

        self.woodpiece.removeNode()
        del self.woodpiece

        self.cab.removeNode()
        del self.cab

        self.cab_ground.removeNode()
        del self.cab_ground

        self.pstacks.removeNode()
        del self.pstacks

        self.whirlwind.removeNode()
        del self.whirlwind

        self.whirlwind2.removeNode()
        del self.whirlwind2

        self.whirlTrack.finish()
        del self.whirlTrack

        self.whirlTrack2.finish()
        del self.whirlTrack2

        self.cabTrack.finish()
        del self.cabTrack

        self.cabPace.finish()
        del self.cabPace

        self.whirlPace.finish()
        del self.whirlPace

        self.whirlPace2.finish()
        del self.whirlPace2

        self.flyingCrateTrack.finish()
        del self.flyingCrateTrack

        self.flyingCratePace.finish()
        del self.flyingCratePace

        self.cutsceneSite.removeNode()

        if self.skyBoxLoop:
            self.skyBoxLoop.finish()
            self.skyBoxLoop = None

    def exit(self):
        taskMgr.remove('TT-birds')

        if base.cr.newsManager.isStormEnabled():
            self.unloadStormProps()

        Playground.Playground.exit(self)

    def showPaths(self):
        self.showPathPoints(CCharPaths.getPaths(TTLocalizer.Mickey))

    def __birds(self, task):
        base.playSfx(random.choice(self.loader.birdSound))
        time = random.random() * 20.0 + 1
        taskMgr.doMethodLater(time, self.__birds, 'TT-birds')
        return Task.done

    def enableTimeEffects(self):
        if not base.cr.newsManager.isStormEnabled():
            Playground.Playground.enableTimeEffects(self)
            return
        
        self.loader.hood.startSpookySky()
        render.setColorScale(0.55, 0.55, 0.65, 1)
    
    def disableTimeEffects(self):
        if not base.cr.newsManager.isStormEnabled():
            Playground.Playground.disableTimeEffects(self)
            return
        
        render.setColorScale(1, 1, 1, 1)
