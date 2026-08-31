from panda3d.direct import DCFile
from panda3d.core import StringStream
import atexit
import copy
import shutil
import tempfile
import builtins
import yaml
import os

from direct.directnotify.DirectNotifyGlobal import *
from direct.fsm.FSM import FSM
from toontown.server.ProcessThread import ProcessThread
from toontown.server.ServerGlobals import *
from toontown.toonbase import TTLocalizer, ToontownGlobals


class DedicatedServer(FSM):
    """
    The whole server stack with no client attached.

    A headless environment runs this and nothing else.
    """

    notify = directNotify.newCategory('DedicatedServer')

    # How long a process gets to say it is ready before it counts as failed:
    STARTUP_TIMEOUT = 60

    def __init__(self, port=DefaultPort, districtName=DefaultDistrict,
                 mongoUrl=None, config=()):
        FSM.__init__(self, 'DedicatedServer')

        self.port = port
        self.districtName = districtName

        # An external database means one less process to supervise, and is how
        # anyone running more than one server instance will want it:
        self.mongoUrl = mongoUrl
        self.mongoPort = MongoPort
        self.mongoPath = os.path.join(
            ToontownGlobals.CurrentDirectory, 'astron', 'data')

        self.processes = getProcesses(
            districtName=districtName, mongo=mongoUrl is None, config=config)
        self.lastProcess = len(self.processes)
        self.currentProcess = 0
        self.threads = []

        # Create a temporary directory:
        self.tempDir = tempfile.mkdtemp()
        atexit.register(shutil.rmtree, self.tempDir, True)

        self.readDCFile()

        self.path = os.path.abspath('.')
        self.mdPort = MessageDirectorPort
        self.logPort = EventLoggerPort
        self.astronConfig = os.path.join(self.tempDir, 'server.yml')

    def databaseUrl(self):
        return self.mongoUrl or 'mongodb://127.0.0.1:%d/game' % self.mongoPort

    def isServerAlive(self):
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.33)
        return sock.connect_ex(('127.0.0.1', self.port)) == 0

    def killThreads(self):
        self.ignoreAll()

        for thread in self.threads:
            thread.kill()

        self.threads = []

    def enterStart(self):
        if self.isServerAlive():
            self.notify.error(TTLocalizer.ServerRunningAlready)
            return

        # mongod will not create its own data directory, and a fresh install
        # has no empty directories in it:
        if self.mongoUrl is None:
            os.makedirs(self.mongoPath, exist_ok=True)

        self.accept('processStarted', self.__processStarted)
        self.accept('processFailed', self.__processFailed)
        atexit.register(self.killThreads)

        os.chdir(self.path)
        self.__nextProcess()

    def exitStart(self):
        self.ignore('processStarted')
        taskMgr.remove('processFailed')
        os.chdir(self.path)

    def enterBegun(self):
        self.accept('processFailed', self.__processFailed)
        self.notify.info(TTLocalizer.DedicatedServerDone)
        self.notify.info('Players connect to port %d, district "%s".'
                         % (self.port, self.districtName))

    def enterFailed(self):
        self.killThreads()
        self.notify.error(TTLocalizer.StartingFailed % self.process[2])

    def __nextProcess(self):
        self.process = copy.deepcopy(self.processes[self.currentProcess])
        self.currentProcess += 1

        self.notify.info(TTLocalizer.StartingServerDev % self.process[2])

        thread = ProcessThread(self.path, self.process)

        # The astrond entry is a path (`./astrond-linux`) because POSIX does
        # not search the working directory for executables:
        executable = os.path.basename(thread.processInfo[0])

        if executable.startswith('astrond'):
            thread.processInfo.append(self.astronConfig)
        elif executable.startswith('mongod'):
            thread.processInfo += [
                '--port', str(self.mongoPort), '--dbpath', self.mongoPath]
        elif UberdogTarget[-1] in thread.processInfo or AITarget[-1] in thread.processInfo:
            thread.processInfo += [
                '--astron-ip', '127.0.0.1:%d' % self.mdPort,
                '--eventlogger-ip', '127.0.0.1:%d' % self.logPort,
                '--mongodb-ip', self.databaseUrl()]

        thread.start()
        self.threads.append(thread)

        taskMgr.doMethodLater(
            self.STARTUP_TIMEOUT,
            lambda task: self.__processFailed(self.process[2]),
            'processFailed')

    def __processStarted(self, name):
        taskMgr.remove('processFailed')

        if self.currentProcess == self.lastProcess:
            taskMgr.doMethodLater(1, lambda task: self.demand('Begun'), 'processStarted')
        else:
            self.__nextProcess()

    def __processFailed(self, name):
        if self.getCurrentOrNextState() == 'Start':
            self.request('Failed')
        else:
            message = TTLocalizer.ServerDownRestart % name
            self.notify.warning(message)

            self.killThreads()
            self.currentProcess = 0

            taskMgr.doMethodLater(1, lambda task: self.demand('Start'), 'serverRestart')

    def readDCFile(self, dcFileNames=None):
        dcFile = DCFile()
        dcFile.clear()

        if isinstance(dcFileNames, (str,)):
            # If we were given a single string, make it a list.
            dcFileNames = [dcFileNames]

        if hasattr(builtins, 'dcData'):
            dcFileNames = [StringStream(dcData)]

        if dcFileNames is None:
            readResult = dcFile.readAll()
            if not readResult:
                self.notify.error('Could not read DC file.')
        else:
            for dcFileName in dcFileNames:
                if isinstance(dcFileName, StringStream):
                    readResult = dcFile.read(dcFileName, 'DC stream')
                else:
                    readResult = dcFile.read(dcFileName)
                if not readResult:
                    self.notify.error('Could not read DC file.')

        # Output the DC data to a temporary file (for use with Astron).
        dcFilePath = os.path.join(self.tempDir, 'vanilla.dc')
        dcFile.write(dcFilePath, False)

        # Get the modified config for Astron.
        path = os.path.join(self.tempDir, 'server.yml')
        data = getAstronConfig(dcFileNames=(dcFilePath,), version=version,
                               server=1, port=self.port,
                               mongoUrl=self.databaseUrl())
        with open(path, 'w') as f:
            yaml.dump(data, f)
