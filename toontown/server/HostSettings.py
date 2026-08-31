"""
A hosted server's settings & status, written where the launcher can read it.
"""
import json
import os
import time

from direct.directnotify import DirectNotifyGlobal
from panda3d.core import ConfigVariableString

from toontown.server import ServerGlobals
from toontown.toon.DistributedToonAI import DistributedToonAI


def settingsPath():
    path = ConfigVariableString('host-settings-file', '').getValue()

    return os.path.abspath(path) if path else None


class HostSettingsWriter:
    """
    Keeps the JSON settings file current as the district's own objects report in.
    """

    notify = DirectNotifyGlobal.directNotify.newCategory('HostSettingsWriter')

    # Population moves on every login and logout, so changes are combined
    # rather than written one at a time:
    FLUSH_DELAY = 1.0

    def __init__(self, air, path):
        self.air = air
        self.path = path
        self.status = {}
        self.pending = False
        self.startedAt = int(time.time())

    def update(self, status):
        """
        Folds in one of the partial updates the district's objects send.
        """
        self.status.update(status)

        if self.pending:
            return

        self.pending = True
        taskMgr.doMethodLater(
            self.FLUSH_DELAY, self.__flushTask, 'HostSettingsWriter-flush')

    def __flushTask(self, task):
        self.pending = False
        self.flush()
        return task.done

    def players(self):
        """
        Who is on the server right now, newest last.
        """
        found = [
            {'id': do.doId, 'name': do.getName()}
            for do in list(self.air.doId2do.values())
            if isinstance(do, DistributedToonAI) and do.isPlayerControlled()
        ]

        return sorted(found, key=lambda player: player['id'])

    def flush(self):
        players = self.players()

        payload = {
            'district': self.status.get('name') or self.air.districtName,
            'available': bool(self.status.get('available', True)),
            'population': len(players),
            'players': players,
            'port': ServerGlobals.getHostPort(),
            'invasion': self.status.get('invasion'),
            'startedAt': self.status.get('created', self.startedAt),
            'updatedAt': int(time.time()),
        }

        # Written whole or not at all: the launcher polls this file and would
        # otherwise catch it half-written:
        staging = '%s.part' % self.path

        try:
            with open(staging, 'w') as f:
                json.dump(payload, f)

            os.replace(staging, self.path)
        except OSError as error:
            self.notify.warning('Could not write %s: %s' % (self.path, error))

            try:
                os.remove(staging)
            except OSError:
                pass

    def stop(self):
        taskMgr.remove('HostSettingsWriter-flush')
        self.pending = False

        # Say so, rather than leaving a status that claims the server is up:
        self.status['available'] = False
        self.flush()
