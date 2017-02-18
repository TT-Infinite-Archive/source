from direct.directnotify import DirectNotifyGlobal
from direct.task import Task
from direct.distributed.DistributedObjectGlobalUD import \
    DistributedObjectGlobalUD

from toontown.chat.TTWhiteList import TTWhiteList
from otp.distributed import OtpDoGlobals
from otp.chat.ChatGlobals import ChannelToType
from toontown.chat.TTBlacklist import BLACKLIST, SEQUENCES
import time


class ChatAgentUD(DistributedObjectGlobalUD):
    notify = DirectNotifyGlobal.directNotify.newCategory("ChatAgentUD")

    def announceGenerate(self):
        DistributedObjectGlobalUD.announceGenerate(self)

        self.wantWhiteList = config.GetBool('want-whitelist', True)
        self.wantBlackList = config.GetBool('want-blacklist', True)

        self.whiteList = None
        if self.wantWhiteList:
            self.whiteList = TTWhiteList()

        self.mutedDict = {}
        self.accept('nameCheck', self.checkBadNames)

    def checkBadNames(self, toonName, nameCheck=False):
        isBadName = self.detectBadWords(toonName)
        sequenceChecks = self.lookForSequences(toonName.split(' '))
        for check in sequenceChecks:
            if check[0]:
                isBadName = True
                break

        if nameCheck:
            return isBadName

        simbase.air.sendNetEvent('badNameResponse', [isBadName], channels=[OtpDoGlobals.MESSENGER_CHANNEL_AI])

    def chatMessage(self, message, name, channel):
        senderId = self.air.getAvatarIdFromSender()
        accountId = self.air.getAccountIdFromSender()
        if senderId == 0:
            self.air.writeServerEvent('suspicious',
                                      self.air.getAccountIdFromSender(),
                                      'Account sent chat without an avatar',
                                      message)
            return

        if accountId in self.mutedDict:
            # Check if this account is muted.
            return

        self.air.writeServerEvent('chat-said', senderId, message, message)

        if config.GetBool('want-chat-logging', False):
            def handleQueryObjectLocationResp(parentId, zoneId):
                self.air.mongodb.chat.messages.insert_one(
                    {'type': ChannelToType[channel],
                     'timestamp': int(time.time()),
                     'sender': senderId,
                     'recipient': 0,
                     'location': [parentId, zoneId],
                     'message': message})

            self.air.queryObjectLocation(senderId, handleQueryObjectLocationResp)

        dclass = self.air.dclassesByName['DistributedAvatarUD']
        dg = dclass.aiFormatUpdate(
            'setTalk', senderId, senderId, self.air.ourChannel,
            [senderId, accountId, name, message, [], 0, channel])
        self.air.send(dg)

    def muteAccount(self, accountId, timestamp, timeLeft):
        self.mutedDict[int(accountId)] = timestamp
        taskMgr.remove('muted-' + str(accountId))
        taskMgr.doMethodLater(timeLeft, self.unmuteAccount, 'muted-' + str(accountId), extraArgs=[accountId])

    def unmuteAccount(self, accountId):
        if accountId in self.mutedDict:
            del self.mutedDict[int(accountId)]
            self.air.dbInterface.updateObject(
              self.air.dbId,
              accountId,
              self.air.dclassesByName['AccountUD'],
              {'MUTE_TIMESTAMP': 0})
        return Task.done

    def checkMuted(self, accountId):

        def __handleRetrieve(dclass, fields):
            if dclass != self.air.dclassesByName['AccountUD']:
                return

            timestamp = fields.get('MUTE_TIMESTAMP', 0)
            muteTime = timestamp - time.time()
            if muteTime <= 20:
                # Timestamp is unreasonable or expired.
                self.air.dbInterface.updateObject(
                  self.air.dbId, accountId, self.air.dclassesByName['AccountUD'],{'MUTE_TIMESTAMP': 0})
                self.unmuteAccount(accountId)
                return

            self.muteAccount(accountId, timestamp, muteTime)
            return

        self.air.dbInterface.queryObject(
            self.air.dbId, accountId, __handleRetrieve)

    def detectBadWords(self, message):
        words = message.split()
        for word in words:
            if word.lower().strip(',.!?\'\"') in BLACKLIST or message.lower().strip(',.!?\'\"') in BLACKLIST:
                return True

            phrase = ''
            for letter in word:
                phrase += letter
                if phrase.lower().strip(',.!?\'\"') in BLACKLIST:
                    return True

        return False

    def lookForSequences(self, words):
        flaggedIndexes = []
        seqCheckList = [(i, SEQUENCES.get(word.lower().strip(',.!?\'\"'))) for i, word in enumerate(words)
                        if word.lower().strip(',.!?\'\"') in SEQUENCES and self.whiteList.isWord(word)]
        for candidate in seqCheckList:
            currentIndex = candidate[0]
            strings = candidate[1]
            for string in strings:
                subseqStrings = string.split()
                rangeEnd = len(subseqStrings) + 1
                cleanSlice = [word.lower().strip(',.!?\'\"') for word in
                              words[currentIndex + 1:currentIndex + rangeEnd]]
                if not cleanSlice:
                    break
                if cleanSlice != subseqStrings:
                    continue
                flaggedIndexes.extend(range(currentIndex, currentIndex + rangeEnd))
                break

        return [(i, self.wantWhiteList) for i in flaggedIndexes]
