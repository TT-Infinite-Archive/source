from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectGlobalAI import DistributedObjectGlobalAI
from toontown.golf import GolfGlobals
from toontown.guilds import GuildGlobals, GuildQuestGlobals
from toontown.toonbase import ToontownGlobals, TTLocalizer
from toontown.toon import GuildMasterGlobals
from otp.ai.MagicWordGlobal import *


class GuildManagerAI(DistributedObjectGlobalAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('GuildManagerAI')

    def announceGenerate(self):
        DistributedObjectGlobalAI.announceGenerate(self)
    
    def handleInstanceCompleted(self, points, involvedToonIds):
        guildId2ToonIds = self.getGuildToInvloved(involvedToonIds)

        for guildId in guildId2ToonIds:
            involvedToons = guildId2ToonIds[guildId]
            guildMemberCount = len(involvedToons)
            multiplier = GuildGlobals.GUILD_BONUS_MULTIPLIER[guildMemberCount]
            guildPoints = points * multiplier
            
            # Alert the UD of the guild's points
            self.d_handleGuildPoints(guildId, guildPoints)
            
            for avId in involvedToons:
                self.notify.debug('Handling Avatar %d defeating boss with %s' % (avId, repr(involvedToonIds)))
                contributionPoints = guildPoints / guildMemberCount
                
                # Alert the UD of this toon's contribution points
                self.d_handleContributionPoints(avId, contributionPoints)
        
    def handleBossDefeated(self, dept, involvedToonIds):
        points = GuildGlobals.BOSS_DEPT_TO_GP[dept]

        # Handle points for instance being completed
        self.handleInstanceCompleted(points, involvedToonIds)

        # Attempt to progress respective quests
        if self.air.wantGuildQuests:
            category = GuildQuestGlobals.GUILD_QUEST_CAT_BOSS
            possibleObjectives = ('any', ToontownGlobals.DeptToDeptName[dept])

            # Pair guilds to involved toons
            guildId2ToonIds = self.getGuildToInvloved(involvedToonIds)
            for guildId in guildId2ToonIds:
                involvedToons = guildId2ToonIds[guildId]
                self.d_attemptProgressQuest(guildId, involvedToons, category, possibleObjectives)

    def handleFactoryDefeated(self, factoryInt, involvedToonIds):
        points = GuildGlobals.INSTANCE_ID_TO_GP[factoryInt]

        # Handle points for instance being completed
        self.handleInstanceCompleted(points, involvedToonIds)
        
        # Attempt to progress respective quests
        if self.air.wantGuildQuests:
            category = GuildQuestGlobals.GUILD_QUEST_CAT_INSTANCE
            possibleObjectives = ('any', ToontownGlobals.InstanceToDept[factoryInt], ToontownGlobals.InstanceToUniqueName[factoryInt])

            # Pair guilds to involved toons
            guildId2ToonIds = self.getGuildToInvloved(involvedToonIds)
            for guildId in guildId2ToonIds:
                involvedToons = guildId2ToonIds[guildId]
                self.d_attemptProgressQuest(guildId, involvedToons, category, possibleObjectives)

    def handleCogDefeated(self, involvedToonIds, suit, zoneId):
        # Pair guilds to involved toons
        self.notify.debug('Handling Cog Defeated %s' % repr(involvedToonIds))
        guildId2ToonIds = self.getGuildToInvloved(involvedToonIds)

        for guildId in guildId2ToonIds:
            involvedToons = guildId2ToonIds[guildId]

            suitType = suit['type']
            if suitType not in ToontownGlobals.SuitToDeptNames.keys():
                self.notify.warning('We don\'t handle suit %s' % suitType)
                return
            self.notify.debug('Handling members %s of guild %s defeating a cog of type %s' % (involvedToons, guildId, suitType))
            
            category = GuildQuestGlobals.GUILD_QUEST_CAT_COG
            possibleObjectives = ('any', ToontownGlobals.SuitToDeptNames[suitType], suitType)
            
            self.d_attemptProgressQuest(guildId, involvedToons, category, possibleObjectives)
    
    def handleFishCaptured(self, avId, fish):
        self.notify.debug('Handling Avatar %d catching a fish %s' % (avId, fish))
        av = self.air.doId2do.get(avId)
        if av is None or av.getGuildId() == 0:
            return
        guildId = av.getGuildId()

        genusId = fish.getGenus()
        speciesId = fish.getSpecies()
        genus = TTLocalizer.FishGenusNames[genusId]
        species = TTLocalizer.FishSpeciesNames[genusId][speciesId]
        
        category = GuildQuestGlobals.GUILD_QUEST_CAT_FISH
        possibleObjectives = ('any', genus, species)
        self.d_attemptProgressQuest(guildId, [avId], category, possibleObjectives)

    def handleGolfCompleted(self, involvedToonIds, courseId):
        self.notify.debug('Handling avs %s finishing courseId %d' % (repr(involvedToonIds), courseId))
        guildId2ToonIds = self.getGuildToInvloved(involvedToonIds)

        for guildId in guildId2ToonIds:
            involvedToons = guildId2ToonIds[guildId]

            category = GuildQuestGlobals.GUILD_QUEST_CAT_GOLF
            possibleObjectives = ('any', GolfGlobals.CourseId2Difficulty[courseId])

            self.d_attemptProgressQuest(guildId, involvedToons, category, possibleObjectives)
    
    def handleTrolleyCompleted(self, involvedToonIds):
        # Pair guilds to involved toons
        guildId2ToonIds = self.getGuildToInvloved(involvedToonIds)

        for guildId in guildId2ToonIds:
            involvedToons = guildId2ToonIds[guildId]

            self.notify.debug('Handling members %s of guild %s completing trolley game' % (involvedToons, guildId))
            
            category = GuildQuestGlobals.GUILD_QUEST_CAT_TROLLEY
            possibleObjectives = ('any',)
            self.d_attemptProgressQuest(guildId, involvedToons, category, possibleObjectives)

    def requestCreateGuildAI(self, name, iconId):
        avId = self.air.getAvatarIdFromSender()
        self.notify.debug('Avatar %d requesting to create a guild... Routing to UD' % avId)

        # Validate the creator
        av = self.air.doId2do.get(avId)
        if av is None:
            return
        if av.getGuildId() != 0:
            self.notify.warning('Avatar %d attempted to create guild but he\'s already in a guild %d' % (avId, av.getGuildId()))
            return
        if av.getMoney() < GuildMasterGlobals.GUILD_COST and not self.air.wantFreeGuilds:
            self.notify.warning('Avatar %d requested to create a guild but they don\'t have enough money' % avId)
            self.sendUpdate('guildError', [GuildGlobals.GUILD_NOT_ENOUGH_JB])
            return

        # Deduct money from the avatar
        money = av.getMoney()
        money -= GuildMasterGlobals.GUILD_COST
        if money < 0:
            money = 0
        av.b_setMoney(money)

        # Send the creation request to the UD
        self.d_requestCreateGuild(avId, name, iconId)

    def requestInvite(self, targetId):
        avId = self.air.getAvatarIdFromSender()
        self.notify.debug('Avatar %d requesting to invite' % avId)
        # Validate the avatar
        av = self.air.doId2do.get(avId)
        if av is None:
            return
        if av.getGuildId() == 0:
            self.notify.warning('Avatar %d requested to invite %d but he wasn\'t in a guild' % (avId, targetId))
            return

        # Send this message on to the UD
        self.d_requestInvite(avId, targetId)

    def toonLaffChanged(self, toonId, laff):
        av = self.air.doId2do.get(toonId)
        if av is None or av.getGuildId() == 0:
            return
        self.d_toonLaffChanged(toonId, laff)

    # Route to UD
    def d_requestInvite(self, senderId, targetId):
        self.sendUpdate('invite', [senderId, targetId])

    def d_requestCreateGuild(self, senderId, guildName, iconId):
        self.sendUpdate('requestCreateGuild', [senderId, guildName, iconId])

    def d_handleGuildPoints(self, guildId, points):
        self.sendUpdate('handleGuildPoints', [guildId, points])

    def d_handleContributionPoints(self, avId, points):
        self.sendUpdate('handleContributionPoints', [avId, points])

    def d_attemptProgressQuest(self, guildId, avIds, category, possibleObjectives):
        self.notify.debug('Sending Quest Progression to the UD for guild %s, with members %s and details %s, %s' % (guildId, avIds, category, repr(possibleObjectives)))
        self.sendUpdate('attemptProgressQuest', [guildId, avIds, category, possibleObjectives])

    def d_completeQuest(self, avId, guildId):
        self.sendUpdate('completeQuest', [avId, guildId])

    def d_progressQuest(self, avId, guildId, amount):
        self.sendUpdate('progressQuest', [avId, guildId, amount])

    def d_resetGuildName(self, guildId, response):
        self.sendUpdate('nameResponse', [guildId, response])

    def d_toonLaffChanged(self, avId, laff):
        self.sendUpdate('toonLaffChanged', [avId, laff])

    def d_adminJoinGuild(self, avId, guildId):
        self.sendUpdate('adminJoinGuild', [avId, guildId])

    def d_adminLeaveGuild(self, avId):
        self.sendUpdate('adminLeaveGuild', [avId])

    # Utilities

    def getGuildToInvloved(self, involvedIds):
        guild2ToonIds = {}

        for avId in involvedIds:
            av = self.air.doId2do.get(avId)
            if av is None:
                continue
            guildId = av.getGuildId()
            if guildId == 0:
                continue

            if guildId not in guild2ToonIds:
                guild2ToonIds[guildId] = []
                guild2ToonIds[guildId].append(avId)
            else:
                guild2ToonIds[guildId].append(avId)

        return guild2ToonIds


@magicWord(category=CATEGORY_ADMINISTRATOR, types=[str, str])
def guildQuest(command, arg=""):
    invoker = spellbook.getInvoker()
    if command == 'complete':
        guildId = invoker.getGuildId()
        if guildId == 0:
            return 'Cant complete quest for non existent guild'
        simbase.air.guildManager.d_completeQuest(invoker.doId, guildId)
        return 'Completed quest for guild %d' % guildId
    if command == 'progress':
        if arg == "":
            arg = 1
        else:
            arg = int(arg)
        if arg > 100:
            arg = 100
        guildId = invoker.getGuildId()
        if guildId == 0:
            return 'Cant progress quest for non existent guild'
        simbase.air.guildManager.d_progressQuest(invoker.doId, guildId, arg)
        return 'Progressed %d counts of quest for guild %d' % (arg, guildId)
    return 'No command %s exists.' % command


@magicWord(category=CATEGORY_MODERATOR, types=[int])
def badGuildName(wantSelf=0):
    target = spellbook.getTarget()
    invoker = spellbook.getInvoker()
    if invoker == target and not wantSelf:
        return 'If you want to bad name your own guild, enter 1 as an argument.'
    guildId = target.getGuildId()
    if guildId == 0:
        return 'Cant bad name non existent guild'

    simbase.air.guildManager.d_resetGuildName(guildId, 0)
    return 'Revoked %s as a guild name' % target.getGuildName()


@magicWord(category=CATEGORY_ADMINISTRATOR, types=[int])
def joinGuild(guildId=0):
    target = spellbook.getTarget()
    invoker = spellbook.getInvoker()
    if target is None and guildId == 0:
        return 'Target or guildId required!'
    if target == invoker and guildId == 0:
        return 'Target required!'
    if invoker.getGuildId():
        return 'Please leave your Guild before performing this command!'
    if guildId == 0:
        guildId = target.getGuildId()
    if guildId == 0:
        return 'Must specify guildId or target must belong to a Guild!'
    simbase.air.guildManager.d_adminJoinGuild(invoker.doId, guildId)


@magicWord(category=CATEGORY_ADMINISTRATOR)
def leaveGuild():
    invoker = spellbook.getInvoker()
    if invoker is None or invoker.getGuildId() == 0:
        return 'Error trying to force leave guild'
    simbase.air.guildManager.d_adminLeaveGuild(invoker.doId)


@magicWord(category=CATEGORY_MODERATOR)
def guildId():
    target = spellbook.getTarget()
    guildId = target.getGuildId()
    if guildId == 0:
        return 'Target does not belong to a Guild!'
    print('Got guildId: %d' % guildId)
    return 'Guild Id: %d' % guildId


