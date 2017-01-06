from direct.directnotify.DirectNotifyGlobal import directNotify
from otp.avatar.AvatarDetail import AvatarDetail
from toontown.pets.DistributedPet import DistributedPet


class PetDetail(AvatarDetail):
    notify = directNotify.newCategory('PetDetail')

    def getDClass(self):
        return 'DistributedPet'

    def createHolder(self):
        pet = DistributedPet(base.cr, bFake=True)
        pet.forceAllowDelayDelete()
        pet.generateInit()
        pet.generate()
        return pet

    def __handleResponse(self, gotData, avatar, dclass):
        if avatar != self.avatar:
            self.notify.warning('Ignoring unexpected request for avatar %s' % avatar.doId)
            return
        if gotData:
            avatar.announceGenerate()
            self.callback(avatar)
        else:
            self.callback(None)
        self.callback = None