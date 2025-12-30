
class ToontownInviteDatabaseUD:

    def __init__(self, air):
        pass

    def getOneInvite(self, inviteKey):
        return None

    def getInvites(self, avatarId: int):
        return []

    def getInviteesOfParty(self, partyId: int):
        return []

    def getReplies(self, partyId: int):
        return []

    def putInvite(self, partyId: int, inviteeId):
        return False

    def updateInvite(self, inviteKey, inviteStatus):
        pass
