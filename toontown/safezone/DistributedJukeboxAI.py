from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.distributed.DistributedObjectAI import DistributedObjectAI
from toontown.safezone import JukeboxGlobals


class DistributedJukeboxAI(DistributedObjectAI):
    notify = directNotify.newCategory('DistributedJukeboxAI')
    
    def __init__(self, air, defaultSong):
        DistributedObjectAI.__init__(self, air)
        self.defaultSong = defaultSong
        self.queue = []
        self.posHpr = [0, 0, 0, 0, 0, 0]
        self.songId = self.defaultSong

    def announceGenerate(self):
        DistributedObjectAI.announceGenerate(self)
        self.requestPlaySong(self.defaultSong)

    def delete(self):
        DistributedObjectAI.delete(self)
        taskMgr.remove(self.getTaskName())

    def setPosHpr(self, x, y, z, h, p, r):
        self.posHpr = [x, y, z, h, p, r]

    def getPosHpr(self):
        return self.posHpr

    def requestPlaySong(self, songId):
        self.notify.debug('Got request to play %s' % songId)
        self.addToQueue(songId)

    def addToQueue(self, songId):
        self.notify.debug('Adding song %s to queue' % songId)
        if len(self.queue) == 0:
            self.b_setMusic(songId)
        elif songId in self.queue:
            pass
        else:
            self.queue.append(songId)
            self.d_setQueue(self.queue)

    def playNextSong(self):
        self.notify.debug('Playing next song')
        if len(self.queue) == 0:
            songId = self.defaultSong
        else:
            songId = self.queue.pop()
            self.d_setQueue(self.queue)
        self.songId = songId
        self.b_setMusic(songId)

    def setMusic(self, songId):
        song = JukeboxGlobals.Songs.get(songId)
        if song is None:
            return
        taskMgr.doMethodLater(song.getLength(), self.playNextSong, self.getTaskName(), extraArgs=[])

    def getTaskName(self):
        return 'Jukebox-%d-task' % self.doId

    def b_setMusic(self, songId):
        self.setMusic(songId)
        self.d_setMusic(songId)

    def d_setMusic(self, songId):
        self.sendUpdate('setMusic', [songId])

    def d_setQueue(self, queue):
        self.sendUpdate('setQueue', [queue])

    def getMusic(self):
        return self.songId

    def getQueue(self):
        return self.queue
