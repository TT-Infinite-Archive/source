from panda3d.core import ConfigVariableString, loadPrcFile
import builtins


builtins.process = 'dedicated'


builtins.version = ConfigVariableString('server-version', 'n/a').getValue()

if __debug__:

    loadPrcFile('config/general.prc')
    loadPrcFile('config/server.prc')
    loadPrcFile('config/distribution/dev.prc')
    loadPrcFile('config/distribution/dev-server.prc')

from toontown.server import Deployment
Deployment.load()

from otp.ai.AIBaseGlobal import *

from .DedicatedServer import DedicatedServer
simbase.dedi = DedicatedServer()
simbase.dedi.request('Start')
simbase.run()