import copy
BOARDCODE_OKAY = 1
BOARDCODE_MISSING = 0
BOARDCODE_MINLAFF = -1
BOARDCODE_PROMOTION = -2
BOARDCODE_BATTLE = -3
BOARDCODE_SPACE = -4
BOARDCODE_NOT_PAID = -5
BOARDCODE_DIFF_GROUP = -6
BOARDCODE_PENDING_INVITE = -7
BOARDCODE_IN_ELEVATOR = -8
BOARDCODE_GROUPS_TO_LARGE = -9
INVITE_ACCEPT_FAIL_GROUP_FULL = -1


class BoardingPartyBase:
    def __init__(self):
        self.groupListDict = {}
        self.avIdDict = {}
        self.mergeDict = {}
        self.maxSize = 0

    def cleanup(self):
        del self.groupListDict
        del self.avIdDict
        del self.mergeDict

    def getGroupSize(self):
        return self.maxSize

    def setGroupSize(self, groupSize):
        self.maxSize = groupSize

    def getGroupLeader(self, avatarId):
        if avatarId in self.avIdDict:
            leaderId = self.avIdDict[avatarId]
            return leaderId
        return None

    def isGroupLeader(self, avatarId):
        leaderId = self.getGroupLeader(avatarId)
        if leaderId is None:
            return False
        return avatarId == leaderId

    def getGroupMemberList(self, avatarId):
        if avatarId in self.avIdDict:
            leaderId = self.avIdDict[avatarId]
            group = self.groupListDict.get(leaderId)
            if group is not None:
                returnList = copy.copy(group[0])
                if 0 in returnList:
                    returnList.remove(0)
                return returnList
        return []

    def getGroupInviteList(self, avatarId):
        if avatarId in self.avIdDict:
            leaderId = self.avIdDict[avatarId]
            group = self.groupListDict.get(leaderId)
            if group is not None:
                returnList = copy.copy(group[1])
                if 0 in returnList:
                    returnList.remove(0)
                return returnList
        return []

    def getGroupKickList(self, avatarId):
        if avatarId in self.avIdDict:
            leaderId = self.avIdDict[avatarId]
            group = self.groupListDict.get(leaderId)
            if group is not None:
                returnList = copy.copy(group[2])
                if 0 in returnList:
                    returnList.remove(0)
                return returnList
        return []

    def hasActiveGroup(self, avatarId):
        memberList = self.getGroupMemberList(avatarId)
        if avatarId in memberList:
            if len(memberList) > 1:
                return True
        return False

    def hasPendingInvite(self, avatarId):
        pendingInvite = False
        if avatarId in self.mergeDict:
            return True
        if avatarId in self.avIdDict:
            leaderId = self.avIdDict[avatarId]
            leaderInviteList = self.getGroupInviteList(leaderId)
            if leaderId == avatarId:
                if len(leaderInviteList):
                    pendingInvite = True
                else:
                    pendingInvite = False
            elif avatarId in leaderInviteList:
                pendingInvite = True
            else:
                pendingInvite = False
        return pendingInvite

    def isInGroup(self, memberId, leaderId):
        return memberId in self.getGroupMemberList(leaderId) or memberId in self.getGroupInviteList(leaderId)
