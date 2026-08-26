import json
import os

from direct.directnotify import DirectNotifyGlobal


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
                return json.load(f)
        except (OSError, ValueError) as error:
            # a single unreadable file would otherwise take the whole district
            # down and keep doing it on every restart. The next save replaces it!
            self.notify.warning(
                'Ignoring unreadable backup %s: %s' % (filename, error))
            return default

    def save(self, category, info, data):
        filepath = os.path.join(self.filepath, category)
        if not os.path.exists(filepath):
            os.makedirs(filepath)
        filename = self.getFileName(category, info)
        partial = filename + '.partial'

        with open(partial, 'w') as f:
            json.dump(data, f)
            f.flush()
            os.fsync(f.fileno())

        os.replace(partial, filename)
