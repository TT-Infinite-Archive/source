from pandac.PandaModules import *
from toontown.toonbase.ToontownGlobals import *
from direct.interval.IntervalGlobal import *
from toontown.effects.DustCloud import DustCloud
from direct.distributed import DistributedObject


class DistributedFactoryQuestBarrel(DistributedObject.DistributedObject, NodePath):
    def __init__(self, cr):
        DistributedObject.DistributedObject.__init__(self, cr)
        node = render.attachNewNode('DistributedFactoryQuestBarrel')
        NodePath.__init__(self, node)
        self.animTrack = None
        self.shadow = 0
        self.barrelScale = 0.5
        self.sphereRadius = 3.5
        self.playSoundForRemoteToons = 1
        self.gagNode = None
        self.gagModel = None
        self.barrel = None
        self.meritImage = None

    def generate(self):
        DistributedObject.DistributedObject.generate(self)

    def delete(self):
        if self.gagNode is not None:
            self.gagNode.removeNode()
            self.gagNode = None
        if self.barrel is not None:
            self.barrel.removeNode()
            self.barrel = None
        if self.meritImage is not None:
            self.meritImage.removeNode()
            self.meritImage = None
        self.removeNode()
        DistributedObject.DistributedObject.delete(self)

    def announceGenerate(self):
        DistributedObject.DistributedObject.announceGenerate(self)
        self.loadModel()
        self.collSphere = CollisionSphere(0, 0, 0, self.sphereRadius)
        self.collSphere.setTangible(0)
        self.collNode = CollisionNode(self.uniqueName('barrelSphere'))
        self.collNode.setIntoCollideMask(WallBitmask)
        self.collNode.addSolid(self.collSphere)
        self.collNodePath = self.barrel.attachNewNode(self.collNode)
        self.collNodePath.hide()
        self.accept(self.uniqueName('enterbarrelSphere'), self.handleEnterSphere)

    def loadModel(self):
        self.barrel = loader.loadModel('phase_4/models/cogHQ/gagTank')
        self.barrel.setScale(self.barrelScale)
        self.barrel.reparentTo(self)

        dcsNode = self.barrel.find('**/gagLabelDCS')
        dcsNode.setColor(0.15, 0.15, 0.1)

        self.gagNode = self.barrel.attachNewNode('gagNode')
        self.gagNode.setPosHpr(0.0, -2.62, 4.0, 0, 0, 0)
        self.gagNode.setColorScale(0.7, 0.7, 0.6, 1)

        self.meritImage = loader.loadModel('phase_4/models/minigames/salesIcon')
        self.meritImage.reparentTo(self.gagNode)
        self.meritImage.setScale(1.5)
        self.meritImage.setPos(0, -0.1, 0)

    def handleEnterSphere(self, collEntry = None):
        self.d_requestGrab()

    def d_requestGrab(self):
        self.sendUpdate('requestGrab', [])

    def setGrab(self, avId):
        self.notify.debug('handleGrab %s' % avId)
        self.avId = avId
        self.ignore(self.uniqueName('entertreasureSphere'))
        if self.animTrack:
            self.animTrack.finish()
            self.animTrack = None

        def getDustCloudSequence(node):
            dustCloud = DustCloud(fBillboard=0, wantSound=1)
            dustCloud.setBillboardAxis(2.0)
            dustCloud.setScale(0.35, 0.35, 0.5)
            dustCloud.setPos(0.0, 0.0, 0.1)
            dustCloud.createTrack()
            return Sequence(Func(dustCloud.reparentTo, node), dustCloud.track, Func(dustCloud.destroy), name='barrelPoofOut')

        dustCloudSeq = getDustCloudSequence(self)
        self.animTrack = Sequence(Func(self.barrel.hide), dustCloudSeq, Func(self.resetBarrel), Func(self.deleteLater), name=self.uniqueName('animTrack'))
        self.animTrack.start()

    def resetBarrel(self):
        self.barrel.setScale(self.barrelScale)
        self.accept(self.uniqueName('entertreasureSphere'), self.handleEnterSphere)

    def deleteLater(self):
        self.collNodePath.stash()
        taskMgr.doMethodLater(1.0, self.deleteNow, self.uniqueName('-deleteLater'))

    def deleteNow(self, task=None):
        self.delete()
