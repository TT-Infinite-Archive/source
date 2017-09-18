import atexit
import copy

from direct.fsm.FSM import FSM

from toontown.chat import ChatGlobals
from toontown.chat.WhisperPopup import WhisperPopup
from toontown.server.ProcessThread import ProcessThread
from toontown.server.ServerGlobals import *
from toontown.toonbase import ToontownGlobals, SettingsGlobals, EventGlobals


class LocalServerStarter(FSM):

    def __init__(self):
        FSM.__init__(self, 'LocalServerStarter')
        
        self.path = os.path.abspath('.')
        self.threads = []
        self.currentProcess = 0
        self.lastProcess = len(Processes)

        self.mdPort = 7010
        self.logPort = 7020
        self.mongoPort = 7030
        self.mongoPath = os.path.join(ToontownGlobals.CurrentDirectory, 'astron', 'data')
        self.astronConfig = os.path.join(base.tempDir, 'server.yml')

    def enterOff(self):
        base.cr.sendDisconnect()
        self.killThreads()

    def exitOff(self):
        pass
    
    def enterStart(self):
        if self.isServerAlive():
            messenger.send(EventGlobals.LocalServerStarterFailedRunning)
            return
        messenger.send(EventGlobals.LocalServerStarterStart)
        self.accept('processStarted', self.__processStarted)
        self.accept('processFailed', self.__processFailed)
        atexit.register(self.killThreads)

        os.chdir(self.path)
        self.__nextProcess()
    
    def exitStart(self):
        self.ignore('processStarted')
        taskMgr.remove('processFailed')
        os.chdir(self.path)

    def enterRunning(self):
        messenger.send(EventGlobals.LocalServerStarterDone)
        base.connectToServer('127.0.0.1', self.getPort())
        base.cr.loginFSM.request('serverMenu')

    def exitRunning(self):
        pass
    
    def __nextProcess(self):
        self.process = copy.deepcopy(Processes[self.currentProcess])
        self.currentProcess += 1
        messenger.send(EventGlobals.LocalServerStarterProcess, [self.process[2]])

        thread = ProcessThread(self.path, self.process)
        
        if thread.processInfo[0].startswith('astrond'):
            thread.processInfo.append(self.astronConfig)
        elif thread.processInfo[0].startswith('mongod'):
            thread.processInfo += ['--port', str(self.mongoPort), '--dbpath', self.mongoPath]
        elif UberdogTarget[-1] in thread.processInfo or AITarget[-1] in thread.processInfo:
            thread.processInfo += ['--astron-ip', '127.0.0.1:%d' % self.mdPort, '--eventlogger-ip', '127.0.0.1:%d' % self.logPort, '--mongodb-ip', 'mongodb://127.0.0.1:%d' % self.mongoPort]
            if base.isSinglePlayer:
                thread.processInfo += ['--singleplayer']

        thread.start()
        self.threads.append(thread)
        taskMgr.doMethodLater(settings.get(SettingsGlobals.ProcessFailback, 60), lambda task: self.__processFailed(self.process[2]), 'processFailed')
    
    def __processStarted(self, name):
        taskMgr.remove('processFailed')

        if self.currentProcess == self.lastProcess:
            taskMgr.doMethodLater(1, lambda task: self.demand('Running'), 'localServerStarterDone')
        else:
            self.__nextProcess()
    
    def __processFailed(self, name):
        if self.getCurrentOrNextState() == 'Start':
            messenger.send(EventGlobals.LocalServerStarterFailed, [name])
            self.demand('Off')
        else:
            message = TTLocalizer.ServerDown % name

            if hasattr(base, 'localAvatar') and base.localAvatar:
                base.localAvatar.setSystemMessage(0, message)
            else:
                WhisperPopup(message, ToontownGlobals.getInterfaceFont(), ChatGlobals.WTSystem).manage(base.marginManager)

    def getPort(self):
        return 7000

    def getPids(self):
        return [thread.getPid() for thread in self.threads if thread.hasPid()]

    def isServerAlive(self):
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.33)
        return sock.connect_ex(('127.0.0.1', self.getPort())) == 0

    def killThreads(self):
        self.ignoreAll()

        for thread in self.threads:
            thread.kill()

        self.threads = []
        self.currentProcess = 0