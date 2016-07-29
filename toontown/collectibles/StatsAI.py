from direct.directnotify.DirectNotifyGlobal import directNotify
from toontown.collectibles.StatGlobals import *


class StatsAI:
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

        self.statToSaveFunc = {
            StatCategoryFish: self.av.d_setStatFish,
            StatCategoryCog: self.av.d_setStatCog,
            StatCategoryGolf: self.av.d_setStatGolf,
            StatCategoryRace: self.av.d_setStatRace,
            StatCategoryTreasure: self.av.d_setStatTreasure
        }

    def fillFromNetList(self, netList):
        for item in netList:
            if item[0] not in self.stats:
                self.stats[item[0]] = {}
            self.stats[item[0]][item[1]] = item[2]
        self.notify.debug('Filled Stats: %s From NetList: %s' % (self.stats, netList))

    def makeNetList(self, category=None):
        netList = []
        if category is not None:
            for objective in self.stats[category]:
                amount = self.stats[category][objective]
                netList.append((category, objective, amount))
        else:
            for cat in self.stats:
                catStat = self.stats[cat]
                for objective in catStat:
                    amount = catStat[objective]
                    netList.append((cat, objective, amount))
        return netList

    def setStatistic(self, category, objective, amount):
        self.notify.debug('Setting stat for av %d: [cat: %d, obj: %d, amt: %s]' % (self.av.doId, category, objective, amount))
        self.stats[category][objective] = amount

    def getStatistic(self, category, objective):
        return self.stats[category][objective]

    def saveStat(self, category):
        self.notify.debug('Saving stats for av %d in category %d' % (self.av.doId, category))
        func = self.statToSaveFunc[category]
        func(self.makeNetList(category))
