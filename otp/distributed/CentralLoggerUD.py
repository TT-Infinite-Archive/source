import time

from direct.distributed.DistributedObjectGlobalUD import DistributedObjectGlobalUD

from otp.distributed.CentralLogger import REPORT_PLAYER, ReportBadName, ReportFoulLanguage, ReportHacking, \
    ReportPersonalInfo, ReportRudeBehavior
from toontown.web.ReportLog import reportLogOf

REPORT_CATEGORIES = (ReportFoulLanguage, ReportPersonalInfo, ReportRudeBehavior, ReportBadName, ReportHacking)


class CentralLoggerUD(DistributedObjectGlobalUD):
    MIN_INTERVAL = 2
    REPORT_REPEAT_SECONDS = 60 * 60

    def __init__(self, air):
        DistributedObjectGlobalUD.__init__(self, air)
        self.lastMessage = {}
        self.lastReport = {}
        self.reported = {}

    def sendMessage(self, category, description, targetAccountId, targetAvId):
        senderId = self.air.getAvatarIdFromSender()

        if category in REPORT_CATEGORIES and description == REPORT_PLAYER:
            self.reportPlayer(senderId, category, targetAvId)
            return

        if not self.allow(self.lastMessage, senderId):
            return

        if category == 'client-event':
            self.air.writeServerEvent('client-event', senderId, description)
        else:
            self.air.writeServerEvent('suspicious', senderId, 'CentralLogger.sendMessage category %r' % category)

    def reportPlayer(self, senderId, category, targetAvId):
        if not targetAvId or targetAvId == senderId:
            self.air.writeServerEvent('suspicious', senderId, 'CentralLogger report of %r' % targetAvId)
            return

        if not self.allow(self.lastReport, senderId):
            return

        now = time.time()
        self.reported = {pair: at for pair, at in self.reported.items()
                         if now - at < self.REPORT_REPEAT_SECONDS}
        if (senderId, targetAvId) in self.reported:
            return
        self.reported[senderId, targetAvId] = now

        self.air.writeServerEvent(REPORT_PLAYER, senderId, targetAvId, category)

        reportLog = reportLogOf(self.air)
        if reportLog is not None:
            reportLog.record(category, senderId, self.air.getAccountIdFromSender(), targetAvId)

    def allow(self, last, senderId):
        now = time.time()
        if now - last.get(senderId, 0) < self.MIN_INTERVAL:
            return False
        last[senderId] = now
        return True

    def logAIGarbage(self):
        pass
