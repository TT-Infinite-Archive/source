from direct.stdpy.threading2 import Thread
from direct.controls.ControlManager import CollisionHandlerRayStart

from toontown.toonbase import ToontownGlobals
from toontown.dna.DNAStorage import DNAStorage
from toontown.dna import DNAParser

from pandac.PandaModules import NodePath, CollisionTraverser, CollisionRay, CollisionNode
from pandac.PandaModules import CollisionHandlerQueue, BitMask32


class OSTZCalculatorAI(Thread):
    INSTANCE = None

    def __init__(self):
        Thread.__init__(self, target=self.__process, name='ost-z-calculator')

        store = DNAStorage()
        storageFiles = ['phase_4/dna/storage.pdna', 'phase_4/dna/storage_TT.pdna', 'phase_4/dna/storage_OST.pdna']
        DNAParser.DNABulkLoader(store, storageFiles).loadDNAFiles()

        node = DNAParser.loadDNAFile(store, 'phase_4/dna/operation_save_toontown.pdna')
        self.parent = NodePath('ost-z-calculator')
        self.geom = self.parent.attachNewNode(node)

        self.np = NodePath('ost-z-calculator-np')
        self.np.reparentTo(self.parent)

        self.cTrav = CollisionTraverser('ost-z-calculator-ctrav')
        cRay = CollisionRay(0.0, 0.0, CollisionHandlerRayStart, 0.0, 0.0, -1.0)

        cn = CollisionNode('ost-z-calculator-ray')
        cn.addSolid(cRay)
        cn.setFromCollideMask(ToontownGlobals.FloorBitmask)
        cn.setIntoCollideMask(BitMask32.allOff())
        cnp = self.np.attachNewNode(cn)

        self.cHandler = CollisionHandlerQueue()
        self.cTrav.addCollider(cnp, self.cHandler)

        self.queue = []

    def calculateZ(self, x, y, callback):
        self.queue.append((x, y, callback))

    def __process(self):
        while True:
            if len(self.queue) == 0:
                continue

            x, y, callback = self.queue.pop(0)
            self.np.setPos(x, y, 0)

            self.cTrav.traverse(self.parent)

            entries = []

            for i in xrange(self.cHandler.getNumEntries()):
                entry = self.cHandler.getEntry(i)
                entries.append(entry)

            entries.sort(lambda x, y: cmp(y.getSurfacePoint(self.parent).getZ(),
                                          x.getSurfacePoint(self.parent).getZ()))
            if len(entries) > 0:
                z = entries[0].getSurfacePoint(self.parent).getZ()
            else:
                z = 0

            callback(z)

    @staticmethod
    def createInstance():
        OSTZCalculatorAI.INSTANCE = OSTZCalculatorAI()
        OSTZCalculatorAI.INSTANCE.start()
