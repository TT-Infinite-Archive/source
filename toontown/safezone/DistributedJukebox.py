from direct.actor.Actor import Actor, CollisionNode, CollisionTube
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.distributed.DistributedObject import DistributedObject
# from direct.filter.CommonFilters import CommonFilters
from panda3d.core import TextNode

from toontown.safezone import JukeboxGlobals
from toontown.toonbase import ToontownGlobals, SettingsGlobals
from toontown.toontowngui.JukeboxGui import JukeboxGui
from toontown.util.VolumeInterval import VolumeInterval
from direct.filter.CommonFilters import CommonFilters
import sys

filters = CommonFilters(base.win, base.cam)

class DistributedJukebox(DistributedObject):
    notify = directNotify.newCategory('DistributedJukebox')

    def __init__(self, cr):
        self.notify.debug('Initializing...')
        DistributedObject.__init__(self, cr)
        self.music = None
        self.songId = 0
        self.queue = []
        self.jukebox = None
        self.sign = None
        self.signText = None
        self.signTextNP = None
        self.collNodePath = None
        self.collNode = None
        self.gui = None
        self.posHpr = [0, 0, 0, 0, 0, 0]
        self.volumeInterval = None
        self.inGui = False

    def generate(self):
        self.notify.debug('Generating...')
        DistributedObject.generate(self)
        self.load()
        self.activateCollision()
        self.gui = JukeboxGui(self)
        self.gui.hide()

    def load(self):
        self.notify.debug('Loading...')
        self.jukebox = Actor(
            'phase_13/models/parties/jukebox_model', {'dance': 'phase_13/models/parties/jukebox_dance'}
        )
        self.jukebox.reparentTo(render)
        self.jukebox.loop('dance', fromFrame=0, toFrame=48)
        self.jukebox.setPosHpr(*self.posHpr)
        if settings.get(SettingsGlobals.AnimationSmoothing):
            self.jukebox.setBlend(frameBlend=True)
        self.collNode = CollisionNode(self.getCollisionName())
        self.collNode.setCollideMask(ToontownGlobals.CameraBitmask | ToontownGlobals.WallBitmask)
        collTube = CollisionTube(0, 0, 0, 0.0, 0.0, 4.25, 2.25)
        collTube.setTangible(1)
        self.collNode.addSolid(collTube)
        self.collNodePath = self.jukebox.attachNewNode(self.collNode)
        self.sign = loader.loadModel('phase_5.5/models/estate/garden_sign.bam')
        self.sign.setPos(3.75, -3.35, 0.01)
        self.sign.setScale(1.5)
        self.sign.reparentTo(self.jukebox)
        self.signText = TextNode('%s-textNode' % self.getDoId())
        self.signText.setText('')
        self.signText.setFont(ToontownGlobals.ToonFont)
        self.signText.setTextColor(0.0, 0.0, 0.0, 1.0)
        self.signText.setAlign(TextNode.ACenter)
        self.signText.setWordwrap(12)
        self.signTextNP = self.sign.attachNewNode(self.signText)
        self.signTextNP.setPos(0.15, -0.15, 1.85)
        self.signTextNP.setScale(0.125)

    def delete(self):
        self.notify.debug('Deleting...')
        self.exitGui()
        self.deactivateCollision()
        if self.signTextNP is not None:
            self.signTextNP.removeNode()
            self.signTextNP = None
        if self.sign is not None:
            self.sign.removeNode()
            self.sign = None
        if self.jukebox is not None:
            self.jukebox.delete()
            self.jukebox = None
        if self.volumeInterval is not None:
            self.volumeInterval.cleanup()
            self.volumeInterval = None
        if self.music is not None:
            self.music.stop()
            self.music = None
        if self.gui is not None:
            self.gui.destroy()
            self.gui = None
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
        self.enterGui()

    def enterGui(self):
        if self.inGui:
            return
        self.inGui = True
        self.gui.show()
        base.cr.playGame.getPlace().setState('purchase')

        if not sys.platform == 'android':
            filters.setBlurSharpen(0)

    def exitGui(self):
        if not self.inGui:
            return
        self.inGui = False
        self.gui.hide()
        base.cr.playGame.getPlace().setState('walk')

        # Remove the blur when the user is done with the jukebox
        if not sys.platform == 'android':
            filters.setBlurSharpen(1)
            filters.delBlurSharpen()

    def d_requestPlaySong(self, songId):
        self.notify.debug('Sending request to play song %s' % songId)
        self.sendUpdate('requestPlaySong', [songId])

    def setMusic(self, songId):
        self.notify.debug('Playing song %s' % songId)
        self.songId = songId
        song = JukeboxGlobals.Songs.get(songId)
        if self.music is not None:
            self.stopMusic()
            self.music = song.getAudioSound()
        else:
            self.music = song.getAudioSound()
            self.playMusic()

    def setQueue(self, queue):
        self.notify.debug('Updating queue %s' % queue)
        self.queue = queue
        self.gui.updateQueue(queue)

    def stopMusic(self):
        self.notify.debug('Stopping music')
        if self.music is not None:
            if self.volumeInterval is not None:
                self.volumeInterval.cleanup()
                self.volumeInterval = None
            self.volumeInterval = VolumeInterval(self.music, 0, JukeboxGlobals.FadeTime, self.handleVolumeIntervalDone)

    def handleVolumeIntervalDone(self):
        self.notify.debug('Volume interval done, playing next song')
        self.volumeInterval = None
        if self.music is not None:
            self.playMusic()

    def playMusic(self):
        self.music.play()
        self.gui.setSongId(self.songId)
        self.setSignSongId(self.songId)

    def setSignSongId(self, songId):
        ttsong = JukeboxGlobals.Songs.get(self.songId)
        if ttsong is None:
            text = 'Error'
        else:
            text = ttsong.name
        self.signText.setText('Currently Playing:\n\n%s' % text)

    def setPosHpr(self, x, y, z, h, p, r):
        self.notify.debug('Setting position')
        self.posHpr = [x, y, z, h, p, r]
        if self.jukebox:
            self.jukebox.setPosHpr(*self.posHpr)
