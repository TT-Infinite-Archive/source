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

        if not self.endpoint:
            self.notify.warning(
                'account-service-url is unset; the website cannot be reached.')

        # Written by worker threads, drained by the poll task on the main thread
        self.results = queue.Queue()

        # Unique, because the account database and the gateway each keep one
        taskMgr.add(self.pollTask, 'AccountServiceClient-poll-%d' % id(self))

    def post(self, path, payload, callback, errback):
        self.send('POST', path, payload, callback, errback)

    def get(self, path, callback, errback, timeout=None):
        self.send('GET', path, None, callback, errback, timeout)

    def send(self, method, path, payload, callback, errback, timeout=None):
        url = '%s/%s' % (self.endpoint, path.lstrip('/'))

        thread = threading.Thread(
            target=self.request,
            args=(method, url, payload, callback, errback, timeout),
            name='AccountServiceClient-%s' % path, daemon=True)
        thread.start()

    def request(self, method, url, payload, callback, errback, timeout=None):
        # Runs on a worker thread
        headers = {
            'Authorization': 'Token %s' % self.secret,
            'User-Agent': 'AccountServiceClient (Toontown Infinite; src)'
        }

        data = None
        if payload is not None:
            headers['Content-Type'] = 'application/json'
            data = json.dumps(payload).encode('utf-8')

        try:
            request = urllib.request.Request(
                url, data=data, headers=headers, method=method)

            with urllib.request.urlopen(
                    request, timeout=timeout or self.TIMEOUT) as response:
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
