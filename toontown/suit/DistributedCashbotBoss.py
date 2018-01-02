from direct.showbase import PythonUtil
from direct.task.Task import Task
from toontown.building import ElevatorConstants, ElevatorUtils
from toontown.chat import ResistanceChat
from toontown.nametag import NametagGlobals
from toontown.toonbase import BulkLoader

from BossBattleLeaderboard import BossBattleLeaderboard
from BossBattleTimer import BossBattleTimer
# from BossBattleHealthBar import BossBattleHealthBar
import DistributedCashbotBossGoon

from direct.fsm import FSM
from direct.gui.DirectGui import *
from direct.interval.IntervalGlobal import *
from direct.task import Task
import math

import DistributedBossCog
import SuitDNA
from toontown.battle import MovieToonVictory
from toontown.battle import RewardPanel
from toontown.battle import SuitBattleGlobals
from toontown.battle.BattleProps import *
from toontown.chat.ChatGlobals import *
from toontown.coghq import CogDisguiseGlobals
from toontown.distributed import DelayDelete
from toontown.nametag.NametagGlobals import *
from toontown.toon import NPCToons
from toontown.toonbase import TTLocalizer
from toontown.toonbase import TTLocalizerEnglish
from toontown.toonbase import ToontownGlobals, SettingsGlobals

from toontown.debug.DebugTools import timeFunc
OneBossCog = None

ModelAssets = [
    'phase_10/models/cogHQ/MidVault.bam',
    'phase_10/models/cogHQ/EndVault.bam',
    'phase_10/models/cogHQ/CBLightning.bam',
    'phase_10/models/cogHQ/CBMagnet.bam',
    'phase_10/models/cogHQ/CBMagnetB.bam',
    'phase_10/models/cogHQ/CBCraneArm.bam',
    'phase_10/models/cogHQ/CBCraneControls.bam',
    'phase_10/models/cogHQ/CBCraneStick.bam',
    'phase_10/models/cogHQ/CBSafe.bam',
    'phase_10/models/cogHQ/CashBotBossEyes.bam',
    'phase_10/models/cogHQ/CFOElevator'
]


