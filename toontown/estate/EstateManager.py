from direct.distributed import DistributedObject
from direct.directnotify import DirectNotifyGlobal
from . import Estate

class EstateManager(DistributedObject.DistributedObject):
    notify = DirectNotifyGlobal.directNotify.newCategory('EstateManager')
    neverDisable = 1

    def __init__(self, cr):
        DistributedObject.DistributedObject.__init__(self, cr)
        self.availableZones = 0
        self.popupInfo = None
        return

    def disable(self):
        self.notify.debug("i'm disabling EstateManager rightnow.")
        self.ignore('getLocalEstateZone')
        self.ignoreAll()
        if self.popupInfo:
            self.popupInfo.destroy()
            self.popupInfo = None
        DistributedObject.DistributedObject.disable(self)
        return

    def allocateMyEstateZone(self):
        self.getLocalEstateZone(base.localAvatar.getDoId())

    def getLocalEstateZone(self, avId):
        self.sendUpdate('getEstateZone', [avId])

    def setEstateZone(self, ownerId, zoneId, shardId):
        self.notify.debug('setEstateZone(%s, %s, %s)' % (ownerId, zoneId, shardId))
        if shardId > 0:
            base.localAvatar.switchingShards = True
        messenger.send('setLocalEstateZone', [ownerId, zoneId, shardId])

    def mapAvatar(self, ownerId):
        self.sendUpdate('mapAvatar', [ownerId])

    def generate(self):
        self.notify.debug('BASE: generate')
        DistributedObject.DistributedObject.generate(self)
        base.cr.estateManager = self
        self.accept('getLocalEstateZone', self.getLocalEstateZone)
        self.announceGenerateName = self.uniqueName('generate')

        if base.localAvatar.switchingShards:
            self.mapAvatar(base.localAvatar.switchingShards)
            base.localAvatar.switchingShards = False

    def setAvHouseId(self, avId, houseIds):
        self.notify.debug('setAvHouseId %d' % base.localAvatar.doId)
        for av in base.cr.avList:
            if av.id == avId:
                houseId = houseIds[av.position]
                ownerAv = base.cr.doId2do.get(avId)
                if ownerAv:
                    ownerAv.b_setHouseId(houseId)
                return

    def sendAvToPlayground(self, avId, retCode):
        self.notify.debug('sendAvToPlayground: %d' % avId)
        messenger.send('kickToPlayground', [retCode])

    def leaveEstate(self):
        if self.isDisabled():
            self.notify.warning('EstateManager disabled; unable to leave estate.')
            return
        self.sendUpdate('exitEstate')

    def removeFriend(self, ownerId, avId):
        self.notify.debug('removeFriend ownerId = %s, avId = %s' % (ownerId, avId))
        self.sendUpdate('removeFriend', [ownerId, avId])

    def startAprilFools(self):
        if isinstance(base.cr.playGame.getPlace(), Estate.Estate):
            base.cr.playGame.getPlace().startAprilFoolsControls()

    def stopAprilFools(self):
        if isinstance(base.cr.playGame.getPlace(), Estate.Estate):
            base.cr.playGame.getPlace().stopAprilFoolsControls()
