import builtins


builtins.process = 'dedicated'

from panda3d.core import ConfigVariableString

builtins.version = ConfigVariableString('server-version', 'n/a').getValue()

if __debug__:
    from panda3d.core import loadPrcFile

    loadPrcFile('config/general.prc')
    loadPrcFile('config/distribution/dev.prc')

from otp.ai.AIBaseGlobal import *

from .DedicatedServer import DedicatedServer
simbase.dedi = DedicatedServer()
simbase.dedi.request('Start')
simbase.run()