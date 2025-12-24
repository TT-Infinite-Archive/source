from .Catalog import MetaItem
from .CatalogSchedule import AllWeeklyCatalogs, AllSeasonalCatalogs, PermenantCatalog, NO_YEAR
from . import CatalogItem
from . import CatalogItemList
from .CatalogFurnitureItem import nextAvailableCloset, get50ItemTrunk
from .CatalogPoleItem import nextAvailablePole
from datetime import datetime


class CatalogGenerator:
    notify = directNotify.newCategory('CatalogGenerator')

    def __init__(self):
        self.__itemLists = {}
        self.__releasedItemLists = {}

    def getReleasedCatalogList(self, weekStart):
        dayNumber = weekStart // (24 * 60)
        itemLists = self.__getReleasedItemLists(dayNumber, weekStart)
        return itemLists

    def generateMonthlyCatalog(self, avatar, weekStart):
        dayNumber = weekStart // (24 * 60)
        itemLists = self.__getMonthlyItemLists(dayNumber)
        monthlyCatalog = CatalogItemList.CatalogItemList()

        for items in itemLists:
            for item in items:
                if isinstance(item, MetaItem):
                    saleItem = False
                else:
                    saleItem = item.saleItem

                monthlyCatalog += self.__selectItem(avatar, item, [], saleItem=saleItem)

        return monthlyCatalog

    def generateWeeklyCatalog(self, avatar, week, monthlyCatalog):
        weeklyCatalog = CatalogItemList.CatalogItemList()

        if 1 <= week <= len(AllWeeklyCatalogs):
            catalog = AllWeeklyCatalogs[week - 1]

            for item in catalog.items:
                weeklyCatalog += self.__selectItem(avatar, item, monthlyCatalog, saleItem=catalog.isSale)

            for item in catalog.metaItems:
                weeklyCatalog += self.__selectItem(avatar, item, monthlyCatalog, saleItem=catalog.isSale)

            if catalog.newCloset:
                weeklyCatalog += self.__selectItem(avatar, nextAvailableCloset, monthlyCatalog, saleItem=0)

            if catalog.newRod:
                weeklyCatalog += self.__selectItem(avatar, nextAvailablePole, monthlyCatalog, saleItem=0)

            weeklyCatalog += self.__selectItem(avatar, get50ItemTrunk, monthlyCatalog, saleItem=0)

        return weeklyCatalog

    def generateBackCatalog(self, avatar, week, previousWeek, weeklyCatalog):
        backCatalog = CatalogItemList.CatalogItemList()
        lastBackCatalog = avatar.backCatalog[:]
        thisWeek = min(len(AllWeeklyCatalogs), week - 1)
        lastWeek = min(len(AllWeeklyCatalogs), previousWeek)

        for week in range(thisWeek, lastWeek, -1):
            catalog = AllWeeklyCatalogs[week - 1]
            if not catalog.isSale:
                for item in catalog.items:
                    for obj in self.__selectItem(avatar, item, weeklyCatalog + backCatalog):
                        if obj in PermenantCatalog.items:
                            continue
                        obj.putInBackCatalog(backCatalog, lastBackCatalog)

        if previousWeek < week:
            for item in avatar.weeklyCatalog:
                item.putInBackCatalog(backCatalog, lastBackCatalog)

        backCatalog += lastBackCatalog
        for item in weeklyCatalog:
            while item in backCatalog:
                backCatalog.remove(item)

        return backCatalog

    def __getReleasedItemLists(self, dayNumber, weekStart):
        itemLists = self.__releasedItemLists.get(dayNumber)
        if itemLists is not None:
            return itemLists
        else:
            self.__releasedItemLists.clear()
        now = datetime.now()
        itemLists = []
        for catalog in AllSeasonalCatalogs:
            startTime = catalog.startTime
            endTime = catalog.endTime

            if endTime.year == NO_YEAR:
                if endTime.month < startTime.month:
                    endTime = endTime.replace(year=now.year + 1)
                else:
                    endTime = endTime.replace(year=now.year)

            for item in catalog.items:
                item.saleItem = catalog.isSale

            items = catalog.items

            if catalog.metaItems:
                items.extend(catalog.metaItems)

            if startTime < now < endTime:
                itemLists.append(items)

        self.__releasedItemLists[dayNumber] = itemLists
        return itemLists

    def __getMonthlyItemLists(self, dayNumber):
        itemLists = self.__itemLists.get(dayNumber)
        if itemLists is not None:
            return itemLists

        now = datetime.now()
        itemLists = [PermenantCatalog.items]

        for catalog in AllSeasonalCatalogs:
            startTime = catalog.startTime
            endTime = catalog.endTime

            if startTime.year == NO_YEAR:
                startTime.replace(year=now.year)

            if endTime.year == NO_YEAR:
                if endTime.month < startTime.month:
                    endTime = endTime.replace(year=now.year + 1)
                else:
                    endTime = endTime.replace(year=now.year)

            if startTime < now < endTime:
                items = catalog.items
                if catalog.metaItems:
                    items.extend(catalog.metaItems)
                itemLists.append(items)

        self.__itemLists[dayNumber] = itemLists
        return itemLists

    def __selectItem(self, avatar, item, duplicateItems, saleItem=0):
        selection = []
        if isinstance(item, MetaItem):
            items = item.getItems(avatar, duplicateItems)
            for item in items:
                if item.notOfferedTo(avatar):
                    continue
                item.saleItem = saleItem
                selection.append(item)
            return selection

        if callable(item):
            item = item(avatar, duplicateItems)

        if isinstance(item, CatalogItem.CatalogItem):
            if item.notOfferedTo(avatar):
                return selection
            item.saleItem = saleItem
            selection.append(item)

        return selection
