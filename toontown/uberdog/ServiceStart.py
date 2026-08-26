from panda3d.core import ConfigVariableInt, ConfigVariableString, HTTPChannel, loadPrcFile, loadPrcFileData
import builtins


builtins.process = 'uberdog'


from direct.showbase import PythonUtil

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--base-channel', help='The base channel that the server may use.')
parser.add_argument('--max-channels', help='The number of channels the server may use.')
parser.add_argument('--stateserver', help="The control channel of this UD's designated State Server.")
parser.add_argument('--astron-ip', help="The IP address of the Astron Message Director to connect to.")
parser.add_argument('--eventlogger-ip', help="The IP address of the Astron Event Logger to log to.")
parser.add_argument('--mongodb-ip', help="The IP address of the MongoDB server to connect to.")
parser.add_argument('--singleplayer', help="If passed, the server will start in singleplayer mode.", action='store_true')
parser.add_argument('--cheats', help="If passed, the server will start in with cheats enabled.", action='store_true')
parser.add_argument('--accountdb', choices=('developer', 'offline', 'production'),
                    help="'developer' and 'offline' both take login screen credentials and register an unknown \
                    username on the spot, granting access level 500 and 100 respectively. 'production' \
                    skips the login screen and redeems the launcher's launch token against the website. \
                    Overrides accountdb-type from the PRC files.")
if __debug__: parser.add_argument('config', nargs='*', default=['config/general.prc', 'config/server.prc', 'config/distribution/dev.prc', 'config/distribution/dev-server.prc'], help="PRC file(s) to load.")
builtins.args = parser.parse_known_args()[0]

if __debug__:
    for prc in args.config:
        loadPrcFile(prc)

from toontown.server import Deployment
Deployment.load()

localconfig = ''
if args.base_channel: localconfig += 'air-base-channel %s\n' % args.base_channel
if args.max_channels: localconfig += 'air-channel-allocation %s\n' % args.max_channels
if args.stateserver: localconfig += 'air-stateserver %s\n' % args.stateserver
if args.astron_ip: localconfig += 'air-connect %s\n' % args.astron_ip
if args.eventlogger_ip: localconfig += 'eventlog-host %s\n' % args.eventlogger_ip
if args.mongodb_ip: localconfig += 'mongodb-url %s\n' % args.mongodb_ip
if args.singleplayer: localconfig += 'want-singleplayer #t\n'
if args.cheats: localconfig += 'want-cheats #f\n'
if args.accountdb: localconfig += 'accountdb-type %s\n' % args.accountdb
loadPrcFileData('Command-line', localconfig)


from otp.ai.AIBaseGlobal import *

from toontown.uberdog.ToontownUberRepository import ToontownUberRepository
simbase.air = ToontownUberRepository(ConfigVariableInt('air-base-channel', 400000000).getValue(),
                                     ConfigVariableInt('air-stateserver', 4002).getValue())
host = ConfigVariableString('air-connect', '127.0.0.1').getValue()
port = 7010
if ':' in host:
    host, port = host.split(':', 1)
    port = int(port)
simbase.air.connect(host, port)

try:
    simbase.run()
except SystemExit:
    raise
except Exception:
    import traceback
    info = traceback.format_exc()
    simbase.air.writeServerEvent('uberdog-exception', simbase.air.getAvatarIdFromSender(), simbase.air.getAccountIdFromSender(), info)
    raise
