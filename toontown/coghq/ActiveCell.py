from otp.level import BasicEntities
from direct.directnotify import DirectNotifyGlobal

class ActiveCell(BasicEntities.DistributedNodePathEntity):
    notify = DirectNotifyGlobal.directNotify.newCategory('ActiveCell')

    def __init__(self, cr):
        BasicEntities.DistributedNodePathEntity.__init__(self, cr)
        self.occupantId = -1
        self.state = 0

    def announceGenerate(self):
        BasicEntities.DistributedNodePathEntity.announceGenerate(self)

    def setState(self, state, objId):
        self.state = state
        self.occupantId = objId
