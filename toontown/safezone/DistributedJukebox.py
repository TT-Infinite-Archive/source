from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.distributed.DistributedObject import DistributedObject
from direct.actor.Actor import Actor, CollisionNode, CollisionTube
from toontown.toonbase import ToontownGlobals
from toontown.safezone import JukeboxGlobals
import random


class DistributedJukebox(DistributedObject):
    notify = directNotify.newCategory('DistributedJukebox')

    def __init__(self, cr):
        DistributedObject.__init__(self, cr)
        self.music = None
        self.queue = []
        self.jukebox = None
        self.collNodePath = None
        self.collNode = None
        self.gui = None
        self.posHpr = [0, 0, 0, 0, 0, 0]

    def generate(self):
        DistributedObject.generate(self)
        self.load()
        self.activateCollision()

    def load(self):
        self.jukebox = Actor(
            'phase_13/models/parties/jukebox_model', {'dance': 'phase_13/models/parties/jukebox_dance'}
        )
        self.jukebox.reparentTo(render)
        self.jukebox.loop('dance', fromFrame=0, toFrame=48)
        self.jukebox.setPosHpr(*self.posHpr)
        self.collNode = CollisionNode(self.getCollisionName())
        self.collNode.setCollideMask(ToontownGlobals.CameraBitmask | ToontownGlobals.WallBitmask)
        collTube = CollisionTube(0, 0, 0, 0.0, 0.0, 4.25, 2.25)
        collTube.setTangible(1)
        self.collNode.addSolid(collTube)
        self.collNodePath = self.jukebox.attachNewNode(self.collNode)

    def delete(self):
        self.deactivateCollision()
        self.collNode.removeNode()
        self.collNodePath.removeNode()
        self.jukebox.delete()
        DistributedObject.delete(self)

    def getCollisionName(self):
        return self.uniqueName('jukeboxCollision')

    def activateCollision(self):
        self.accept('enter' + self.getCollisionName(), self.__handleEnterCollision)

    def deactivateCollision(self):
        self.ignore('enter' + self.getCollisionName())

    def __handleEnterCollision(self, collisionEntry):
        # Play a random song for now
        self.d_requestPlaySong(random.choice(JukeboxGlobals.Songs.keys()))

    def d_requestPlaySong(self, songId):
        self.sendUpdate('requestPlaySong', [songId])

    def setMusic(self, songId):
        self.stopMusic()
        song = JukeboxGlobals.Songs.get(songId)
        self.music = song.getAudioSound()
        self.music.play()

    def setQueue(self, queue):
        self.queue = queue

    def stopMusic(self):
        if self.music is not None:
            self.music.stop()
            self.music = None

    def setPosHpr(self, x, y, z, h, p, r):
        self.posHpr = [x, y, z, h, p, r]
        if self.jukebox:
            self.jukebox.setPosHpr(*self.posHpr)
