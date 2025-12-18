
from toontown.guilds.GuildGlobals import *


class GuildRoleUD:
    def __init__(self, mgr, guild):
        self.mgr = mgr
        self.guild = guild

        self.id = 0
        self.name = 'Role'
        self.sortIndex = 0
        self.permissions = []
        
    # Property setter
    def makeFromRoleFields(self, role):
        self.id = role[GUILD_ROLE_ID]
        self.name = role[GUILD_ROLE_NAME]
        self.sortIndex = role[GUILD_ROLE_SORT_INDEX]
        self.permissions = role[GUILD_ROLE_PERMISSIONS]
        
    # Hierarchy
    def overpowers(self, otherRole):
        return self.sortIndex < otherRole.sortIndex
    
    # Permissions
    def addPermission(self, permission):
        if permission not in self.permissions:
            self.permissions.append(permission)
        
    def removePermission(self, permission):
        if permission in self.permissions:
            self.permissions.remove(permission)
        
    def setPermissions(self, permissions):
        self.permissions = permissions
        
    def getPermissions(self):
        return self.permissions

    def getIndex(self):
        return self.sortIndex
        
    # Arguments for field update
    def asStruct(self):
        # Return the role as a GuildRole struct
        struct = (
            self.id,
            self.name,
            self.sortIndex,
            self.permissions
        )
        
        return struct