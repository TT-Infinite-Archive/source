from direct.directnotify import DirectNotifyGlobal
from direct.distributed.PyDatagram import PyDatagram
from direct.showbase.DirectObject import DirectObject
from otp.util.Compressor import Compressor
import pickle

class ToontownNetMessengerAI(DirectObject):
    """
    This works very much like the NetMessenger class except that
    this is much simpler and makes much more sense.
    """
    notify = DirectNotifyGlobal.directNotify.newCategory('ToontownNetMessengerAI')

    def __init__(self, air, msgChannel=52000, msgType=22442):
        self.air = air
        self.msgChannel = msgChannel
        self.msgType = msgType
        self.registered = False

    def register(self):
        if self.registered:
            return

        self.air.registerForChannel(self.msgChannel)
        self.registered = True

    def prepare(self, message, sentArgs=[]):
        dg = PyDatagram()
        dg.addServerHeader(self.msgChannel, self.air.ourChannel, self.msgType)
        dg.addString(message)
        dg.addBlob(Compressor.compress(pickle.dumps(sentArgs), 3))
        return dg

    def send(self, message, sentArgs=[]):
        dg = self.prepare(message, sentArgs)
        self.air.send(dg)

    def handle(self, di):
        message = di.getString()
        data = Compressor.decompress(di.getBlob())
        sentArgs = pickle.loads(data)
        messenger.send(message, sentArgs)
