from toontown.coghq import CogHQLoader
from toontown.coghq import StrikeZoneCogHQExterior
from toontown.coghq import StrikeZoneHQBossBattle

from toontown.dna import DNAParser
from toontown.dna.DNAParser import DNABulkLoader
from pandac.PandaModules import NodePath


class StrikeZoneCogHQLoader(CogHQLoader.CogHQLoader):

    def __init__(self, hood, parentFSM, doneEvent):
        CogHQLoader.CogHQLoader.__init__(self, hood, parentFSM, doneEvent)
        self.musicFile = 'phase_4/audio/corpstrike/GOV_strikezone_nbrhood.ogg'
        self.activityMusicFile = 'phase_3.5/audio/bgm/TC_SZ_activity.ogg'  # TODO: Change music.
        self.dnaFile = 'phase_6/dna/strike_zone_sz.pdna'
        self.storageDna = 'phase_6/dna/storage_SZ.pdna'
        self.battleMusic = base.loadMusic('phase_4/audio/bgm/TTC_SZ_Halloween_Battle.ogg')

        self.geom = None
        self.hood = hood
        self.zoneDict = {}
        self.nodeList = []

    def load(self, zoneId):
        CogHQLoader.CogHQLoader.load(self, zoneId)

        if self.storageDna:
            dnaBulk = DNABulkLoader(self.hood.dnaStore, (self.storageDna,))
            dnaBulk.loadDNAFiles()
        node = DNAParser.loadDNAFile(self.hood.dnaStore, self.dnaFile)
        if node.getNumParents() == 1:
            self.geom = NodePath(node.getParent(0))
            self.geom.reparentTo(hidden)
        else:
            self.geom = hidden.attachNewNode(node)
        self.makeDictionaries(self.hood.dnaStore)

        gsg = base.win.getGsg()
        if gsg:
            self.geom.prepareScene(gsg)
        self.geom.flattenMedium()

    def makeDictionaries(self, dnaStore):
        self.nodeList = []
        for i in xrange(dnaStore.getNumDNAVisGroups()):
            groupFullName = dnaStore.getDNAVisGroupName(i)
            groupName = base.cr.hoodMgr.extractGroupName(groupFullName)
            groupNode = self.geom.find('**/' + groupFullName)
            if groupNode.isEmpty():
                self.notify.error('Could not find visgroup')
            groupNode.flattenMedium()
            self.nodeList.append(groupNode)

        self.hood.dnaStore.resetPlaceNodes()
        self.hood.dnaStore.resetDNAGroups()
        self.hood.dnaStore.resetDNAVisGroups()
        self.hood.dnaStore.resetDNAVisGroupsAI()

    def unload(self):
        # TODO: Cleanup
        CogHQLoader.CogHQLoader.unload(self)

    def getExteriorPlaceClass(self):
        return StrikeZoneCogHQExterior.StrikeZoneCogHQExterior

    def getBossPlaceClass(self):
        return StrikeZoneHQBossBattle.SZHQBossBattle
