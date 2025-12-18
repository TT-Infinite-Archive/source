from direct.distributed.PyDatagram import *
from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import *

from toontown.toon.ToonDNA import ToonDNA
from toontown.guilds.GuildGlobals import *
from otp.distributed import OtpDoGlobals


class GuildMemberUD(DirectObject):
    def __init__(self, guild):
        DirectObject.__init__(self)

        self.name = "Default"
        self.id = 0
        self.dna = ToonDNA(type='t').makeNetString()
        self.petId = 0
        self.roleId = 0
        self.laff = 15
        self.contribution = 0

        self.online = False
        self.client = 0

        self.guild = guild
        self.mgr = simbase.air.getGlobalObject('GuildManager')

    # Property setter
    def makeFromEntryFields(self, fields, callback):
        self.id = fields[GUILD_MEMBER_ENTRY_ID]
        self.roleId = fields[GUILD_MEMBER_ENTRY_ROLE]
        self.contribution = fields[GUILD_MEMBER_ENTRY_CONTRIBUTION]

        def handleRetrieved(dclass, fields):
            if dclass != simbase.air.dclassesByName['DistributedToonUD']:
                # The guild might as well not exist, clearly broken.
                # TODO: Find out how to handle this bloody error..
                # For now, we'll remove the member.
                self.guild.removeMember(self.id, self.id)
                return

            self.name = fields['setName'][0]
            self.dna = fields['setDNAString'][0]
            self.petId = fields['setPetId'][0]
            self.laff = fields['setMaxHp'][0]

            # Let the guild know this member is done loading
            # destroys race conditions..
            callback()

        # Get the rest of the details from the database
        simbase.air.dbInterface.queryObject(simbase.air.dbId, self.id, handleRetrieved)

    # Index
    def getIndex(self):
        entry = self.asEntry()
        if entry in self.guild.members:
            return self.guild.members.index(entry)
        return None

    # Online status
    def goOnline(self, client):
        if self.online:
            print(('GuildMemberUD: Avatar %d is going online, but was already online. Still processing' % self.id))
        self.online = True
        self.client = client

        self.subscribeToChannel()
        self.sendUpdate('guildInfo', [self.guild.asInfo()])

        # Send the pre-calculated rank to the client that logged in
        self.sendUpdate('setRank', [self.guild.rank])

        # If the guild is rejected, send an update to this avatar to remind them its rejected
        if self.guild.nameStatus == GUILD_NAME_REJECTED:
            self.sendUpdate('alertNameChanged', [self.name, GUILD_NAME_REJECTED])

    def goOffline(self):
        if not self.online:
            return
        self.online = False

        self.unsubscribeFromChannel()
        self.client = 0

    # Leaving
    def leaveGuild(self):
        self.saveFieldToDB('setGuildId', 0)
        self.saveFieldToDB('setGuildName', '')
        self.saveFieldToDB('setGuildIcon', 0)

        if self.online:
            self.goOffline()

    # Channel
    def subscribeToChannel(self):
        # Subscribe them to the guilds channel
        datagram = PyDatagram()
        datagram.addServerHeader(
            self.client,
            simbase.air.ourChannel,
            CLIENTAGENT_OPEN_CHANNEL)

        # Add the guilds channel
        datagram.addChannel(self.guild.id)

        # Send the datagram
        simbase.air.send(datagram)

    def unsubscribeFromChannel(self):
        # Unsubscribe them from the guilds channel
        datagram = PyDatagram()
        datagram.addServerHeader(
            self.client,
            simbase.air.ourChannel,
            CLIENTAGENT_CLOSE_CHANNEL)

        # Add the guilds channel
        datagram.addChannel(self.guild.id)

        # Send the datagram
        simbase.air.send(datagram)

    # Role
    def setRoleId(self, roleId):
        self.roleId = roleId

    def setRole(self, role):
        self.setRoleId(role.id)

    def getRole(self):
        return self.guild.getRole(self.roleId)

    # Laff update
    def setLaff(self, laff):
        self.laff = laff

    # Hierarchy
    def overpowers(self, otherMember):
        myRole = self.getRole()
        otherRole = otherMember.getRole()

        return myRole.overpowers(otherRole)

    # Contribution
    def addContribution(self, contribution):
        self.contribution += contribution

    # Saving
    def saveFieldToDB(self, field, value):
        if self.online:
            dg = simbase.air.dclassesByName['DistributedToonUD'].aiFormatUpdate(
                field, self.id, self.id, simbase.air.ourChannel, [value]
            )
            simbase.air.send(dg)
        else:
            simbase.air.dbInterface.updateObject(simbase.air.dbId, self.id,
                simbase.air.dclassesByName['DistributedToonUD'],
                {field: [value]}
            )

    # Send updates
    def sendUpdate(self, field, args=None):
        if args is None:
            args = []
        self.mgr.sendUpdateToAvatarId(self.id, field, args)

    # Arguments for field update
    def asStruct(self):
        # Return the member as a GuildMember struct
        struct = (
            self.id,
            self.name,
            self.dna,
            self.petId,
            self.roleId,
            self.laff,
            self.online,
            self.contribution
        )

        return struct

    def asEntry(self):
        # Return the member as a GuildMemberEntry struct
        entry = (
            self.id,
            self.roleId,
            self.contribution
        )

        return entry