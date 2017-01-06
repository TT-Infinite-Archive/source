from datetime import datetime
import random


class Catalog():
    def __init__(self, items=None, metaItems=None):
        self.items = items
        self.metaItems = metaItems

    def getMetaItems(self, avatar, duplicateItems):
        items = []
        for metaItem in self.metaItems:
            items.extend(metaItem.getItems(avatar, duplicateItems))
        return items


class WeeklyCatalog(Catalog):
    def __init__(self, series=None, number=None, items=None, metaItems=None, isSale=False, newRod=False,
                 newCloset=False):
        Catalog.__init__(self, items=items, metaItems=metaItems)
        self.series = series
        self.number = number
        self.isSale = isSale
        self.newRod = newRod
        self.newCloset = newCloset


class SeasonalCatalog(Catalog):
    def __init__(self, startTime, endTime, items=None, metaItems=None):
        self.startTime = startTime
        self.endTime = endTime
        Catalog.__init__(self, items=items, metaItems=metaItems)


class YearlyCatalog(SeasonalCatalog):
    def __init__(self, items=None, metaItems=None, startYear=2003, endYear=2003):
        SeasonalCatalog.__init__(self,
            startTime=datetime(month=1, day=1, year=startYear),
            endTime=datetime(month=12, day=31, year=endYear),
            items=items, metaItems=metaItems)


class MetaItem():
    def __init__(self, metaId=None, count=1):
        self.metaId = metaId
        self.count = count

    def getItems(self, avatar, duplicateItems):
        choosenItems = []
        items = MetaItems[self.metaId][:]
        for i in xrange(self.count):
            item = self.choose(items, avatar, duplicateItems)
            if not item:
                continue
            choosenItems.append(item)
        return choosenItems

    def choose(self, items, avatar, duplicateItems):
        if len(items) == 0:
            return
        index = random.randrange(len(items))
        item = items.pop(index)
        if self.isInvalid(item, avatar, duplicateItems):
            self.choose(items, avatar, duplicateItems)
        return item

    def isInvalid(self, item, avatar, duplicateItems):
        return item.notOfferedTo(avatar)\
            or item.reachedPurchaseLimit(avatar)\
            or item in duplicateItems\
            or item in avatar.backCatalog \
            or item in avatar.weeklyCatalog


from CatalogClothingItem import getAllClothes
from CatalogChatItem import getChatRange
from CatalogWallpaperItem import getWallpapers
from CatalogFlooringItem import getFloorings
from CatalogMouldingItem import getAllMouldings
from CatalogWainscotingItem import getAllWainscotings
from CatalogPetTrickItem import getAllPetTricks

MetaItems = {
    100: getAllClothes(101, 102, 103, 104, 105, 106, 107, 108, 109, 109, 111, 115, 201, 202, 203, 204, 205,
                       206, 207, 208, 209, 209, 211, 215),
    300: getAllClothes(301, 302, 303, 304, 305, 308, 401, 403, 404, 405, 407, 451, 452, 453),
    2000: getChatRange(0, 1999),
    2010: getChatRange(2000, 2999),
    2020: getChatRange(3000, 3999),
    2030: getChatRange(4000, 4999),
    2040: getChatRange(6000, 6999),
    2050: getChatRange(7000, 7999),
    2900: getChatRange(10000, 10002, 10005, 10005, 10007, 10008, 10010, 10099),
    2910: getChatRange(11000, 11005, 11008, 11008, 11012, 11015, 11017, 11019, 11021, 11022),
    2920: getChatRange(12000, 12049),
    2921: getChatRange(12050, 12099),
    2930: getChatRange(13000, 13099),
    2940: getChatRange(14000, 14099),
    3000: getWallpapers(1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100),
    3010: getWallpapers(2200, 2300, 2400, 2500, 2600, 2700, 2800),
    3020: getWallpapers(2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600),
    3030: getWallpapers(3700, 3800, 3900),
    3500: getAllWainscotings(1000, 1010),
    3510: getAllWainscotings(1020),
    3520: getAllWainscotings(1030),
    3530: getAllWainscotings(1040),
    4000: getFloorings(1000, 1010, 1020, 1030, 1040, 1050, 1060, 1070, 1080, 1090, 1100),
    4010: getFloorings(1110, 1120, 1130),
    4020: getFloorings(1140, 1150, 1160, 1170, 1180, 1190),
    4500: getAllMouldings(1000, 1010),
    4510: getAllMouldings(1020, 1030, 1040),
    4520: getAllMouldings(1070),
    5000: getAllPetTricks()}
MetaItemChatKeysSold = (2000, 2010, 2020, 2030, 2040, 2050, 2900, 2910, 2920, 2921, 2930)


def getAllChatItemsSold():
    result = []
    for key in MetaItemChatKeysSold:
        result += MetaItems[key]

    return result