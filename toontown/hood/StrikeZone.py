from panda3d.core import Fog

from toontown.coghq.StrikeZoneCogHQLoader import StrikeZoneCogHQLoader
from toontown.toonbase import ToontownGlobals
from toontown.hood.CogHood import CogHood
from otp.otpbase.OTPGlobals import DefaultCameraFov
from panda3d.core import Vec4, Filename
from toontown.battle import BattleParticles
from toontown.hood import SkyUtil
from direct.actor import Actor
from toontown.util.PlacerTool3D import PlacerTool3D


class StrikeZone(CogHood):
    notify = directNotify.newCategory('StrikeZone')

    ID = ToontownGlobals.StrikeZone
    LOADER_CLASS = StrikeZoneCogHQLoader
    STORAGE_DNA = 'phase_6/dna/storage_SZ.pdna'
    SKY_FILE = 'phase_3.5/models/props/TT_sky'
    TITLE_COLOR = (0.5, 0.5, 0.5, 1.0)

    def __init__(self, parentFSM, doneEvent, dnaStore, hoodId):
        CogHood.__init__(self, parentFSM, doneEvent, dnaStore, hoodId)

        self.rain = None
        self.rainRender = None

    def load(self, *args):
        CogHood.load(self)
        self.fog = Fog('GSZFog')
        self.startRain()
        SkyUtil.startCloudSky(self)
        self.sky.setScale(3)
        base.localAvatar.setCameraFov(ToontownGlobals.CogHQCameraFov)
        base.camLens.setNearFar(ToontownGlobals.StrikeZoneCameraNear, ToontownGlobals.StrikeZoneCameraFar)

        render.setColorScale(Vec4(0.55, 0.35, 0.35, 1))

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

        self.toonHall = loader.loadModel('phase_4/models/corpstrike/destroyed_toonhall')
        self.toonHall.reparentTo(render)
        self.toonHall.setPos(116.66, 24.29, 4)
        self.toonHall.setHpr(-90, 0, 0)

        self.bank = loader.loadModel('phase_4/models/corpstrike/destroyed_bank')
        self.bank.reparentTo(render)
        self.bank.setPos(57.1796, 38.6656, 0.3)

        self.library = loader.loadModel('phase_4/models/corpstrike/destroyed_library')
        self.library.reparentTo(render)
        self.library.setPos(91.4475, -44.9255, 4)
        self.library.setHpr(180, 0, 0)

        self.hqTelescope = Actor.Actor('phase_4/models/corpstrike/hqTT_telescope_ost', {'animation': 'phase_4/models/corpstrike/hqTT_telescope_ost'})
        self.hqTelescope.loop('animation')
        self.hqTelescope.reparentTo(render)
        self.hqTelescope.setPosHpr(20.5, 29, 16.7, -70, 0, 0)

        self.fieldOffice = loader.loadModel('phase_5/models/cogdominium/tt_m_ara_cbe_fieldOfficePhilip')
        self.fieldOffice.reparentTo(render)
        self.fieldOffice.setPosHpr(-130, -73, 0, 130, 0, 0)
        # PlacerTool3D(self.fieldOffice, increment=1)

        self.suitWall = loader.loadModel('phase_5/models/cogdominium/tt_m_ara_cbe_walls.bam')
        self.fieldOfficeWall = self.suitWall.find('**/wall_cogdo_build2_ur')
        self.fieldOfficeWall.reparentTo(render)
        self.fieldOfficeWall.setPosHpr(-106, -91, 0, 149, 0, 0)
        self.fieldOfficeWall.setScale(20)
        # PlacerTool3D(self.fieldOfficeWall, increment=1)

        self.suitWall2 = loader.loadModel('phase_5/models/cogdominium/tt_m_ara_cbe_walls.bam')
        self.fieldOfficeWall2 = self.suitWall2.find('**/wall_cogdo_build2_ur')
        self.fieldOfficeWall2.reparentTo(render)
        self.fieldOfficeWall2.setPosHpr(-87, -96, 0, 165, 0, 0)
        self.fieldOfficeWall2.setScale(20)
        # PlacerTool3D(self.fieldOfficeWall2, increment=1)

        self.suitWall3 = loader.loadModel('phase_5/models/cogdominium/tt_m_ara_cbe_walls.bam')
        self.fieldOfficeWall3 = self.suitWall3.find('**/wall_cogdo_build2_ur')
        self.fieldOfficeWall3.reparentTo(render)
        self.fieldOfficeWall3.setPosHpr(-67.68, -98.23, 0, 173.30, 0, 0)
        self.fieldOfficeWall3.setScale(20)
        # PlacerTool3D(self.fieldOfficeWall3, increment=1)

        self.suitWall4 = loader.loadModel('phase_5/models/cogdominium/tt_m_ara_cbe_walls.bam')
        self.fieldOfficeWall4 = self.suitWall4.find('**/wall_cogdo_build2_ur')
        self.fieldOfficeWall4.reparentTo(render)
        self.fieldOfficeWall4.setPosHpr(-138, -60, 0, 108.30, 0, 0)
        self.fieldOfficeWall4.setScale(20)
        # PlacerTool3D(self.fieldOfficeWall4, increment=1)

        self.suitWall5 = loader.loadModel('phase_5/models/cogdominium/tt_m_ara_cbe_walls.bam')
        self.fieldOfficeWall5 = self.suitWall5.find('**/wall_cogdo_build2_ur')
        self.fieldOfficeWall5.reparentTo(render)
        self.fieldOfficeWall5.setPosHpr(-144, -42, 0, 103, 0, 0)
        self.fieldOfficeWall5.setScale(20)

        self.suitWall6 = loader.loadModel('phase_5/models/cogdominium/tt_m_ara_cbe_walls.bam')
        self.fieldOfficeWall6 = self.suitWall6.find('**/wall_cogdo_build2_ur')
        self.fieldOfficeWall6.reparentTo(render)
        self.fieldOfficeWall6.setPosHpr(-147.8, -29, 0, 93.3, 0, 0)
        self.fieldOfficeWall6.setScale(20)

        self.elevator = loader.loadModel('phase_5/models/cogdominium/tt_m_ara_csa_elevatorB.bam')
        self.elevator.reparentTo(self.fieldOffice)

        # self.statue = loader.loadModel('phase_4/models/corpstrike/pns_statue_body')
        # self.statue.reparentTo(render)
        # PlacerTool3D(self.statue, increment=1)

        # self.painting = loader.loadModel('phase_4/models/corpstrike/gov_philip_painting')
        # self.painting.reparentTo(render)
        # PlacerTool3D(self.painting, increment=1)

        # self.painting2 = loader.loadModel('phase_4/models/corpstrike/gov_philip_painting')
        # self.painting2.reparentTo(render)
        # PlacerTool3D(self.painting2, increment=1)

    def skyTrack(self, task):
        return SkyUtil.cloudSkyTrack(task)

    def unload(self):
        self.stopRain()
        del self.rain
        del self.rainRender

        self.sky.setScale(1)
        self.hqTelescope.removeNode()
        del self.hqTelescope
        self.hqTelescope = None

        render.setColorScale(Vec4(0.55, 0.35, 0.35, 1))

        if __debug__:
            skyblue2Filename = Filename('../resources/phase_3.5/maps/skyblue2.jpg')
            middayskyBFilename = Filename('../resources/phase_3.5/maps/middayskyB.jpg')
            toontown_central_tutorial_palette_4amla_1Filename = Filename(
                '../resources/phase_3.5/maps/toontown_central_tutorial_palette_4amla_1.jpg')
            toontown_central_tutorial_palette_4amla_1_aFilename = Filename(
                '../resources/phase_3.5/maps/toontown_central_tutorial_palette_4amla_1_a.rgb')
        else:
            skyblue2Filename = Filename('/phase_3.5/maps/skyblue2.jpg')
            middayskyBFilename = Filename('/phase_3.5/maps/middayskyB.jpg')
            toontown_central_tutorial_palette_4amla_1Filename = Filename(
                '/phase_3.5/maps/toontown_central_tutorial_palette_4amla_1.jpg')
            toontown_central_tutorial_palette_4amla_1_aFilename = Filename(
                '/phase_3.5/maps/toontown_central_tutorial_palette_4amla_1_a.rgb')

        self.sky.findTexture('skyblue2').read(skyblue2Filename)
        self.sky.findTexture('middayskyB').read(middayskyBFilename)
        self.sky.findTexture('toontown_central_tutorial_palette_4amla_1').read(
            toontown_central_tutorial_palette_4amla_1Filename, toontown_central_tutorial_palette_4amla_1_aFilename, 0,
            0)

        CogHood.exit(self)
        base.localAvatar.setCameraFov(DefaultCameraFov)

    def startRain(self):
        self.rain = BattleParticles.loadParticleFile('raindisk.ptf')
        self.rain.setPos(0, 0, 20)
        self.rainRender = render.attachNewNode('rainRender')
        self.rainRender.setDepthWrite(0)
        self.rainRender.setBin('fixed', 1)
        self.rain.start(camera, self.rainRender)

    def stopRain(self):
        if self.rain:
            self.rain.cleanup()

    def processTime(self):
        pass