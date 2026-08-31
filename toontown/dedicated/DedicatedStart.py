"""
Entry point for a server with no client attached.
"""
from panda3d.core import ConfigVariableString, loadPrcFile, loadPrcFileData
import argparse
import builtins
import signal
import sys


builtins.process = 'dedicated'


parser = argparse.ArgumentParser(
    prog='Toontown Infinite Server',
    description='Run a Toontown Infinite server without a client.')
parser.add_argument(
    '--port', type=int, default=None,
    help='The port players connect to. Defaults to 7000.')
parser.add_argument(
    '--district-name', default=None,
    help='What the district is called.')
parser.add_argument(
    '--mongodb-url', default=None,
    help='An existing database to use, e.g. mongodb://127.0.0.1:27017/game. '
         'Without this a mongod is started alongside the server.')
parser.add_argument(
    '--settings-file', default=None,
    help='Where to write the JSON settings the launcher reads. Relative to the '
         'install root.')
if __debug__:
    parser.add_argument(
        'config', nargs='*',
        default=['config/general.prc', 'config/server.prc',
                 'config/distribution/dev.prc',
                 'config/distribution/dev-server.prc'],
        help='PRC file(s) to load.')

builtins.args = parser.parse_known_args()[0]
childConfig = ()

if __debug__:
    childConfig = tuple(args.config) + ('config/distribution/host-server.prc',)

    for prc in childConfig:
        loadPrcFile(prc)

if args.settings_file:
    loadPrcFileData('Command-line', 'host-settings-file %s\n' % args.settings_file)

builtins.version = ConfigVariableString('server-version', 'n/a').getValue()

from toontown.server import Deployment
Deployment.load()

from otp.ai.AIBaseGlobal import *

from toontown.server.ServerGlobals import DefaultDistrict, DefaultPort
from toontown.toonbase import ServerSettingsGlobals

# The command line wins, then server-settings.json, then the defaults:
port = args.port or int(
    serverSettings.get(ServerSettingsGlobals.HostPort, DefaultPort))
districtName = args.district_name or serverSettings.get(
    ServerSettingsGlobals.DistrictName, DefaultDistrict)

serverSettings[ServerSettingsGlobals.HostPort] = port
serverSettings[ServerSettingsGlobals.DistrictName] = districtName

from .DedicatedServer import DedicatedServer

simbase.dedi = DedicatedServer(
    port=port, districtName=districtName, mongoUrl=args.mongodb_url,
    config=childConfig)


def shutdown(signum, frame):
    """
    Take the stack down, so a stopped service leaves nothing behind.
    """
    simbase.dedi.killThreads()
    sys.exit(0)

signal.signal(signal.SIGTERM, shutdown)
signal.signal(signal.SIGINT, shutdown)

simbase.dedi.request('Start')
simbase.run()
