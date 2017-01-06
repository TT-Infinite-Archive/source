from otp.avatar.Avatar import teleportNotify
from toontown.toonbase import ToontownGlobals
import copy
from toontown.chat import ToonChatGarbler


class FriendHandle:
    def __init__(self, doId, name, style, petId, isAPet = False):
        self.doId = doId
        self.style = style
        self.commonChatFlags = 0
        self.whitelistChatFlags = 0
        self.chatMode = 0
        self.petId = petId
        self.isAPet = isAPet
        self.chatGarbler = ToonChatGarbler.ToonChatGarbler()
        self.name = name
        self.guildId = -1

    def getDoId(self):
        return self.doId

    def getPetId(self):
        return self.petId

    def hasPet(self):
        return self.getPetId() != 0

    def isPet(self):
        return self.isAPet

    def getName(self):
        return self.name

    def getFont(self):
        return ToontownGlobals.getToonFont()

    def getStyle(self):
        return self.style

    def getGuildId(self):
        return self.guildId

    def uniqueName(self, idString):
        return idString + '-' + str(self.getDoId())

    def d_battleSOS(self, sendToId):
        base.cr.ttiFriendsManager.d_battleSOS(self.doId)

    def d_teleportQuery(self, requesterId):
        teleportNotify.debug('sending d_teleportQuery(%s)' % (requesterId,))

        base.cr.ttiFriendsManager.d_teleportQuery(self.doId)

    def d_teleportResponse(self, avId, available, shardId, hoodId, zoneId):
        teleportNotify.debug('sending teleportResponse%s' % ((avId, available,
            shardId, hoodId, zoneId),)
        )

        base.cr.ttiFriendsManager.d_teleportResponse(self.doId, available,
            shardId, hoodId, zoneId
        )

    def d_teleportGiveup(self, requesterId):
        teleportNotify.debug('sending d_teleportGiveup(%s)' % (requesterId,))

        base.cr.ttiFriendsManager.d_teleportGiveup(self.doId)

    def isUnderstandable(self):
        if self.commonChatFlags & base.localAvatar.commonChatFlags & ToontownGlobals.CommonChat:
            understandable = 1
        elif self.commonChatFlags & ToontownGlobals.SuperChat:
            understandable = 1
        elif base.localAvatar.commonChatFlags & ToontownGlobals.SuperChat:
            understandable = 1
        elif base.cr.getFriendFlags(self.doId) & ToontownGlobals.FriendChat:
            understandable = 1
        elif self.whitelistChatFlags & base.localAvatar.whitelistChatFlags:
            understandable = 1
        elif base.localAvatar.chatMode == 1:
            understandable = self.chatMode
        else:
            understandable = 0
        return understandable

    def scrubTalk(self, message, mods):
        scrubbed = 0
        text = copy.copy(message)
        flag = 0
        trueFriends = False
        admin = False

        for friendId, flags in base.localAvatar.friendsList:
            if flags & ToontownGlobals.FriendChat:
                flag = 1

        if base.cr.getFriendFlags(self.doId) & ToontownGlobals.FriendChat or flag:
            trueFriends = True
        elif base.localAvatar.adminAccess >= 200:
            admin = True
        else:
            for mod in mods:
                index = mod[0]
                length = mod[1] - mod[0] + 1
                newText = text[0:index] + length * '\x07' + text[index + length:]
                text = newText

        words = text.split(' ')
        newwords = []
        for word in words:
            if word == '':
                newwords.append(word)
            elif word[0] == '\x07':
                newwords.append('\x01WLDisplay\x01' + self.chatGarbler.garbleSingle(self, word) + '\x02')
                scrubbed = 1
            elif base.whiteList.isWord(word):
                newwords.append(word)
            elif trueFriends:
                newwords.append('\x01WLDisplay\x01' + word + '\x02')
                scrubbed = 1
            elif admin:
                newwords.append('\x01WLEnter\x01' + word + '\x02')
                scrubbed = 1
            elif not base.localAvatar.canChat():
                newwords.append('\x01WLDisplay\x01' + self.chatGarbler.garbleSingle(self, word) + '\x02')
                scrubbed = 1
            elif not self.isUnderstandable():
                newwords.append('\x01WLDisplay\x01' + self.chatGarbler.garbleSingle(self, word) + '\x02')
                scrubbed = 1
            else:
                newwords.append('\x01WLDisplay\x01' + self.chatGarbler.garbleSingle(self, word) + '\x02')
                scrubbed = 1

        newText = ' '.join(newwords)
        return (newText, scrubbed)

    def replaceBadWords(self, text):
        words = text.split(' ')
        newwords = []
        for word in words:
            if word == '':
                newwords.append(word)
            elif word[0] == '\x07':
                newwords.append('\x01WLRed\x01' + self.chatGarbler.garbleSingle(self, word) + '\x02')
            elif base.whiteList.isWord(word):
                newwords.append(word)
            else:
                newwords.append('\x01WLRed\x01' + word + '\x02')

        newText = ' '.join(newwords)
        return newText

    def setCommonAndWhitelistChatFlags(self, commonChatFlags, whitelistChatFlags):
        self.commonChatFlags = commonChatFlags
        self.whitelistChatFlags = whitelistChatFlags

    def setChatMode(self, chatMode):
        self.chatMode = chatMode
