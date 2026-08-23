import json
import queue
import threading
import urllib.error
import urllib.request

from direct.directnotify import DirectNotifyGlobal


class AccountServiceClient:
    """
    The UberDOG's back channel to the website.
    
    Requests run on a worker thread to prevent blocking 
    the server and affecting all logins if the website is slow.
    """

    notify = DirectNotifyGlobal.directNotify.newCategory('AccountServiceClient')

    # Long enough for slow server startup, but short enough to avoid waiting too long if the website is slow
    TIMEOUT = 10

    def __init__(self, endpoint, secret):
        self.endpoint = endpoint.rstrip('/')
        self.secret = secret

        # Written by worker threads, drained by the poll task on the main thread
        self.results = queue.Queue()

        taskMgr.add(self.pollTask, 'AccountServiceClient-poll')

    def post(self, path, payload, callback, errback):
        url = '%s/%s' % (self.endpoint, path.lstrip('/'))

        thread = threading.Thread(
            target=self.request, args=(url, payload, callback, errback),
            name='AccountServiceClient-%s' % path, daemon=True)
        thread.start()

    def request(self, url, payload, callback, errback):
        # Runs on a worker thread
        request = urllib.request.Request(
            url,
            data=json.dumps(payload).encode('utf-8'),
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'Token %s' % self.secret,
                'User-Agent': 'AccountServiceClient (Toontown Infinite; src)'
            },
            method='POST')

        try:
            with urllib.request.urlopen(request, timeout=self.TIMEOUT) as response:
                body = json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as error:
            # A 401 here is an expired or already used token
            self.notify.debug('%s returned HTTP %s.' % (url, error.code))
            self.results.put((errback, (error.code,)))
        except Exception as error:
            self.notify.warning('%s failed: %s' % (url, error))
            self.results.put((errback, (None,)))
        else:
            self.results.put((callback, (body,)))

    def pollTask(self, task):
        while True:
            try:
                handler, args = self.results.get_nowait()
            except queue.Empty:
                return task.cont
            try:
                handler(*args)
            except Exception:
                self.notify.warning(
                    'Unhandled exception in an account service handler.')
                import traceback
                self.notify.warning(traceback.format_exc())
