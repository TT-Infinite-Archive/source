import json
import os
import queue
import threading
import urllib.parse

import websocket

from direct.directnotify import DirectNotifyGlobal
from direct.showbase.DirectObject import DirectObject


class GatewaySocket(DirectObject):
    """
    A game process's authenticated socket to the website.
    """

    notify = DirectNotifyGlobal.directNotify.newCategory('GatewaySocket')

    # Long enough not to hammer the site while it restarts, short enough that a
    # district is not missing from the website for long
    RECONNECT_SECONDS = 5

    def __init__(self, url, token, onCommand=None, onReady=None):
        self.url = url
        self.token = token
        self.onCommand = onCommand
        self.onReady = onReady
        self.identity = None
        self.inbox = queue.Queue()
        self.lock = threading.Lock()
        self.app = None
        self.stopped = False

        if not self.token:
            self.notify.warning(
                'No gateway token; this process will not reach the website.')
            return

        taskMgr.add(self.pollTask, 'GatewaySocket-poll-%d' % id(self))

        thread = threading.Thread(
            target=self.run, name='GatewaySocket', daemon=True)
        thread.start()

    def run(self):
        # Runs on the worker thread for the life of the process
        self.app = websocket.WebSocketApp(
            self.url,
            header={'Authorization': 'Token %s' % self.token},
            on_open=self.onOpen,
            on_message=self.onMessage,
            on_close=self.onClose,
            on_error=self.onError)

        self.app.run_forever(reconnect=self.RECONNECT_SECONDS)

    def onOpen(self, app):
        self.notify.info('Connected to %s.' % self.url)

    def onMessage(self, app, raw):
        try:
            message = json.loads(raw)
        except ValueError:
            self.notify.warning('Ignoring a frame that was not JSON.')
            return

        self.inbox.put(message)

    def onClose(self, app, status, reason):
        # A 1012 is the website telling us a newer connection took our place,
        # which happens when a process is restarted and the old socket lingers
        self.notify.info('Disconnected (%s): %s' % (status, reason))
        self.identity = None

    def onError(self, app, error):
        self.notify.warning('Socket error: %s' % error)

    def send(self, message):
        """Queues a frame for the website. Safe to call from the main thread."""
        if self.stopped or not self.app:
            return

        socket = self.app.sock
        if not socket or not socket.connected:
            # Status is sent again on the next change, and results are retried
            # by the website, so dropping this is better than blocking
            return

        try:
            with self.lock:
                self.app.send(json.dumps(message))
        except Exception as error:
            self.notify.warning('Failed to send: %s' % error)

    def sendStatus(self, channel, status):
        self.send({'type': 'status', 'channel': str(channel), 'status': status})

    def sendResult(self, commandId, ok, result=None):
        message = {'type': 'result', 'id': commandId, 'ok': bool(ok)}
        if result is not None:
            message['result'] = result
        self.send(message)

    def pollTask(self, task):
        # Runs on the main thread
        while True:
            try:
                message = self.inbox.get_nowait()
            except queue.Empty:
                return task.cont

            try:
                self.handle(message)
            except Exception:
                self.notify.warning('Unhandled exception in a gateway handler.')
                import traceback
                self.notify.warning(traceback.format_exc())

    def handle(self, message):
        kind = message.get('type')

        if kind == 'ready':
            self.identity = message.get('name')
            self.notify.info('Authenticated as %s (%s).'
                             % (self.identity, message.get('kind')))
            if self.onReady:
                self.onReady(message)
            return

        if kind == 'command':
            if self.onCommand:
                self.onCommand(message)
            return

        if kind == 'error':
            self.notify.warning('Website refused a frame: %s'
                                % message.get('error'))
            return

        self.notify.warning('Ignoring an unknown frame type: %s' % kind)

    def stop(self):
        self.stopped = True
        taskMgr.remove('GatewaySocket-poll-%d' % id(self))
        if self.app:
            self.app.close()


def socketUrl(endpoint, path='/api/game/socket'):
    """Turns the account service's http(s) URL into a ws(s) socket URL."""
    parts = urllib.parse.urlsplit(endpoint.rstrip('/'))
    scheme = 'wss' if parts.scheme == 'https' else 'ws'
    return urllib.parse.urlunsplit(
        (scheme, parts.netloc, (parts.path or '') + path, '', ''))


def gatewayToken():
    """
    The process's own credential.
    """
    return os.environ.get('TTI_GATEWAY_TOKEN', '')
