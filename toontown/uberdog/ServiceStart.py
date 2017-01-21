import __builtin__


__builtin__.process = 'uberdog'


# Temporary hack patch:
__builtin__.__dict__.update(__import__('pandac.PandaModules', fromlist=['*']).__dict__)
from direct.extensions_native import HTTPChannel_extensions


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
parser.add_argument('config', nargs='*', default=['config/general.prc', 'config/distribution/dev.prc'], help="PRC file(s) to load.")
__builtin__.args = parser.parse_known_args()[0]

for prc in args.config:
    loadPrcFile(prc)

localconfig = ''
if args.base_channel: localconfig += 'air-base-channel %s\n' % args.base_channel
if args.max_channels: localconfig += 'air-channel-allocation %s\n' % args.max_channels
if args.stateserver: localconfig += 'air-stateserver %s\n' % args.stateserver
if args.astron_ip: localconfig += 'air-connect %s\n' % args.astron_ip
if args.eventlogger_ip: localconfig += 'eventlog-host %s\n' % args.eventlogger_ip
if args.mongodb_ip: localconfig += 'mongodb-url %s\n' % args.mongodb_ip
if args.singleplayer: localconfig += 'want-singleplayer #t\n'
loadPrcFileData('Command-line', localconfig)


from otp.ai.AIBaseGlobal import *

from toontown.uberdog.ToontownUberRepository import ToontownUberRepository
simbase.air = ToontownUberRepository(config.GetInt('air-base-channel', 400000000),
                                     config.GetInt('air-stateserver', 4002))
host = config.GetString('air-connect', '127.0.0.1')
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
