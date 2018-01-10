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

        self.buildings = []
        self.props = []
        self.fieldOffice = []
        self.geom = None

    def load(self, zoneId):
        CogHQLoader.CogHQLoader.load(self, zoneId)
        self.battleMusic = base.loadMusic('phase_4/audio/corpstrike/cs_courtyard_battleMusic.ogg')

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

        self.tunnel = loader.loadModel('phase_4/models/corpstrike/safe_zone_tunnel_TT_ost')
        self.tunnel.reparentTo(render)
        self.tunnel.setPosHpr(-239.67, 64.08, -6.18, -90, 0, 0)

        self.tunnel2 = loader.loadModel('phase_4/models/corpstrike/safe_zone_tunnel_TT_ost')
        self.tunnel2.reparentTo(render)
        self.tunnel2.setPosHpr(-68.38, -202.64, -3.58, -31, 0, 0)

        self.tunnel3 = loader.loadModel('phase_4/models/corpstrike/safe_zone_tunnel_TT_ost')
        self.tunnel3.reparentTo(render)
        self.tunnel3.setPosHpr(27.6402, 176.475, -6.18, 171, 0, 0)

        self.streetLight = loader.loadModel('phase_4/models/corpstrike/streetlight_TT_ost')
        self.oneLight = self.streetLight.find('**/prop_post_one_light')
        self.oneLight.reparentTo(render)
        self.oneLight.setPosHpr(3.84337, 118.504, 3, -110, 0, 0)

        self.streetLight2 = loader.loadModel('phase_4/models/corpstrike/streetlight_TT_ost')
        self.oneLight2 = self.streetLight2.find('**/prop_post_one_light')
        self.oneLight2.reparentTo(render)
        self.oneLight2.setPosHpr(116.979, 146.926, 3, 145, 0, 0)

        self.streetLight3 = loader.loadModel('phase_4/models/corpstrike/streetlight_TT_ost')
        self.oneLight3 = self.streetLight3.find('**/prop_post_one_light')
        self.oneLight3.reparentTo(render)
        self.oneLight3.setPosHpr(86.808, 164.831, 3, -95, 0, 0)

        self.streetLight4 = loader.loadModel('phase_4/models/corpstrike/streetlight_TT_ost')
        self.threeLight = self.streetLight4.find('**/prop_post_three_light')
        self.threeLight.reparentTo(render)
        self.threeLight.setPosHpr(46.7488, -86.2016, 3.00007, -2, 0, 0)

        self.streetLight5 = loader.loadModel('phase_4/models/corpstrike/streetlight_TT_ost')
        self.threeLight2 = self.streetLight5.find('**/prop_post_three_light')
        self.threeLight2.reparentTo(render)
        self.threeLight2.setPosHpr(77.3059, -86.4255, 2.9999, -2, 0, 0)

        self.streetLight6 = loader.loadModel('phase_4/models/corpstrike/streetlight_TT_ost')
        self.threeLight3 = self.streetLight6.find('**/prop_post_three_light')
        self.threeLight3.reparentTo(render)
        self.threeLight3.setPosHpr(58.8052, 92.6999, 3, -90, 0, 0)

        self.streetLight7 = loader.loadModel('phase_4/models/corpstrike/streetlight_TT_ost')
        self.threeLight4 = self.streetLight7.find('**/prop_post_three_light')
        self.threeLight4.reparentTo(render)
        self.threeLight4.setPosHpr(94.8051, 92.6997, 3, -90, 0, 0)

        self.streetLight8 = loader.loadModel('phase_4/models/corpstrike/streetlight_TT_ost')
        self.oneLight4 = self.streetLight8.find('**/prop_post_one_light')
        self.oneLight4.reparentTo(render)
        self.oneLight4.setPosHpr(134.882, -125.532, 3, -130, 0, 0)

        self.streetLight9 = loader.loadModel('phase_4/models/corpstrike/streetlight_TT_ost')
        self.oneLight5 = self.streetLight9.find('**/prop_post_one_light')
        self.oneLight5.reparentTo(render)
        self.oneLight5.setPosHpr(4.9912, -116.182, 3, -155, 0, 0)

        self.streetLight10 = loader.loadModel('phase_4/models/corpstrike/streetlight_TT_ost')
        self.threeLight5 = self.streetLight10.find('**/prop_post_three_light')
        self.threeLight5.reparentTo(render)
        self.threeLight5.setPosHpr(108.962, -28.0532, 4, -180, 0, 0)

        self.streetLight11 = loader.loadModel('phase_4/models/corpstrike/streetlight_TT_ost')
        self.threeLight6 = self.streetLight11.find('**/prop_post_three_light')
        self.threeLight6.reparentTo(render)
        self.threeLight6.setPosHpr(108.205, 32.0659, 4, -180, 0, 0)

        self.streetLight12 = loader.loadModel('phase_4/models/corpstrike/streetlight_TT_ost')
        self.threeLight7 = self.streetLight12.find('**/prop_post_three_light')
        self.threeLight7.reparentTo(render)
        self.threeLight7.setPosHpr(32.9609, 61.9462, 4, 180, 0, 0)

        self.streetLight13 = loader.loadModel('phase_4/models/corpstrike/streetlight_TT_ost')
        self.threeLight8 = self.streetLight13.find('**/prop_post_three_light')
        self.threeLight8.reparentTo(render)
        self.threeLight8.setPosHpr(28.9617, -57.0532, 4, 180, 0, 0)

        self.streetLight14 = loader.loadModel('phase_4/models/corpstrike/streetlight_TT_ost')
        self.threeLight9 = self.streetLight14.find('**/prop_post_three_light')
        self.threeLight9.reparentTo(render)
        self.threeLight9.setPosHpr(-99.98, -66.4832, 0.5, 175, 0, 0)

        self.streetLight14 = loader.loadModel('phase_4/models/corpstrike/streetlight_TT_ost')
        self.threeLight10 = self.streetLight14.find('**/prop_post_three_light')
        self.threeLight10.reparentTo(render)
        self.threeLight10.setPosHpr(-125.889, -42.5582, 0.5, 175, 0, 0)

        self.streetLight15 = loader.loadModel('phase_4/models/corpstrike/streetlight_TT_ost')
        self.oneLight6 = self.streetLight15.find('**/prop_post_one_light')
        self.oneLight6.reparentTo(render)
        self.oneLight6.setPosHpr(-125, 60, 0.525, 52, 0, 0)

        self.fieldOffice = loader.loadModel('phase_4/models/corpstrike/tt_m_ara_cbe_fieldOfficePhilip_full')
        self.fieldOffice.reparentTo(render)

        self.buildings.append(self.toonHall)
        self.buildings.append(self.bank)
        self.buildings.append(self.library)
        self.buildings.append(self.toonHQ)
        self.buildings.append(self.fieldOffice)
        self.props.append(self.hqTelescope)
        self.props.append(self.gazebo)
        self.props.append(self.tunnel)
        self.props.append(self.tunnel2)
        self.props.append(self.tunnel3)

        self.props.append(self.oneLight)
        self.props.append(self.oneLight2)
        self.props.append(self.oneLight3)
        self.props.append(self.oneLight4)
        self.props.append(self.oneLight5)
        self.props.append(self.oneLight6)
        self.props.append(self.threeLight)
        self.props.append(self.threeLight2)
        self.props.append(self.threeLight3)
        self.props.append(self.threeLight4)
        self.props.append(self.threeLight5)
        self.props.append(self.threeLight6)
        self.props.append(self.threeLight7)
        self.props.append(self.threeLight8)
        self.props.append(self.threeLight9)
        self.props.append(self.threeLight10)

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
