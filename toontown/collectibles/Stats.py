from direct.directnotify.DirectNotifyGlobal import directNotify
from toontown.toonbase import EventGlobals
from toontown.collectibles.StatGlobals import CollectibleCategoryToObjective


class Stats:
    notify = directNotify.newCategory('Stats')

    def __init__(self, av):
        # { Category: { Objective: Amount } }
        self.stats = {}
        self.av = av

        for category in CollectibleCategoryToObjective:
            self.stats[category] = {}
            for objective in CollectibleCategoryToObjective[category]:
                self.stats[category][objective] = 0

        self.notify.debug('Instantiated %s' % self.stats)

    def fillFromNetList(self, netList):
        for item in netList:
            if item[0] not in self.stats:
                self.stats[item[0]] = {}
            self.stats[item[0]][item[1]] = item[2]
        self.notify.debug('Filled Stats: %s From NetList: %s' % (self.stats, netList))

    def makeNetList(self):
        netList = []
        for category in self.stats:
            catStat = self.stats[category]
            for objective in catStat:
                amount = catStat[objective]
                netList.append((category, objective, amount))
        self.notify.debug(netList)
        return netList

    def setStatistic(self, category, objective, amount):
        if self.getStatistic(category, objective) == amount:
            return
        self.stats[category][objective] = amount
        messenger.send(EventGlobals.StatUpdated, [category, objective])

    def getStatistic(self, category, objective):
        return self.stats[category][objective]
