from direct.distributed.DistributedObject import DistributedObject
from direct.directnotify.DirectNotifyGlobal import directNotify
from toontown.toonbase import ToontownGlobals

class BanManager(DistributedObject):
    notify = directNotify.newCategory('BanManager')
    neverDisable = 1

    def announceGenerate(self):
        self.cr.banManager = self

    def requestUserInfo(self):
        public_ip = ToontownGlobals.getIp()
        mac_address = ToontownGlobals.getMac()
        self.sendUpdate('sendUserInfo', [mac_address, public_ip])
