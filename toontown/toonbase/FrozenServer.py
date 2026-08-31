"""
Entry point for a compiled build of the Toontown Infinite server.
"""
from panda3d.core import loadPrcFile
import sys

from toontown.toonbase.FrozenCommon import prepare

prepare()

loadPrcFile('config/server.prc')
loadPrcFile('config/distribution/host-server.prc')

if '--uberdog' in sys.argv:
    import toontown.uberdog.ServiceStart
elif '--ai' in sys.argv:
    import toontown.ai.ServiceStart
elif '--dedicated' in sys.argv:
    import toontown.dedicated.DedicatedStart
else:
    sys.exit('Pass --dedicated to run a server, or --ai or --uberdog to run '
             'one service of one.')
