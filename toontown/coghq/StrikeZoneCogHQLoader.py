from direct.actor import Actor
from toontown.coghq import CogHQLoader
from toontown.coghq import StrikeZoneCogHQExterior
from toontown.coghq import StrikeZoneHQBossBattle


class StrikeZoneCogHQLoader(CogHQLoader.CogHQLoader):

    def __init__(self, hood, parentFSM, doneEvent):
        CogHQLoader.CogHQLoader.__init__(self, hood, parentFSM, doneEvent)
        self.musicFile = 'phase_4/audio/corpstrike/GOV_strikezone_nbrhood.ogg'
        self.cogHQExteriorModelPath = 'phase_4/models/corpstrike/toontown_central_strike_zone'
        # self.dnaFile = 'phase_6/dna/cog_hq_strike_zone_sz.pdna'
        # self.battleMusic = base.loadMusic('phase_4/audio/bgm/TTC_SZ_Halloween_Battle.ogg')

        self.buildings = []
        self.props = []
        self.govWall = []
        self.geom = None

    def load(self, zoneId):
        CogHQLoader.CogHQLoader.load(self, zoneId)

    def loadPlaceGeom(self, zoneId):
        self.geom = loader.loadModel(self.cogHQExteriorModelPath)
        self.geom.setHpr(-90, 0, 0)

        self.toonHall = loader.loadModel('phase_4/models/corpstrike/destroyed_toonhall')
        self.toonHall.reparentTo(render)
        self.toonHall.setPosHpr(116.66, 24.29, 4, -90, 0, 0)

        self.bank = loader.loadModel('phase_4/models/corpstrike/destroyed_bank')
        self.bank.reparentTo(render)
        self.bank.setPos(57.1796, 38.6656, 0.3)

        self.library = loader.loadModel('phase_4/models/corpstrike/destroyed_library')
        self.library.reparentTo(render)
        self.library.setPosHpr(91.4475, -44.9255, 4, 180, 0, 0)

        self.toonHQ = loader.loadModel('phase_4/models/corpstrike/hqTT_ost')
        self.toonHQ.reparentTo(render)
        self.toonHQ.setPosHpr(23.6425, 24.8587, 4, 135, 0, 0)

        self.hqTelescope = Actor.Actor('phase_4/models/corpstrike/hqTT_telescope_ost', {'animation': 'phase_4/models/corpstrike/hqTT_telescope_ost'})
        self.hqTelescope.loop('animation')
        self.hqTelescope.reparentTo(render)
        self.hqTelescope.setPosHpr(20.5, 29, 16.7, -70, 0, 0)

        self.gazebo = loader.loadModel('phase_4/models/corpstrike/gazebo_ost')
        self.gazebo.reparentTo(render)
        self.gazebo.setPosHpr(-60.94, -8.8, -2, -178, 0, 0)

        self.buildings.append(self.toonHall)
        self.buildings.append(self.bank)
        self.buildings.append(self.library)
        self.buildings.append(self.toonHQ)
        self.props.append(self.hqTelescope)
        self.props.append(self.gazebo)

        """
        self.fieldOffice = loader.loadModel('phase_5/models/cogdominium/tt_m_ara_cbe_fieldOfficePhilip')
        self.fieldOffice.reparentTo(render)
        self.fieldOffice.setPosHpr(-130, -73, 0, 130, 0, 0)

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
        """

    def unload(self):
        CogHQLoader.CogHQLoader.unload(self)

    def unloadPlaceGeom(self):
        if self.geom:
            self.geom.removeNode()
            self.geom = None
        for building in self.buildings:
            building.removeNode()
        for prop in self.props:
            prop.removeNode()
        CogHQLoader.CogHQLoader.unloadPlaceGeom(self)

    def getExteriorPlaceClass(self):
        return StrikeZoneCogHQExterior.StrikeZoneCogHQExterior

    def getBossPlaceClass(self):
        return StrikeZoneHQBossBattle.SZHQBossBattle
