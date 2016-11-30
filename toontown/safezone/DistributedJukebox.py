from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.distributed.DistributedObject import DistributedObject
from direct.actor.Actor import Actor, CollisionNode, CollisionTube
from toontown.toonbase import ToontownGlobals
from toontown.safezone import JukeboxGlobals
import random


class DistributedJukebox(DistributedObject):
    notify = directNotify.newCategory('DistributedJukebox')

    def __init__(self, cr):
        self.notify.debug('Initializing...')
        DistributedObject.__init__(self, cr)
        self.music = None
        self.queue = []
        self.jukebox = None
        self.collNodePath = None
        self.collNode = None
        self.gui = None
        self.posHpr = [0, 0, 0, 0, 0, 0]

    def generate(self):
        self.notify.debug('Generating...')
        DistributedObject.generate(self)
        self.load()
        self.activateCollision()

    def load(self):
        self.notify.debug('Loading...')
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
        self.notify.debug('Deleting...')
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
        self.notify.debug('Toon Collided')
        self.d_requestPlaySong(random.choice(JukeboxGlobals.Songs.keys()))

    def d_requestPlaySong(self, songId):
        self.notify.debug('Sending request to play song %s' % songId)
        self.sendUpdate('requestPlaySong', [songId])

    def setMusic(self, songId):
        self.notify.debug('Playing song %s' % songId)
        self.stopMusic()
        song = JukeboxGlobals.Songs.get(songId)
        self.music = song.getAudioSound()
        self.music.play()

    def setQueue(self, queue):
        self.notify.debug('Updating queue %s' % queue)
        self.queue = queue

    def stopMusic(self):
        self.notify.debug('Stopping music')
        if self.music is not None:
            self.music.stop()
            self.music = None

    def setPosHpr(self, x, y, z, h, p, r):
        self.notify.debug('Setting position')
        self.posHpr = [x, y, z, h, p, r]
        if self.jukebox:
            self.jukebox.setPosHpr(*self.posHpr)
