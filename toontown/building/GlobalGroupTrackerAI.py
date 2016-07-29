from direct.distributed.DistributedObjectGlobalAI import DistributedObjectGlobalAI
from direct.directnotify import DirectNotifyGlobal
from toontown.building.GroupTrackerGlobals import SPECIAL_GROUPS, JELLYBEAN_FEST, GROUP_TYPE_JELLYBEAN
from toontown.chat.ResistanceChat import getMenuName
from toontown.toonbase import TTLocalizer, ToontownGlobals


class GlobalGroupTrackerAI(DistributedObjectGlobalAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('GlobalGroupTrackerAI')

    def announceGenerate(self):
        self.jellybeanFestOwners = []
        DistributedObjectGlobalAI.announceGenerate(self)

    def delete(self):
        DistributedObjectGlobalAI.delete(self)
        taskMgr.remove('groupTrackerAI-updateSpecialPop')
        del self.jellybeanFestOwners[:]

    def addGroupAI(self, leaderId, leaderName, shardName, shardId, category, memberIds, memberNames, show, type, zoneId):
        self.sendUpdate('addGroup', [leaderId, [leaderName, shardName, shardId, category, memberIds, memberNames, show, type, zoneId]])

    def updateGroupAI(self, leaderId, category, memberIds, memberNames, show):
        self.sendUpdate('updateGroup', [leaderId, category, memberIds, memberNames, show])
    
    def showMe(self, show):
        avId = self.air.getAvatarIdFromSender()
        self.sendUpdate('showGroup', [avId, show])

    def requestCreateSpecialGroup(self, type):
        avId = self.air.getAvatarIdFromSender()
        av = self.air.doId2do.get(avId)
        if av is None:
            return
        if type not in SPECIAL_GROUPS:
            self.notify.warning('Av %s tried to request non existent special group %s' % (avId, type))
            return
        if type == GROUP_TYPE_JELLYBEAN:
            # Validate our special group
            if av.zoneId not in ToontownGlobals.Hoods:
                self.notify.warning('Av %s tried to start a jellybean fest out of a safezone' % avId)
                return
            if not av.resistanceMessages:
                self.notify.warning('Av %s without unites tried to make a jellybean fest' % avId)
                return
            allowed = 0
            for message in av.resistanceMessages:
                textId = message[0]
                charges = message[1]
                if getMenuName(textId) == TTLocalizer.ResistanceMoneyMenu and charges > 0:
                    allowed = 1
            if not allowed:
                self.notify.warning('Av %s tried to make a jellybean fest without jellybean unites' % avId)
                return
            self.jellybeanFestOwners.append(avId)

        self.addGroupAI(
            avId,
            av.name,
            self.air.distributedDistrict.name,
            self.air.districtId,
            JELLYBEAN_FEST,
            self.getHoodAvIds(av),
            [''],
            av.wantGroupTracker,
            GROUP_TYPE_JELLYBEAN,
            av.zoneId
        )
        if not taskMgr.hasTaskNamed('groupTrackerAI-updateSpecialPop'):
            taskMgr.doMethodLater(10, self.updateSpecialPopulation, 'groupTrackerAI-updateSpecialPop', extraArgs=[type])

    def updateSpecialPopulation(self, type, task=None):
        def recall():
            taskMgr.doMethodLater(10, self.updateSpecialPopulation, 'groupTrackerAI-updateSpecialPop', extraArgs=[type])

        if type == GROUP_TYPE_JELLYBEAN:
            for avId in self.jellybeanFestOwners:
                av = self.air.doId2do.get(avId)
                if av is None:
                    self.jellybeanFestOwners.remove(avId)
                    return
                self.updateGroupAI(av.doId, JELLYBEAN_FEST, self.getHoodAvIds(av), [''], av.wantGroupTracker)
            if self.jellybeanFestOwners:
                recall()

    def getHoodAvIds(self, av):
        memberIds = [av.doId]
        for hood in self.air.hoods:
            if hood.zoneId == av.zoneId:
                memberIds = [doId for doId in hood.avIds]
        return memberIds
