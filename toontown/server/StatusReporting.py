"""
A district's status, gathered once and handed over.

The website fetches over the district's gateway socket, 
and a self-hosting player's launcher, as JSON next to the install. 
"""
import json
import os
import time

from direct.directnotify import DirectNotifyGlobal
from direct.showbase.DirectObject import DirectObject

from toontown.server import ServerGlobals
from toontown.toon.DistributedToonAI import DistributedToonAI


class StatusSink:
    """
    Somewhere a district's status goes.
    """

    notify = DirectNotifyGlobal.directNotify.newCategory('StatusSink')

    def write(self, status):
        raise NotImplementedError

    def close(self):
        pass


class GatewaySink(StatusSink):
    """
    The website's copy over the district's gateway socket.
    """

    notify = DirectNotifyGlobal.directNotify.newCategory('GatewaySink')

    REQUIRED = ('name', 'available', 'population', 'created', 'timezone')

    def __init__(self, air, socket):
        self.air = air
        self.socket = socket

    def write(self, status):
        missing = [key for key in self.REQUIRED if key not in status]

        if missing:
            self.notify.debug('Not reporting yet, still missing: %s'
                              % ', '.join(missing))
            return

        payload = dict(status)
        payload.setdefault('invasion', None)
        payload.setdefault('nextInvasion', 0)

        self.socket.sendStatus(self.air.ourChannel, payload)


class FileSink(StatusSink):
    """
    A self-hosting player's copy, as JSON beside the install.
    """

    notify = DirectNotifyGlobal.directNotify.newCategory('FileSink')

    def __init__(self, air, path):
        self.air = air
        self.path = path
        self.startedAt = int(time.time())

    def players(self):
        found = [
            {'id': do.doId, 'name': do.getName()}
            for do in list(self.air.doId2do.values())
            if isinstance(do, DistributedToonAI) and do.isPlayerControlled()
        ]

        return sorted(found, key=lambda player: player['id'])

    def write(self, status):
        players = self.players()

        payload = {
            'district': status.get('name') or self.air.districtName,
            'available': bool(status.get('available', True)),
            'population': len(players),
            'players': players,
            'port': ServerGlobals.getHostPort(),
            'invasion': status.get('invasion'),
            'startedAt': status.get('created', self.startedAt),
            'updatedAt': int(time.time()),
        }

        # Written whole or not at all: the launcher polls this file and would
        # otherwise catch it half-written.
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

    def close(self):
        # rather than leaving a status that claims the server is up:
        self.write({'available': False})


class StatusReporter(DirectObject):
    notify = DirectNotifyGlobal.directNotify.newCategory('StatusReporter')

    # Population moves on every login and logout, so changes are combined:
    FLUSH_DELAY = 1.0

    def __init__(self, air):
        self.air = air
        self.status = {}
        self.sinks = []
        self.pending = False
        self.task = 'StatusReporter-flush-%d' % id(self)

    def add(self, sink):
        self.sinks.append(sink)

        return sink

    def update(self, status):
        self.status.update(status)

        if self.pending:
            return

        self.pending = True
        taskMgr.doMethodLater(self.FLUSH_DELAY, self.__flushTask, self.task)

    def __flushTask(self, task):
        self.pending = False
        self.flush()

        return task.done

    def flush(self):
        for sink in self.sinks:
            try:
                sink.write(self.status)
            except Exception as error:
                self.notify.warning('%s could not take the status: %s'
                                    % (type(sink).__name__, error))

    def stop(self):
        taskMgr.remove(self.task)
        self.pending = False

        for sink in self.sinks:
            try:
                sink.close()
            except Exception as error:
                self.notify.warning('%s would not close: %s'
                                    % (type(sink).__name__, error))
