from direct.distributed.PyDatagram import *
from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import *

from toontown.guilds.GuildGlobals import *
from toontown.toon.ToonDNA import ToonDNA
from toontown.toonbase import ToontownGlobals


class GuildMember(DirectObject):
    def __init__(self, guild):
        DirectObject.__init__(self)

        self.doId = 0
        self.name = ''
        self.style = ToonDNA()
        self.petId = 0
        self.roleId = 0
        self.laff = 15
        self.online = False
        self.contribution = 0

        self.isAPet = False
        self.guild = guild

    # Property setter
    def makeFromMemberFields(self, member):
        self.doId = member[GUILD_MEMBER_ID]
        self.name = member[GUILD_MEMBER_NAME]
        self.style.makeFromNetString(member[GUILD_MEMBER_DNA])
        self.petId = member[GUILD_MEMBER_PET]
        self.roleId = member[GUILD_MEMBER_ROLE]
        self.laff = member[GUILD_MEMBER_LAFF]
        self.online = member[GUILD_MEMBER_ONLINE]
        self.contribution = member[GUILD_MEMBER_CONTRIBUTION]

    # Online Status
    def goOnline(self):
        if self.online:
            return

        self.online = True

    def goOffline(self):
        if not self.online:
            return

        self.online = False

    # FriendHandle Functions
    def getDoId(self):
        return self.doId

    def getPetId(self):
        return self.petId

    def hasPet(self):
        return self.getPetId() != 0

    def isPet(self):
        return self.isAPet

    def getName(self):
        return self.name

    def getFont(self):
        return ToontownGlobals.getToonFont()

    def getStyle(self):
        return self.style

    def uniqueName(self, idString):
        return idString + '-' + str(self.getDoId())

    def setLaff(self, laff):
        self.laff = laff

    def getLaff(self):
        return self.laff
        
    # Points
    def setContribution(self, contribution):
        self.contribution = contribution
    
    def getContribution(self):
        return self.contribution
    
    # Roles
    def setRoleId(self, roleId):
        self.roleId = roleId

    def getRoleId(self):
        return self.roleId

    def setRole(self, role):
        self.roleId = role.id
    
    def getRole(self):
        return self.guild.getRole(self.roleId)

