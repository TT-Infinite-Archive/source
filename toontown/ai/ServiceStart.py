from panda3d.core import ConfigVariableBool, ConfigVariableInt, ConfigVariableString, HTTPChannel, loadPrcFileData
import builtins

from toontown.toonbase import ConfigFiles


builtins.process = 'ai'


from direct.showbase import PythonUtil

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--base-channel', help='The base channel that the server may use.')
parser.add_argument('--max-channels', help='The number of channels the server may use.')
parser.add_argument('--stateserver', help="The control channel of this AI's designated State Server.")
parser.add_argument('--district-name', help="What this AI Server's district will be named.")
parser.add_argument('--astron-ip', help="The IP address of the Astron Message Director to connect to.")
parser.add_argument('--eventlogger-ip', help="The IP address of the Astron Event Logger to log to.")
parser.add_argument('--mongodb-ip', help="The IP address of the MongoDB server to connect to.")
parser.add_argument('--gateway', action='store_true',
                    help="Open the socket to the website, so the district asks \
                    for its identity and registers itself there. dev-server.prc \
                    leaves it off, since a developer with no website running does \
                    not want a process retrying a connection forever. \
                    Overrides want-game-gateway from the PRC files.")
if __debug__:
    parser.add_argument('--distribution', choices=ConfigFiles.CHOICES, default=ConfigFiles.DEV,
                        help="Which distribution's config to load. Defaults to dev.")
    parser.add_argument('config', nargs='*',
                        help="Extra PRC file(s), loaded after the distribution's own.")
builtins.args = parser.parse_known_args()[0]

if __debug__:
    ConfigFiles.load(ConfigFiles.serverFor(args.distribution) + tuple(args.config))

from toontown.server import Deployment
Deployment.load()

localconfig = ''
if args.base_channel: localconfig += 'air-base-channel %s\n' % args.base_channel
if args.max_channels: localconfig += 'air-channel-allocation %s\n' % args.max_channels
if args.stateserver: localconfig += 'air-stateserver %s\n' % args.stateserver
if args.district_name: localconfig += 'district-name %s\n' % args.district_name
if args.astron_ip: localconfig += 'air-connect %s\n' % args.astron_ip
if args.eventlogger_ip: localconfig += 'eventlog-host %s\n' % args.eventlogger_ip
if args.mongodb_ip: localconfig += 'mongodb-url %s\n' % args.mongodb_ip
if args.gateway: localconfig += 'want-game-gateway #t\n'

loadPrcFileData('Command-line', localconfig)

from otp.ai.AIBaseGlobal import *

# We need to disable garbage collection during the AI startup process or we will
# crash due to some bug im looking into
import gc
gc.disable()

# Ask the website for this district's identity before starting anything else
#
#
# If there is no gateway (development or private servers) or the website is down, 
# fallback to config values
from toontown.web import GatewaySocket

gateway = GatewaySocket.openSocket()
if gateway:
    ready = gateway.waitForReady(ConfigVariableInt('gateway-ready-timeout', 15).getValue())
    if ready:
        settings = dict(ready.get('config') or {})
        if ready.get('name'):
            settings.setdefault('district-name', ready['name'])

        loadPrcFileData('Gateway', ''.join(
            '%s %s\n' % (variable, value) for variable, value in sorted(settings.items())))

        Deployment.load()
        loadPrcFileData('Command-line', localconfig)

from toontown.ai.ToontownAIRepository import ToontownAIRepository
simbase.air = ToontownAIRepository(ConfigVariableInt('air-base-channel', 401000000).getValue(),
                                   ConfigVariableInt('air-stateserver', 4002).getValue(),
                                   ConfigVariableString('district-name', 'Devhaven').getValue(),
                                   gateway=gateway)
host = ConfigVariableString('air-connect', '127.0.0.1').getValue()
port = 7010
if ':' in host:
    host, port = host.split(':', 1)
    port = int(port)
simbase.air.connect(host, port)

try:
    if ConfigVariableBool('want-leak-graph-ai', False).getValue():
        from toontown.debug import LeakGraph
        LeakGraph.outputLeaking()
    simbase.run()
except SystemExit:
    raise
except Exception:
    import traceback
    info = traceback.format_exc()
    simbase.air.writeServerEvent('ai-exception', simbase.air.getAvatarIdFromSender(), simbase.air.getAccountIdFromSender(), info)
    raise
