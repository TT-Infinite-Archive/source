from toontown.coghq.FactoryExterior import FactoryExterior


class BossbotOfficeExterior(FactoryExterior):
    notify = directNotify.newCategory('BossbotOfficeExterior')

    def enterWalk(self, teleportIn=0):
        FactoryExterior.enterWalk(self, teleportIn)

        self.ignore('teleportQuery')
        base.localAvatar.setTeleportAvailable(0)
