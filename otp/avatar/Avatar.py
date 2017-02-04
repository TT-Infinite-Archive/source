from panda3d.core import CollisionNode, CollisionTube, Point3

from direct.actor.Actor import Actor
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.distributed import ClockDelta

from otp.ai import MagicWordManager
from otp.ai.MagicWordGlobal import *
from otp.avatar.ShadowCaster import ShadowCaster
from otp.chat.ChatGlobals import isThought
from otp.otpbase import OTPGlobals, OTPLocalizer, OTPRender
from toontown.chat.ChatGlobals import CFSpeech, CFThought, CFTimeout, CFPageButton, CFReversed, CFQuicktalker
from toontown.nametag import NametagGlobals
from toontown.nametag.NametagGroup import NametagGroup
from toontown.toonbase import EventGlobals

import random


teleportNotify = directNotify.newCategory('Teleport')
teleportNotify.showTime = True


def reconsiderAllUnderstandable():
    for av in Avatar.ActiveAvatars:
        av.considerUnderstandable()


class Avatar(Actor, ShadowCaster):
    notify = directNotify.newCategory('Avatar')
    ActiveAvatars = []
    ManagesNametagAmbientLightChanged = False

    def __init__(self, other=None):
        Actor.__init__(self, None, None, other, flattenable=0, setFinal=1)
        ShadowCaster.__init__(self)

        self.chatMode = None
        self.collTube = None
        self.collNode = None
        self.collNodePath = None
        self.commonChatFlags = 0
        self.ghostMode = 0
        self.height = 0.0
        self.isDisguised = 0
        self.name = ''
        self.nametag = None
        self.nametag3d = None
        self.nametagNodePath = None
        self.radius = OTPGlobals.AvatarDefaultRadius
        self.scale = 1.0
        self.soundChatBubble = None
        self.style = None
        self.understandable = 1
        self.whitelistChatFlags = 0
        self.__nameVisible = 1
        self.__chatParagraph = None
        self.__chatMessage = None
        self.__chatFlags = 0
        self.__chatPageNumber = None
        self.__chatAddressee = None
        self.__chatDialogueList = []
        self.__chatSet = 0
        self.__chatLocal = 0
        self.__chatQuitButton = False
        self.__currentDialogue = None
        self.getGeomNode().showThrough(OTPRender.ShadowCameraBitmask)
        self.setupNametag()
        self.setPlayerType(NametagGlobals.CCNormal)

    def delete(self):
        self.ignoreAll()
        self.deleteNametag3d()
        Actor.cleanup(self)
        self.style = None
        self.soundChatBubble = None
        self.cleanupNametag()
        ShadowCaster.delete(self)
        Actor.delete(self)

    def acceptNametagAmbientLightChange(self):
        self.accept('nametagAmbientLightChanged', self.nametagAmbientLightChanged)

    def ignoreNametagAmbientLightChange(self):
        self.ignore('nametagAmbientLightChanged')

    def isLocal(self):
        return 0

    def isPet(self):
        return False

    def isProxy(self):
        return False

    def setupNametag(self):
        interfaceFont = OTPGlobals.getInterfaceFont()
        self.cleanupNametag()

        self.nametag = NametagGroup()
        self.nametag.setAvatar(self)
        self.nametag.setFont(interfaceFont)
        self.nametag.setGuildFont(interfaceFont)
        self.nametag.setChatFont(interfaceFont)
        self.nametag3d = self.attachNewNode('nametag3d')
        self.nametag3d.setTag('cam', 'nametag')
        self.nametag3d.setLightOff()
        if self.ManagesNametagAmbientLightChanged:
            self.acceptNametagAmbientLightChange()
        OTPRender.renderReflection(False, self.nametag3d, 'otp_avatar_nametag', None)
        self.nametag3d.hide(OTPRender.ShadowCameraBitmask)

    def cleanupNametag(self):
        if self.nametag:
            self.nametag.destroy()
            self.nametag = None
        if self.nametag3d:
            self.nametag3d.removeNode()
            self.nametag3d = None

    def setPlayerType(self, playerType):
        self.playerType = playerType
        if not self.nametag:
            self.notify.warning('setPlayerType has no nametag to apply to!')
            return
        if self.isUnderstandable():
            nametagColor = NametagGlobals.NametagColors[self.playerType]
            self.nametag.setNametagColor(nametagColor)
            chatColor = NametagGlobals.ChatColors[self.playerType]
            self.nametag.setChatColor(chatColor)
        else:
            nametagColor = NametagGlobals.NametagColors[NametagGlobals.CCNoChat]
            self.nametag.setNametagColor(nametagColor)
            chatColor = NametagGlobals.ChatColors[NametagGlobals.CCNoChat]
            self.nametag.setChatColor(chatColor)
        self.nametag.updateAll()

    def setCommonChatFlags(self, commonChatFlags):
        self.commonChatFlags = commonChatFlags
        self.considerUnderstandable()
        if self == base.localAvatar:
            reconsiderAllUnderstandable()

    def setWhitelistChatFlags(self, whitelistChatFlags):
        self.whitelistChatFlags = whitelistChatFlags
        self.considerUnderstandable()
        if self == base.localAvatar:
            reconsiderAllUnderstandable()

    def considerUnderstandable(self):
        if hasattr(base, 'localAvatar') and (self == base.localAvatar):
            # Local Avatar
            self.understandable = 1
            self.setPlayerType(NametagGlobals.CCFreeChat)
        elif self.playerType in (NametagGlobals.CCSpeedChat, NametagGlobals.CCFreeChat, NametagGlobals.CCNormal):
            self.understandable = 1
            if base.cr.getFriendFlags(self.doId) & OTPGlobals.FriendChat:
                # True Friend
                self.setPlayerType(NametagGlobals.CCNormal)
            else:
                # Normal Player
                if base.localAvatar.chatMode == 0:
                    # Check if the localAvatar is chatless.
                    self.understandable = 0
                else:
                    # localAvatar has SpeedChat Plus, Depend on the chat mode of the other player.
                    self.understandable = self.chatMode
                self.setPlayerType(NametagGlobals.CCSpeedChat)
        elif self.playerType == NametagGlobals.CCSuit:
            # Cog
            self.understandable = 1
            self.setPlayerType(self.playerType)
        else:
            # Everything else
            self.understandable = 0
            self.setPlayerType(self.playerType)

        if self.nametag:
            nametagColor = NametagGlobals.NametagColors[self.playerType]
            self.nametag.setNametagColor(nametagColor)
            chatColor = NametagGlobals.ChatColors[self.playerType]
            self.nametag.setChatColor(chatColor)
            self.nametag.updateAll()
        else:
            self.notify.warning('no nametag attributed, but would have been used')

    def isUnderstandable(self):
        return self.understandable

    def setDNAString(self, dnaString):
        pass

    def setDNA(self, dna):
        pass

    def setAvatarScale(self, scale):
        if self.scale != scale:
            self.scale = scale
            self.getGeomNode().setScale(scale)
            self.setHeight(self.height)

    def getNametagScale(self):
        return self.nametag3d.getScale()

    def setNametagScale(self, scale):
        self.nametag3d.setScale(scale)

    def adjustNametag3d(self, parentScale=1.0):
        self.nametag3d.setPos(0, 0, self.height + 0.5)

    def getHeight(self):
        return self.height

    def setHeight(self, height):
        self.height = height
        self.adjustNametag3d()
        if self.collTube:
            self.collTube.setPointB(0, 0, height - self.getRadius())
            if self.collNodePath:
                self.collNodePath.forceRecomputeBounds()

    def getRadius(self):
        return self.radius

    def getName(self):
        return self.name

    def setName(self, name):
        if self.isDisguised:
            return
        self.name = name
        if self.nametag:
            self.nametag.setText(name)

    def setDisplayName(self, str):
        if self.isDisguised:
            return
        self.nametag.setText(str)

    def getFont(self):
        if not self.nametag:
            return OTPGlobals.getInterfaceFont()
        return self.nametag.getFont()

    def setFont(self, font):
        self.nametag.setFont(font)
        self.nametag.setChatFont(font)
        
    def setGuildText(self, text):
        self.nametag.setGuildText(text)
    
    def getGuildText(self):
        if self.nametag is None:
            return None
        return self.nametag.getGuildText()

    def getStyle(self):
        return self.style

    def setStyle(self, style):
        self.style = style

    def getDialogueArray(self):
        return None

    def playCurrentDialogue(self, dialogue, chatFlags, interrupt = 1):
        if interrupt and self.__currentDialogue is not None:
            self.__currentDialogue.stop()
        self.__currentDialogue = dialogue
        if dialogue:
            base.playSfx(dialogue, node=self)
        elif chatFlags & CFSpeech != 0 and self.nametag.getNumChatPages() > 0:
            self.playDialogueForString(self.nametag.getChatText())
            if self.soundChatBubble != None:
                base.playSfx(self.soundChatBubble, node=self)

    def playDialogueForString(self, chatString):
        searchString = chatString.lower()
        if searchString.find(OTPLocalizer.DialogSpecial) >= 0:
            type = 'special'
        elif searchString.find(OTPLocalizer.DialogExclamation) >= 0:
            type = 'exclamation'
        elif searchString.find(OTPLocalizer.DialogQuestion) >= 0:
            type = 'question'
        elif random.randint(0, 1):
            type = 'statementA'
        else:
            type = 'statementB'
        stringLength = len(chatString)
        if stringLength <= OTPLocalizer.DialogLength1:
            length = 1
        elif stringLength <= OTPLocalizer.DialogLength2:
            length = 2
        elif stringLength <= OTPLocalizer.DialogLength3:
            length = 3
        else:
            length = 4
        self.playDialogue(type, length)

    def playDialogue(self, type, length):
        dialogSfx = self.getDialogueSfx(type, length)
        if dialogSfx is not None:
            base.playSfx(dialogSfx, node=self)

    def getDialogueSfx(self, type, length):
        retval = None
        dialogueArray = self.getDialogueArray()
        if dialogueArray is None:
            return
        sfxIndex = None
        if type == 'statementA' or type == 'statementB':
            if length == 1:
                sfxIndex = 0
            elif length == 2:
                sfxIndex = 1
            elif length >= 3:
                sfxIndex = 2
        elif type == 'question':
            sfxIndex = 3
        elif type == 'exclamation':
            sfxIndex = 4
        elif type == 'special':
            sfxIndex = 5
        else:
            self.notify.error('unrecognized dialogue type: ', type)
        if sfxIndex != None and sfxIndex < len(dialogueArray) and dialogueArray[sfxIndex] != None:
            retval = dialogueArray[sfxIndex]
        return retval

    def setChatAbsolute(self, chatString, chatFlags, dialogue=None, interrupt=1):
        self.clearChat()

        if chatFlags & CFQuicktalker:
            self.nametag.setChatType(NametagGlobals.SPEEDCHAT)
        else:
            self.nametag.setChatType(NametagGlobals.CHAT)

        if chatFlags & CFThought:
            self.nametag.setChatBalloonType(NametagGlobals.THOUGHT_BALLOON)
        else:
            self.nametag.setChatBalloonType(NametagGlobals.CHAT_BALLOON)

        if chatFlags & CFPageButton:
            self.nametag.setChatButton(NametagGlobals.pageButton)
        else:
            self.nametag.setChatButton(NametagGlobals.noButton)

        if chatFlags & CFReversed:
            self.nametag.setChatReversed(True)
        else:
            self.nametag.setChatReversed(False)

        self.nametag.setChatText(chatString, timeout=(chatFlags & CFTimeout))
        self.playCurrentDialogue(dialogue, chatFlags, interrupt)

    def setChatMuted(self, chatString, chatFlags, dialogue = None, interrupt = 1, quiet = 0):
        pass

    def displayTalk(self, chatString, timestamp=None):
        if not base.cr.ttiFriendsManager.checkIgnored(self.doId):
            self.clearChat()
            self.nametag.setChatType(NametagGlobals.CHAT)
            self.nametag.setChatButton(NametagGlobals.noButton)
            if isThought(chatString):
                chatString = base.talkAssistant.removeThoughtPrefix(chatString)
                self.nametag.setChatBalloonType(NametagGlobals.THOUGHT_BALLOON)
                self.nametag.setChatText(chatString)
            else:
                self.nametag.setChatBalloonType(NametagGlobals.CHAT_BALLOON)
                self.nametag.setChatText(chatString, timeout=True)

    def clearChat(self):
        self.nametag.clearChatText()

    def isInView(self):
        pos = self.getPos(base.camera)
        eyePos = Point3(pos[0], pos[1], pos[2] + self.getHeight())
        return base.camNode.isInView(eyePos)

    def getNameVisible(self):
        return self.__nameVisible

    def setNameVisible(self, visible):
        self.__nameVisible = visible
        if visible:
            self.showName()
        if not visible:
            self.hideName()

    def hideName(self):
        nametag3d = self.nametag.getNametag3d()
        nametag3d.hideNametag()
        nametag3d.showChat()
        nametag3d.showThought()
        nametag3d.update()

    def showName(self):
        if self.__nameVisible and (not self.ghostMode):
            nametag3d = self.nametag.getNametag3d()
            nametag3d.showNametag()
            nametag3d.showChat()
            nametag3d.showThought()
            nametag3d.update()

    def hideNametag2d(self):
        nametag2d = self.nametag.getNametag2d()
        nametag2d.hideNametag()
        nametag2d.hideChat()
        nametag2d.update()

    def showNametag2d(self):
        nametag2d = self.nametag.getNametag2d()
        if not self.ghostMode:
            nametag2d.showNametag()
            nametag2d.showChat()
        else:
            nametag2d.hideNametag()
            nametag2d.hideChat()
        nametag2d.update()

    def hideNametag3d(self):
        nametag3d = self.nametag.getNametag3d()
        nametag3d.hideNametag()
        nametag3d.hideChat()
        nametag3d.hideThought()
        nametag3d.update()

    def showNametag3d(self):
        nametag3d = self.nametag.getNametag3d()
        if self.__nameVisible and (not self.ghostMode):
            nametag3d.showNametag()
            nametag3d.showChat()
            nametag3d.showThought()
        else:
            nametag3d.hideNametag()
            nametag3d.hideChat()
            nametag3d.hideThought()
        nametag3d.update()

    def setPickable(self, flag):
        self.nametag.setActive(flag)

    def clickedNametag(self):
        MagicWordManager.lastClickedNametag = self
        if self.nametag.getChatText() and self.nametag.hasChatButton():
            self.advancePageNumber()
        elif self.nametag.getActive():
            messenger.send(EventGlobals.ClickedNameTag, [self])

    def setPageChat(self, addressee, paragraph, message, quitButton,
                    extraChatFlags=None, dialogueList=None, pageButton=True):
        self.__chatAddressee = addressee
        self.__chatPageNumber = None
        self.__chatParagraph = paragraph
        self.__chatMessage = message
        self.__chatFlags = CFSpeech
        if extraChatFlags is not None:
            self.__chatFlags |= extraChatFlags
        self.__chatDialogueList = dialogueList if dialogueList is not None else []
        self.__chatSet = 0
        self.__chatLocal = 0
        self.__updatePageChat()
        if addressee == base.localAvatar.doId:
            if pageButton:
                self.__chatFlags |= CFPageButton
            self.__chatQuitButton = quitButton
            self.b_setPageNumber(self.__chatParagraph, 0)

    def setLocalPageChat(self, message, quitButton, extraChatFlags=None,
                         dialogueList=None):
        self.__chatAddressee = base.localAvatar.doId
        self.__chatPageNumber = None
        self.__chatParagraph = None
        self.__chatMessage = message
        self.__chatFlags = CFSpeech
        if extraChatFlags is not None:
            self.__chatFlags |= extraChatFlags
        self.__chatDialogueList = dialogueList if dialogueList is not None else []
        self.__chatSet = 1
        self.__chatLocal = 1
        self.__chatFlags |= CFPageButton
        self.__chatQuitButton = quitButton
        if len(self.__chatDialogueList) > 0:
            dialogue = self.__chatDialogueList[0]
        else:
            dialogue = None
        self.clearChat()
        self.setChatAbsolute(message, self.__chatFlags, dialogue)
        self.setPageNumber(None, 0)

    def setPageNumber(self, paragraph, pageNumber, timestamp=None):
        if timestamp is None:
            elapsed = 0.0
        else:
            elapsed = ClockDelta.globalClockDelta.localElapsedTime(timestamp)
        self.__chatPageNumber = [paragraph, pageNumber]
        self.__updatePageChat()
        if hasattr(self, 'uniqueName'):
            if pageNumber >= 0:
                messenger.send(self.uniqueName('nextChatPage'), [pageNumber, elapsed])
            else:
                messenger.send(self.uniqueName('doneChatPage'), [elapsed])
        elif pageNumber >= 0:
            messenger.send('nextChatPage', [pageNumber, elapsed])
        else:
            messenger.send('doneChatPage', [elapsed])

    def advancePageNumber(self):
        if (self.__chatAddressee == base.localAvatar.doId) and (
            self.__chatPageNumber is not None) and (
            self.__chatPageNumber[0] == self.__chatParagraph):
            pageNumber = self.__chatPageNumber[1]
            if pageNumber >= 0:
                pageNumber += 1
                if pageNumber >= self.nametag.getNumChatPages():
                    pageNumber = -1
                if self.__chatQuitButton:
                    if pageNumber == self.nametag.getNumChatPages() - 1:
                        self.nametag.setChatButton(NametagGlobals.quitButton)
                if self.__chatLocal:
                    self.setPageNumber(self.__chatParagraph, pageNumber)
                else:
                    self.b_setPageNumber(self.__chatParagraph, pageNumber)

    def __updatePageChat(self):
        if (self.__chatPageNumber is not None) and (
            self.__chatPageNumber[0] == self.__chatParagraph):
            pageNumber = self.__chatPageNumber[1]
            if pageNumber >= 0:
                if not self.__chatSet:
                    if len(self.__chatDialogueList) > 0:
                        dialogue = self.__chatDialogueList[0]
                    else:
                        dialogue = None
                    self.setChatAbsolute(self.__chatMessage, self.__chatFlags, dialogue)
                    self.__chatSet = 1
                if pageNumber < self.nametag.getNumChatPages():
                    if (self.__chatAddressee == base.localAvatar.doId) and self.__chatQuitButton:
                        if pageNumber == self.nametag.getNumChatPages() - 1:
                            self.nametag.setChatButton(NametagGlobals.quitButton)
                    self.nametag.setChatPageIndex(pageNumber)
                    if pageNumber > 0:
                        if len(self.__chatDialogueList) > pageNumber:
                            dialogue = self.__chatDialogueList[pageNumber]
                        else:
                            dialogue = None
                        self.playCurrentDialogue(dialogue, self.__chatFlags)
                else:
                    self.clearChat()
            else:
                self.clearChat()

    def getAirborneHeight(self):
        height = self.getPos(self.shadowPlacer.shadowNodePath)
        return height.getZ() + 0.025

    def initializeNametag3d(self):
        self.deleteNametag3d()
        nametagNode = self.nametag.getNametag3d()
        self.nametagNodePath = self.nametag3d.attachNewNode(nametagNode)
        for cJoint in self.getNametagJoints():
            cJoint.clearNetTransforms()
            cJoint.addNetTransform(nametagNode)

    def nametagAmbientLightChanged(self, newlight):
        self.nametag3d.setLightOff()
        if newlight:
            self.nametag3d.setLight(newlight)

    def deleteNametag3d(self):
        if self.nametagNodePath:
            self.nametagNodePath.removeNode()
            self.nametagNodePath = None

    def initializeBodyCollisions(self, collIdStr):
        self.collTube = CollisionTube(0, 0, 0.5, 0, 0, self.height - self.getRadius(), self.getRadius())
        self.collNode = CollisionNode(collIdStr)
        self.collNode.addSolid(self.collTube)
        self.collNodePath = self.attachNewNode(self.collNode)
        if self.ghostMode:
            self.collNode.setCollideMask(OTPGlobals.GhostBitmask)
        else:
            self.collNode.setCollideMask(OTPGlobals.WallBitmask)

    def stashBodyCollisions(self):
        if self.collNodePath:
            self.collNodePath.stash()

    def unstashBodyCollisions(self):
        if self.collNodePath:
            self.collNodePath.unstash()

    def disableBodyCollisions(self):
        if self.collNodePath:
            self.collNodePath.removeNode()
            self.collNodePath = None
        self.collTube = None

    def isActive(self):
        return self in Avatar.ActiveAvatars

    def addActive(self):
        if (not base.wantNametags) or self.isActive():
            return
        
        Avatar.ActiveAvatars.append(self)
        self.nametag.manage(base.marginManager)
        self.accept(self.nametag.getUniqueName(), self.clickedNametag)

    def removeActive(self):
        if not base.wantNametags or not self.isActive():
            return
        
        Avatar.ActiveAvatars.remove(self)
        self.nametag.unmanage(base.marginManager)
        self.ignore(self.nametag.getUniqueName())

    def loop(self, animName, restart = 1, partName = None, fromFrame = None, toFrame = None):
        return Actor.loop(self, animName, restart, partName, fromFrame, toFrame)


@magicWord(category=CATEGORY_MODERATOR)
def target():
    """
    Returns the current Spellbook target.
    """
    target = spellbook.getTarget()
    return 'Target: %s-%d [%d]' % (target.getName(), target.doId, target.getAdminAccess())
