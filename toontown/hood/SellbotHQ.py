from toontown.coghq.SellbotCogHQLoader import SellbotCogHQLoader
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import ToontownClientGlobals
from toontown.hood.CogHood import CogHood


class SellbotHQ(CogHood):
    notify = directNotify.newCategory('SellbotHQ')

    ID = ToontownGlobals.SellbotHQ
    LOADER_CLASS = SellbotCogHQLoader

    def load(self):
        CogHood.load(self)

        self.sky.setScale(3)

    def enter(self, requestStatus):
        CogHood.enter(self, requestStatus)

        base.localAvatar.setCameraFov(ToontownClientGlobals.CogHQCameraFov)
        base.camLens.setNearFar(ToontownClientGlobals.SellbotHQCameraNear, ToontownClientGlobals.SellbotHQCameraFar)
