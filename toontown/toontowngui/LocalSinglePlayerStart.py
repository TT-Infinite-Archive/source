import atexit
import copy
import socket

from direct.fsm.FSM import FSM
from direct.gui.DirectGui import *

from toontown.chat import ChatGlobals
from toontown.chat.WhisperPopup import WhisperPopup
from toontown.makeatoon.MakeAToonGUI import MATShuffleButton
from toontown.singleplayer.ProcessThread import ProcessThread
from toontown.singleplayer.SinglePlayerGlobals import *
from toontown.toonbase import ToontownGlobals, SettingsGlobals


class LocalSinglePlayerStart(DirectFrame, FSM):

    def __init__(self, mainMenu, singlePlayer, **kwargs):
        DirectFrame.__init__(self, aspect2d, **kwargs)
        FSM.__init__(self, 'LocalSinglePlayerStart')
        self.initialiseoptions(LocalSinglePlayerStart)
        
        self.path = os.path.abspath('.')
        self.threads = []
        self.currentProcess = 0
        self.lastProcess = len(Processes)
        
        self.mainMenu = mainMenu
        self.singlePlayer = singlePlayer
        
        if self.singlePlayer:
            self.mdPort = 7011
            self.logPort = 7021
            self.mongoPort = 7031
            self.mongoPath = 'data/singleplayer'
            self.astronConfig = os.path.join(base.tempDir, 'singleplayer.yml')
        else:
            self.mdPort = 7010
            self.logPort = 7020
            self.mongoPort = 7030
            self.mongoPath = 'data/multiplayer'
            self.astronConfig = os.path.join(base.tempDir, 'multiplayer.yml')
        
        buttonScale = (-1, 1, 1)

        self.label = DirectLabel(self, relief=None, text='', text_fg=(1, 1, 1, 1), text_font=ToontownGlobals.getToonFont(), text_scale=0.1, text_wordwrap=25, pos=(0, 0, -0.2))

        self.backButton = MATShuffleButton(parent=self, pos=(0, 0, -0.75), text=TTLocalizer.MakeAToonLast, wantArrows=False, image_scale=buttonScale, image2_scale=buttonScale, image1_scale=buttonScale, text_scale=0.09, command=lambda: self.request('Back'))
        self.backButton.hide()

    def destroy(self):
        DirectFrame.destroy(self)
        self.ignoreAll()

        if self.label:
            self.label.destroy()
            self.label = None

        if self.backButton:
            self.backButton.destroy()
            self.backButton = None
    
    def getPort(self):
        return 7001 if self.singlePlayer else 7000
    
    def getPids(self):
        return [thread.getPid() for thread in self.threads if thread.hasPid()]
    
    def isServerAlive(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.33)
        return sock.connect_ex(('127.0.0.1', self.getPort())) == 0

    def killThreads(self):
        self.ignoreAll()
        
        for thread in self.threads:
            thread.kill()

        self.threads = []
    
    def enterOff(self):
        self.destroy()
        base.cr.sendDisconnect()
        base.cr.mainMenu.LocalSinglePlayerStart.killThreads()
    
    def enterBack(self):
        self.demand('Off')
        self.mainMenu.demand('Idle')
    
    def enterStart(self):
        if self.isServerAlive():
            self.demand('ServerRunning')
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
        self.destroy()
        self.accept('processFailed', self.__processFailed)
        base.connectToServer('127.0.0.1', self.getPort(), isMultiplayer = False)
    
    def enterFailed(self):
        self.label['text'] = TTLocalizer.StartingFailed % self.process[2]
        self.backButton.show()
        self.killThreads()
    
    def enterServerRunning(self):
        if self.singlePlayer:
            self.label['text'] = TTLocalizer.ServerRunningAlready
        else:
            self.label['text'] = TTLocalizer.MultiServerRunningAlready
        self.backButton.show()
    
    def __nextProcess(self):
        self.process = copy.deepcopy(Processes[self.currentProcess])
        self.currentProcess += 1

        if __debug__:
            self.label['text'] = TTLocalizer.StartingServerDev % self.process[2]
        else:
            self.label['text'] = TTLocalizer.StartingServerLive

        thread = ProcessThread(self.path, self.process)
        
        if thread.processInfo[0].startswith('astrond'):
            thread.processInfo.append(self.astronConfig)
        elif thread.processInfo[0].startswith('mongod'):
            thread.processInfo += ['--port', str(self.mongoPort), '--dbpath', self.mongoPath]
        elif UberdogTarget[-1] in thread.processInfo or AITarget[-1] in thread.processInfo:
            thread.processInfo += ['--astron-ip', '127.0.0.1:%d' % self.mdPort, '--eventlogger-ip', '127.0.0.1:%d' % self.logPort, '--mongodb-ip', 'mongodb://127.0.0.1:%d' % self.mongoPort]
            if self.singlePlayer:
                thread.processInfo += ['--singleplayer']

        thread.start()
        self.threads.append(thread)

        taskMgr.doMethodLater(settings.get(SettingsGlobals.ProcessFailback, 60), lambda task: self.__processFailed(self.process[2]), 'processFailed')
    
    def __processStarted(self, name):
        taskMgr.remove('processFailed')

        if self.currentProcess == self.lastProcess:
            self.label['text'] = TTLocalizer.StartingGame
            taskMgr.doMethodLater(1, lambda task: self.demand('Begun'), 'processStarted')
        else:
            self.__nextProcess()
    
    def __processFailed(self, name):
        if self.getCurrentOrNextState() == 'Start':
            self.request('Failed')
        else:
            message = TTLocalizer.ServerDown % name

            if hasattr(base, 'localAvatar') and base.localAvatar:
                base.localAvatar.setSystemMessage(0, message)
            else:
                WhisperPopup(message, ToontownGlobals.getInterfaceFont(), ChatGlobals.WTSystem).manage(base.marginManager)