from direct.showbase.DirectObject import DirectObject
from toontown.guilds import GuildQuestGlobals


class GuildQuestUD(DirectObject):
    def __init__(self, guild):
        DirectObject.__init__(self)

        self.guild = guild

        self.questId = None
        self.goal = None
        self.reward = None

        self.progress = 0

    def makeFromField(self, quest):
        self.questId = quest[GuildQuestGlobals.GUILD_QUEST_ID]
        self.goal = quest[GuildQuestGlobals.GUILD_QUEST_GOAL]
        self.reward = quest[GuildQuestGlobals.GUILD_QUEST_REWARD]
        self.progress = quest[GuildQuestGlobals.GUILD_QUEST_PROGRESS]

    def attemptProgress(self, category, posObjectives):
        myCat = GuildQuestGlobals.GuildQuestDict[self.questId][0]
        myObj = GuildQuestGlobals.GuildQuestDict[self.questId][1]

        if myCat != category:
            # Incorrect category, these quests don't match
            return
        if myObj not in posObjectives:
            # Objectives don't match
            return

        if self.progress >= self.goal:
            # This quest is done?
            return

        self.progress += 1

    def complete(self):
        self.guild.finishQuest()

    def asStruct(self):
        struct = [
            self.questId,
            self.goal,
            self.reward,
            self.progress
        ]
        return struct