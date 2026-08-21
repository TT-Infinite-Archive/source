from panda3d.core import ConfigVariableList
import builtins
import os
import sys


from toontown.toonbase import TTLocalizer, ToontownGlobals

LogsPath = os.path.join(ToontownGlobals.CurrentDirectory, 'logs')
print(str(LogsPath))
if sys.platform == 'android':
    UberdogTarget = []
    AITarget = []
elif hasattr(builtins, '__nirai__'):
    UberdogTarget = [__nirai__.filename, '--uberdog']
    AITarget = [__nirai__.filename, '--ai']
else:
    PythonPath = sys.executable
    UberdogTarget = [PythonPath, '-m', 'toontown.uberdog.ServiceStart']
    AITarget = [PythonPath, '-m', 'toontown.ai.ServiceStart']

Processes = [
    [
        ['mongod'],
        'astron',
        TTLocalizer.MongoDB,
        'shutting down',
        'Waiting for connections'
    ],
    [
        [os.path.join('.', 'astrond')],
        'astron',
        TTLocalizer.Astron,
        'FATAL',
        'Opened new log.'
    ],
    [
        UberdogTarget + [
            '--base-channel', '1000000', '--max-channels', '9999',
            '--stateserver', '4002'
        ],
        None,
        TTLocalizer.Uberdog,
        'Failed to connect!',
        'Done.'
    ],
    [
        AITarget + [
            '--base-channel', '401000000', '--max-channels', '999999',
            '--stateserver', '4002', '--district-name', 'Toontown'
        ],
        None,
        TTLocalizer.District,
        'Failed to connect!',
        'Done.'
    ]
]

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


def getAstronConfig(dcFileNames=('dclass/vanilla.dc',), version='dev', server=0):
    config = AstronConfig.copy()
    config['general']['eventlogger'] = '127.0.0.1:7020'
    config['messagedirector']['bind'] = '127.0.0.1:7010'
    config['roles'][0]['bind'] = '0.0.0.0:7000'
    config['roles'][2]['backend']['server'] = 'mongodb://127.0.0.1:7030/game'
    config['roles'][4]['bind'] = '127.0.0.1:7020'
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
