from toontown.safezone.DistributedTreasureAI import DistributedTreasureAI


class DistributedMeritTreasureAI(DistributedTreasureAI):
    def __init__(self, air, treasureManager, treasureType, meritValue, pos, finalPos, dropImmediate=False):
        DistributedTreasureAI.__init__(self, air, treasureManager, treasureType, pos[0], pos[1], pos[2])

        self.meritValue = meritValue
        self.finalPos = finalPos
        self.grabberId = 0  # When the local playDropTrack plays, this will tell it to be grabbed now and who to go to
        self.dropImmediate = dropImmediate  # If we want the treasure to drop immediately

    def generate(self):
        DistributedTreasureAI.generate(self)
        self.d_setFinalPosition(self.finalPos)

        if self.dropImmediate:
            self.d_playDropTrack()

    def getFinalPosition(self):
        return self.finalPos

    def getMeritValue(self):
        return self.meritValue

    def b_setFinalPosition(self, finalPos):
        self.setFinalPosition(finalPos)
        self.d_setFinalPosition(finalPos)

    def setFinalPosition(self, finalPos):
        self.finalPos = (finalPos[0], finalPos[1], finalPos[2])

    def d_setFinalPosition(self, finalPos):
        self.sendUpdate('setFinalPosition', [finalPos[0], finalPos[1], finalPos[2]])

    def d_playDropTrack(self):
        self.sendUpdate('playDropTrack', [])

    def setGrabberId(self, grabberId):
        self.grabberId = grabberId

    def requestGrabberGrab(self):
        # If we have a grabber on the AI side, this will make the grabberId grab the treasure
        if self.grabberId == 0:
            return
        grabberId = self.grabberId
        self.grabberId = 0
        if grabberId not in self.treasurePlanner.factory.avIdList:
            self.notify.warning('Tried to make toon %s whose not in factory grab a treasure.' % grabberId)
            return

        self.requestGrab(grabberId)




