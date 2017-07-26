from direct.distributed.DistributedObjectGlobal import DistributedObjectGlobal
from panda3d.core import Multifile, Filename, VirtualFileSystem
import os


class ZoneManager(DistributedObjectGlobal):
    notify = directNotify.newCategory('ZoneManager')
    notify.setDebug(1)
    COMPLETED = 1
    NOT_DOWNLOADED = 0
    OUTDATED = -1

    def __init__(self, cr):
        DistributedObjectGlobal.__init__(self, cr)

        self.completedZones = []
        self.modifiedZones = []
        self.modifiedZonesSet = False
        self.zone2blob = {}
        self.currentRequestedZone = 0
        self.currentFileSize = 0

    def announceGenerate(self):
        DistributedObjectGlobal.announceGenerate(self)

    def requestModifiedZones(self):
        self.sendUpdate('requestModifiedZones', [])

    def delete(self):
        DistributedObjectGlobal.delete(self)

    def setModifiedZones(self, zones):
        self.modifiedZones = zones

        del self.completedZones[:]

        self.modifiedZonesSet = True

    def getModifiedZones(self):
        return self.modifiedZones

    def requestZoneData(self, zone):
        self.currentRequestedZone = zone
        location = os.path.join('..', 'resources', 'zone_%d.mf' % zone)
        if not os.path.exists(location):
            self.sendUpdate('requestZoneData', [zone, ''])
        else:
            import hashlib
            with open(location, 'rb') as f:
                currentZoneData = f.read()
                hash = hashlib.md5(currentZoneData).hexdigest()
                self.sendUpdate('requestZoneData', [zone, hash])

    def setZoneComplete(self, zone):
        self.completedZones.append(zone)
        self.currentRequestedZone = 0
        self.currentFileSize = 0

    def setZoneOutdated(self, zone):
        if zone in self.completedZones:
            self.completedZones.remove(zone)
            location = os.path.join('..', 'resources', 'zone_%d.mf' % zone)
            if os.path.exists(location):
                os.remove(location)

    def setBlobId(self, blobId, mode, filesize):
        if mode == ZoneManager.COMPLETED:
            self.notify.debug('Zone %s is completed. Mounting...' % self.currentRequestedZone)
            filename = os.path.join('..', 'resources', 'zone_%d.mf' % self.currentRequestedZone)
            self.mountFile(filename)
            self.setZoneComplete(self.currentRequestedZone)
            self.notify.debug('Completed zones: %s' % self.completedZones)
            return
        elif mode == ZoneManager.OUTDATED:
            self.notify.debug('Zone %s is outdated! Removing...' % self.currentRequestedZone)
            self.setZoneOutdated(self.currentRequestedZone)

        self.currentFileSize = filesize
        blob = base.cr.doId2do.get(blobId)
        if not blob:
            self.acceptOnce('blob-generated-%d' % blobId, self.__handleBlobGenerated)
        else:
            self.__handleBlobGenerated(blob)

    def __handleBlobGenerated(self, blob):
        if blob.isComplete():
            filename = os.path.join('..', 'resources', 'zone_%d.mf' % self.currentRequestedZone)
            self.mountFile(filename)
            self.setZoneComplete(self.currentRequestedZone)
            blob.sendAck()
        else:
            from toontown.launcher.ToontownDownloadWatcher import ToontownDownloadWatcher
            base.downloadWatcher = ToontownDownloadWatcher()

            evtName = self.uniqueName('zoneDone-%d' % self.currentRequestedZone)
            blob.setDoneEvent(evtName)
            self.zone2blob[self.currentRequestedZone] = blob
            self.acceptOnce(evtName, self.__handleBlobDone, extraArgs=[self.currentRequestedZone])

    def __handleBlobDone(self, zone, blob):
        self.notify.debug("Zone blob done.")
        filename = os.path.join('..', 'resources', 'zone_%d.mf' % zone)
        if not blob or not zone:
            return

        self.zone2blob[zone].sendAck()
        del self.zone2blob[zone]

        with open(filename, 'wb+') as f:
            f.write(blob)
            self.notify.info('Wrote file of size: %s' % len(blob))

        self.mountFile(filename)
        self.setZoneComplete(zone)
        base.cleanupDownloadWatcher()

    def mountFile(self, filename):
        mf = Multifile()
        f = Filename(filename)
        mf.openRead(f)
        vfs = VirtualFileSystem.getGlobalPtr()

        mountPoint = '/'

        vfs.mount(mf, mountPoint, 0)

    def getZoneComplete(self, zone):
        r = (zone in self.completedZones or (zone not in self.modifiedZones and self.modifiedZonesSet))
        self.notify.debug('getZoneComplete %s %s %s %s' % (zone, r, self.completedZones, self.currentRequestedZone))
        return r

    def getPercentZoneComplete(self, zone):
        if zone in self.completedZones:
            return 1.0
        elif zone in self.zone2blob:
            blob = self.zone2blob[zone]
            return len(blob.blob) / float(self.currentFileSize)

    def getDNAFiles(self, zone):
        return 'zone_%d/zone_%d.pdna' % (zone, zone), 'zone_%d/storage_zone_%d.pdna' % (zone, zone)
