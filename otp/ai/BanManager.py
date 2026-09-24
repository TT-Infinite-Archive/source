from direct.distributed.DistributedObject import DistributedObject
from direct.directnotify.DirectNotifyGlobal import directNotify
from toontown.toonbase import ToontownClientGlobals

class BanManager(DistributedObject):
    notify = directNotify.newCategory('BanManager')
    neverDisable = 1

    def announceGenerate(self):
        self.cr.banManager = self

    def requestUserInfo(self):
        public_ip = ToontownClientGlobals.getIp()
        mac_address = ToontownClientGlobals.getMac()
        self.sendUpdate('sendUserInfo', [mac_address, public_ip])
