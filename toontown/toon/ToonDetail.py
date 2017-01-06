from direct.directnotify.DirectNotifyGlobal import directNotify
from otp.avatar.AvatarDetail import AvatarDetail
from toontown.toon.DistributedToon import DistributedToon


class ToonDetail(AvatarDetail):
    notify = directNotify.newCategory('ToonDetail')

    def getDClass(self):
        return 'DistributedToon'

    def createHolder(self):
        toon = DistributedToon(base.cr, bFake=True)
        toon.forceAllowDelayDelete()
        return toon
