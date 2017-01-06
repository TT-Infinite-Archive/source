import requests


class WebserverAPIClient:
    def __init__(self, endpoint, token):
        self.endpoint = endpoint
        self.token = token

    def execute(self, url, payload={}, method='post', callback=None, errback=None, extraArgs=[]):
        headers = {'Authorization': 'Token ' + self.token,
                   'User-Agent': 'WebserverAPIClient (Toontown Infinite; src)'}

        try:
            response = requests.request(method, self.endpoint + url + '/', json=payload, headers=headers).json()
            if callback:
                callback(response, *extraArgs)
        except:
            if errback:
                errback(*extraArgs)


# Non working async version
'''
import json

from panda3d.core import URLSpec, HTTPClient, StringStream, DocumentSpec


class ProtocolError(Exception):
    pass


class WebserverAPIClient:
    notify = directNotify.newCategory('WebserverAPIClient')

    def __init__(self, endpoint, token):
        self.url = URLSpec(endpoint)
        self.token = token

        self.http = HTTPClient()
        self.http.setVerifySsl(1)

        self.channels = {}

        # Start polling:
        taskName = self.getUniqueName() + '-pollTask'
        taskMgr.add(self.pollTask, taskName)

    def getUniqueName(self):
        return 'WebserverAPIClient-' + str(id(self))

    def execute(self, url, payload, callback=None, errback=None, extraArgs=[]):
        call = WebserverAPICall(self, url, payload, callback, errback, extraArgs)
        call.send()

    def pollOnce(self):
        for channel, method in self.channels.items():
            if not channel.run():
                del self.channels[channel]
                method.finish()

    def pollTask(self, task):
        self.pollOnce()
        return task.cont


class WebserverAPICall:
    def __init__(self, client, url, payload, callback, errback, extraArgs):
        self.client = client
        self.name = url

        self.notify = directNotify.newCategory('WebserverAPICall[%s]' % url)

        self.channel = None
        self.stream = StringStream()
        self.callback = callback
        self.errback = errback
        self.payload = payload
        self.extraArgs = extraArgs

    def send(self):
        if not self.client.url.hasServer():
            if self.errback is not None:
                self.errback(*self.extraArgs)
            return

        self.channel = self.client.http.makeChannel(False)

        self.channel.sendExtraHeader('Authorization', 'Token '+self.client.token)
        self.channel.sendExtraHeader('User-Agent', 'WebserverAPIClient (Toontown Infinite; src)')

        data = json.dumps(self.payload)

        ds = DocumentSpec(self.client.url)

        self.channel.beginPostForm(ds, data)
        self.channel.downloadToStream(self.stream)

        self.client.channels[self.channel] = self

    def finish(self):
        if not self.channel.isValid():
            self.notify.warning('Failed to make HTTP request.')
            if self.errback is not None:
                self.errback(*self.extraArgs)
            return

        if not self.channel.isDownloadComplete():
            self.notify.warning('Received an incomplete response.')
            if self.errback is not None:
                self.errback(*self.extraArgs)
            return

        data = self.stream.getData()
        try:
            response = json.loads(data)
        except ValueError:
            self.notify.warning('Received an invalid response.')
            if self.errback is not None:
                self.errback(*self.extraArgs)
            return

        if self.callback:
            self.callback(response, *self.extraArgs)
'''
