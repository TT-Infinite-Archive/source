from direct.fsm.FSM import FSM
from direct.gui.DirectGui import *
from toontown.chat.WhisperPopup import WhisperPopup
from toontown.chat import ChatGlobals
from toontown.toonbase import ToontownGlobals, TTLocalizer
from toontown.singleplayer.SinglePlayerGlobals import *
from toontown.singleplayer.ProcessThread import ProcessThread
from toontown.makeatoon.MakeAToonGUI import MATShuffleButton
import psutil, os

class SinglePlayerMenu(DirectFrame, FSM):

    def __init__(self, mainMenu, **kwargs):
        DirectFrame.__init__(self, aspect2d, **kwargs)
        FSM.__init__(self, 'SinglePlayerMenu')
        self.initialiseoptions(SinglePlayerMenu)
        
        self.path = os.path.abspath('.')
        self.threads = []
        self.currentProcess = 0
        self.lastProcess = len(Processes)
        
        self.mainMenu = mainMenu
        
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
                self.demand('Question')
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
        base.connectToServer('localhost')
    
    def enterFailed(self):
        self.label['text'] = TTLocalizer.StartingFailed % self.process[2]
        self.backButton.show()
        self.killThreads()
    
    def __nextProcess(self):
        self.process = Processes[self.currentProcess]
        self.currentProcess += 1
        
        self.label['text'] = TTLocalizer.StartingServer % self.process[2]
        
        thread = ProcessThread(self.path, self.process)
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