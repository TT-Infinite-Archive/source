import time
import uuid
from collections import deque

from direct.directnotify import DirectNotifyGlobal
from direct.task import Task


class ReportLog:
    """
    Hands player reports to the website's moderation queue.
    """

    notify = DirectNotifyGlobal.directNotify.newCategory('ReportLog')

    FLUSH_SECONDS = 1.0
    # REPORT_BATCH_MAX
    MAX_BATCH = 25
    MAX_QUEUE = 1000
    # The reported Toon's location arrives from a query of its own
    SETTLE_SECONDS = 2.0

    def __init__(self, air, socket, chatLog):
        self.air = air
        self.socket = socket
        self.chatLog = chatLog
        self.queue = deque()
        self.dropped = 0

        taskMgr.doMethodLater(
            self.FLUSH_SECONDS, self.flushTask, 'report-log-flush')

    def record(self, category, reporterId, reporterAccountId, targetId):
        if self.socket is None:
            return

        targetAccountId = self.accountIdOf(targetId)

        event = {
            'id': uuid.uuid4().hex,
            'category': category,
            'reportedAt': time.time(),
            'reporter': str(reporterId),
            'reporterName': self.chatLog.toonNameFor(reporterId) or '(unknown)',
            'reporterUserId': self.chatLog.userIdFor(reporterAccountId),
            'target': str(targetId),
            'targetName': self.chatLog.toonNameFor(targetId) or '(unknown)',
            'targetUserId': self.chatLog.userIdFor(targetAccountId),
            'district': None,
            'zone': None,
            'location': None,
        }

        if len(self.queue) >= self.MAX_QUEUE:
            self.queue.popleft()
            self.dropped += 1
            self.notify.warning(
                'The report backlog is full; %d reports have been dropped.'
                % self.dropped)

        self.queue.append(event)

        self.air.queryObjectLocation(
            targetId,
            lambda parentId, zoneId: self.setLocation(event, parentId, zoneId))

    def setLocation(self, event, parentId, zoneId):
        event['district'] = str(parentId or 0)
        event['zone'] = int(zoneId or 0)
        event['location'] = self.chatLog.placeName(zoneId)

    def accountIdOf(self, avId):
        try:
            toon = self.air.dbAstronCursor.objects.find_one({'_id': int(avId)})
        except Exception as error:
            self.notify.warning('Could not read %s: %s' % (avId, error))
            return None

        if not toon:
            return None

        return toon['fields'].get('setDISLid', {}).get('_0')

    def flushTask(self, task):
        self.flush()
        return Task.again

    def flush(self):
        if not self.queue or self.socket is None:
            return

        app = getattr(self.socket, 'app', None)
        connection = getattr(app, 'sock', None)
        if not connection or not connection.connected:
            return

        settled = time.time() - self.SETTLE_SECONDS
        batch = []

        while self.queue and len(batch) < self.MAX_BATCH:
            if self.queue[0]['reportedAt'] > settled:
                break
            batch.append(self.queue.popleft())

        if batch:
            self.socket.send({'type': 'reports', 'reports': batch})


def reportLogOf(air):
    return getattr(getattr(air, 'gateway', None), 'reportLog', None)
