"""
Entry point for a compiled build of Toontown Infinite.
"""
from panda3d.core import Filename, VirtualFileSystem, loadPrcFile
import os
import sys

sys.frozen = True

sys.executable = os.path.abspath(sys.argv[0])

INSTALL = os.path.dirname(sys.executable)

os.chdir(INSTALL)

DISTRIBUTION = 'live'

PHASES = ('3', '3.5', '4', '5', '5.5', '6', '7', '8', '9', '10', '11', '12', '13')

vfs = VirtualFileSystem.getGlobalPtr()

for phase in PHASES:
    multifile = Filename.fromOsSpecific(os.path.join(INSTALL, 'resources', 'phase_%s.mf' % phase))
    if not vfs.mount(multifile, '/', 0):
        sys.exit('Failed to mount %s.' % multifile)

# ClientStart and both ServiceStarts load their config only under __debug__.
loadPrcFile('config/general.prc')
loadPrcFile('config/distribution/%s.prc' % DISTRIBUTION)

server = '--ai' in sys.argv or '--uberdog' in sys.argv

if server:
    loadPrcFile('config/server.prc')
    loadPrcFile('config/distribution/host-server.prc')

if '--uberdog' in sys.argv:
    import toontown.uberdog.ServiceStart
elif '--ai' in sys.argv:
    import toontown.ai.ServiceStart
else:
    import toontown.toonbase.ClientStart
