from direct.fsm.FSM import FSM
from direct.gui.DirectGui import *
from toontown.chat.WhisperPopup import WhisperPopup
from toontown.chat import ChatGlobals
from toontown.toonbase import ToontownGlobals, TTLocalizer
from toontown.singleplayer.SinglePlayerGlobals import *
from toontown.singleplayer.ProcessThread import ProcessThread
from toontown.makeatoon.MakeAToonGUI import MATShuffleButton
import atexit, psutil, os

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
        
        buttonScale = (-1, 1, 1)

        self.label = DirectLabel(self, relief=None, text='', text_fg=(1, 1, 1, 1), text_font=ToontownGlobals.getToonFont(), text_scale=0.1, text_wordwrap=25, pos=(0, 0, -0.2))

        self.backButton = MATShuffleButton(parent=self, pos=(0, 0, -0.75), text=TTLocalizer.MakeAToonLast, wantArrows=False, image_scale=buttonScale, image2_scale=buttonScale, image1_scale=buttonScale, text_scale=0.09, command=lambda: self.request('Back'))
        self.backButton.hide()
        
        self.restartButton = MATShuffleButton(parent=self, pos=(-0.4, 0, -0.75), text=TTLocalizer.StartingRestart, wantArrows=False, image_scale=buttonScale, image2_scale=buttonScale, image1_scale=buttonScale, text_scale=0.09, command=lambda: self.request('StartingKill'))
        self.restartButton.hide()

        self.joinButton = MATShuffleButton(parent=self, pos=(0.4, 0, -0.75), text=TTLocalizer.StartingJoin, wantArrows=False, image_scale=buttonScale, image2_scale=buttonScale, image1_scale=buttonScale, text_scale=0.09, command=lambda: self.request('Begun'))
        self.joinButton.hide()

    def destroy(self):
        DirectFrame.destroy(self)
        self.ignoreAll()

        if self.label:
            self.label.destroy()
            self.label = None

        if self.backButton:
            self.backButton.destroy()
            self.backButton = None
        
        if self.restartButton:
            self.restartButton.destroy()
            self.restartButton = None
        
        if self.joinButton:
            self.joinButton.destroy()
            self.joinButton = None

    def killThreads(self):
        self.ignoreAll()
        
        for thread in self.threads:
            thread.kill()
        
        pid = os.getpid()
        processNames = set([process[0][0].split(os.sep)[-1] for process in Processes])

        for subProcess in psutil.process_iter():
            if pid == subProcess.pid:
                continue
            
            subName = subProcess.name()

            for name in processNames:
                if subName.startswith(name):
                    subProcess.kill()
                    break
    
    def enterOff(self):
        self.destroy()
        base.cr.sendDisconnect()
    
    def enterBack(self):
        self.demand('Off')
        self.mainMenu.demand('Idle')
    
    def enterQuestion(self):
        self.label['text'] = TTLocalizer.StartingQuestion
        self.restartButton.show()
        self.joinButton.show()
    
    def exitQuestion(self):
        self.restartButton.hide()
        self.joinButton.hide()
    
    def enterStart(self):
        for subProcess in psutil.process_iter():
            if subProcess.name().startswith('astrond'):
                self.demand('ServerRunning' if self.singlePlayer else 'Question')
                return
        
        self.demand('StartingKill')
    
    def enterStartingKill(self):
        self.killThreads()
        taskMgr.doMethodLater(0.25, lambda task: self.demand('Starting'), 'enterStart')
    
    def exitStartingKill(self):
        taskMgr.remove('enterStart')
    
    def enterStarting(self):
        self.accept('processStarted', self.__processStarted)
        self.accept('processFailed', self.__processFailed)
        self.__nextProcess()
    
    def exitStarting(self):
        self.ignore('processStarted')
        taskMgr.remove('processFailed')
        os.chdir(self.path)
    
    def enterBegun(self):
        self.destroy()
        self.accept('processFailed', self.__processFailed)
        
        atexit.register(self.killThreads)
        base.connectToServer('localhost')
    
    def enterFailed(self):
        self.label['text'] = TTLocalizer.StartingFailed % self.process[2]
        self.backButton.show()
        self.killThreads()
    
    def enterServerRunning(self):
        self.label['text'] = TTLocalizer.ServerRunningAlready
        self.backButton.show()
    
    def __nextProcess(self):
        self.process = Processes[self.currentProcess]
        self.currentProcess += 1

        if base.wantDevDebug:
            self.label['text'] = TTLocalizer.StartingServerDev % self.process[2]
        else:
            self.label['text'] = TTLocalizer.StartingServerLive

        thread = ProcessThread(self.path, self.process)
        
        if (not self.singlePlayer) and thread.processInfo[0].startswith('astrond'):
            thread.processInfo.append('astrond_mp.yml')

        thread.start()
        self.threads.append(thread)

        taskMgr.doMethodLater(15, self.__processFailed, 'processFailed')
    
    def __processStarted(self, name):
        taskMgr.remove('processFailed')

        if self.currentProcess == self.lastProcess:
            self.label['text'] = TTLocalizer.StartingGame
            taskMgr.doMethodLater(1, lambda task: self.demand('Begun'), 'processStarted')
        else:
            self.__nextProcess()
    
    def __processFailed(self, name):
        if self.getCurrentOrNextState() == 'Starting':
            self.request('Failed')
        else:
            message = TTLocalizer.ServerDown % name

            if hasattr(base, 'localAvatar') and base.localAvatar:
                base.localAvatar.setSystemMessage(0, message)
            else:
                WhisperPopup(message, ToontownGlobals.getInterfaceFont(), ChatGlobals.WTSystem).manage(base.marginManager)