class DistributedCashbotBoss(DistributedBossCog.DistributedBossCog, FSM.FSM):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedCashbotBoss')
    numFakeGoons = 3

    def __init__(self, cr):
        DistributedBossCog.DistributedBossCog.__init__(self, cr)
        FSM.FSM.__init__(self, 'DistributedCashbotBoss')
        self.resistanceToon = None
        self.resistanceToonOnstage = 0
        self.cranes = {}
        self.safes = {}
        self.goons = []
        self.bossMaxDamage = ToontownGlobals.CashbotBossMaxDamage
        self.elevatorType = ElevatorConstants.ELEVATOR_CFO
        self.warningSfx = None
        self.battleDifficulty = None
        self.fakeGoons = []
        self.rewardIds = []
        self.battleTwoToons = []
        self.battleTwoBattles = []
        self.bossBattleTimer = None
        self.bossBattleLeaderboard = None
        # self.bossBattleHealthBar = None
        base.boss = self
        self.titleText = None
        self.bulkLoader = BulkLoader.BulkLoader(ModelAssets)
        return

    @timeFunc
    def announceGenerate(self):
        DistributedBossCog.DistributedBossCog.announceGenerate(self)
        self.bulkLoader.load()
        self.midVault = self.bulkLoader.getModel('phase_10/models/cogHQ/MidVault.bam')
        self.endVault = self.bulkLoader.getModel('phase_10/models/cogHQ/EndVault.bam')
        self.lightning = self.bulkLoader.getModel('phase_10/models/cogHQ/CBLightning.bam')
        self.magnet = self.bulkLoader.getModel('phase_10/models/cogHQ/CBMagnet.bam')
        self.magnetB = self.bulkLoader.getModel('phase_10/models/cogHQ/CBMagnetB.bam')
        self.craneArm = self.bulkLoader.getModel('phase_10/models/cogHQ/CBCraneArm.bam')
        self.controls = self.bulkLoader.getModel('phase_10/models/cogHQ/CBCraneControls.bam')
        self.stick = self.bulkLoader.getModel('phase_10/models/cogHQ/CBCraneStick.bam')
        self.safe = self.bulkLoader.getModel('phase_10/models/cogHQ/CBSafe.bam')
        self.eyes = self.bulkLoader.getModel('phase_10/models/cogHQ/CashBotBossEyes.bam')
        self.setName(TTLocalizer.CashbotBossName)
        self.titleText = OnscreenText(TTLocalizer.CashbotBossArea, fg=(1, 1, 1, 1), shadow=(0, 0, 0, 1), font=ToontownGlobals.getSuitFont(), pos=(0, -0.5), scale=0.16, drawOrder=0, mayChange=1)
        self.titleText.hide()
        nameInfo = TTLocalizer.BossCogNameWithDept % {'name': self.name,
         'dept': SuitDNA.getDeptFullname(self.style.dept)}
        self.setDisplayName(nameInfo)
        target = CollisionSphere(2, 0, 0, 3)
        targetNode = CollisionNode('headTarget')
        targetNode.addSolid(target)
        targetNode.setCollideMask(ToontownGlobals.PieBitmask)
        self.headTarget = self.neck.attachNewNode(targetNode)
        shield = CollisionSphere(0, 0, 0.8, 7)
        shieldNode = CollisionNode('shield')
        shieldNode.addSolid(shield)
        shieldNode.setCollideMask(ToontownGlobals.PieBitmask)
        shieldNodePath = self.pelvis.attachNewNode(shieldNode)
        self.heldObject = None
        self.bossDamage = 0
        self.loadEnvironment()
        self.physicsMgr = PhysicsManager()
        integrator = LinearEulerIntegrator()
        self.physicsMgr.attachLinearIntegrator(integrator)
        fn = ForceNode('gravity')
        self.fnp = self.geom.attachNewNode(fn)
        gravity = LinearVectorForce(0, 0, -32)
        fn.addForce(gravity)
        self.physicsMgr.addLinearForce(gravity)
        base.localAvatar.chatMgr.chatInputSpeedChat.addCFOMenu()
        self.warningSfx = loader.loadSfx('phase_9/audio/sfx/CHQ_GOON_tractor_beam_alarmed.ogg')
        global OneBossCog
        if OneBossCog != None:
            self.notify.warning('Multiple BossCogs visible.')
        OneBossCog = self

    def disable(self):
        global OneBossCog
        DistributedBossCog.DistributedBossCog.disable(self)
        self.demand('Off')
        self.unloadEnvironment()
        self.__cleanupFakeGoons()
        self.__cleanupResistanceToon()
        self.fnp.removeNode()
        self.physicsMgr.clearLinearForces()
        self.battleThreeMusic.stop()
        self.epilogueMusic.stop()
        render.setColorScale(1, 1, 1, 1)
        aspect2d.setColorScale(1, 1, 1, 1)

        if self.bossBattleTimer:
            self.bossBattleTimer.destroy()

        if self.bossBattleLeaderboard:
            self.bossBattleLeaderboard.destroy()

        base.localAvatar.chatMgr.chatInputSpeedChat.removeCFOMenu()
        if OneBossCog == self:
            OneBossCog = None

        if hasattr(self, 'bulkLoader'):
            self.bulkLoader.unload()

        return

    def setBattleDifficulty(self, diff):
        self.battleDifficulty = diff

    def setAttackSpeed(self, speed):
        self.attackSpeed = speed

    def getToonDifficulty(self):
        totalCogSuitTier = 0
        totalToons = 0
        for toonId in self.involvedToons:
            toon = self.cr.doId2do.get(toonId)
            if toon:
                totalToons += 1
                totalCogSuitTier += toon.cogTypes[2]
        averageTier = math.ceil(totalCogSuitTier / totalToons)
        return int(averageTier)

    def __makeResistanceToon(self):
        if self.resistanceToon:
            return
        menuIndex, itemIndex = ResistanceChat.decodeId(self.rewardIds[0])
        self.npcId = ResistanceChat.resistanceDict[menuIndex]['npcs'][itemIndex]
        npc = NPCToons.createLocalNPC(self.npcId)
        npc.setPickable(0)
        npc.setPlayerType(NametagGlobals.CCNonPlayer)
        npc.animFSM.request('neutral')
        self.resistanceToon = npc
        self.resistanceToon.setPosHpr(*ToontownGlobals.CashbotRTBattleOneStartPosHpr)
        state = random.getstate()
        random.seed(self.doId)
        self.resistanceToon.suitType = SuitDNA.getRandomSuitByDept('m')
        random.setstate(state)

    def __cleanupResistanceToon(self):
        self.__hideResistanceToon()
        if self.resistanceToon:
            self.resistanceToon.removeActive()
            self.resistanceToon.delete()
            self.resistanceToon = None
        return

    def __showResistanceToon(self, withSuit):
        if not self.resistanceToonOnstage:
            if not self.resistanceToon:
                self.__makeResistanceToon()
            self.resistanceToon.addActive()
            self.resistanceToon.reparentTo(self.geom)
            self.resistanceToonOnstage = 1
        if withSuit:
            index = self.getToonDifficulty()
            suit = SuitDNA.getSuitName(2, index)
            self.resistanceToon.putOnSuit(suit, False)
        else:
            self.resistanceToon.takeOffSuit()

    def __hideResistanceToon(self):
        if self.resistanceToonOnstage:
            self.resistanceToon.removeActive()
            self.resistanceToon.detachNode()
            self.resistanceToonOnstage = 0

    def __cleanupFakeGoons(self):
        if self.fakeGoons:
            for i in xrange(self.numFakeGoons):
                self.fakeGoons[i].disable()
                self.fakeGoons[i].delete()
                self.fakeGoons[i] = None

    def __makeFakeGoons(self):
        self.fakeGoons = []
        for i in xrange(self.numFakeGoons):
            goon = DistributedCashbotBossGoon.DistributedCashbotBossGoon(base.cr)
            goon.doId = -1 - i
            goon.setBossCogId(self.doId)
            goon.setStrength((self.battleDifficulty * 20) + 1)
            goon.setScale(1.5)
            goon.setAttackRadius((self.battleDifficulty * 1.5) + 1)
            goon.generate()
            goon.announceGenerate()
            self.fakeGoons.append(goon)

    def __hideFakeGoons(self):
        if self.fakeGoons:
            for goon in self.fakeGoons:
                goon.request('Off')

    def __showFakeGoons(self, state):
        if self.fakeGoons:
            for goon in self.fakeGoons:
                goon.request(state)

    def loadEnvironment(self):
        DistributedBossCog.DistributedBossCog.loadEnvironment(self)
        self.cableTex = self.craneArm.findTexture('MagnetControl')
        self.eyes.setPosHprScale(4.5, 0, -2.5, 90, 90, 0, 0.4, 0.4, 0.4)
        self.eyes.reparentTo(self.neck)
        self.eyes.hide()
        self.midVault.setPos(0, -222, -70.7)
        self.endVault.setPos(84, -201, -6)
        self.geom = NodePath('geom')
        self.midVault.reparentTo(self.geom)
        self.endVault.reparentTo(self.geom)
        self.endVault.findAllMatches('**/MagnetArms').detach()
        self.endVault.findAllMatches('**/Safes').detach()
        self.endVault.findAllMatches('**/MagnetControlsAll').detach()
        cn = self.endVault.find('**/wallsCollision').node()
        cn.setIntoCollideMask(OTPGlobals.WallBitmask | ToontownGlobals.PieBitmask)
        self.door1 = self.midVault.find('**/SlidingDoor1/')
        self.door2 = self.midVault.find('**/SlidingDoor/')
        self.door3 = self.endVault.find('**/SlidingDoor/')
        elevatorModel = self.bulkLoader.getModel('phase_10/models/cogHQ/CFOElevator')
        elevatorOrigin = self.midVault.find('**/elevator_origin')
        elevatorOrigin.setScale(1)
        elevatorModel.reparentTo(elevatorOrigin)
        leftDoor = elevatorModel.find('**/left_door')
        leftDoor.setName('left-door')
        rightDoor = elevatorModel.find('**/right_door')
        rightDoor.setName('right-door')
        self.setupElevator(elevatorOrigin)
        ElevatorUtils.closeDoors(leftDoor, rightDoor, ElevatorConstants.ELEVATOR_CFO)
        walls = self.endVault.find('**/RollUpFrameCillison')
        walls.detachNode()
        self.evWalls = self.replaceCollisionPolysWithPlanes(walls)
        self.evWalls.reparentTo(self.endVault)
        self.evWalls.stash()
        floor = self.endVault.find('**/EndVaultFloorCollision')
        floor.detachNode()
        self.evFloor = self.replaceCollisionPolysWithPlanes(floor)
        self.evFloor.reparentTo(self.endVault)
        self.evFloor.setName('floor')
        plane = CollisionPlane(Plane(Vec3(0, 0, 1), Point3(0, 0, -50)))
        planeNode = CollisionNode('dropPlane')
        planeNode.addSolid(plane)
        planeNode.setCollideMask(ToontownGlobals.PieBitmask)
        self.geom.attachNewNode(planeNode)
        self.geom.reparentTo(render)

        self.bossBattleTimer = BossBattleTimer()
        self.bossBattleTimer.load()

        self.bossBattleLeaderboard = BossBattleLeaderboard()
        self.bossBattleLeaderboard.load()

        self.battleOneMusic = base.loadMusic('phase_9/audio/bgm/CFO_round_1.ogg')
        self.battleTwoMusic = base.loadMusic('phase_9/audio/bgm/CFO_round_2.ogg')
        self.battleThreeMusic = base.loadMusic('phase_9/audio/bgm/encntr_cfo_boss.ogg')

        self.battleTwoCutsceneMusic = base.loadMusic('phase_9/audio/bgm/CBHQ_Mint_bg.ogg') #Place Holder Track

        self.rbc = RigidBodyCombiner("goon-rbc")
        self.rbcnp = NodePath(self.rbc)
        self.rbcnp.reparentTo(render)

    def unloadEnvironment(self):
        DistributedBossCog.DistributedBossCog.unloadEnvironment(self)
        self.geom.removeNode()

    def replaceCollisionPolysWithPlanes(self, model):
        newCollisionNode = CollisionNode('collisions')
        newCollideMask = BitMask32(0)
        planes = []
        collList = model.findAllMatches('**/+CollisionNode')
        if not collList:
            collList = [model]
        for cnp in collList:
            cn = cnp.node()
            if not isinstance(cn, CollisionNode):
                self.notify.warning('Not a collision node: %s' % repr(cnp))
                break
            newCollideMask = newCollideMask | cn.getIntoCollideMask()
            for i in xrange(cn.getNumSolids()):
                solid = cn.getSolid(i)
                if isinstance(solid, CollisionPolygon):
                    plane = Plane(solid.getPlane())
                    planes.append(plane)
                else:
                    self.notify.warning('Unexpected collision solid: %s' % repr(solid))
                    newCollisionNode.addSolid(plane)

        newCollisionNode.setIntoCollideMask(newCollideMask)
        threshold = 0.1
        planes.sort(lambda p1, p2: p1.compareTo(p2, threshold))
        lastPlane = None
        for plane in planes:
            if lastPlane == None or plane.compareTo(lastPlane, threshold) != 0:
                cp = CollisionPlane(plane)
                newCollisionNode.addSolid(cp)
                lastPlane = plane

        return NodePath(newCollisionNode)

    def __makeGoonMovieForIntro(self):
        goonTrack = Parallel()
        goon = self.fakeGoons[0]
        goonTrack.append(Sequence(
            goon.posHprInterval(0, Point3(111, -287, 0), VBase3(165, 0, 0)),
            goon.posHprInterval(9, Point3(101, -323, 0), VBase3(165, 0, 0)),
            goon.hprInterval(1, VBase3(345, 0, 0)),
            goon.posHprInterval(9, Point3(111, -287, 0), VBase3(345, 0, 0)),
            goon.hprInterval(1, VBase3(165, 0, 0)),
            goon.posHprInterval(9.5, Point3(104, -316, 0), VBase3(165, 0, 0)),
            Wait(7.3),
            Func(goon.request, 'Stunned'),
            Wait(1)))
        goon = self.fakeGoons[1]
        goonTrack.append(Sequence(
            goon.posHprInterval(0, Point3(119, -315, 0), VBase3(357, 0, 0)),
            goon.posHprInterval(9, Point3(121, -280, 0), VBase3(357, 0, 0)),
            goon.hprInterval(1, VBase3(177, 0, 0)),
            goon.posHprInterval(9, Point3(119, -315, 0), VBase3(177, 0, 0)),
            goon.hprInterval(1, VBase3(357, 0, 0)),
            goon.posHprInterval(9, Point3(121, -280, 0), VBase3(357, 0, 0))))
        goon = self.fakeGoons[2]
        goonTrack.append(Sequence(
            goon.posHprInterval(0, Point3(102, -320, 0), VBase3(231, 0, 0)),
            goon.posHprInterval(9, Point3(127, -337, 0), VBase3(231, 0, 0)),
            goon.hprInterval(1, VBase3(51, 0, 0)),
            goon.posHprInterval(9, Point3(102, -320, 0), VBase3(51, 0, 0)),
            goon.hprInterval(1, VBase3(231, 0, 0)),
            goon.posHprInterval(9, Point3(127, -337, 0), VBase3(231, 0, 0))))

        return Sequence(Func(self.__showFakeGoons, 'Walk'), goonTrack, Func(self.__hideFakeGoons))

    def makeIntroductionMovie(self, delayDeletes):
        for toonId in self.involvedToons:
            toon = self.cr.doId2do.get(toonId)
            if toon:
                delayDeletes.append(DelayDelete.DelayDelete(toon, 'CashbotBoss.makeIntroductionMovie'))

        rtTrack = Sequence()
        startPos = Point3(ToontownGlobals.CashbotBossOffstagePosHpr[0], ToontownGlobals.CashbotBossOffstagePosHpr[1], ToontownGlobals.CashbotBossOffstagePosHpr[2])
        battlePos = Point3(ToontownGlobals.CashbotBossBattleOnePosHpr[0], ToontownGlobals.CashbotBossBattleOnePosHpr[1], ToontownGlobals.CashbotBossBattleOnePosHpr[2])
        battleHpr = VBase3(ToontownGlobals.CashbotBossBattleOnePosHpr[3], ToontownGlobals.CashbotBossBattleOnePosHpr[4], ToontownGlobals.CashbotBossBattleOnePosHpr[5])
        bossTrack = Sequence()
        bossTrack.append(Func(self.reparentTo, render))
        bossTrack.append(Func(self.getGeomNode().setH, 180))
        bossTrack.append(Func(self.pelvis.setHpr, self.pelvisForwardHpr))
        bossTrack.append(Func(self.loop, 'Ff_neutral'))
        track, hpr = self.rollBossToPoint(startPos, None, battlePos, None, 0)
        bossTrack.append(track)
        track, hpr = self.rollBossToPoint(battlePos, hpr, battlePos, battleHpr, 0)
        bossTrack.append(track)
        bossTrack.append(Func(self.getGeomNode().setH, 0))
        bossTrack.append(Func(self.pelvis.setHpr, self.pelvisReversedHpr))
        goonTrack = self.__makeGoonMovieForIntro()
        attackToons = TTLocalizer.CashbotBossCogAttack
        rToon = self.resistanceToon
        rToon.setPosHpr(*ToontownGlobals.CashbotRTBattleOneStartPosHpr)
        t = Parallel()
        t.append(Sequence(Wait(3), goonTrack))
        track = Sequence(
            Func(base.camera.setPosHpr, 68.55, -222.21, 7, 267, 0, 0),
            Parallel(
            Func(self.titleText.show),
            Func(rToon.setChatAbsolute, TTLocalizer.ResistanceToonWelcome, CFSpeech),
            Wait(3)),
            Parallel(
                base.camera.posHprInterval(4, Point3(108, -244, 4), VBase3(211.5, 0, 0)),
                Sequence(
                    Func(rToon.suit.setPlayRate, 1.4, 'walk'),
                    Func(rToon.suit.loop, 'walk'),
                    Parallel(
                        rToon.hprInterval(1, VBase3(180, 0, 0)),
                        rToon.posInterval(3, VBase3(120, -255, 0)),
                        Sequence(
                            Wait(2),
                            Func(rToon.clearChat),
                            LerpColorScaleInterval(self.titleText, 1, VBase4(1, 1, 1, 0))
                        )
                    ),
                    Func(rToon.suit.loop, 'neutral'),
                    self.door2.posInterval(3, VBase3(0, 0, 30))
                )
            ),
            Func(rToon.setHpr, 180, 0, 0),
            Func(rToon.setChatAbsolute, TTLocalizer.ResistanceToonTooLate, CFSpeech),
            Func(base.camera.reparentTo, render),
            Func(base.camera.setPosHpr, 120.04, -229.33, 6.36, 180.00, 0, 0),
            Sequence(
                Func(rToon.suit.loop, 'walk'),
                rToon.hprInterval(1, VBase3(0, 0, 0))),
                Func(rToon.suit.loop, 'neutral'),

            self.door1.posInterval(2, VBase3(0, 0, 30)),
            Parallel(
                bossTrack,
                Sequence(
                    Func(base.camera.setPosHpr, 61.1, -228.8, 10.2, -90, 0, 0),
                    Wait(1),
                    Func(rToon.clearChat),
                    self.door1.posInterval(3, VBase3(0, 0, 0))
                )
            ),
            Func(self.setChatAbsolute, TTLocalizer.CashbotBossDiscoverToons1, CFSpeech),
            base.camera.posHprInterval(1.5, Point3(93.3, -230, 0.7), VBase3(-92.9, 39.7, 8.3)),
            Func(self.setChatAbsolute, TTLocalizer.CashbotBossDiscoverToons2, CFSpeech),
            Wait(4),
            Func(self.clearChat),
            self.loseCogSuits(self.toonsA + self.toonsB, render, (113, -228, 10, 90, 0, 0)),
            Wait(1),
            Func(rToon.setHpr, 0, 0, 0),
            self.loseCogSuits([rToon], render, (133, -243, 5, 143, 0, 0), True),
            Func(rToon.setChatAbsolute, TTLocalizer.ResistanceToonKeepHimBusy, CFSpeech),
            Wait(1),
            Func(self.__showResistanceToon, False),
            Sequence(
                Func(rToon.animFSM.request, 'run'),
                rToon.hprInterval(1, VBase3(180, 0, 0)),
                Parallel(
                    Sequence(
                        rToon.posInterval(1.5, VBase3(109, -294, 0)),
                        Parallel(Func(rToon.animFSM.request, 'jump')),
                        rToon.posInterval(1.5, VBase3(93.935, -341.065, 2))
                    ),
                    self.door2.posInterval(3, VBase3(0, 0, 0))
                ),
                Func(rToon.animFSM.request, 'neutral')
            ),
            self.toonNormalEyes(self.involvedToons),
            self.toonNormalEyes([self.resistanceToon], True),
            Func(rToon.clearChat),
            Func(base.camera.setPosHpr, 93.3, -230, 0.7, -92.9, 39.7, 8.3),
            Func(self.setChatAbsolute, attackToons, CFSpeech),
            Parallel(
                LerpColorScaleInterval(render, 3, Vec4(0.7, 0.98, 0.8, 1)),
            ),
            Wait(2),
            Func(self.clearChat)
        )
        t.append(track)
        return Sequence(Func(base.camera.reparentTo, render), t)

    def __makeGoonMovieForBattleThree(self):
        goonPosHprs = [[Point3(111, -287, 0),
          VBase3(165, 0, 0),
          Point3(101, -323, 0),
          VBase3(165, 0, 0)], [Point3(119, -315, 0),
          VBase3(357, 0, 0),
          Point3(121, -280, 0),
          VBase3(357, 0, 0)], [Point3(102, -320, 0),
          VBase3(231, 0, 0),
          Point3(127, -337, 0),
          VBase3(231, 0, 0)]]
        mainGoon = self.fakeGoons[0]
        goonLoop = Parallel()
        for i in xrange(1, self.numFakeGoons):
            goon = self.fakeGoons[i]
            goonLoop.append(Sequence(goon.posHprInterval(8, goonPosHprs[i][0], goonPosHprs[i][1]), goon.posHprInterval(8, goonPosHprs[i][2], goonPosHprs[i][3])))

        goonTrack = Sequence(Func(self.__showFakeGoons, 'Walk'), Func(mainGoon.request, 'Stunned'), Func(goonLoop.loop), Wait(20))
        return goonTrack

    def __makeGearThrowTrack(self):
        gearRoot = self.rotateNode.attachNewNode('gearRoot')
        gearRoot.setZ(10)
        gearRoot.setTag('attackCode', str(ToontownGlobals.BossCogDirectedAttack))
        gearModel = self.getGearFrisbee()
        gearModel.setScale(0.2)
        gearRoot.headsUp(self.resistanceToon)
        toToonH = PythonUtil.fitDestAngle2Src(0, gearRoot.getH() + 180)
        gearRoot.lookAt(self.resistanceToon)
        neutral = 'Fb_neutral'
        if not self.twoFaced:
            neutral = 'Ff_neutral'
        gearTrack = Parallel()
        for i in xrange(4):
            node = gearRoot.attachNewNode(str(i))
            node.hide()
            node.setPos(0, 5.85, 4.0)
            gear = gearModel.instanceTo(node)
            x = random.uniform(-5, 5)
            z = random.uniform(-3, 3)
            h = random.uniform(-720, 720)
            gearTrack.append(Sequence(Wait(i * 0.15), Func(node.show), Parallel(node.posInterval(1, Point3(x, 50, z), fluid=1), node.hprInterval(1, VBase3(h, 0, 0), fluid=1)), Func(node.detachNode)))

        if not self.raised:
            neutral1Anim = self.getAnim('down2Up')
            self.raised = 1
        else:
            neutral1Anim = ActorInterval(self, neutral, startFrame=48)
        throwAnim = self.getAnim('throw')
        neutral2Anim = ActorInterval(self, neutral)
        seq = Sequence(
            neutral1Anim,
            Parallel(
                Sequence(
                    Wait(0.19),
                    gearTrack,
                    Func(gearRoot.detachNode),
                ),
                Sequence(throwAnim, neutral2Anim)
            ),
        )
        self.doAnimate(seq, now=1, raised=1)

    def __makeResistanceToonReactTrack(self):
        def getSlideToPos(toon=self.resistanceToon):
            return render.getRelativePoint(toon, Point3(0, -5, 0))

        seq = Sequence(
            Wait(1.5),
            Parallel(
                ActorInterval(self.resistanceToon, 'slip-backward'),
                Func(self.resistanceToon.setChatAbsolute, 'Oooow!', CFSpeech|CFTimeout),
                self.resistanceToon.posInterval(0.5, getSlideToPos, fluid=1),
            ),
            Func(self.resistanceToon.loop, 'neutral'),
            Func(self.resistanceToon.setChatAbsolute, "The cranes are ready to go!", CFSpeech|CFTimeout),
            Func(self.resistanceToon.loop, 'walk'),
            self.resistanceToon.posInterval(1, render.getRelativePoint(self.resistanceToon, Point3(0, -1, 0)), fluid=1),
            Func(self.resistanceToon.loop, 'neutral'),
            Wait(1.5),
            Func(self.resistanceToon.setChatAbsolute, "This ends now!", CFSpeech),
            Wait(3),
            Func(self.resistanceToon.clearChat),
            Func(base.camera.setPosHpr, 103.42, -333.37, 17.64, 320, 11.09, 0),
            Wait(0.5),
            Func(self.setChatAbsolute, "Ha ha! Those cranes are meaningless!", CFSpeech|CFTimeout),
            Wait(3.3),
            Parallel(
                base.camera.posInterval(1, Vec3(104.42, -334.37, 19.54), Vec3(103.42, -333.37, 17.64), blendType='easeInOut'),
                Func(self.setChatAbsolute, "We've spent thousands of Cogbucks making this vault secure.", CFSpeech|CFTimeout),
            ),
            Wait(4),
            Func(self.setChatAbsolute, "Little trespassers like you aren't a problem to us or the vault.", CFSpeech|CFTimeout),
            Wait(4),
            Parallel(
                base.camera.posInterval(1, Vec3(104.42, -334.37, 20.10), Vec3(104.42, -334.37, 19.54), blendType='easeInOut'),
                Func(self.setChatAbsolute, "After all, this is one of the most secured depositories to ever be created.", CFSpeech|CFTimeout),
            ),
            Wait(4),
            Parallel(
                Func(self.setChatAbsolute, "Let me introduce to you--the vault's defense system!", CFSpeech|CFTimeout),
                Func(self.__makeBattleTwoFlyDownMovie),
                LerpPosHprInterval(base.camera, 6, Vec3(81.01, -356.56, 3.56), Vec3(320.19, 4.76, 0), Vec3(104.42, -334.37, 20.10), Vec3(320, 11.09, 0), blendType='easeInOut'),
            ),
            Func(self.resistanceToon.setChatAbsolute, "Uh oh...", CFSpeech|CFTimeout),
            Wait(6),
            Func(self.resistanceToon.setChatAbsolute, 'Defeat them and enable the cranes! I know you can do it!', CFSpeech|CFTimeout),
            Func(self.cranes[0].request, 'Free')
        )
        seq.start()

    def __makeBattleTwoFlyDownMovie(self):
        for battle in self.battleTwoBattles:
            battle.doInitialFlyDown()

    def makePrepareBattleTwoMovie(self, delayDeletes, crane, safe):
        for toonId in self.involvedToons:
            toon = self.cr.doId2do.get(toonId)
            if toon:
                delayDeletes.append(DelayDelete.DelayDelete(toon, 'CashbotBoss.makePrepareBattleTwoMovie'))

        base.playMusic(self.battleTwoCutsceneMusic, looping=1, volume=0.9)
        base.camLens.setMinFov(ToontownGlobals.CFOElevatorFov/(4./3.))

        startPos = Point3(ToontownGlobals.CashbotBossBattleOnePosHpr[0], ToontownGlobals.CashbotBossBattleOnePosHpr[1], ToontownGlobals.CashbotBossBattleOnePosHpr[2])
        battlePos = Point3(ToontownGlobals.CashbotBossBattleThreePosHpr[0], ToontownGlobals.CashbotBossBattleThreePosHpr[1], ToontownGlobals.CashbotBossBattleThreePosHpr[2])
        startHpr = Point3(ToontownGlobals.CashbotBossBattleOnePosHpr[3], ToontownGlobals.CashbotBossBattleOnePosHpr[4], ToontownGlobals.CashbotBossBattleOnePosHpr[5])
        battleHpr = VBase3(ToontownGlobals.CashbotBossBattleThreePosHpr[3], ToontownGlobals.CashbotBossBattleThreePosHpr[4], ToontownGlobals.CashbotBossBattleThreePosHpr[5])
        finalHpr = VBase3(135, 0, 0)
        bossTrack = Sequence()
        bossTrack.append(Func(self.reparentTo, render))
        bossTrack.append(Func(self.getGeomNode().setH, 180))
        bossTrack.append(Func(self.pelvis.setHpr, self.pelvisForwardHpr))
        bossTrack.append(Func(self.loop, 'Ff_neutral'))
        track, hpr = self.rollBossToPoint(startPos, startHpr, startPos, battleHpr, 0)
        bossTrack.append(track)
        track, hpr = self.rollBossToPoint(startPos, None, battlePos, None, 0)
        bossTrack.append(track)
        track, hpr = self.rollBossToPoint(battlePos, battleHpr, battlePos, finalHpr, 0)
        bossTrack.append(track)
        rToon = self.resistanceToon
        rToon.setPosHpr(93.935, -341.065, 0, -45, 0, 0)
        goon = self.fakeGoons[0]
        crane = self.cranes[0]
        track = Sequence(
            Func(self.__hideToons),
            Func(crane.request, 'Movie'),
            Func(crane.accomodateToon, rToon),
            Func(goon.request, 'Stunned'),
            Func(goon.setPosHpr, 104, -316, 0, 165, 0, 0),
            Parallel(
                self.door2.posInterval(4.5, VBase3(0, 0, 30)),
                self.door3.posInterval(4.5, VBase3(0, 0, 30)),
                bossTrack),
            Func(rToon.loop, 'leverNeutral'),
            Func(base.camera.reparentTo, self.geom),
            Func(base.camera.setPosHpr, 104.92, -327.09, 4.20, 136.3, 0, 0),
            Func(rToon.setChatAbsolute, TTLocalizer.ResistanceToonWatchThis, CFSpeech),
            Wait(2),
            Func(rToon.clearChat),
            base.camera.posHprInterval(0.5, Point3(101.02, -334.60, 18), Point3(315.00, 10.30, 0), blendType='easeInOut'),
            Func(self.setChatAbsolute, TTLocalizer.CashbotBossGetAwayFromThat, CFSpeech),
            Wait(4),
            Parallel(
                base.camera.posHprInterval(1.75, Point3(104.92, -327.09, 4.20), Point3(136.3, 0, 0), blendType='easeInOut'),
                Func(self.__makeGearThrowTrack),
                Func(self.__makeResistanceToonReactTrack),
            ),
            Func(self.clearChat),
            Parallel(
                Sequence(
                    Wait(3),
                ),
            ),
            Wait(31),
            Func(base.camera.setPosHpr, 91.54, -330.79, 3, 325.01, 0, 0),
            Func(goon.request, 'Recovery'),
            Wait(2),
            Func(base.camera.setPosHpr, 94.17, -321.14, 3.14, 167.10, 5.19, 0),
            Func(rToon.setChatAbsolute, TTLocalizer.ResistanceToonGetaway, CFSpeech),
            Func(rToon.animFSM.request, 'jump'),
            Wait(1.8),
            Func(rToon.clearChat),
            Func(base.camera.setPosHpr, 109.1, -300.7, 13.9, -15.6, -13.6, 0),
            Func(rToon.animFSM.request, 'run'),
            Func(goon.request, 'Walk'),
            Parallel(
                self.door3.posInterval(3, VBase3(0, 0, 0)),
                rToon.posHprInterval(3, Point3(136, -212.9, 0), VBase3(-14, 0, 0), startPos=Point3(110.8, -292.7, 0), startHpr=VBase3(-14, 0, 0)),
                goon.posHprInterval(3, Point3(125.2, -243.5, 0), VBase3(-14, 0, 0), startPos=Point3(104.8, -309.5, 0), startHpr=VBase3(-14, 0, 0))),
            Func(self.__hideFakeGoons),
            base.camera.posHprInterval(0.5, Point3(105, -333, 18), Point3(-45, 15, 0), blendType='easeInOut'),
            Func(self.hideBattleThreeObjects),
            self.moveToonsToBattleThreePos(self.involvedToons),
            Func(self.__showToons),
            Func(self.saySomething, TTLocalizer.BossCogAttackToons),
            Wait(3),
            Func(self.__hideResistanceToon))
        return Sequence(Func(base.camera.reparentTo, self), Func(base.camera.setPosHpr, 0, -27, 25, 0, -18, 0), track)

    def moveToonsToBattleThreePos(self, toons):
        track = Parallel()
        for i in xrange(len(toons)):
            toon = base.cr.doId2do.get(toons[i])
            if toon:
                posHpr = ToontownGlobals.CashbotToonsBattleThreeStartPosHpr[i]
                pos = Point3(*posHpr[0:3])
                hpr = VBase3(*posHpr[3:6])
                track.append(toon.posHprInterval(0.2, pos, hpr))

        return track

    def makeBossFleeMovie(self):
        hadEnough = TTLocalizer.CashbotBossHadEnough
        outtaHere = TTLocalizer.CashbotBossOuttaHere
        loco = loader.loadModel('phase_10/models/cogHQ/CashBotLocomotive')
        car1 = loader.loadModel('phase_10/models/cogHQ/CashBotBoxCar')
        car2 = loader.loadModel('phase_10/models/cogHQ/CashBotTankCar')
        trainPassingSfx = loader.loadSfx('phase_10/audio/sfx/CBHQ_TRAIN_pass.ogg')
        boomSfx = loader.loadSfx('phase_3.5/audio/sfx/ENC_cogfall_apart.ogg')
        rollThroughDoor = self.rollBossToPoint(fromPos=Point3(120, -280, 0), fromHpr=None, toPos=Point3(120, -250, 0), toHpr=None, reverse=0)
        rollTrack = Sequence(Func(self.getGeomNode().setH, 180), rollThroughDoor[0], Func(self.getGeomNode().setH, 0))
        g = 80.0 / 300.0
        trainTrack = Track(
            (0 * g, loco.posInterval(0.5, Point3(0, -242, 0), startPos=Point3(150, -242, 0))),
            (1 * g, car2.posInterval(0.5, Point3(0, -242, 0), startPos=Point3(150, -242, 0))),
            (2 * g, car1.posInterval(0.5, Point3(0, -242, 0), startPos=Point3(150, -242, 0))),
            (3 * g, car2.posInterval(0.5, Point3(0, -242, 0), startPos=Point3(150, -242, 0))),
            (4 * g, car1.posInterval(0.5, Point3(0, -242, 0), startPos=Point3(150, -242, 0))),
            (5 * g, car2.posInterval(0.5, Point3(0, -242, 0), startPos=Point3(150, -242, 0))),
            (6 * g, car1.posInterval(0.5, Point3(0, -242, 0), startPos=Point3(150, -242, 0))),
            (7 * g, car2.posInterval(0.5, Point3(0, -242, 0), startPos=Point3(150, -242, 0))),
            (8 * g, car1.posInterval(0.5, Point3(0, -242, 0), startPos=Point3(150, -242, 0))),
            (9 * g, car2.posInterval(0.5, Point3(0, -242, 0), startPos=Point3(150, -242, 0))),
            (10 * g, car1.posInterval(0.5, Point3(0, -242, 0), startPos=Point3(150, -242, 0))),
            (11 * g, car2.posInterval(0.5, Point3(0, -242, 0), startPos=Point3(150, -242, 0))),
            (12 * g, car1.posInterval(0.5, Point3(0, -242, 0), startPos=Point3(150, -242, 0))),
            (13 * g, car2.posInterval(0.5, Point3(0, -242, 0), startPos=Point3(150, -242, 0))),
            (14 * g, car1.posInterval(0.5, Point3(0, -242, 0), startPos=Point3(150, -242, 0))))
        bossTrack = Track(
            (0.0, Sequence(
                Func(base.camera.reparentTo, render),
                Func(base.camera.setPosHpr, 105, -280, 20, -158, -3, 0),
                Func(self.reparentTo, render),
                Func(self.show),
                Func(self.clearChat),
                Func(self.setPosHpr, *ToontownGlobals.CashbotBossBattleThreePosHpr),
                Func(self.reverseHead),
                ActorInterval(self, 'Fb_firstHit'),
                ActorInterval(self, 'Fb_down2Up'))),
            (1.0, Func(self.setChatAbsolute, hadEnough, CFSpeech)),
            (5.5, Parallel(
                Func(base.camera.setPosHpr, 100, -315, 16, -20, 0, 0),
                Func(self.hideBattleThreeObjects),
                Func(self.forwardHead),
                Func(self.loop, 'Ff_neutral'),
                rollTrack,
                self.door3.posInterval(2.5, Point3(0, 0, 25), startPos=Point3(0, 0, 18)))),
            (5.5, Func(self.setChatAbsolute, outtaHere, CFSpeech)),
            (5.5, SoundInterval(trainPassingSfx)),
            (8.1, Func(self.clearChat)),
            (9.4, Sequence(
                Func(loco.reparentTo, render),
                Func(car1.reparentTo, render),
                Func(car2.reparentTo, render),
                trainTrack,
                Func(loco.detachNode),
                Func(car1.detachNode),
                Func(car2.detachNode),
                Wait(2))),
            (9.5, SoundInterval(boomSfx)),
            (9.5, Sequence(
                self.posInterval(0.4, Point3(0, -250, 0)),
                Func(self.stash))),
            (9.5, Parallel(
                LerpColorScaleInterval(render, 3, Vec4(1, 1, 1, 1)),
                LerpColorScaleInterval(aspect2d, 3, Vec4(1, 1, 1, 1)),
            )))
        return bossTrack

    def grabObject(self, obj):
        obj.wrtReparentTo(self.neck)
        obj.hideShadows()
        obj.stashCollisions()
        if obj.lerpInterval:
            obj.lerpInterval.finish()
        obj.lerpInterval = Parallel(
            obj.posInterval(ToontownGlobals.CashbotBossToMagnetTime, Point3(-1, 0, 0.2)),
            obj.quatInterval(ToontownGlobals.CashbotBossToMagnetTime, VBase3(0, -90, 90)),
            Sequence(
                Wait(ToontownGlobals.CashbotBossToMagnetTime),
                ShowInterval(self.eyes)
            ),
            obj.toMagnetSoundInterval)
        obj.lerpInterval.start()
        self.heldObject = obj

        # if self.bossBattleHealthBar:
            # self.bossBattleHealthBar.setHelmet(True)

    def dropObject(self, obj):
        if obj.lerpInterval:
            obj.lerpInterval.finish()
            obj.lerpInterval = None
        obj = self.heldObject
        obj.wrtReparentTo(render)
        obj.setHpr(obj.getH(), 0, 0)
        self.eyes.hide()
        obj.showShadows()
        obj.unstashCollisions()
        self.heldObject = None

        # if self.bossBattleHealthBar:
            # self.bossBattleHealthBar.setHelmet(False)

    def setBossDamage(self, bossDamage):
        if bossDamage > self.bossDamage:
            delta = bossDamage - self.bossDamage
            self.flashRed()
            self.doAnimate('hit', now=1)
            self.showHpText(-delta, scale=5)
        self.bossDamage = bossDamage
        self.updateHealthBar()

    def setRewardIds(self, rewardIds):
        self.rewardIds = rewardIds

    def d_applyReward(self):
        self.sendUpdate('applyReward', [])

    def stunAllGoons(self):
        for goon in self.goons:
            if goon.state == 'Walk' or goon.state == 'Battle':
                goon.demand('Stunned')
                goon.sendUpdate('requestStunned', [0])

    def destroyAllGoons(self):
        for goon in self.goons:
            if goon.state != 'Off' and not goon.isDead:
                goon.b_destroyGoon()

    def deactivateCranes(self):
        for crane in self.cranes.values():
            crane.demand('Free')

    def hideBattleThreeObjects(self):
        for goon in self.goons:
            goon.demand('Off')

        for safe in self.safes.values():
            safe.demand('Off')

        for crane in self.cranes.values():
            crane.demand('Off')

    def showBattleThreeObjects(self):
        for safe in self.safes.values():
            safe.demand('Initial')

        for crane in self.cranes.values():
            crane.demand('Free')

    def __doPhysics(self, task):
        dt = globalClock.getDt()
        self.physicsMgr.doPhysics(dt)
        return Task.cont

    def __hideToons(self):
        for toonId in self.involvedToons:
            toon = self.cr.doId2do.get(toonId)
            if toon:
                toon.hide()

    def __showToons(self):
        for toonId in self.involvedToons:
            toon = self.cr.doId2do.get(toonId)
            if toon:
                toon.show()

    def __arrangeToonsAroundResistanceToon(self):
        radius = 7
        numToons = len(self.involvedToons)
        center = (numToons - 1) / 2.0
        for i in xrange(numToons):
            toon = self.cr.doId2do.get(self.involvedToons[i])
            if toon:
                angle = 90 - 15 * (i - center)
                radians = angle * math.pi / 180.0
                x = math.cos(radians) * radius
                y = math.sin(radians) * radius
                toon.setPos(self.resistanceToon, x, y, 0)
                toon.headsUp(self.resistanceToon)
                toon.loop('neutral')
                toon.show()

    def __talkAboutPromotion(self, speech):
        if self.prevCogSuitLevel < ToontownGlobals.MaxCogSuitLevel:
            deptIndex = CogDisguiseGlobals.dept2deptIndex(self.style.dept)
            cogLevels = base.localAvatar.getCogLevels()
            newCogSuitLevel = cogLevels[deptIndex]
            cogTypes = base.localAvatar.getCogTypes()
            maxCogSuitLevel = (SuitDNA.levelsPerSuit-1) + cogTypes[deptIndex]
            if self.prevCogSuitLevel != maxCogSuitLevel:
                speech += TTLocalizer.ResistanceToonLevelPromotion
            if newCogSuitLevel == maxCogSuitLevel:
                if newCogSuitLevel != ToontownGlobals.MaxCogSuitLevel:
                    suitIndex = (SuitDNA.suitsPerDept*deptIndex) + cogTypes[deptIndex]
                    cogTypeStr = SuitDNA.suitHeadTypes[suitIndex]
                    cogName = SuitBattleGlobals.SuitAttributes[cogTypeStr]['name']
                    speech += TTLocalizer.ResistanceToonSuitPromotion % cogName
        else:
            speech += TTLocalizer.ResistanceToonMaxed % (ToontownGlobals.MaxCogSuitLevel + 1)
        return speech

    def enterOff(self):
        DistributedBossCog.DistributedBossCog.enterOff(self)
        if self.resistanceToon:
            self.resistanceToon.clearChat()
        # if self.bossBattleHealthBar:
            # self.bossBattleHealthBar.destroy()
            # self.bossBattleHealthBar = None
        if self.bossBattleLeaderboard:
            self.bossBattleLeaderboard.destroy()
            self.bossBattleLeaderboard = None
        if self.bossBattleTimer:
            self.bossBattleTimer.destroy()
            self.bossBattleTimer = None

    def enterWaitForToons(self):
        DistributedBossCog.DistributedBossCog.enterWaitForToons(self)
        self.detachNode()
        self.geom.hide()

    def exitWaitForToons(self):
        DistributedBossCog.DistributedBossCog.exitWaitForToons(self)
        self.geom.show()
        self.__makeResistanceToon()
        self.__makeFakeGoons()

    def enterElevator(self):
        DistributedBossCog.DistributedBossCog.enterElevator(self)
        self.detachNode()
        self.endVault.stash()
        self.midVault.unstash()
        self.__showResistanceToon(True)
        base.camLens.setMinFov(ToontownGlobals.CFOElevatorFov/(4./3.))

    def exitElevator(self):
        DistributedBossCog.DistributedBossCog.exitElevator(self)
        self.resistanceToon.addActive()

    def enterIntroduction(self):
        self.detachNode()
        self.stopAnimate()
        self.endVault.unstash()
        self.evWalls.stash()
        self.midVault.unstash()
        self.__showResistanceToon(True)
        base.playMusic(self.stingMusic, looping=1, volume=0.9)
        DistributedBossCog.DistributedBossCog.enterIntroduction(self)

    def exitIntroduction(self):
        DistributedBossCog.DistributedBossCog.exitIntroduction(self)
        self.stingMusic.stop()

    def enterBattleOne(self):
        DistributedBossCog.DistributedBossCog.enterBattleOne(self)
        self.reparentTo(render)
        self.setPosHpr(*ToontownGlobals.CashbotBossBattleOnePosHpr)
        self.show()
        self.pelvis.setHpr(self.pelvisReversedHpr)
        self.doAnimate()
        self.endVault.stash()
        self.midVault.unstash()
        self.__hideResistanceToon()

    def exitBattleOne(self):
        DistributedBossCog.DistributedBossCog.exitBattleOne(self)

    def saySomething(self, chatString):
        intervalName = 'CFOTaunt'
        seq = Sequence(name=intervalName)
        seq.append(Func(self.setChatAbsolute, chatString, CFSpeech))
        seq.append(Wait(4.0))
        seq.append(Func(self.clearChat))
        oldSeq = self.activeIntervals.get(intervalName)
        if oldSeq:
            oldSeq.finish()
        seq.start()
        self.storeInterval(seq, intervalName)

    def setAttackCode(self, attackCode, avId=0):
        DistributedBossCog.DistributedBossCog.setAttackCode(self, attackCode, avId)
        if attackCode == ToontownGlobals.BossCogAreaAttack:
            self.saySomething(TTLocalizer.CashbotBossAreaAttackTaunt)
            self.flashRed()
            base.playSfx(self.warningSfx)

    def enterPrepareBattleTwo(self):
        self.controlToons()
        NametagGlobals.setWant2dNametags(False)
        intervalName = 'PrepareBattleTwoMovie'
        delayDeletes = []
        self.movieCrane = self.cranes[0]
        self.movieSafe = self.safes[1]
        self.movieCrane.request('Movie')

        seq = Sequence(self.makePrepareBattleTwoMovie(delayDeletes, self.movieCrane, self.movieSafe),
                       Func(self.__beginBattleTwo), name=intervalName)
        seq.delayDeletes = delayDeletes
        seq.start()
        self.storeInterval(seq, intervalName)
        self.endVault.unstash()
        self.evWalls.stash()
        self.midVault.unstash()
        self.__showResistanceToon(False)
        taskMgr.add(self.__doPhysics, self.uniqueName('physics'), priority=25)

    def __beginBattleTwo(self):
        intervalName = 'PrepareBattleTwoMovie'
        self.clearInterval(intervalName)
        self.doneBarrier('PrepareBattleTwo')

    def exitPrepareBattleTwo(self):
        intervalName = 'PrepareBattleTwoMovie'
        self.clearInterval(intervalName)
        if self.newState == 'BattleThree':
            self.movieCrane.request('Free')
            self.movieSafe.request('Initial')
        NametagGlobals.setWant2dNametags(True)
        ElevatorUtils.closeDoors(self.leftDoor, self.rightDoor, ElevatorConstants.ELEVATOR_CFO)
        taskMgr.remove(self.uniqueName('physics'))

    def enterBattleTwo(self):
        self.cleanupIntervals()
        self.evWalls.unstash()
        base.playMusic(self.battleTwoMusic, looping=1, volume=0.9)

    def exitBattleTwo(self):
        self.cleanupBattles(battleTwo=True)

    def makePrepareBattleThreeMovie(self, delayDeletes):
        for toonId in self.involvedToons:
            toon = self.cr.doId2do.get(toonId)
            if toon:
                delayDeletes.append(DelayDelete.DelayDelete(toon, 'CashbotBoss.makePrepareBattleThreeMovie'))

        track = Sequence(
            Func(base.camera.reparentTo, self.geom),
            Func(base.camera.setPosHpr, 103.42, -333.37, 17.54, 320, 11.09, 0),
            self.moveToonsToBattleThreePos(self.involvedToons),
        )

        for s in TTLocalizer.CashbotBossBattleThreeSpeech:
            track.append(Wait(3.45))
            track.append(Func(self.saySomething, s))

        track.append(Wait(5))

        return track

    def enterPrepareBattleThree(self):
        self.cleanupBattles(battleTwo=True)
        self.controlToons()
        self.endVault.unstash()
        self.evWalls.unstash()
        self.midVault.stash()
        self.__showResistanceToon(False)
        self.showBattleThreeObjects()

        if self.battleDifficulty == 2:
            self.bossMaxDamage = 1000
        elif self.battleDifficulty == 3:
            self.bossMaxDamage = 2000

        NametagGlobals.setWant2dNametags(False)
        intervalName = 'PrepareBattleThreeMovie'
        delayDeletes = []
        seq = Sequence(
            self.makePrepareBattleThreeMovie(delayDeletes),
            Func(self.__beginBattleThree), name=intervalName)
        seq.delayDeletes = delayDeletes
        seq.start()
        self.storeInterval(seq, intervalName)

    def __beginBattleThree(self):
        intervalName = 'PrepareBattleThreeMovie'
        self.clearInterval(intervalName)
        self.doneBarrier('PrepareBattleThree')

    def exitPrepareBattleThree(self):
        intervalName = 'PrepareBattleThreeMovie'
        self.clearInterval(intervalName)
        NametagGlobals.setWant2dNametags(True)

    @timeFunc
    def enterBattleThree(self):
        self.getGeomNode().setH(0)
        DistributedBossCog.DistributedBossCog.enterBattleThree(self)
        self.clearChat()
        if self.resistanceToon:
            self.resistanceToon.clearChat()
        self.reparentTo(render)
        self.setPosHpr(*ToontownGlobals.CashbotBossBattleThreePosHpr)
        self.happy = 1
        self.raised = 1
        self.forward = 1
        self.doAnimate()
        self.endVault.unstash()
        self.evWalls.unstash()
        self.midVault.stash()
        self.__hideResistanceToon()
        localAvatar.setCameraFov(ToontownGlobals.BossBattleCameraFov)
        self.generateHealthBar()
        self.updateHealthBar()

        # self.bossBattleHealthBar = BossBattleHealthBar(self.dna.dept, self.bossMaxDamage)
        # self.bossBattleHealthBar.load()

        base.playMusic(self.battleThreeMusic, looping=1, volume=0.9)
        taskMgr.add(self.__doPhysics, self.uniqueName('physics'), priority=25)

    def exitBattleThree(self):
        DistributedBossCog.DistributedBossCog.exitBattleThree(self)
        bossDoneEventName = self.uniqueName('DestroyedBoss')
        self.ignore(bossDoneEventName)
        self.stopAnimate()
        self.cleanupAttacks()
        self.setDizzy(0)
        self.removeHealthBar()
        localAvatar.setCameraFov(ToontownGlobals.CogHQCameraFov)
        if self.newState != 'Victory':
            self.battleThreeMusic.stop()
        taskMgr.remove(self.uniqueName('physics'))

    def enterVictory(self):
        self.stopLookAtToon()
        self.cleanupIntervals()
        self.reparentTo(render)
        self.setPosHpr(*ToontownGlobals.CashbotBossBattleThreePosHpr)
        self.stopAnimate()
        self.endVault.unstash()
        self.evWalls.unstash()
        self.midVault.unstash()
        self.__hideResistanceToon()
        self.__hideToons()
        self.clearChat()
        self.resistanceToon.clearChat()
        self.deactivateCranes()
        if self.cranes:
            self.cranes[1].demand('Off')
        self.releaseToons(finalBattle=1)
        # if self.bossBattleHealthBar:
            # self.bossBattleHealthBar.destroy()
            # self.bossBattleHealthBar = None
        if self.hasLocalToon():
            self.toMovieMode()
        intervalName = 'VictoryMovie'
        seq = Sequence(self.makeBossFleeMovie(), Func(self.__continueVictory), name=intervalName)
        seq.start()
        self.storeInterval(seq, intervalName)
        if self.oldState != 'BattleThree':
            base.playMusic(self.battleThreeMusic, looping=1, volume=0.9)

    def __continueVictory(self):
        self.doneBarrier('Victory')

    def exitVictory(self):
        self.cleanupIntervals()
        if self.newState != 'Reward':
            if self.hasLocalToon():
                self.toWalkMode()
        self.__showToons()
        self.door3.setPos(0, 0, 0)
        if self.newState != 'Reward':
            self.battleThreeMusic.stop()

    def enterReward(self):
        self.cleanupIntervals()
        self.clearChat()

        if self.bossBattleTimer:
            self.bossBattleTimer.destroy()
            self.bossBattleTimer = None

        if self.bossBattleLeaderboard:
            self.bossBattleLeaderboard.destroy()
            self.bossBattleLeaderboard = None

        self.resistanceToon.clearChat()
        self.stash()
        self.stopAnimate()
        self.controlToons()
        panelName = self.uniqueName('reward')
        self.rewardPanel = RewardPanel.RewardPanel(panelName)
        victory, camVictory, skipper = MovieToonVictory.doToonVictory(1, self.involvedToons, self.toonRewardIds, self.toonRewardDicts, self.deathList, self.rewardPanel, allowGroupShot=0, uberList=self.uberList, noSkip=True)
        ival = Sequence(Parallel(victory, camVictory), Func(self.__doneReward))
        intervalName = 'RewardMovie'
        delayDeletes = []
        for toonId in self.involvedToons:
            toon = self.cr.doId2do.get(toonId)
            if toon:
                delayDeletes.append(DelayDelete.DelayDelete(toon, 'CashbotBoss.enterReward'))

        ival.delayDeletes = delayDeletes
        ival.start()
        self.storeInterval(ival, intervalName)
        if self.oldState != 'Victory':
            base.playMusic(self.battleThreeMusic, looping=1, volume=0.9)

    def __doneReward(self):
        self.doneBarrier('Reward')
        self.toWalkMode()

    def exitReward(self):
        intervalName = 'RewardMovie'
        self.clearInterval(intervalName)
        if self.newState != 'Epilogue':
            self.releaseToons()
        self.unstash()
        self.rewardPanel.destroy()
        del self.rewardPanel
        self.battleThreeMusic.stop()

    def enterEpilogue(self):
        self.cleanupIntervals()
        self.clearChat()
        self.resistanceToon.clearChat()
        self.stash()
        self.stopAnimate()
        self.controlToons()
        self.__showResistanceToon(False)
        self.resistanceToon.setPosHpr(*ToontownGlobals.CashbotBossBattleThreePosHpr)
        self.resistanceToon.loop('neutral')
        self.__arrangeToonsAroundResistanceToon()
        base.camera.reparentTo(render)
        base.camera.setPos(self.resistanceToon, -9, 12, 6)
        base.camera.lookAt(self.resistanceToon, 0, 0, 3)
        intervalName = 'EpilogueMovie'
        text = ResistanceChat.getChatText(self.rewardIds[0])
        menuIndex, itemIndex = ResistanceChat.decodeId(self.rewardIds[0])
        value = ResistanceChat.getItemValue(self.rewardIds[0])
        if menuIndex == ResistanceChat.RESISTANCE_TOONUP:
            if value == -1:
                instructions = TTLocalizer.ResistanceToonToonupAllInstructions
            else:
                instructions = TTLocalizer.ResistanceToonToonupInstructions % value
        elif menuIndex == ResistanceChat.RESISTANCE_MONEY:
            if value == -1:
                instructions = TTLocalizer.ResistanceToonMoneyAllInstructions
            else:
                instructions = TTLocalizer.ResistanceToonMoneyInstructions % value
        elif menuIndex == ResistanceChat.RESISTANCE_RESTOCK:
            if value == -1:
                instructions = TTLocalizer.ResistanceToonRestockAllInstructions
            else:
                trackName = TTLocalizer.BattleGlobalTracks[value]
                instructions = TTLocalizer.ResistanceToonRestockInstructions % trackName
        elif menuIndex == ResistanceChat.RESISTANCE_DANCE:
            instructions = TTLocalizer.ResistanceToonDanceInstructions

        speech = TTLocalizer.ResistanceToonCongratulations % (text, instructions)

        if self.battleDifficulty > 1:
            speech += TTLocalizer.ResistanceToonAdditionalUnites % (self.battleDifficulty - 1)

        speech = self.__talkAboutPromotion(speech)
        self.resistanceToon.setLocalPageChat(speech, 0)
        self.accept('nextChatPage', self.__epilogueChatNext)
        self.accept('doneChatPage', self.__epilogueChatDone)
        base.playMusic(self.epilogueMusic, looping=1, volume=0.9)

    def __epilogueChatNext(self, pageNumber, elapsed):
        if pageNumber == 1:
            toon = self.resistanceToon
            playRate = 0.75
            track = Sequence(ActorInterval(toon, 'victory', playRate=playRate, startFrame=0, endFrame=9), ActorInterval(toon, 'victory', playRate=playRate, startFrame=9, endFrame=0), Func(self.resistanceToon.loop, 'neutral'))
            intervalName = 'EpilogueMovieToonAnim'
            self.storeInterval(track, intervalName)
            track.start()
        elif pageNumber == 3:
            self.d_applyReward()
            ResistanceChat.doEffect(self.rewardIds[0], self.resistanceToon, self.involvedToons)

    def __epilogueChatDone(self, elapsed):
        self.resistanceToon.setChatAbsolute(TTLocalizer.CagedToonGoodbye, CFSpeech)
        self.ignore('nextChatPage')
        self.ignore('doneChatPage')
        intervalName = 'EpilogueMovieToonAnim'
        self.clearInterval(intervalName)
        track = Parallel(Sequence(ActorInterval(self.resistanceToon, 'wave'), Func(self.resistanceToon.loop, 'neutral')), Sequence(Wait(0.5), Func(self.localToonToSafeZone)))
        self.storeInterval(track, intervalName)
        track.start()

    def exitEpilogue(self):
        self.clearInterval('EpilogueMovieToonAnim')
        self.unstash()
        self.epilogueMusic.stop()

    def enterFrolic(self):
        DistributedBossCog.DistributedBossCog.enterFrolic(self)
        self.setPosHpr(*ToontownGlobals.CashbotBossBattleOnePosHpr)
        self.releaseToons()
        if self.hasLocalToon():
            self.toWalkMode()
        self.door3.setZ(25)
        self.door2.setZ(25)
        self.endVault.unstash()
        self.evWalls.stash()
        self.midVault.unstash()
        self.__hideResistanceToon()

    def exitFrolic(self):
        self.door3.setZ(0)
        self.door2.setZ(0)

    def setBattleTwoGroups(self, battleTwoToons):
        self.battleTwoToons = battleTwoToons

    def setBattleTwoIds(self, battleIds):
        self.battleNumber = 2
        self.cr.relatedObjectMgr.abortRequest(self.battleRequest)
        self.battleRequest = self.cr.relatedObjectMgr.requestObjects(battleIds, allCallback=self.__gotBattleTwo)

    def __gotBattleTwo(self, battles):
        self.battleTwoBattles = battles

    def cleanupBattles(self, battleTwo=False):
        if battleTwo:
            for battle in self.battleTwoBattles:
                battle.cleanupBattle()

        DistributedBossCog.DistributedBossCog.cleanupBattles(self)

    def timerStart(self, startTime):
        if self.bossBattleTimer:
            self.bossBattleTimer.start(startTime)

    def timerStop(self, endTime):
        if self.bossBattleTimer:
            self.bossBattleTimer.stop(endTime)

    def leaderboardUpdateAvatar(self, avId, damage):
        if self.bossBattleLeaderboard:
            if not self.bossBattleLeaderboard.hasAvatar(avId):
                av = base.cr.doId2do.get(avId)
                if not av:
                    return
                self.bossBattleLeaderboard.addAvatar(avId, av.getName(), damage)
            else:
                self.bossBattleLeaderboard.updateAvatar(avId, damage)

    # def healthBarUpdate(self):
        # if self.bossBattleHealthBar:
            # self.bossBattleHealthBar.updateHealthBar(self.bossMaxDamage - self.bossDamage)

    def setDizzy(self, dizzy):
        DistributedBossCog.DistributedBossCog.setDizzy(self, dizzy)
        # if self.bossBattleHealthBar:
            # self.bossBattleHealthBar.setDizzy(dizzy)
