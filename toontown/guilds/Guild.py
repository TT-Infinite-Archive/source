from direct.showbase.DirectObject import DirectObject

from toontown.guilds.GuildGlobals import *
from toontown.guilds.GuildRole import GuildRole
from toontown.guilds.GuildMember import GuildMember
from toontown.guilds import GuildQuestGlobals


class Guild(DirectObject):
    def __init__(self, info=None):
        DirectObject.__init__(self)

        if info is None:
            self.name = ''
            self.rolePosition2Role = {}
            self.roleId2Role = {}
            self.members = []
            self.avId2Member = {}
            self.iconId = 0
            self.guildPoints = 0
            self.rankPoints = 0
            self.buffs = []
            self.quest = GuildQuestGlobals.GUILD_QUEST_EMPTY
            self.roles = []
            self.roleId2Role = {}
            self.bossTimings = []
            self.rank = 0
            self.rejected = 0
            return

        self.makeFromInfo(info)

    # Property Setters
    def makeFromInfo(self, info):
        self.name = info[GUILD_NAME]
        
        self.roleId2Role = {}
        roles = info[GUILD_ROLES]
        for role in roles:
            self.handleRole(role)
            
        self.members = []
        self.avId2Member = {}
        members = info[GUILD_MEMBERS]
        for member in members:
            self.handleMember(member)
        
        self.iconId = info[GUILD_ICON]
        self.guildPoints = info[GUILD_GUILD_POINTS]
        self.rankPoints = info[GUILD_RANK_POINTS]
        self.buffs = info[GUILD_BUFFS]
        self.quest = info[GUILD_QUEST]
        self.bossTimings = info[GUILD_BOSS_TIMINGS]

    # Member Functions
    def memberOnline(self, avId):
        if avId in self.avId2Member:
            self.avId2Member[avId].goOnline()

    def memberOffline(self, avId):
        if avId in self.avId2Member:
            self.avId2Member[avId].goOffline()

    def handleMember(self, member):
        memberInstance = GuildMember(self)
        memberInstance.makeFromMemberFields(member)
        
        existingMember = self.getMember(memberInstance.doId)
        if existingMember is not None:
            # This member is already in our local guild members, so remove them first
            self.members.remove(existingMember)

        self.avId2Member[memberInstance.doId] = memberInstance
        self.members.append(memberInstance)
    
    def removeMember(self, memberId):
        memberInstance = self.avId2Member.get(memberId)
        if memberInstance is None:
            return
        
        self.members.remove(memberInstance)
        del self.avId2Member[memberId]

    def getLocalAvatar(self):
        return self.getMember(base.localAvatar.doId)

    def getMember(self, avId):
        return self.avId2Member.get(avId)

    def getOwner(self):
        for member in self.members:
            if member.getRole().sortIndex == 0:
                return member
        return None
        
    # Points
    def setGuildPoints(self, guildPoints):
        self.guildPoints = guildPoints

    def getGuildPoints(self):
        return self.guildPoints
        
    def setRankPoints(self, rankPoints):
        self.rankPoints = rankPoints
        
    def getRankPoints(self):
        return self.rankPoints

    def setRank(self, rank):
        self.rank = rank

    def getRank(self):
        return self.rank

    # Roles
    def handleRole(self, role):
        roleInstance = GuildRole(self)
        roleInstance.makeFromRoleFields(role)
        
        self.roleId2Role[roleInstance.id] = roleInstance
        self.rolePosition2Role[roleInstance.sortIndex] = roleInstance
        
    def getRole(self, roleId):
        # Return the role, or None if it doesn't exist
        return self.roleId2Role.get(roleId, None)
        
    def getRoleAtPosition(self, position):
        # Return the role, or None if it doesn't exist
        return self.rolePosition2Role.get(position, None)

    def getHighestSortedRole(self):
        highestSort = 0
        for position in self.rolePosition2Role:
            if self.rolePosition2Role[position].sortIndex > highestSort:
                highestSort = self.rolePosition2Role[position].sortIndex
        return highestSort

    # Quest
    def setQuest(self, quest):
        self.quest = list(quest)

    def setQuestProgress(self, progress):
        self.quest = list(self.quest)
        if self.quest != GuildQuestGlobals.GUILD_QUEST_EMPTY:
            self.quest[GuildQuestGlobals.GUILD_QUEST_PROGRESS] = progress
