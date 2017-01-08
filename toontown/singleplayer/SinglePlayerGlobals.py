from toontown.toonbase import TTLocalizer
import sys, os

LogsPath = os.path.join(os.getcwd(), 'logs')

if not os.path.exists(LogsPath):
    os.makedirs(LogsPath)

try:
    PythonPath = os.path.join(os.getcwd(), builtFile)
    LogsPath = os.path.join(os.getcwd(), 'logs')
    print('logs:', LogsPath)
except:
    if sys.platform.startswith('linux'):
        PythonPath = '/usr/bin/python2'
    else:
        PythonPath = os.path.join(os.path.dirname(sys.path[1]), 'python')

Processes = [
    [
        ['mongod'],
        'astron',
        TTLocalizer.MongoDB,
        'shutting down',
        'waiting for connections'
    ],
    [
        ['astrond'],
        'astron',
        TTLocalizer.Astron,
        'FATAL',
        'Opened new log.'
    ],
    [
        [PythonPath, '-m', 'toontown.uberdog.ServiceStart',
        '--base-channel', '1000000', '--max-channels', '9999', '--stateserver', '4002'],
        None,
        TTLocalizer.Uberdog,
        'Failed to connect!',
        'Done.'
    ],
    [
        [PythonPath, '-m', 'toontown.ai.ServiceStart',
        '--base-channel', '401000000', '--max-channels', '999999', '--stateserver', '4002',
        '--district-name', 'Toontown'],
        None,
        TTLocalizer.District,
        'Failed to connect!',
        'Done.'
    ]
]