from direct.directnotify import DirectNotifyGlobal
from toontown.suit import SuitDNA
from toontown.coghq import CogDisguiseGlobals
from toontown.hood import ZoneUtil

MeritMultiplier = 0.5


class PromotionManagerAI:
    notify = DirectNotifyGlobal.directNotify.newCategory('PromotionManagerAI')

    def __init__(self, air):
        self.air = air

    def awardMerits(self, avId, deptId, amount):
        av = self.air.doId2do.get(avId)
        if av is None:
            return
        if not CogDisguiseGlobals.isSuitComplete(av.getCogParts(), SuitDNA.suitDepts[deptId]):
            self.notify.debug('Av %d without suit for dept %d cannot receive merits.' % (avId, deptId))
            return

        # Get the most merits this av can have at the moment
        max = CogDisguiseGlobals.getTotalMerits(av, deptId)
        # Get the merit list the av has at the moment
        meritList = av.getCogMerits()
        # Add the amount the av earned
        meritList[deptId] += amount
        if meritList[deptId] > max:
            # Cap the amount
            meritList[deptId] = max
        # Update the avatar with the new list
        av.b_setCogMerits(meritList)

    def recoverMerits(self, av, cogList, zoneId, extraMerits=None, hardValue=0, multiplier=1):
        avId = av.getDoId()
        meritsRecovered = [0, 0, 0, 0]
        multiplier *= self.air.holidayManager.meritMultiplier
        if extraMerits is None:
            extraMerits = [0, 0, 0, 0]
        for i in xrange(len(extraMerits)):
            if CogDisguiseGlobals.isSuitComplete(av.getCogParts(), i):
                meritsRecovered[i] += extraMerits[i]
                self.notify.debug('recoverMerits: extra merits = %s' % extraMerits[i])
        if ZoneUtil.getHoodId(zoneId) == ZoneUtil.SellbotHQ:
            # Patch for factory merit system
            if CogDisguiseGlobals.isSuitComplete(av.getCogParts(), SuitDNA.suitDepts[3]):
                meritsRecovered[3] += (hardValue * multiplier)
        for cogDict in cogList:
            # If we pass a hard value, we don't need to check cogs
            if hardValue:
                break
            # Add the worth of each cog the avatar destroyed
            dept = SuitDNA.suitDepts.index(cogDict['track'])
            if avId in cogDict['activeToons']:
                if CogDisguiseGlobals.isSuitComplete(av.getCogParts(), SuitDNA.suitDepts.index(cogDict['track'])):
                    self.notify.debug('recoverMerits: checking against cogDict: %s' % cogDict)
                    if not cogDict['isVirtual']:
                        merits = cogDict['level'] * MeritMultiplier
                        if cogDict['track'] != 3:
                            merits *= multiplier
                        merits = int(round(merits))
                        if cogDict['hasRevives']:
                            merits *= 2
                        meritsRecovered[dept] += merits
                        self.notify.debug('recoverMerits: merits = %s' % merits)
                    else:
                        self.notify.debug('recoverMerits: virtual cog!')
        if meritsRecovered != [0, 0, 0, 0]:
            actualCounted = [0, 0, 0, 0]
            merits = av.getCogMerits()
            for i in xrange(len(meritsRecovered)):
                max = CogDisguiseGlobals.getTotalMerits(av, i)
                if max:
                    if merits[i] + meritsRecovered[i] <= max:
                        actualCounted[i] = meritsRecovered[i]
                        merits[i] += meritsRecovered[i]
                    else:
                        actualCounted[i] = max - merits[i]
                        merits[i] = max
                    av.b_setCogMerits(merits)
            if reduce(lambda x, y: x + y, actualCounted):
                self.air.writeServerEvent('merits', avId, '%s|%s|%s|%s' % tuple(actualCounted))
                self.notify.debug('recoverMerits: av %s recovered merits %s' % (avId, actualCounted))

        return meritsRecovered
