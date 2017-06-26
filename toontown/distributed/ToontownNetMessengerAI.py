from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.distributed.PyDatagram import PyDatagram

from otp.distributed import OtpDoGlobals

import json, zlib


class ToontownNetMessengerAI:
    notify = directNotify.newCategory('ToontownNetMessengerAI')

    def __init__(self, air, msgType=42069):
        self.air = air
        self.air.registerForChannel(OtpDoGlobals.MESSENGER_CHANNEL_ALL)
        self.msgType = msgType

    def prepare(self, message, sentArgs=[], channels=None):
        dg = PyDatagram()

        if channels is None:
            channels = [OtpDoGlobals.MESSENGER_CHANNEL_ALL]

        dg.addInt8(len(channels))
        for channel in channels:
            dg.addChannel(channel)

        dg.addChannel(self.air.ourChannel)
        dg.addUint16(self.msgType)
        dg.addString(message)
        dg.addString(zlib.compress(json.dumps(sentArgs, encoding='latin-1')))
        return dg

    def send(self, message, sentArgs=[], channels=None):
        self.notify.debug('sendNetEvent: %s %r' % (message, sentArgs))
        dg = self.prepare(message, sentArgs, channels)
        self.air.send(dg)

    def handle(self, msgType, di):
        message = di.getString()
        data = zlib.decompress(di.getString())
        sentArgs = json.loads(data, encoding='latin-1')
        messenger.send(message, sentArgs)
