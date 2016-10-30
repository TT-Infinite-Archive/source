from toontown.toonbase import TTLocalizer
import sys, os

try:
    PythonPath = os.path.join(os.getcwd(), builtFile)
except:
    PythonPath = os.path.join(os.getcwd(), 'python')

Processes = [
    [
        ['mongod', '--dbpath', 'databases'],
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
        '--base-channel', '1000000', '--max-channels', '9999', '--stateserver', '4002',
        '--astron-ip', '127.0.0.1:7100', '--eventlogger-ip', '127.0.0.1:7198'],
        None,
        TTLocalizer.Uberdog,
        'Failed to connect!',
        'Done.'
    ],
    [
        [PythonPath, '-m', 'toontown.ai.ServiceStart',
        '--base-channel', '401000000', '--max-channels', '999999', '--stateserver', '4002',
        '--astron-ip', '127.0.0.1:7100', '--eventlogger-ip', '127.0.0.1:7198',
        '--district-name', 'Toontown'],
        None,
        TTLocalizer.District,
        'Failed to connect!',
        'Done.'
    ]
]