from panda3d.core import ConfigVariableBool, ConfigVariableDouble, Filename, NodePath, TPLow, Vec4, getModelPath
import re
import time
import tempfile
import atexit
import shutil
import sys
from . import OTPGlobals
from . import OTPRender
from direct.showbase.ShowBase import ShowBase
from otp.ai.MagicWordGlobal import *

class OTPBase(ShowBase):

    def __init__(self, windowType = None):
        # Create a temporary directory:
        if sys.platform == 'android':
            self.tempDir = ''
        else:
            self.tempDir = tempfile.mkdtemp()
            atexit.register(shutil.rmtree, self.tempDir)

        self.wantEnviroDR = False
        ShowBase.__init__(self, windowType=windowType)
        if ConfigVariableBool('want-phase-checker', False).getValue():
            from direct.showbase import Loader
            Loader.phaseChecker = self.loaderPhaseChecker
            self.errorAccumulatorBuffer = ''
            taskMgr.add(self.delayedErrorCheck, 'delayedErrorCheck', priority=10000)
        self.idTags = ConfigVariableBool('want-id-tags', False).getValue()
        if not self.idTags:
            del self.idTags
        self.wantNametags = ConfigVariableBool('want-nametags', True).getValue()
        self.slowCloseShard = ConfigVariableBool('slow-close-shard', False).getValue()
        self.slowCloseShardDelay = ConfigVariableDouble('slow-close-shard-delay', 10.0).getValue()
        self.fillShardsToIdealPop = ConfigVariableBool('fill-shards-to-ideal-pop', True).getValue()
        self.logPrivateInfo = ConfigVariableBool('log-private-info', __dev__).getValue()
        self.wantDynamicShadows = 1
        self.gameOptionsCode = ''
        self.locationCode = ''
        self.locationCodeChanged = time.time()
        if base.cam:
            if self.wantEnviroDR:
                base.cam.node().setCameraMask(OTPRender.MainCameraBitmask)
            else:
                base.cam.node().setCameraMask(OTPRender.MainCameraBitmask | OTPRender.EnviroCameraBitmask)
        taskMgr.setupTaskChain('net')

    def setTaskChainNetThreaded(self):
        if ConfigVariableBool('want-threaded-network', False):
            taskMgr.setupTaskChain('net', numThreads=1, frameBudget=0.001, threadPriority=TPLow)

    def setTaskChainNetNonthreaded(self):
        taskMgr.setupTaskChain('net', numThreads=0, frameBudget=-1)

    def getShardPopLimits(self):
        return (100, 200, -1)

    def setLocationCode(self, locationCode):
        if locationCode != self.locationCode:
            self.locationCode = locationCode
            self.locationCodeChanged = time.time()

    def delayedErrorCheck(self, task):
        if self.errorAccumulatorBuffer:
            buffer = self.errorAccumulatorBuffer
            self.errorAccumulatorBuffer = ''
            self.notify.error('\nAccumulated Phase Errors!:\n %s' % buffer)
        return task.cont

    def loaderPhaseChecker(self, path, loaderOptions):
        if 'audio/' in path:
            return 1
        file = Filename(path)
        if not file.getExtension():
            file.setExtension('bam')
        mp = getModelPath()
        path = mp.findFile(file).cStr()
        if not path:
            return
        match = re.match('.*phase_([^/]+)/', path)
        if not match:
            if 'dmodels' in path:
                return
            else:
                self.errorAccumulatorBuffer += 'file not in phase (%s, %s)\n' % (file, path)
                return
        basePhase = float(match.groups()[0])
        if not launcher.getPhaseComplete(basePhase):
            self.errorAccumulatorBuffer += 'phase is not loaded for this model %s\n' % path
        model = loader.loader.loadSync(Filename(path), loaderOptions)
        if model:
            model = NodePath(model)
            for tex in model.findAllTextures():
                texPath = tex.getFullpath().cStr()
                match = re.match('.*phase_([^/]+)/', texPath)
                if match:
                    texPhase = float(match.groups()[0])
                    if texPhase > basePhase:
                        self.errorAccumulatorBuffer += 'texture phase is higher than the models (%s, %s)\n' % (path, texPath)

    def getRepository(self):
        return self.cr

    def openMainWindow(self, *args, **kw):
        result = ShowBase.openMainWindow(self, *args, **kw)
        if result:
            self.wantEnviroDR = not self.win.getGsg().isHardware() or ConfigVariableBool('want-background-region', True).getValue()
        return result

    def run(self):
        try:
            taskMgr.run()
        except SystemExit:
            self.notify.info('Normal exit.')
            self.destroy()
            raise
        except:
            self.notify.warning('Handling Python exception.')
            if getattr(self, 'cr', None):
                if self.cr.timeManager:
                    from otp.otpbase import OTPGlobals
                    self.cr.timeManager.setDisconnectReason(OTPGlobals.DisconnectPythonError)
                    self.cr.timeManager.setExceptionInfo()
                self.cr.sendDisconnect()
            self.notify.info('Exception exit.\n')
            self.destroy()
            import traceback
            traceback.print_exc()


@magicWord(category=CATEGORY_USER)
def oobe():
    """
    Toggle the 'out of body experience' view.
    """
    base.oobe()

@magicWord(category=CATEGORY_ADMINISTRATOR)
def oobeCull():
    """
    Toggle the 'out of body experience' view with culling debugging.
    """
    base.oobeCull()

@magicWord(category=CATEGORY_USER)
def wire():
    """
    Toggle the 'wireframe' view.
    """
    base.toggleWireframe()

@magicWord(category=CATEGORY_MODERATOR)
def idNametags():
    """
    Display avatar IDs inside nametags.
    """
    messenger.send('nameTagShowAvId')

@magicWord(category=CATEGORY_MODERATOR)
def nameNametags():
    """
    Display only avatar names inside nametags.
    """
    messenger.send('nameTagShowName')

@magicWord(category=CATEGORY_MODERATOR)
def a2d():
    """
    Toggle aspect2d.
    """
    if aspect2d.isHidden():
        aspect2d.show()
    else:
        aspect2d.hide()

@magicWord(category=CATEGORY_MODERATOR)
def placer():
    """
    Toggle the camera placer.
    """
    base.camera.place()

@magicWord(category=CATEGORY_MODERATOR)
def explorer():
    """
    Toggle the scene graph explorer.
    """
    base.render.explore()


@magicWord(category=CATEGORY_MODERATOR)
def neglect():
    """
    toggle the neglection of network updates on the invoker's client.
    """
    if base.cr.networkPlugPulled():
        base.cr.restoreNetworkPlug()
        return 'You are no longer neglecting network updates.'
    else:
        base.cr.pullNetworkPlug()
        return 'You are now neglecting network updates.'


@magicWord(category=CATEGORY_USER, types=[float, float, float, float])
def backgroundColor(r=None, g=1, b=1, a=1):
    """
    set the background color. Specify no arguments for the default background
    color.
    """
    if r is None:
        r, g, b, a = OTPGlobals.DefaultBackgroundColor
    base.setBackgroundColor(Vec4(r, g, b, a))
    return 'The background color has been changed.'
