from direct.directnotify import DirectNotifyGlobal
from direct.showbase.DirectObject import DirectObject


class ShardStatusReporter(DirectObject):
    """
    A district's own status, pushed over its gateway socket.

    Nothing is sent until every field the website requires is present.
    """

    notify = DirectNotifyGlobal.directNotify.newCategory('ShardStatusReporter')

    REQUIRED = ('name', 'available', 'population', 'created', 'timezone')

    # Population moves on every login and logout, so changes are combined
    # rather than sent one at a time.
    FLUSH_DELAY = 1.0

    def __init__(self, air, socket):
        self.air = air
        self.socket = socket
        self.status = {}
        self.pending = False

    def update(self, status):
        """Folds in one of the partial updates the district's objects send."""
        self.status.update(status)

        if self.pending:
            return

        self.pending = True
        taskMgr.doMethodLater(
            self.FLUSH_DELAY, self.flushTask, 'ShardStatusReporter-flush')

    def flushTask(self, task):
        self.pending = False
        self.flush()
        return task.done

    def flush(self):
        """Sends the whole status, if there is a whole status to send."""
        missing = [key for key in self.REQUIRED if key not in self.status]
        if missing:
            self.notify.debug('Not reporting yet, still missing: %s'
                              % ', '.join(missing))
            return

        status = dict(self.status)

        # The website defaults these, but sending them keeps a district that
        # has never been invaded from looking different to one that has
        status.setdefault('invasion', None)
        status.setdefault('nextInvasion', 0)

        self.socket.sendStatus(self.air.ourChannel, status)

    def stop(self):
        taskMgr.remove('ShardStatusReporter-flush')
        self.pending = False
