from toontown.safezone import SafeZoneLoader
from toontown.safezone import SZPlayground
from toontown.toonbase import ToontownGlobals
from toontown.hood import ZoneUtil
from toontown.dna.DNAStorage import DNAStorage
from toontown.dna.DNAParser import loadDNAFileAI


class SZSafeZoneLoader(SafeZoneLoader.SafeZoneLoader):

    def __init__(self, hood, parentFSM, doneEvent):
        SafeZoneLoader.SafeZoneLoader.__init__(self, hood, parentFSM, doneEvent)
        self.playgroundClass = SZPlayground.SZPlayground
        self.musicFile = 'phase_4/audio/corpstrike/GOV_strikezone_nbrhood.ogg'
        self.activityMusicFile = 'phase_3.5/audio/bgm/TC_SZ_activity.ogg'  # TODO: Change music.
        self.dnaFile = 'phase_6/dna/strike_zone_sz.pdna'
        self.safeZoneStorageDNAFile = 'phase_6/dna/storage_SZ_sz.pdna'
        self.battleMusic = base.loadMusic('phase_4/audio/bgm/TTC_SZ_Halloween_Battle.ogg')

        self.zoneDict = {}

    def load(self):
        SafeZoneLoader.SafeZoneLoader.load(self)
        self.createDictionaries()

    def unload(self):
        SafeZoneLoader.SafeZoneLoader.unload(self)

    def createDictionaries(self):
        dnaStore = DNAStorage()
        loadDNAFileAI(dnaStore, 'phase_4/dna/toontown_central_sz.pdna')

        for i in xrange(dnaStore.getNumDNAVisGroupsAI()):
            groupFullName = dnaStore.getDNAVisGroupName(i)
            groupName = base.cr.hoodMgr.extractGroupName(groupFullName)
            zoneId = int(groupName)
            zoneId = ZoneUtil.getTrueZoneId(zoneId, ToontownGlobals.ToontownCentral)
            groupNode = self.geom.find('**/*' + groupFullName)
            if groupNode.isEmpty():
                self.notify.warning('Could not find visgroup %s' % groupFullName)
                continue
            else:
                if ':' in groupName:
                    groupName = '%s%s' % (zoneId, groupName[groupName.index(':'):])
                else:
                    groupName = '%s' % zoneId
                groupNode.setName(groupName)
            groupNode.flattenMedium()
            self.zoneDict[zoneId] = groupNode

        dnaStore.cleanup()
