from direct.showbase.DirectObject import DirectObject

from toontown.guilds.GuildGlobals import *

class GuildRole(DirectObject):
    def __init__(self, guild):
        DirectObject.__init__(self)
        
        self.id = 0
        self.name = "Role"
        self.sortIndex = 0
        self.permissions = []
        
        self.guild = guild
        self.mgr = base.cr.guildManager
        
    # Property setter
    def makeFromRoleFields(self, role):
        self.id = role[GUILD_ROLE_ID]
        self.name = role[GUILD_ROLE_NAME]
        self.sortIndex = role[GUILD_ROLE_SORT_INDEX]
        self.permissions = role[GUILD_ROLE_PERMISSIONS]
        
    # Hierarchy
    def overpowers(self, otherRole):
        return self.sortIndex < otherRole.sortIndex
        
    # Arguments for field update
    def asStruct(self):
        # Return the member as a GuildMember struct
        struct = [
            self.id,
            self.name,
            self.sortIndex,
            self.permissions
        ]
        
        return struct