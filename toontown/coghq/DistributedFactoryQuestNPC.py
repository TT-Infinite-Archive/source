from pandac.PandaModules import *
from toontown.toonbase.ToontownGlobals import *
from direct.interval.IntervalGlobal import *
from direct.distributed import DistributedObject
from toontown.toon import NPCToons
from toontown.chat.ChatGlobals import CFSpeech


class DistributedFactoryQuestNPC(DistributedObject.DistributedObject, NodePath):
    def __init__(self, cr):
        DistributedObject.DistributedObject.__init__(self, cr)
        node = render.attachNewNode('DistributedFactoryQuestNPC')
        NodePath.__init__(self, node)
        self.animTrack = None
        self.cage = None
        self.cageDoor = None
        self.toon = None

        self.sphereRadius = 4.5
        self.npcId = 0

    def generate(self):
        DistributedObject.DistributedObject.generate(self)

    def delete(self):
        if self.toon is not None:
            self.toon.removeNode()
            self.toon = None
        if self.cage is not None:
            self.cage.removeNode()
            self.cage = None
        if self.cageDoor is not None:
            self.cageDoor.removeNode()
            self.cageDoor = None
        if self.animTrack is not None:
            if self.animTrack.isPlaying():
                self.animTrack.finish()
            self.animTrack = None
        if self.collNode is not None:
            self.collNode.clearSolids()

        self.ignore(self.uniqueName('enterCageSphere'))
        self.removeNode()
        DistributedObject.DistributedObject.delete(self)

    def announceGenerate(self):
        DistributedObject.DistributedObject.announceGenerate(self)
        self.load()
        self.coll = CollisionSphere(0, 0, 2, self.sphereRadius)
        self.coll.setTangible(1)
        self.collNode = CollisionNode(self.uniqueName('CageSphere'))
        self.collNode.setCollideMask(WallBitmask)
        self.collNode.addSolid(self.coll)
        self.cage.attachNewNode(self.collNode)
        self.accept(self.uniqueName('enterCageSphere'), self.handleEnterSphere)

    def setNpcId(self, npcId):
        self.npcId = npcId

    def load(self):
        self.cageDoorSfx = loader.loadSfx('phase_5/audio/sfx/CHQ_SOS_cage_door.ogg')
        self.cageLowerSfx = loader.loadSfx('phase_5/audio/sfx/CHQ_SOS_cage_lower.ogg')
        sellbotRoom = loader.loadModel('phase_9/models/cogHQ/BossRoomHQ')

        self.cage = sellbotRoom.find('**/cage')
        self.cage.setPos(0.0, 0.0, 0.0)
        self.cage.setHpr(180, 0.0, 0.0)
        self.cage.setScale(1.0)

        self.cageDoor = sellbotRoom.find('**/cage_door')
        self.toon = NPCToons.createLocalNPC(self.npcId)
        self.toon.setHpr(180, 0.0, 0.0)

        self.cage.reparentTo(self)
        self.cageDoor.reparentTo(self.cage)
        self.toon.reparentTo(self.cage)

        sellbotRoom.removeNode()
        del sellbotRoom

    def handleEnterSphere(self, collEntry = None):
        self.d_requestSave()

    def d_requestSave(self):
        self.sendUpdate('requestSave', [])

    def saveNpc(self, avId):
        self.avId = avId
        self.ignore(self.uniqueName('enterCageSphere'))
        if self.animTrack:
            self.animTrack.finish()
            self.animTrack = None

        self.animTrack = Sequence()
        self.animTrack.append(Parallel(self.cageDoor.hprInterval(0.5, VBase3(0, 90, 0), blendType='easeOut'),
                                        Sequence(SoundInterval(self.cageDoorSfx), duration=0.5)))
        self.animTrack.append(Wait(0.2))
        self.animTrack.append(Func(self.toon.animFSM.request, 'walk'))
        self.animTrack.append(self.toon.posInterval(0.8, Point3(0, -6, 0)))
        self.animTrack.append(Func(self.toon.animFSM.request, 'neutral'))
        self.animTrack.append(Func(self.toon.setChatAbsolute, TTLocalizer.FactoryQuestNPCSpeech[self.npcId], CFSpeech))
        self.animTrack.append(Wait(3.0))
        self.animTrack.append(Func(self.toon.clearChat))
        self.animTrack.append(ActorInterval(self.toon, 'wave'))
        self.animTrack.append(Func(self.toon.animFSM.request, 'TeleportOut'))
        self.animTrack.append(Wait(4.0))
        self.animTrack.append(Func(self.toon.delete))
        self.animTrack.append(Parallel(self.cageDoor.hprInterval(0.5, VBase3(0, 0, 0), blendType='easeOut'),
                                       SoundInterval(self.cageDoorSfx)))
        self.animTrack.append(Parallel(self.cage.posInterval(0.5, Point3(0.0, 0.0, 15)),
                                       SoundInterval(self.cageLowerSfx, duration=1)))
        self.animTrack.append(Func(self.cage.hide))
        self.animTrack.append(Func(self.saveFinish))
        self.animTrack.start()

    def saveFinish(self):
        self.sendUpdate('saveFinish', [])