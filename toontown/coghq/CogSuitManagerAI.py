from toontown.coghq import CogDisguiseGlobals
from toontown.toonbase import ToontownGlobals
from otp.otpbase.OTPGlobals import DisconnectPythonError, DisconnectGraphicsError, DisconnectUnknown

import random


class CogSuitManagerAI:
    def __init__(self, air):
        self.air = air

    def recoverPart(self, av, factoryType, suitTrack, zoneId, avList):
        partsRecovered = [0, 0, 0, 0]
        parts = av.getCogParts()
        suitIndex = ToontownGlobals.cogDept2index[suitTrack]

        if CogDisguiseGlobals.isSuitComplete(parts, suitIndex):
            zoneId = ToontownGlobals.dept2cogHQ(suitTrack)
            av.addTeleportAccess(zoneId)
            return partsRecovered

        partsRecovered[suitIndex] = av.giveGenericCogPart(factoryType, suitIndex)

        if CogDisguiseGlobals.isSuitComplete(av.getCogParts(), suitIndex):
            zoneId = ToontownGlobals.dept2cogHQ(suitTrack)
            toon.addTeleportAccess(zoneId)

        return partsRecovered

    def removeParts(self, toonId, suitDeptIndex):
        toon = self.air.doId2do.get(toonId)

        # Check if the toon is in our doId2do:
        if toon is not None:
            parts = toon.getCogParts()
            if CogDisguiseGlobals.isSuitComplete(parts, suitDeptIndex):
                toon.loseCogParts(suitDeptIndex)
                return

        disconnectReason = self.air.getAvatarDisconnectReason(toonId)
        # Check if the toon crashed:
        if disconnectReason in (DisconnectPythonError, DisconnectGraphicsError, DisconnectUnknown):
            return

        def dbCallback(dclass, fields, toonId=toonId, suitDeptIndex=suitDeptIndex):
            if dclass != self.air.dclassesByName['DistributedToonAI']:
                return

            parts = fields['setCogParts'][0]
            if CogDisguiseGlobals.isSuitComplete(parts, suitDeptIndex):
                # Code from DistributedToonAI.loseCogParts:
                loseCount = random.randrange(CogDisguiseGlobals.MinPartLoss,
                                             CogDisguiseGlobals.MaxPartLoss+1)

                partBitmask = parts[suitDeptIndex]
                partList = list(range(17))

                while loseCount > 0 and partList:
                    losePart = random.choice(partList)
                    partList.remove(losePart)

                    losePartBit = 1 << losePart
                    if partBitmask & losePartBit:
                        partBitmask &= ~losePartBit
                        loseCount -= 1

                parts[suitDeptIndex] = partBitmask

                # Update the cog parts in the db:
                self.air.dbInterface.updateObject(
                    self.air.dbId, toonId,
                    self.air.dclassesByName['DistributedToonAI'],
                    {'setCogParts': (parts,)}
                )

        # It doesn't look like the toon was in our doId2do. Lets query the db:
        self.air.dbInterface.queryObject(self.air.dbId, toonId, dbCallback)
