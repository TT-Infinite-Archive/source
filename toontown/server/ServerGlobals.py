from panda3d.core import ConfigVariableList
import copy
import os
import sys


from toontown.toonbase import ServerSettingsGlobals, TTLocalizer, ToontownGlobals

LogsPath = os.path.join(ToontownGlobals.CurrentDirectory, 'logs')
print(str(LogsPath))
if sys.platform == 'android':
    UberdogTarget = []
    AITarget = []
elif getattr(sys, 'frozen', False):
    # The server is its own binary, and an optional download. A player who
    # only joins other people's servers never receives it
    ServerBinary = os.path.join(
        ToontownGlobals.CurrentDirectory, 'bin', 'server',
        'Toontown Infinite Server' + ('.exe' if sys.platform == 'win32' else ''))

    UberdogTarget = [ServerBinary, '--uberdog']
    AITarget = [ServerBinary, '--ai']
else:
    PythonPath = sys.executable
    UberdogTarget = [PythonPath, '-m', 'toontown.uberdog.ServiceStart']
    AITarget = [PythonPath, '-m', 'toontown.ai.ServiceStart']

# astrond is committed per platform rather than built, so the name carries the
# platform with it
AstronBinary = 'astrond-%s%s' % (sys.platform, '.exe' if sys.platform == 'win32' else '')

# The ports a hosted server stack listens on. Only the client agent's is worth
# changing since it's the one players connect to, and the one a router has to
# forward:
DefaultPort = 7000
MessageDirectorPort = 7010
EventLoggerPort = 7020
MongoPort = 7030

DefaultDistrict = 'Kookyboro'


def getHostPort():
    """
    The port a hosted server listens on.
    """
    try:
        return int(serverSettings.get(
            ServerSettingsGlobals.HostPort, DefaultPort))
    except (NameError, TypeError, ValueError):
        return DefaultPort


def getDistrictName():
    try:
        return serverSettings.get(
            ServerSettingsGlobals.DistrictName, DefaultDistrict) or DefaultDistrict
    except NameError:
        return DefaultDistrict


def getProcesses(districtName=DefaultDistrict, mongo=True, config=()):
    """
    The stack a host starts, in the order it has to come up.

    `mongo` is off when the host already has a database to point at, which a
    VPS usually does; the rest of the stack is the same either way.

    `config` is the PRC files the district and the UberDOG should load. It only
    applies to a source checkout: a compiled server reads its own config on the
    way in and would take these as stray arguments. Without it, a child of a
    source run falls back to the development config rather than the host's.
    """
    # ServiceStart takes its PRC files as trailing positional arguments, and
    # only offers them under __debug__ -- the same condition as `not frozen`.
    settings = [] if getattr(sys, 'frozen', False) else list(config)

    processes = []

    if mongo:
        processes.append([
            ['mongod'],
            'astron',
            TTLocalizer.MongoDB,
            'shutting down',
            'Waiting for connections'
        ])

    return processes + [
        [
            [os.path.join('.', AstronBinary)],
            'astron',
            TTLocalizer.Astron,
            'FATAL',
            'Opened new log.'
        ],
        [
            UberdogTarget + [
                '--base-channel', '1000000', '--max-channels', '9999',
                '--stateserver', '4002'
            ] + settings,
            None,
            TTLocalizer.Uberdog,
            'Failed to connect!',
            'Done.'
        ],
        [
            AITarget + [
                '--base-channel', '401000000', '--max-channels', '999999',
                '--stateserver', '4002', '--district-name', districtName
            ] + settings,
            None,
            TTLocalizer.District,
            'Failed to connect!',
            'Done.'
        ]
    ]


# The default stack, for hosts that never rename the district:
Processes = getProcesses()

AstronConfig = {
    'general': {
        'eventlogger': '127.0.0.1:7021',
        'dc_files': []
    },
    'uberdogs': [],
    'messagedirector': {
        'bind': '127.0.0.1:7011'
    },
    'roles': [
        {
            'type': 'clientagent',
            'bind': '127.0.0.1:7001',
            'version': None,
            'client': {
                'relocate': True,
                'add_interest': 'enabled'
            },
            'channels': {
                'min': 2000000000,
                'max': 2000999999
            }
        },
        {
            'type': 'stateserver',
            'control': 4002
        },
        {
            'type': 'database',
            'control': 4003,
            'generate': {
                'min': 100000000,
                'max': 399999999
            },
            'backend': {
                'type': 'mongodb',
                'server': 'mongodb://127.0.0.1:7031/game'
            }
        },
        {
            'type': 'dbss',
            'database': 4003,
            'ranges': [
                {
                    'min': 100000000,
                    'max': 399999999
                }
            ]
        },
        {
            'type': 'eventlogger',
            'bind': '127.0.0.1:7021',
            'output': 'logs/events-%y%m%d_%H%M%S.log'
        }
    ]
}


def getAstronConfig(dcFileNames=('dclass/vanilla.dc',), version='dev', server=0,
                    port=DefaultPort, mongoUrl=None):
    # Use a deep copy so each call gets separate config data.
    config = copy.deepcopy(AstronConfig)
    config['general']['eventlogger'] = '127.0.0.1:%d' % EventLoggerPort
    config['messagedirector']['bind'] = '127.0.0.1:%d' % MessageDirectorPort
    # The only role bound off the loopback: this is the port players reach:
    config['roles'][0]['bind'] = '0.0.0.0:%d' % port
    config['roles'][2]['backend']['server'] = (
        mongoUrl or 'mongodb://127.0.0.1:%d/game' % MongoPort)
    config['roles'][4]['bind'] = '127.0.0.1:%d' % EventLoggerPort
    for dcFileName in dcFileNames:
        config['general']['dc_files'].append(dcFileName)
    config['roles'][0]['version'] = version
    globalObjectDefs = ConfigVariableList('generate-global-object')
    for globalObjectDef in globalObjectDefs:
        doId, dcname = globalObjectDef.split(' ', 1)
        doId = int(doId)
        anonymous = False
        if dcname == 'ClientServicesManager':
            anonymous = True
        config['uberdogs'].append({
            'class': dcname,
            'id': doId,
            'anonymous': anonymous
        })
    return config
