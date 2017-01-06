from direct.directnotify.DirectNotifyGlobal import directNotify


class AvatarDetail:
    notify = directNotify.newCategory('AvatarDetail')

    def __init__(self, doId, callback):
        self.id = doId
        self.callback = callback
        self.createdAvatar = 0
        self.avatar = base.cr.doId2do.get(self.id)
        self.enterQuery()

    def cleanup(self):
        self.avatar = None
        self.callback = None

    def getId(self):
        return self.id

    def getDClass(self):
        return None

    def enterQuery(self):
        if self.avatar is not None and not self.avatar.ghostMode:
            dclass = self.getDClass()
            self.__handleResponse(True, self.avatar, dclass)
        else:
            self.avatar = self.createHolder()
            self.createdAvatar = 1
            self.avatar.doId = self.id
            dclass = self.getDClass()
            base.cr.getAvatarDetails(self.avatar, self.__handleResponse, dclass)

    def __handleResponse(self, gotData, avatar, dclass):
        if avatar != self.avatar:
            self.notify.warning('Ignoring unexpected request for avatar %s' % avatar.doId)
            return
        if gotData:
            self.callback(avatar)
        else:
            self.callback(None)
        self.callback = None

    def createHolder(self):
        return None
