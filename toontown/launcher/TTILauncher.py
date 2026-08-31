from panda3d.core import ConfigVariableInt, Filename, HTTPClient, MultiplexStream, Notify, StreamWriter
from direct.directnotify import DirectNotifyGlobal, Notifier
from toontown.toonbase import ToontownGlobals
import os
import sys
import time


class LogAndOutput:
    def __init__(self, orig, log):
        self.orig = orig
        self.log = log

    def write(self, str):
        self.log.write(str)
        self.log.flush()
        self.orig.write(str)
        self.orig.flush()

    def flush(self):
        self.log.flush()
        self.orig.flush()

class TTILauncher:
    notify = DirectNotifyGlobal.directNotify.newCategory('TTILauncher')

    def __init__(self):
        self.http = HTTPClient()

        self.logPrefix = 'infinite-'
        
        if sys.platform == 'android':
            # Can't really set stdout on here without Android freaking out.
            return

        ltime = 1 and time.localtime()
        logSuffix = '%02d%02d%02d_%02d%02d%02d' % (ltime[0] - 2000,  ltime[1], ltime[2],
                                                   ltime[3], ltime[4], ltime[5])

        folder = os.path.join(ToontownGlobals.CurrentDirectory, 'logs')
        
        if not os.path.exists(folder):
            os.mkdir(folder)
            self.notify.info('Made new directory to save logs.')

        logfile = os.path.join(folder, self.logPrefix + logSuffix + '.log')

        log = open(logfile, 'a')
        logOut = LogAndOutput(sys.stdout, log)
        logErr = LogAndOutput(sys.stderr, log)
        sys.stdout = logOut
        sys.stderr = logErr

        self.nout = MultiplexStream()
        Notify.ptr().setOstreamPtr(self.nout, 0)
        Notifier.Notifier.streamWriter = StreamWriter(self.nout, False)
        self.nout.addFile(Filename(logfile))
        self.nout.addStandardOutput()

    def getPlayToken(self):
        return self.getValue('TTI_PLAYCOOKIE')

    def getGameServer(self):
        return self.getValue('TTI_GAMESERVER')

    def getServerMode(self):
        """
        Which server the launcher picked: 'local', 'direct', or 'production'.
        """
        return self.getValue('TTI_SERVER_MODE')

    def getProfile(self):
        """
        The account name to log in under on a server that keeps its own accounts:
        the local profile's name in local mode, and the player's username on a server 
        somebody else hosts.
        """
        return self.getValue('TTI_PROFILE')

    def getProfileKey(self):
        """
        The password that goes with it, generated and kept by the launcher. In
        direct mode it is derived per server, so the one host it is handed to
        can't reuse it anywhere else.
        """
        return self.getValue('TTI_PROFILE_KEY')

    def setPandaErrorCode(self, code):
        self.notify.info('setting panda error code to %s' % code)
        self.pandaErrorCode = code

    def getPandaErrorCode(self):
        return self.pandaErrorCode

    def setDisconnectDetailsNormal(self):
        self.notify.info('Setting Disconnect Details normal')
        self.disconnectCode = 0
        self.disconnectMsg = 'normal'

    def setDisconnectDetails(self, newCode, newMsg):
        self.notify.info('New Disconnect Details: %s - %s ' % (newCode, newMsg))
        self.disconnectCode = newCode
        self.disconnectMsg = newMsg

    def setServerVersion(self, version):
        self.ServerVersion = version

    def getServerVersion(self):
        return self.ServerVersion

    def getGame2Done(self):
        return True

    def getLogFileName(self):
        return 'toontown'

    def getValue(self, key, default = None):
        return os.environ.get(key, default)

    def setValue(self, key, value):
        os.environ[key] = str(value)

    def getVerifyFiles(self):
        return ConfigVariableInt('launcher-verify', 0).getValue()

    def isDownloadComplete(self):
        return 1

    def isTestServer(self):
        return 0

    def getPhaseComplete(self, phase):
        return 1
    
    def getPercentPhaseComplete(self, phase):
        return 1.0
    
    def isDummy(self):
        return False

    def startGame(self):
        self.newTaskManager()
        eventMgr.restart()
        from toontown.toonbase import ToontownStart
