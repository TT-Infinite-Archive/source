from toontown.toonbase import ToontownGlobals
from toontown.hood import ZoneUtil


def canWearSuit(avatarId, zoneId):
    canonicalZoneId = ZoneUtil.getCanonicalHoodId(zoneId)
    allowedSuitZones = [ToontownGlobals.LawbotHQ,
     ToontownGlobals.CashbotHQ,
     ToontownGlobals.SellbotHQ,
     ToontownGlobals.BossbotHQ]
    if canonicalZoneId in allowedSuitZones:
        return True
    elif zoneId >= ToontownGlobals.DynamicZonesBegin:
        return True
    else:
        return False
