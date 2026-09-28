import time

from direct.distributed.DistributedObjectGlobalUD import DistributedObjectGlobalUD

from otp.distributed.CentralLogger import REPORT_PLAYER, ReportBadName, ReportFoulLanguage, ReportHacking, \
    ReportPersonalInfo, ReportRudeBehavior

REPORT_CATEGORIES = (ReportFoulLanguage, ReportPersonalInfo, ReportRudeBehavior, ReportBadName, ReportHacking)


class CentralLoggerUD(DistributedObjectGlobalUD):
    MIN_INTERVAL = 2

    def __init__(self, air):
        DistributedObjectGlobalUD.__init__(self, air)
        self.lastMessage = {}

    def sendMessage(self, category, description, targetAccountId, targetAvId):
        senderId = self.air.getAvatarIdFromSender()
        now = time.time()
        if now - self.lastMessage.get(senderId, 0) < self.MIN_INTERVAL:
            return
        self.lastMessage[senderId] = now

        if category in REPORT_CATEGORIES and description == REPORT_PLAYER:
            self.air.writeServerEvent(REPORT_PLAYER, senderId, targetAvId, targetAccountId, category)
        elif category == 'client-event':
            self.air.writeServerEvent('client-event', senderId, description)
        else:
            self.air.writeServerEvent('suspicious', senderId, 'CentralLogger.sendMessage category %r' % category)

    def logAIGarbage(self):
        pass
