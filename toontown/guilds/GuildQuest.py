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

    def asStruct(self):
        struct = [
            self.questId,
            self.goal,
            self.reward,
            self.progress
        ]
        return struct