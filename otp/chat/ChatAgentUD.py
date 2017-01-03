from direct.directnotify import DirectNotifyGlobal
from direct.task import Task
from direct.distributed.DistributedObjectGlobalUD import \
    DistributedObjectGlobalUD

from toontown.chat.TTWhiteList import TTWhiteList
from otp.chat.ChatGlobals import ChannelToType
from toontown.chat.TTSequenceList import TTSequenceList
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

        self.sequenceList = None
        if self.wantBlackList:
            self.sequenceList = TTSequenceList()

        self.mutedDict = {}

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

        cleanMessage = message
        for modStart, modStop in modifications:
            cleanMessage = cleanMessage[:modStart] + '*'*(modStop-modStart+1) + cleanMessage[modStop+1:]

        if self.wantBlackList:
            modifications += self.cleanSequences(cleanMessage)

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

    # Check for black-listed word sequences and scrub accordingly.
    def cleanSequences(self, message):
        modifications = []
        offset = 0
        words = message.split()
        for wordit in xrange(len(words)):
            word = words[wordit].lower()
            seqlist = self.sequenceList.getList(word)
            if len(seqlist) > 0:
                for seqit in xrange(len(seqlist)):
                    sequence = seqlist[seqit]
                    splitseq = sequence.split()
                    if len(words) - (wordit + 1) >= len(splitseq):
                        cmplist = words[wordit + 1:]
                        del cmplist[len(splitseq):]
                        cmplist = [word.lower() for word in cmplist]
                        if cmp(cmplist, splitseq) == 0:
                            modifications.append((offset, offset + len(word) + len(sequence) - 1))
            offset += len(word) + 1

        return modifications
