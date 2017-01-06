from direct.directnotify.DirectNotifyGlobal import directNotify
from toontown.collectibles import StatGlobals, CollectibleGlobals
from toontown.racing import RaceGlobals
from toontown.suit import SuitBuffGlobals
from toontown.safezone import TreasureGlobals
from otp.ai.MagicWordGlobal import *


class StatManagerAI:
    notify = directNotify.newCategory('StatManagerAI')

    def __init__(self, air):
        self.air = air

    def handleFishCaptured(self, avId, fish):
        self.notify.debug('Handling Avatar %d catching fish %s' % (avId, '\n'.join(str(f) for f in fish)))
        av = self.air.doId2do.get(avId)
        if av is None:
            return
        # Our category is Fish
        category = StatGlobals.StatCategoryFish

        # Fish Count
        self.handleObjectiveCompleted(av, category, StatGlobals.FishAny, len(fish))

        # Unique species
        self.handleObjectiveCompleted(av, category, StatGlobals.FishNewSpecies, len(av.fishCollection), static=1)

        # Save the stats
        av.stats.saveStat(category)

    def handleGolfCompleted(self, avIds, courseId):
        self.notify.debug('Handling avs %s finishing courseId %d' % (repr(avIds), courseId))

        category = StatGlobals.StatCategoryGolf
        for avId in avIds:
            av = self.air.doId2do.get(avId)
            if av is None:
                continue

            # Any Course
            self.handleObjectiveCompleted(av, category, StatGlobals.GolfAny)

            # Course Difficulty
            if courseId == 0:
                self.handleObjectiveCompleted(av, category, StatGlobals.GolfEasy)
            elif courseId == 1:
                self.handleObjectiveCompleted(av, category, StatGlobals.GolfMedium)
            elif courseId == 2:
                self.handleObjectiveCompleted(av, category, StatGlobals.GolfHard)
            else:
                self.notify.warning('Unhandled courseId %s' % courseId)

            # Save this av's stats
            av.stats.saveStat(category)

    def handleGolfTrophyAcquired(self, avId):
        self.notify.debug('Handling avatar %d acquiring golf trophy' % avId)
        av = self.air.doId2do.get(avId)
        if av is None:
            return
        category = StatGlobals.StatCategoryGolf

        # Trophy Count
        self.handleObjectiveCompleted(av, category, StatGlobals.GolfTrophy)

        # Save stats
        av.stats.saveStat(category)

    def handleRaceCompleted(self, avId, won, trackId, qualify, time):
        av = self.air.doId2do.get(avId)
        if av is None:
            return

        category = StatGlobals.StatCategoryRace

        # Race completed
        self.handleObjectiveCompleted(av, category, StatGlobals.RacingAny)

        # Trophies got
        self.handleObjectiveCompleted(av, category, StatGlobals.RacingTrophy, av.getKartingTrophies(), static=1)

        # Genre specific
        genre = RaceGlobals.getTrackGenre(trackId)
        if genre == RaceGlobals.Speedway:
            self.handleObjectiveCompleted(av, category, StatGlobals.RacingSpeedwayAny)
            if won:
                self.handleObjectiveCompleted(av, category, StatGlobals.RacingSpeedwayWon)
        elif genre == RaceGlobals.Rural:
            self.handleObjectiveCompleted(av, category, StatGlobals.RacingRuralAny)
            if won:
                self.handleObjectiveCompleted(av, category, StatGlobals.RacingRuralWon)
        elif genre == RaceGlobals.Urban:
            self.handleObjectiveCompleted(av, category, StatGlobals.RacingUrbanAny)
            if won:
                self.handleObjectiveCompleted(av, category, StatGlobals.RacingUrbanWon)
        else:
            self.notify.warning('Unknown genre for racing stat %d' % genre)

        # Save the stats for racing
        av.stats.saveStat(category)

    def handleCogsDefeated(self, avs, suits, zoneId):
        # Our category is cog
        category = StatGlobals.StatCategoryCog
        objectiveToAmount = {}
        for suit in suits:
            if suit is not None:
                # All suits qualify as 'Any Cog'
                objectives = [StatGlobals.CogAny]
                # Suit Department
                if suit['track'] in StatGlobals.CogDeptToObjective:
                    objectives.append(StatGlobals.CogDeptToObjective[suit['track']])
                else:
                    self.notify.warning('Unhandled suit dept %s. Not counting...' % suit['track'])
                    continue
                # Virtual Flag
                if suit.get('isVirtual', False):
                    objectives.append(StatGlobals.CogVirtual)
                # Skelecog Flag
                if suit.get('isSkelecog', False):
                    objectives.append(StatGlobals.CogSkelecog)
                # V2 'Flag' (We will assume all cogs with revives are v2)
                if suit.get('hasRevives', False):
                    objectives.append(StatGlobals.CogV2)
                # Valentines day cog
                if suit.get('buffIndex', SuitBuffGlobals.SuitBuffNone) == SuitBuffGlobals.SuitBuffLoveStruck:
                    objectives.append(StatGlobals.CogValentines)

                for objective in objectives:
                    if objective in objectiveToAmount:
                        objectiveToAmount[objective] += 1
                    else:
                        objectiveToAmount[objective] = 1
        for av in avs:
            if av is not None:
                # Add the amounts for the objectives we found
                for objective, amount in objectiveToAmount.items():
                    self.handleObjectiveCompleted(av, category, objective, amount)
                # Save this av's stats
                av.stats.saveStat(category)

    def handleBossDefeated(self, avId, dept):
        pass

    def handleQuestCompleted(self, avId, quest):
        pass

    def handleTreasureObtained(self, av, treasure):
        self.notify.debug('Handling treasure obtained %s' % treasure.treasureType)
        if av is None or treasure is None:
            self.notify.warning('Problem occurred when trying to obtain treasure')
            return
        category = StatGlobals.StatCategoryTreasure
        self.handleObjectiveCompleted(av, category, StatGlobals.TreasureAny)
        if treasure.treasureType == TreasureGlobals.TreasurePD:
            self.handleObjectiveCompleted(av, category, StatGlobals.TreasurePatrickDay)
        av.stats.saveStat(category)

    # Utilities

    def handleObjectiveCompleted(self, av, category, objective, amount=1, static=0):
        if not static:
            after = av.stats.getStatistic(category, objective) + amount
        else:
            after = amount
        av.stats.setStatistic(category, objective, after)
        self.handleStatChanging(av, category, objective)

    def handleStatChanging(self, av, category, objective):
        self.notify.debug('Stat changing (%d, %d, %d)' % (av.doId, category, objective))
        collectibles = CollectibleGlobals.getCollectiblesForStat(category, objective)
        self.notify.debug('Collectibles %s' % collectibles)
        for collectible in collectibles:
            self.notify.debug('Checking if %d is less than or equal to %d' % (collectible.goal, av.stats.getStatistic(category, objective)))
            if collectible.goal <= av.stats.getStatistic(category, objective) and \
                    av.collectibleInventory is not None and \
                    not av.collectibleInventory.isObtained(collectible.reward.category, collectible.reward.itemId):
                self.notify.debug('Awarding item %s to %s' % (collectible.reward.name, av.getName()))
                # This means they just got this item, redeem it for them
                collectible.reward.awardTo(av)


@magicWord(category=CATEGORY_PROGRAMMER, types=[int, int, int])
def statistic(category, objective, amount=None):
    invoker = spellbook.getInvoker()
    if not simbase.air.wantToonStats:
        return 'Cannot add statistic, statistics are disabled.'
    beforeAmount = invoker.stats.getStatistic(category, objective)
    if amount is None:
        amount = beforeAmount + 1
    simbase.air.statManager.handleObjectiveCompleted(invoker, category, objective, amount, 1)
    invoker.stats.saveStat(category)
    return 'Set stat in category %d of objective %d as %s' % (category, objective, amount)

