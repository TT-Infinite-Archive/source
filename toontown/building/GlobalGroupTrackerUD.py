from otp.uberdog.GlobalOtpObjectUD import GlobalOtpObjectUD
from direct.directnotify import DirectNotifyGlobal
from GroupTrackerGlobals import *


class GlobalGroupTrackerUD(GlobalOtpObjectUD):
    notify = DirectNotifyGlobal.directNotify.newCategory('GlobalGroupTrackerUD')

    def announceGenerate(self):
        GlobalOtpObjectUD.announceGenerate(self)
        self.notify.info('Starting...')
        # Maps a leaderId to the corresponding BoardingGroup struct.
        self.leader2Group = {}
        # Listeners are people who want to receive updates to their GroupTracker page.
        self.listeners = []

    def addGroup(self, leaderId, groupStruct):
        self.notify.debug('Adding a group %s owned by %d' % (repr(groupStruct), leaderId))
        self.leader2Group[leaderId] = list(groupStruct)

        # Accept this event in case of a unexpected exit from the owner of this group
        self.accept('distObjDelete-%d' % leaderId, self.cleanupAvatar, extraArgs=[leaderId])
        
        for avId in self.listeners:
            self.requestGroupsResponse(avId)

    def updateGroup(self, leaderId, category, memberIds, memberNames, show):
        self.notify.debug('Updating a group owned by %d' % leaderId)

        if leaderId not in self.leader2Group:
            self.notify.warning('Attempted to update a group owned by %d that doesnt exist' % leaderId)
            return

        if category != CATEGORY_NO_UPDATE:
            self.leader2Group[leaderId][CATEGORY] = category
        self.leader2Group[leaderId][MEMBER_IDS] = memberIds
        self.leader2Group[leaderId][MEMBER_NAMES] = memberNames
        self.leader2Group[leaderId][SHOW] = show
        
        for avId in self.listeners:
            self.requestGroupsResponse(avId)

        if len(memberIds) == 0:
            # Dead group
            self.notify.debug('Group owned by %d has died' % leaderId)
            del self.leader2Group[leaderId]

    def requestGroups(self):
        avId = self.air.getAvatarIdFromSender()
        self.notify.debug('Avatar %d requesting groups from group tracker' % avId)
        if avId not in self.listeners:
            # Accept this event in case of a unexpected exit from the client.
            self.accept('distObjDelete-%d' % avId, self.cleanupAvatar, extraArgs=[avId])
            self.listeners.append(avId)
        self.requestGroupsResponse(avId)

    def requestGroupsResponse(self, avId):
        self.sendUpdateToAvatarId(avId, 'requestGroupsResponse', [self.leader2Group.keys(), self.leader2Group.values()])

    def cleanupAvatar(self, avId):
        self.notify.debug('Cleaning up avatar no longer with us %s' % avId)
        self.ignore('distObjDelete-%d' % avId)
        # Make sure the avatar is no longer listening for groups
        self.doneRequesting(avId)
        # Make sure to destroy any groups the avatar may own
        if avId in self.leader2Group:
            self.updateGroup(avId, 0, [], [], False)

    def doneRequesting(self, avId=None):
        if avId is None:
            avId = self.air.getAvatarIdFromSender()
        self.notify.debug('Avatar %d no longer requesting groups from group tracker' % avId)
        if avId in self.listeners:
            self.listeners.remove(avId)
    
    def showGroup(self, leaderId, show):
        if leaderId not in self.leader2Group:
            self.notify.warning('Av %s tried to show group not in leader2Group' % avId)
            return
        self.leader2Group[leaderId][SHOW] = show
        self.d_updateListeners(leaderId)

    def requestInform(self, leaderId, senderName, informCode):
        avId = self.air.getAvatarIdFromSender()
        self.notify.debug('Avatar %d is informing leader %d code %d' % (avId, leaderId, informCode))
        if leaderId not in self.leader2Group:
            self.notify.warning('Avatar %d attempted to inform leader %d who is not in a group!' % (avId, leaderId))
            return

        self.d_informLeader(leaderId, senderName, informCode)

    def d_updateListeners(self, leaderId):
        """
        Updates a group for all the people who are listening for groups
        :param leaderId: The leader of the group that is updating
        """
        if leaderId not in self.leader2Group:
            self.notify.warning('Tried to inform listeners of non-existent group owned by %d.' % leaderId)
            return
        category = self.leader2Group[leaderId][CATEGORY]
        memberIds = self.leader2Group[leaderId][MEMBER_IDS]
        memberNames = self.leader2Group[leaderId][MEMBER_NAMES]
        show = self.leader2Group[leaderId][SHOW]

        for avId in self.listeners:
            self.sendUpdateToAvatarId(avId, 'updateGroup', [leaderId, category, memberIds, memberNames, show])

    def d_informLeader(self, leaderId, senderName, informCode):
        """
        Inform a leader of a group of an event that is occurring
        :param leaderId: avId of the group leader
        :param senderName: name of the person sending this event
        :param informCode: id of the event
        """
        self.sendUpdateToAvatarId(leaderId, 'informLeader', [senderName, informCode])

