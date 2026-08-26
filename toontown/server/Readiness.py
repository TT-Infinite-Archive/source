"""
A file a container healthcheck can look for once startup has finished.
"""
import os

from direct.directnotify import DirectNotifyGlobal

notify = DirectNotifyGlobal.directNotify.newCategory('Readiness')


def markReady():
    path = os.environ.get('READY_FILE')
    if not path:
        return

    try:
        with open(path, 'w') as readyFile:
            readyFile.write('ready\n')
    except OSError as error:
        # A healthcheck that cannot see the file will restart the container
        notify.warning('Could not write %s: %s' % (path, error))
