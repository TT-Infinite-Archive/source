"""
Deployment settings reach a server process through the environment.
"""
import os

from panda3d.core import loadPrcFileData

SETTINGS = {
    'ACCOUNT_SERVICE_SECRET': 'account-service-secret',
    'DISTRICT_NAME': 'district-name',
    'BASE_CHANNEL': 'air-base-channel',
    'ACCOUNTDB_TYPE': 'accountdb-type',
    'ACCOUNT_SERVICE_URL': 'account-service-url',
    'ASTRON_CONNECT': 'air-connect',
    'CHANNEL_ALLOCATION': 'air-channel-allocation',
    'DRAIN_GRACE_SECONDS': 'drain-grace-seconds',
    'EVENTLOG_HOST': 'eventlog-host',
    'MONGODB_URL': 'mongodb-url',
    'WANT_DRAIN_ON_STOP': 'want-drain-on-stop',
}

def load():
    data = ''

    for variable, setting in sorted(SETTINGS.items()):
        value = os.environ.get(variable)
        if value:
            data += '%s %s\n' % (setting, value)

    if data:
        loadPrcFileData('Deployment', data)
