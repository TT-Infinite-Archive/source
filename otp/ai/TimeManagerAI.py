import time
from direct.distributed.DistributedObjectAI import DistributedObjectAI
from direct.distributed.ClockDelta import globalClockDelta

from otp.util.Compressor import Compressor


class TimeManagerAI(DistributedObjectAI):
    notify = directNotify.newCategory("TimeManagerAI")

    def requestServerTime(self, context):
        self.sendUpdateToAvatarId(self.air.getAvatarIdFromSender(),
                                  'serverTime', [context,
                                                 globalClockDelta.getRealNetworkTime(bits=32),
                                                 int(time.time())])

    def setDisconnectReason(self, reason):
        avId = self.air.getAvatarIdFromSender()
        self.air.setAvatarDisconnectReason(avId, reason)
        self.air.writeServerEvent('disconnect-reason', avId, reason)

    def setExceptionInfo(self, exception):
        avId = self.air.getAvatarIdFromSender()

        # Notify the CrashLogManagerAI.
        self.air.crashLogManager.log(avId, Compressor.decompress(exception).decode())

    def setFrameRate(self, todo0, todo1, todo2, todo3, todo4, todo5, todo6, todo7, todo8, todo9, todo10, todo11, todo12, todo13, todo14, todo15, todo16, todo17):
        pass

    def setCpuInfo(self, todo0, todo1):
        pass

    def checkForGarbageLeaks(self, todo0):
        pass

    def setNumAIGarbageLeaks(self, todo0):
        pass

    def setClientGarbageLeak(self, todo0, todo1):
        pass

    def checkAvOnDistrict(self, todo0, todo1):
        pass
