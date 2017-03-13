from toontown.strike import OperationSaveToontownGlobals
from toontown.strike.DistributedCorporateStrike import DistributedCorporateStrike
from toontown.dna.DNAStorage import DNAStorage
from toontown.dna import DNAParser
from toontown.hood import SkyUtil

from panda3d.core import Vec4, Filename


class DistributedOperationSaveToontown(DistributedCorporateStrike):
    SPAWN_SPHERES = OperationSaveToontownGlobals.SPAWN_SPHERES

    def __init__(self, cr):
        DistributedCorporateStrike.__init__(self, cr)

        self.sky = None

    def loadEnvironment(self):
        store = DNAStorage()
        storageFiles = ['phase_4/dna/storage.pdna', 'phase_4/dna/storage_TT.pdna', 'phase_4/dna/storage_OST.pdna']
        DNAParser.DNABulkLoader(store, storageFiles).loadDNAFiles()

        node = DNAParser.loadDNAFile(store, 'phase_4/dna/operation_save_toontown.pdna')
        self.geom = hidden.attachNewNode(node)

        self.sky = loader.loadModel('phase_3.5/models/props/TT_sky')
        SkyUtil.startCloudSky(self)

        if __debug__:
            skyblue2Filename = Filename('../resources/phase_3.5/maps/skyblue2_invasion.jpg')
            middayskyBFilename = Filename('../resources/phase_3.5/maps/middayskyB_invasion.jpg')
            toontown_central_tutorial_palette_4amla_1Filename = Filename(
                '../resources/phase_3.5/maps/toontown_central_tutorial_palette_4amla_1_invasion.jpg')
            toontown_central_tutorial_palette_4amla_1_aFilename = Filename(
                '../resources/phase_3.5/maps/toontown_central_tutorial_palette_4amla_1_a_invasion.rgb')
        else:
            skyblue2Filename = Filename('/phase_3.5/maps/skyblue2_invasion.jpg')
            middayskyBFilename = Filename('/phase_3.5/maps/middayskyB_invasion.jpg')
            toontown_central_tutorial_palette_4amla_1Filename = Filename(
                '/phase_3.5/maps/toontown_central_tutorial_palette_4amla_1_invasion.jpg')
            toontown_central_tutorial_palette_4amla_1_aFilename = Filename(
                '/phase_3.5/maps/toontown_central_tutorial_palette_4amla_1_a_invasion.rgb')
        self.sky.findTexture('skyblue2').read(skyblue2Filename)
        self.sky.findTexture('middayskyB').read(middayskyBFilename)
        self.sky.findTexture('toontown_central_tutorial_palette_4amla_1').read(
            toontown_central_tutorial_palette_4amla_1Filename, toontown_central_tutorial_palette_4amla_1_aFilename, 0,
            0)

        render.setColorScale(Vec4(0.55, 0.35, 0.35, 1))

        DistributedCorporateStrike.loadEnvironment(self)

    def skyTrack(self, task):
        return SkyUtil.cloudSkyTrack(task)
