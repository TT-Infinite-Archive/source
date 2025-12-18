from panda3d.core import ConfigVariableBool, ConfigVariableInt, ConfigVariableString, HTTPChannel, loadPrcFile, loadPrcFileData
import builtins


builtins.process = 'ai'


# Temporary hack patch:
from direct.extensions_native import HTTPChannel_extensions


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
if __debug__: parser.add_argument('config', nargs='*', default=['config/general.prc', 'config/distribution/dev.prc'], help="PRC file(s) to load.")
builtins.args = parser.parse_known_args()[0]

if __debug__:
    for prc in args.config:
        loadPrcFile(prc)

localconfig = ''
if args.base_channel: localconfig += 'air-base-channel %s\n' % args.base_channel
if args.max_channels: localconfig += 'air-channel-allocation %s\n' % args.max_channels
if args.stateserver: localconfig += 'air-stateserver %s\n' % args.stateserver
if args.district_name: localconfig += 'district-name %s\n' % args.district_name
if args.astron_ip: localconfig += 'air-connect %s\n' % args.astron_ip
if args.eventlogger_ip: localconfig += 'eventlog-host %s\n' % args.eventlogger_ip
if args.mongodb_ip: localconfig += 'mongodb-url %s\n' % args.mongodb_ip

loadPrcFileData('Command-line', localconfig)

from otp.ai.AIBaseGlobal import *

# We need to disable garbage collection during the AI startup process or we will
# crash due to some bug im looking into
import gc
gc.disable()

from toontown.ai.ToontownAIRepository import ToontownAIRepository
simbase.air = ToontownAIRepository(ConfigVariableInt('air-base-channel', 401000000).getValue(),
                                   ConfigVariableInt('air-stateserver', 4002).getValue(),
                                   ConfigVariableString('district-name', 'Devhaven').getValue())
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
