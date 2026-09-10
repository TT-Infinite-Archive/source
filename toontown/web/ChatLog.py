import json
import time
from collections import deque, OrderedDict

from panda3d.core import ConfigVariableBool

from direct.directnotify import DirectNotifyGlobal
from direct.showbase.DirectObject import DirectObject
from direct.task import Task

from toontown.chat.TTBlacklist import containsBadWord
from toontown.hood import ZoneUtil
from toontown.toonbase import ToontownGlobals

OPEN = 'open'
WHISPER = 'whisper'
GUILD = 'guild'

# Per ChatGlobals
GUILD_CHANNEL = 1


class ChatLog(DirectObject):
    notify = DirectNotifyGlobal.directNotify.newCategory('ChatLog')

    FLUSH_SECONDS = 1.0
    # CHAT_BATCH_MAX
    MAX_BATCH = 40
    # A frame over 64KB is dropped unread
    MAX_FRAME_BYTES = 48 * 1024
    MAX_BODY = 512
    BATCHES_PER_FLUSH = 4
    MAX_QUEUE = 5000
    # An open-chat location arrives from a query of its own, so a message
    # settles before it goes out.
    SETTLE_SECONDS = 1.0
    MAX_CACHED = 4096
    CACHE_SECONDS = 60

    def __init__(self, air, socket):
        self.air = air
        self.socket = socket
        self.queue = deque()
        self.accounts = OrderedDict()
        self.names = OrderedDict()
        self.dropped = 0

        taskMgr.doMethodLater(
            self.FLUSH_SECONDS, self.flushTask, 'chat-log-flush')

        # A gateway with logging off is almost always a config mistake, and
        # silence looks exactly like a chat log that is quietly failing.
        if socket is not None and not self.wants():
            self.notify.warning(
                'want-chat-logging is off; chat will not reach the website.')

    def wants(self):
        if self.socket is None:
            return False

        return ConfigVariableBool('want-chat-logging', False).getValue()

    def record(self, kind, senderId, senderName, accountId, message,
               recipientId=0, recipientName=None):
        if not self.wants():
            return None

        event = {
            'kind': kind,
            'sentAt': time.time(),
            'sender': str(senderId),
            'senderName': senderName or '(unknown)',
            'userId': self.userIdFor(accountId),
            'recipient': str(recipientId or 0),
            'recipientName': recipientName,
            'district': None,
            'zone': None,
            'location': None,
            'flagged': containsBadWord(message),
            'message': message[:self.MAX_BODY],
        }

        if len(self.queue) >= self.MAX_QUEUE:
            self.queue.popleft()
            self.dropped += 1
            if self.dropped % 100 == 1:
                self.notify.warning(
                    'The chat backlog is full; %d messages have been dropped.'
                    % self.dropped)

        self.queue.append(event)
        return event

    def setLocation(self, event, parentId, zoneId):
        if event is None:
            return

        event['district'] = str(parentId or 0)
        event['zone'] = int(zoneId or 0)
        event['location'] = self.placeName(zoneId)

    def flushTask(self, task):
        self.flush()
        return Task.again

    def flush(self):
        if not self.queue or self.socket is None:
            return

        # Held rather than handed to a socket that would drop it
        app = getattr(self.socket, 'app', None)
        connection = getattr(app, 'sock', None)
        if not connection or not connection.connected:
            return

        for _ in range(self.BATCHES_PER_FLUSH):
            batch = self.nextBatch()
            if not batch:
                return

            self.socket.send({'type': 'chat', 'messages': batch})

    def nextBatch(self):
        batch = []
        budget = self.MAX_FRAME_BYTES
        settled = time.time() - self.SETTLE_SECONDS

        while self.queue and len(batch) < self.MAX_BATCH:
            event = self.queue[0]

            if event['sentAt'] > settled:
                break

            if batch:
                budget -= len(json.dumps(event))
                if budget <= 0:
                    break

            batch.append(self.queue.popleft())

        return batch

    def lookup(self, store, doId, read):
        doId = int(doId)
        now = time.time()

        hit = store.get(doId)
        if hit is not None and now - hit[1] < self.CACHE_SECONDS:
            store.move_to_end(doId)
            return hit[0]

        try:
            document = self.air.dbAstronCursor.objects.find_one({'_id': doId})
        except Exception as error:
            self.notify.warning('Could not read %d: %s' % (doId, error))
            return hit[0] if hit else None

        value = read(document) if document else None

        store[doId] = (value, now)
        store.move_to_end(doId)
        if len(store) > self.MAX_CACHED:
            store.popitem(last=False)

        return value

    def userIdFor(self, accountId):
        if not accountId:
            return None

        return self.lookup(self.accounts, accountId, websiteUserId)

    def toonNameFor(self, avId):
        if not avId:
            return None

        return self.lookup(self.names, avId, toonName)

    def placeName(self, zoneId):
        if not zoneId:
            return None

        try:
            # Estates, house interiors, minigames, parties and Cog facilities
            # all sit in zones the district allocates at runtime, so the number
            # names no place. The zone still tells two instances apart, which
            # is what groups a conversation.
            if ZoneUtil.isDynamicZone(zoneId):
                return 'A private area'

            canonical = ZoneUtil.getCanonicalZoneId(zoneId)
            hoodId = ZoneUtil.getCanonicalHoodId(canonical)

            if hoodId == ToontownGlobals.MyEstate:
                # The game calls this "your house"
                return 'An Estate'

            hood = ToontownGlobals.hoodNameMap.get(hoodId)
            if hood is None:
                return 'Zone %d' % zoneId

            # Phrasing tuples
            hood = hood[-1]

            if ZoneUtil.isPlayground(canonical):
                return hood

            try:
                street = ZoneUtil.getStreetName(
                    ZoneUtil.getCanonicalBranchZone(canonical))
            except KeyError:
                # Cog HQs and minigames have no street.
                return hood

            return '%s, %s' % (street, hood)
        except Exception:
            return 'Zone %d' % zoneId


def websiteUserId(account):
    if account.get('dclass') != 'Account':
        return None

    userId = str(account['fields'].get('ACCOUNT_ID') or '')

    return userId if userId and ':' not in userId else None


def toonName(toon):
    return toon['fields'].get('setName', {}).get('_0')


def kindForChannel(channel):
    return GUILD if channel == GUILD_CHANNEL else OPEN


def chatLogOf(air):
    chatLog = getattr(getattr(air, 'gateway', None), 'chatLog', None)

    if chatLog is None or not chatLog.wants():
        return None

    return chatLog
