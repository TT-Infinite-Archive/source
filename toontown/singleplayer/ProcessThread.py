from direct.directnotify import DirectNotifyGlobal
import subprocess, threading, os

class ProcessThread(threading.Thread):
    notify = DirectNotifyGlobal.directNotify.newCategory('ProcessThread')

    def __init__(self, defaultPath, process):
        threading.Thread.__init__(self)

        self.daemon = True
        self.processInfo, self.folder, self.name, self.failText, self.successText = process
        
        if not self.folder:
            self.folder = defaultPath
        else:
            self.folder = os.path.join(defaultPath, self.folder)
    
    def hasPid(self):
        return hasattr(self, 'process') and self.process is not None
    
    def getPid(self):
        return self.process.pid

    def failed(self):
        messenger.send('processFailed', [self.name])

    def started(self):
        messenger.send('processStarted', [self.name])
    
    def kill(self):
        if hasattr(self, 'process') and self.process:
            self.process.kill()
    
    def run(self):
        try:
            os.chdir(self.folder)
            self.process = subprocess.Popen(self.processInfo, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        except:
            self.failed()
            return

        while True:
            line = self.process.stdout.readline()
            
            if line == '' and self.process.poll() is not None:
                break
            if not line:
                continue
            
            if self.failText in line:
                self.notify.warning('%s quit with line: %s' % (self.name, line))
                self.failed()
                return
            elif self.successText in line:
                self.started()

        self.failed()