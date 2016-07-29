from otp.distributed.DistributedDistrict import DistributedDistrict


class ToontownDistrict(DistributedDistrict):
    notify = directNotify.newCategory('ToontownDistrict')

    def __init__(self, cr):
        DistributedDistrict.__init__(self, cr)

        self.avatarCount = 0
        self.newAvatarCount = 0
        self.invasionStatus = []
        self.timeZone = 0
