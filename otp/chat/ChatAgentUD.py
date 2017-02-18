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

    def chatMessage(self, message, channel):
        sender = self.air.getAvatarIdFromSender()
        accountId = self.air.getAccountIdFromSender()
        if sender == 0:
            self.air.writeServerEvent('suspicious',
                                      self.air.getAccountIdFromSender(),
                                      'Account sent chat without an avatar',
                                      message)
            return

        if accountId in self.mutedDict:
            # Check if this account is muted.
            return

        modifications = []
        words = message.split(' ')
        offset = 0
        for word in words:
            if self.wantWhiteList and word and not self.whiteList.isWord(word):
                modifications.append((offset, offset + len(word) - 1))
            offset += len(word) + 1

        if self.wantBlackList:
            seqMods = self.lookForSequences(words)
            modifications.extend(seqMods)

        cleanMessage = message
        for modStart, modStop in modifications:
            cleanMessage = cleanMessage[:modStart] + '*'*(modStop-modStart+1) + cleanMessage[modStop+1:]

        if self.wantBlackList and self.detectBadWords(message):
            return

        self.air.writeServerEvent('chat-said', sender, message, cleanMessage)

        if config.GetBool('want-chat-logging', False):
            def handleQueryObjectLocationResp(parentId, zoneId):
                self.air.mongodb.chat.messages.insert_one(
                    {'type': ChannelToType[channel],
                     'timestamp': int(time.time()),
                     'sender': sender,
                     'recipient': 0,
                     'location': [parentId, zoneId],
                     'message': message})

            self.air.queryObjectLocation(sender, handleQueryObjectLocationResp)

        DistributedAvatar = self.air.dclassesByName['DistributedAvatarUD']
        dg = DistributedAvatar.aiFormatUpdate(
            'setTalk', sender, sender, self.air.ourChannel,
            [0, 0, '', message, modifications, 0, channel])
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
