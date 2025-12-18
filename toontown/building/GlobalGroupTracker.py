from toontown.chat import ChatGlobals
from toontown.toonbase import EventGlobals
from direct.distributed.DistributedObjectGlobal import DistributedObjectGlobal
from direct.directnotify import DirectNotifyGlobal
from .GroupTrackerGlobals import *



class GlobalGroupTracker(DistributedObjectGlobal):
    notify = DirectNotifyGlobal.directNotify.newCategory('GlobalGroupTracker')

    def announceGenerate(self):
        DistributedObjectGlobal.announceGenerate(self)
        self.leader2Group = {}

    def requestGroupsResponse(self, leaderIds, groups):
        self.leader2Group = dict(zip(leaderIds, [list(group) for group in groups]))
        messenger.send(EventGlobals.GroupTrackerResponse)

    def updateGroup(self, leaderId, category, memberIds, memberNames, show):
        self.notify.debug('Updating Group for %d [%s, %s, %s, %s]' % (leaderId, category, memberIds, memberNames, show))
        if leaderId not in self.leader2Group:
            self.notify.warning('Tried to update group that doesnt exist')
            return

        if category != CATEGORY_NO_UPDATE:
            self.leader2Group[leaderId][CATEGORY] = category
        self.leader2Group[leaderId][MEMBER_IDS] = memberIds
        self.leader2Group[leaderId][MEMBER_NAMES] = memberNames
        self.leader2Group[leaderId][SHOW] = show
        messenger.send(EventGlobals.GroupTrackerResponse)

    def informLeader(self, senderName, informCode):
        self.notify.debug('Being informed of %d' % informCode)
        base.localAvatar.displayWhisper(0, INFORM_CODE_TO_STRING[informCode] % senderName, ChatGlobals.WTToontownBoardingGroup)

    def d_showMe(self, show):
        self.sendUpdate('showMe', [show])

    def d_requestGroups(self):
        self.sendUpdate('requestGroups', [])

    def d_doneRequesting(self):
        self.sendUpdate('doneRequesting', [])

    def d_requestInform(self, leaderId, senderName, informCode):
        self.sendUpdate('requestInform', [leaderId, senderName, informCode])

    def d_requestCreateSpecialGroup(self, type):
        self.sendUpdate('requestCreateSpecialGroup', [type])
