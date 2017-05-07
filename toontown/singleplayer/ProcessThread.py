import os
import threading
import time
import sys

from direct.directnotify import DirectNotifyGlobal

from toontown.singleplayer.SinglePlayerGlobals import LogsPath

if sys.platform != 'android':
    import subprocess

class ProcessThread(threading.Thread):
    notify = DirectNotifyGlobal.directNotify.newCategory('ProcessThread')

    def __init__(self, defaultPath, process):
        threading.Thread.__init__(self)

        self.daemon = True
        self.killed = False
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
        self.killed = True
        messenger.send('processFailed', [self.name])

    def started(self):
        messenger.send('processStarted', [self.name])
    
    def kill(self):
        if hasattr(self, 'process') and self.process and not self.killed:
            self.process.kill()
            self.killed = True
    
    def run(self):
        print('Starting %s in %s' % (self.processInfo, self.folder))
        try:
            print('Creating log file....')
            name = self.name.split(' ', 1)[0].lower()
            path = os.path.join(LogsPath, name)
            if not os.path.exists(path):
                os.makedirs(path)
            filename = os.path.join(path, '%s-%s.log' % (name, int(time.time())))
            f = open(filename, 'w')
            print("Created Log File: " + f.name)
            os.chdir(self.folder)
            self.process = subprocess.Popen(self.processInfo, stdout=subprocess.PIPE, stderr=f)
        except Exception as e:
            print('failed', e.message, e.args)
            self.failed()
            return

        while True:
            line = self.process.stdout.readline()

            if line == '' and self.process.poll() is not None:
                break
            if not line:
                continue

            f.write(line[:-1])

            if self.failText in line:
                self.notify.warning('%s quit with line: %s' % (self.name, line))
                self.failed()
                return
            elif self.successText in line:
                self.started()

        self.failed()
