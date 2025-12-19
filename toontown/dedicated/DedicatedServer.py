from panda3d.direct import DCFile
from panda3d.core import StringStream
import atexit
import copy
import sys
import types
import builtins
import tempfile
import shutil
import yaml
import os

from direct.directnotify.DirectNotifyGlobal import *
from direct.fsm.FSM import FSM
from toontown.server.ProcessThread import ProcessThread
from toontown.server.ServerGlobals import *
from toontown.toonbase import TTLocalizer, ToontownGlobals, SettingsGlobals

class DedicatedServer(FSM):
    notify = directNotify.newCategory('DedicatedServer')

    def __init__(self):
        FSM.__init__(self, 'DedicatedServer')

        # Create a temporary directory:
        self.tempDir = tempfile.mkdtemp()
        atexit.register(shutil.rmtree, self.tempDir)

        self.readDCFile()

        self.path = os.path.abspath('.')
        self.threads = []
        self.currentProcess = 0
        self.lastProcess = len(Processes)

        self.mdPort = 7010
        self.logPort = 7020
        self.mongoPort = 7030
        self.mongoPath = os.path.join(ToontownGlobals.CurrentDirectory, 'astron', 'data')
        self.astronConfig = os.path.join(self.tempDir, 'server.yml')

    def isServerAlive(self):
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.33)
        return sock.connect_ex(('127.0.0.1', 7000)) == 0

    def killThreads(self):
        self.ignoreAll()
        
        for thread in self.threads:
            thread.kill()

        self.threads = []

    def enterStart(self):
        if self.isServerAlive():
            self.notify.error(TTLocalizer.ServerRunningAlready)
            return

        self.accept('processStarted', self.__processStarted)
        self.accept('processFailed', self.__processFailed)
        atexit.register(self.killThreads)

        os.chdir(self.path)
        self.__nextProcess()

    def exitStarting(self):
        self.ignore('processStarted')
        taskMgr.remove('processFailed')
        os.chdir(self.path)

    def enterBegun(self):
        self.accept('processFailed', self.__processFailed)
        self.notify.info(TTLocalizer.DedicatedServerDone)

    def enterFailed(self):
        self.killThreads()
        self.notify.error(TTLocalizer.StartingFailed % self.process[2])

    def __nextProcess(self):
        self.process = copy.deepcopy(Processes[self.currentProcess])
        self.currentProcess += 1

        self.notify.info(TTLocalizer.StartingServerDev % self.process[2])

        thread = ProcessThread(self.path, self.process)
        
        if thread.processInfo[0].startswith('astrond'):
            thread.processInfo.append(self.astronConfig)
        elif thread.processInfo[0].startswith('mongod'):
            thread.processInfo += ['--port', str(self.mongoPort), '--dbpath', self.mongoPath]
        elif UberdogTarget[-1] in thread.processInfo or AITarget[-1] in thread.processInfo:
            thread.processInfo += ['--astron-ip', '127.0.0.1:%d' % self.mdPort, '--eventlogger-ip', '127.0.0.1:%d' % self.logPort, '--mongodb-ip', 'mongodb://127.0.0.1:%d' % self.mongoPort]

        thread.start()
        self.threads.append(thread)

        taskMgr.doMethodLater(60, lambda task: self.__processFailed(self.process[2]), 'processFailed')
    
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

        dcImports = {}
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
        data = getAstronConfig(dcFileNames=(dcFilePath,), version=version, server=1)
        with open(path, 'w') as f:
            yaml.dump(data, f)