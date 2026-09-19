import base64
import json
import os

from direct.directnotify import DirectNotifyGlobal

BYTES_TAG = '_bytes_b64'


def encodeBytes(obj):
    if not isinstance(obj, bytes):
        raise TypeError('%r is not JSON serializable' % (obj,))
    return {BYTES_TAG: base64.b64encode(obj).decode('ascii')}


def decodeBytes(obj):
    if len(obj) == 1 and BYTES_TAG in obj:
        return base64.b64decode(obj[BYTES_TAG])
    return obj


class BackupManager:
    notify = DirectNotifyGlobal.directNotify.newCategory('BackupManager')

    def __init__(self, filepath='backups/', extension='.json'):
        self.filepath = filepath
        self.extension = extension

    def getFileName(self, category, info):
        filename = os.path.join(self.filepath, category) + '/'
        for i in info:
            filename += str(i) + '_'
        return filename[:-1] + self.extension

    def load(self, category, info, default=None):
        filename = self.getFileName(category, info)
        if (not os.path.exists(filename)) or (not os.path.getsize(filename)):
            return default

        try:
            with open(filename, 'r') as f:
                return json.load(f, object_hook=decodeBytes)
        except (OSError, ValueError) as error:
            # a single unreadable file would otherwise take the whole district
            # down and keep doing it on every restart. The next save replaces it!
            self.notify.warning(
                'Ignoring unreadable backup %s: %s' % (filename, error))
            return default

    def save(self, category, info, data):
        filename = self.getFileName(category, info)
        partial = filename + '.partial'

        try:
            filepath = os.path.join(self.filepath, category)
            if not os.path.exists(filepath):
                os.makedirs(filepath)

            with open(partial, 'w') as f:
                json.dump(data, f, default=encodeBytes)
                f.flush()
                os.fsync(f.fileno())

            os.replace(partial, filename)
        except (OSError, TypeError, ValueError) as error:
            # a bad value would otherwise kill whatever task asked for the save,
            # mid-transition. The last good backup stands until the next save.
            self.notify.warning(
                'Failed to save backup %s: %s' % (filename, error))
            if os.path.exists(partial):
                os.remove(partial)
