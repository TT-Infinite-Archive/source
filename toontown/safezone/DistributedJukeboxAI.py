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
        self.songIsActive = False

    def announceGenerate(self):
        DistributedObjectAI.announceGenerate(self)
        self.requestPlaySong(self.defaultSong)

    def delete(self):
        DistributedObjectAI.delete(self)
        self.cleanupTask()

    def cleanupTask(self):
        # Stops next song task
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
        if not self.songIsActive:
            self.notify.debug('Song not active, playing this song now')
            self.b_setMusic(songId)
            self.songIsActive = True
        if songId in self.queue:
            self.notify.debug('Song in queue, doing nothing')
        else:
            self.queue.append(songId)
            self.d_setQueue(self.queue)

    def playNextSong(self):
        self.cleanupTask()
        self.notify.debug('Playing next song')
        if len(self.queue) == 0:
            songId = self.defaultSong
        else:
            songId = self.queue.pop(0)
            self.d_setQueue(self.queue)
        self.songId = songId
        self.b_setMusic(songId)

    def playNextSongTask(self, task):
        self.playNextSong()
        return task.done

    def setMusic(self, songId):
        song = JukeboxGlobals.Songs.get(songId)
        if song is None:
            return
        delay = song.getLength() + JukeboxGlobals.ServerBufferTime
        self.notify.debug('Starting song timer for song %s set to %s seconds' % (songId, delay))
        taskMgr.doMethodLater(delay, self.playNextSongTask, self.getTaskName())

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
