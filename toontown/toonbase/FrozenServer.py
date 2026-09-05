"""
Entry point for a compiled build of the Toontown Infinite server.
"""
import sys

from toontown.toonbase import ConfigFiles
from toontown.toonbase.FrozenCommon import DISTRIBUTION, prepare

# A hosted server is the live distribution with host-server.prc in place of
# live-server.prc:
prepare(ConfigFiles.server(DISTRIBUTION, ConfigFiles.HOST))

if '--uberdog' in sys.argv:
    import toontown.uberdog.ServiceStart
elif '--ai' in sys.argv:
    import toontown.ai.ServiceStart
elif '--dedicated' in sys.argv:
    import toontown.dedicated.DedicatedStart
else:
    sys.exit('Pass --dedicated to run a server, or --ai or --uberdog to run '
             'one service of one.')
