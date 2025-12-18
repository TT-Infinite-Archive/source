from panda3d.core import ClockObject, ConfigVariableBool, ConfigVariableDouble, ConfigVariableInt, ConfigVariableString, GraphicsEngine, NodePath, Notify, PStatClient, PandaNode, TrueClock, VirtualFileSystem, loadPrcFile, loadPrcFileData
import gc
import math
import sys
import time

from direct.directnotify.DirectNotifyGlobal import *
from direct.interval.IntervalManager import ivalMgr
from direct.showbase import EventManager
from direct.showbase import ExceptionVarDump
from direct.showbase import PythonUtil
from direct.showbase.BulletinBoardGlobal import *
from direct.showbase.EventManagerGlobal import *
from direct.showbase.JobManagerGlobal import *
from direct.showbase.MessengerGlobal import *
from direct.showbase.PythonUtil import *
from direct.task import Task
from direct.task.TaskManagerGlobal import *
from otp.otpbase import BackupManager
from toontown.toonbase import ServerSettingsGlobals
import builtins


class AIBase:
    notify = directNotify.newCategory('AIBase')

    from otp.settings.Settings import Settings
    builtins.serverSettings = Settings("serversettings.json")
    from toontown.toonbase import ServerSettingsGlobals
    ServerSettingsGlobals.loadInitialSettings()

    def __init__(self):
        __builtins__['__dev__'] = ConfigVariableBool('want-dev', False).getValue()
        logStackDump = (ConfigVariableBool('log-stack-dump', (not __dev__)).getValue() or ConfigVariableBool('ai-log-stack-dump', (not __dev__)).getValue())
        uploadStackDump = ConfigVariableBool('upload-stack-dump', False).getValue()
        if logStackDump or uploadStackDump:
            ExceptionVarDump.install(logStackDump, uploadStackDump)
        if ConfigVariableBool('use-vfs', True).getValue():
            vfs = VirtualFileSystem.getGlobalPtr()
        else:
            vfs = None
        self.wantTk = ConfigVariableBool('want-tk', False).getValue()
        self.AISleep = ConfigVariableDouble('ai-sleep', 0.04).getValue()
        self.AIRunningNetYield = ConfigVariableBool('ai-running-net-yield', False).getValue()
        self.AIForceSleep = ConfigVariableBool('ai-force-sleep', False).getValue()
        self.eventMgr = eventMgr
        self.messenger = messenger
        self.bboard = bulletinBoard
        self.taskMgr = taskMgr
        Task.TaskManager.taskTimerVerbose = ConfigVariableBool('task-timer-verbose', False).getValue()
        Task.TaskManager.extendedExceptions = ConfigVariableBool('extended-exceptions', False).getValue()
        self.sfxManagerList = None
        self.musicManager = None
        self.jobMgr = jobMgr
        self.hidden = NodePath('hidden')
        self.graphicsEngine = GraphicsEngine()
        globalClock = ClockObject.getGlobalClock()
        self.trueClock = TrueClock.getGlobalPtr()
        globalClock.setRealTime(self.trueClock.getShortTime())
        globalClock.setAverageFrameRateInterval(30.0)
        globalClock.tick()
        taskMgr.globalClock = globalClock
        __builtins__['ostream'] = Notify.out()
        __builtins__['globalClock'] = globalClock
        __builtins__['vfs'] = vfs
        __builtins__['hidden'] = self.hidden
        AIBase.notify.info('__dev__ == %s' % __dev__)
        __builtins__['wantTestObject'] = ConfigVariableBool('want-test-object', False).getValue()
        self.wantStats = ConfigVariableBool('want-pstats', False).getValue()
        Task.TaskManager.pStatsTasks = ConfigVariableBool('pstats-tasks', False).getValue()
        taskMgr.resumeFunc = PStatClient.resumeAfterPause
        defaultValue = 1
        if __dev__:
            defaultValue = 0
        wantFakeTextures = ConfigVariableBool('want-fake-textures-ai', defaultValue).getValue()
        if wantFakeTextures:
            loadPrcFileData('aibase', 'textures-header-only 1')
        self.wantPets = ConfigVariableBool('want-pets', True).getValue()
        if self.wantPets:
            from toontown.pets import PetConstants
            self.petMoodTimescale = ConfigVariableDouble('pet-mood-timescale', 1.0).getValue()
            self.petMoodDriftPeriod = ConfigVariableDouble('pet-mood-drift-period', PetConstants.MoodDriftPeriod).getValue()
            self.petThinkPeriod = ConfigVariableDouble('pet-think-period', PetConstants.ThinkPeriod).getValue()
            self.petMovePeriod = ConfigVariableDouble('pet-move-period', PetConstants.MovePeriod).getValue()
            self.petPosBroadcastPeriod = ConfigVariableDouble('pet-pos-broadcast-period', PetConstants.PosBroadcastPeriod).getValue()
        self.wantBingo = ConfigVariableBool('want-fish-bingo', True).getValue()
        self.wantKarts = ConfigVariableBool('wantKarts', True).getValue()

        # Server Settings options
        self.wantYinYang = serverSettings[ServerSettingsGlobals.YinYang]
        self.baseXpMultiplier = serverSettings[ServerSettingsGlobals.ExpMultiplier]
        self.wantRacing = serverSettings[ServerSettingsGlobals.WantRacing]
        self.wantGolf = serverSettings[ServerSettingsGlobals.WantGolf]
        self.wantTTCJukebox = serverSettings[ServerSettingsGlobals.TTCJukebox]
        self.wantSinglePlayer = None
        # self.wantSinglePlayer = serverSettings[ServerSettingsGlobals.WantSinglePlayer]

        self.newDBRequestGen = ConfigVariableBool('new-database-request-generate', True).getValue()
        self.waitShardDelete = ConfigVariableBool('wait-shard-delete', True).getValue()
        self.blinkTrolley = ConfigVariableBool('blink-trolley', False).getValue()
        self.fakeDistrictPopulations = ConfigVariableBool('fake-district-populations', False).getValue()
        self.wantSwitchboard = ConfigVariableBool('want-switchboard', False).getValue()
        self.wantSwitchboardHacks = ConfigVariableBool('want-switchboard-hacks', False).getValue()
        self.GEMdemoWhisperRecipientDoid = ConfigVariableBool('gem-demo-whisper-recipient-doid', False).getValue()
        self.sqlAvailable = ConfigVariableBool('sql-available', True).getValue()
        self.backups = BackupManager.BackupManager(
            filepath=ConfigVariableString('backups-filepath', 'backups/').getValue(),
            extension=ConfigVariableString('backups-extension', '.json').getValue())
        self.createStats()
        self.restart()

    def setupCpuAffinities(self, minChannel):
        if process == 'uberdog':
            affinityMask = ConfigVariableInt('uberdog-cpu-affinity-mask', -1).getValue()
        else:
            affinityMask = ConfigVariableInt('ai-cpu-affinity-mask', -1).getValue()
        if affinityMask != -1:
            TrueClock.getGlobalPtr().setCpuAffinity(affinityMask)
        else:
            autoAffinity = ConfigVariableBool('auto-single-cpu-affinity', False).getValue()
            if process == 'uberdog':
                affinity = ConfigVariableInt('uberdog-cpu-affinity', -1).getValue()
                if autoAffinity and affinity == -1:
                    affinity = 2
            else:
                affinity = ConfigVariableInt('ai-cpu-affinity', -1).getValue()
                if autoAffinity and affinity == -1:
                    affinity = 1
            if affinity != -1:
                TrueClock.getGlobalPtr().setCpuAffinity(1 << affinity)
            elif autoAffinity:
                if process == 'uberdog':
                    channelSet = int(minChannel / 1000000)
                    channelSet -= 240
                    affinity = channelSet + 3
                    TrueClock.getGlobalPtr().setCpuAffinity(1 << affinity % 4)

    def taskManagerDoYield(self, frameStartTime, nextScheuledTaksTime):
        minFinTime = frameStartTime + self.MaxEpockSpeed
        if nextScheuledTaksTime > 0 and nextScheuledTaksTime < minFinTime:
            minFinTime = nextScheuledTaksTime
        delta = minFinTime - globalClock.getRealTime()
        while delta > 0.002:
            time.sleep(delta)
            delta = minFinTime - globalClock.getRealTime()

    def createStats(self, hostname = None, port = None):
        if not self.wantStats:
            return False
        if PStatClient.isConnected():
            PStatClient.disconnect()
        if hostname is None:
            hostname = ''
        if port is None:
            port = -1
        PStatClient.connect(hostname, port)
        return PStatClient.isConnected()

    def __sleepCycleTask(self, task):
        time.sleep(self.AISleep)
        return Task.cont

    def __resetPrevTransform(self, state):
        PandaNode.resetAllPrevTransform()
        return Task.cont

    def __ivalLoop(self, state):
        ivalMgr.step()
        return Task.cont

    def __igLoop(self, state):
        self.graphicsEngine.renderFrame()
        return Task.cont

    def shutdown(self):
        self.taskMgr.remove('ivalLoop')
        self.taskMgr.remove('igLoop')
        self.taskMgr.remove('aiSleep')
        self.eventMgr.shutdown()

    def restart(self):
        self.shutdown()
        self.taskMgr.add(self.__resetPrevTransform, 'resetPrevTransform', priority=-51)
        self.taskMgr.add(self.__ivalLoop, 'ivalLoop', priority=20)
        self.taskMgr.add(self.__igLoop, 'igLoop', priority=50)
        if self.AISleep >= 0 and (not self.AIRunningNetYield or self.AIForceSleep):
            self.taskMgr.add(self.__sleepCycleTask, 'aiSleep', priority=55)
        self.eventMgr.restart()

    def getRepository(self):
        return self.air

    def run(self):
        self.taskMgr.run()
