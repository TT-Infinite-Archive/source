from direct.interval.IntervalGlobal import *
from toontown.classicchars import CCharPaths
from toontown.safezone import Playground
from toontown.toonbase import TTLocalizer

from toontown.nametag.NametagGroup import *
from toontown.toonbase import ToontownGlobals
from toontown.safezone import Butterfly
from toontown.safezone import ButterflyGlobals

import random


class TTPlayground(Playground.Playground):
    def __init__(self, loader, parentFSM, doneEvent):
        Playground.Playground.__init__(self, loader, parentFSM, doneEvent)

        self.skyBoxLoop = None
        self.butterflies = []

    def enter(self, requestStatus):
        Playground.Playground.enter(self, requestStatus)
        taskMgr.doMethodLater(1, self.__birds, 'TT-birds')
        self.createButterflies()

        if not base.wantTrolleyTTC:
            self.loadTrolleyConstruction()

    def loadTrolleyConstruction(self):
        self.constructionSign = loader.loadModel('phase_4/models/props/construction_sign.bam')
        self.constructionSign.setPosHpr(-131.5, -66.776, 0.545, 127, 0, 0)
        self.constructionSign.reparentTo(render)

        self.cone = loader.loadModel('phase_3.5/models/props/barrier_cone.bam')
        self.cone.setPosHpr(-136, -66, 0.545, 20, 0, 0)
        self.cone.reparentTo(render)

        self.cone2 = loader.loadModel('phase_3.5/models/props/barrier_cone.bam')
        self.cone2.setPosHpr(-143, -84, 0.545, 100, 0, 0)
        self.cone2.reparentTo(render)

        self.cone3 = loader.loadModel('phase_3.5/models/props/barrier_cone.bam')
        self.cone3.setPosHpr(-156, -71, 0.545, 150, 0, 0)
        self.cone3.reparentTo(render)

    def createButterflies(self):
        playground = ButterflyGlobals.TTC
        areas = ButterflyGlobals.PLAYGROUND_TO_POINTS[playground]
        for area in areas:
            butterfly = Butterfly.Butterfly(area)
            self.butterflies.append(butterfly)

    def cleanupButterflies(self):
        for butterfly in self.butterflies:
            butterfly.cleanup()
        del self.butterflies[:]

    def unloadTrolleyConstruction(self):
        self.constructionSign.removeNode()
        del self.constructionSign

        self.cone.removeNode()
        del self.cone

        self.cone2.removeNode()
        del self.cone2

        self.cone3.removeNode()
        del self.cone3

    def exit(self):
        taskMgr.remove('TT-birds')
        self.cleanupButterflies()

        if not base.wantTrolleyTTC:
            self.unloadTrolleyConstruction()

        Playground.Playground.exit(self)

    def showPaths(self):
        self.showPathPoints(CCharPaths.getPaths(TTLocalizer.Mickey))

    def __birds(self, task):
        base.playSfx(random.choice(self.loader.birdSound))
        time = random.random() * 20.0 + 1
        taskMgr.doMethodLater(time, self.__birds, 'TT-birds')
        return Task.done

    def enableTimeEffects(self):
        Playground.Playground.enableTimeEffects(self)
        return
        
        self.loader.hood.startSpookySky()
        render.setColorScale(0.55, 0.55, 0.65, 1)
    
    def disableTimeEffects(self):
        Playground.Playground.disableTimeEffects(self)
        return
        
        render.setColorScale(1, 1, 1, 1)
