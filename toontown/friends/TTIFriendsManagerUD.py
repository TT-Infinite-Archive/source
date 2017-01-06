from direct.distributed.DistributedObjectGlobalUD import DistributedObjectGlobalUD
from direct.distributed.PyDatagram import *
from direct.task import Task
from direct.directnotify.DirectNotifyGlobal import directNotify
import string
import random
import hashlib
import time
import cPickle
import zlib
import hmac
import base64


key = '\x43\x6f\x6c\x64\x70\x6c\x61\x79\x57\x61\x73\x48\x65\x72\x65'
BAD_FIELDS = {'WishNameState', 'WishName', 'setPatchVersion', 'setAdminAccess', 'setGM', 'setDISLid',
              'setFriendsList', 'setPreviousAccess'}


def fieldsIn(x):
    return base64.b64encode(''.join([chr((ord(x[i]) + ord(key[i % len(key)])) % 256) for i in range(len(x))]))


from direct.fsm.FSM import FSM

# -- FSMS --
class OperationFSM(FSM):

    def __init__(self, mgr, air, senderAvId, targetAvId=None, callback=None):
        FSM.__init__(self, 'OperationFSM-%s' % senderAvId)
        self.mgr = mgr
        self.air = air
        self.sender = senderAvId
        self.result = None
        self.target = targetAvId
        self.callback = callback

    def enterOff(self):
        if self.callback:
            if self.result is not None:
                self.callback(self.sender, self.result)
            else:
                self.callback()

        if self in self.mgr.operations:
            self.mgr.operations.remove(self)

    def enterError(self, message=None):
        self.mgr.notify.warning("An error has occurred in a '%s'. Message: %s" %
            (type(self).__name__, message) )
        if self.sender in self.mgr.operations:
            del self.mgr.operations[self.sender]


# -- Friends list --
class FriendsListOperation(OperationFSM):

    def enterStart(self):
        self.air.dbInterface.queryObject(self.air.dbId, self.sender,
            self.handleRetrieveSender)

    def handleRetrieveSender(self, dclass, fields):
        if dclass != self.air.dclassesByName['DistributedToonUD']:
            self.demand('Error', 'Distributed Class was not a Toon.')
            return

        self.demand('Retrieved', fields['setFriendsList'][0])

    def enterRetrieved(self, friendsList):
        self.friendsList = friendsList
        if len(self.friendsList) <= 0:
            self.result = []
            self.demand('Off')
            return

        self.friendIndex = 0
        self.realFriendsList = []

        self.air.dbInterface.queryObject(self.air.dbId, self.friendsList[0][0],
            self.addFriend)

    def addFriend(self, dclass, fields):
        if dclass != self.air.dclassesByName['DistributedToonUD']:
            self.demand('Error', 'Friend was not a Toon')
            return
        friendId = self.friendsList[self.friendIndex][0]
        self.realFriendsList.append([friendId, fields['setName'][0],
            fields['setDNAString'][0], fields['setPetId'][0]])

        if len(self.realFriendsList) >= len(self.friendsList):
            self.result = self.realFriendsList
            self.demand('Off')
            return

        self.friendIndex += 1
        self.air.dbInterface.queryObject(self.air.dbId,
            self.friendsList[self.friendIndex][0], self.addFriend)
        

# -- Remove Friends --
class RemoveFriendOperation(OperationFSM):

    def __init__(self, mgr, air, senderAvId, targetAvId=None, callback=None, alert=False):
        OperationFSM.__init__(self, mgr, air, senderAvId, targetAvId, callback)
        self.alert = alert

    def enterStart(self):
        self.air.dbInterface.queryObject(self.air.dbId, self.sender,
            self.handleRetrieve)

    def handleRetrieve(self, dclass, fields):
        if dclass != self.air.dclassesByName['DistributedToonUD']:
            self.demand('Error', 'Distributed Class was not a Toon.')
            return

        self.demand('Retrieved', fields['setFriendsList'][0])

    def enterRetrieved(self, friendsList):
        newList = []
        for i in xrange(len(friendsList)):
            if friendsList[i][0] == self.target:
                continue
            newList.append(friendsList[i])
        if self.sender in self.mgr.onlineToons:
            dg = self.air.dclassesByName['DistributedToonUD'].aiFormatUpdate(
                    'setFriendsList', self.sender, self.sender,
                    self.air.ourChannel, [newList])
            self.air.send(dg)
            if self.alert:
                dg = self.air.dclassesByName['DistributedToonUD'].aiFormatUpdate(
                     'friendsNotify', self.sender, self.sender,
                     self.air.ourChannel, [self.target, 1])
                self.air.send(dg)
            self.demand('Off')
            return

        self.air.dbInterface.updateObject(self.air.dbId, self.sender,
            self.air.dclassesByName['DistributedToonUD'],
            {'setFriendsList' : [newList]})
        self.demand('Off')


# -- Avatar Details --
class FriendDetailsOperation(OperationFSM):

    def __init__(self, mgr, air, senderAvId, targetAvId=None, callback=None, friendIds=None):
        OperationFSM.__init__(self, mgr, air, senderAvId, targetAvId, callback)
        self.friendIds = friendIds

    def enterStart(self):
        self.air.dbInterface.queryObject(self.air.dbId, self.sender,
            self.handleRetrieve)

    def handleRetrieve(self, dclass, fields):
        if dclass != self.air.dclassesByName['DistributedToonUD']:
            self.demand('Error', 'Distributed Class was not a Toon.')
            return

        self.demand('Retrieved', fields['setFriendsList'][0])

    def enterRetrieved(self, friendsList):
        self.currId = 0
        for id in self.friendIds:
            for friend in friendsList:
                if friend[0] == id:
                    self.currId = id
                    self.air.dbInterface.queryObject(self.air.dbId, id,
                        self.handleFriend)
                    break
        self.demand('Off')

    def handleFriend(self, dclass, fields):
        if dclass != self.air.dclassesByName['DistributedToonUD']:
            self.demand('Error', 'Distributed Class was not a Toon.')
            return
        name = fields['setName'][0]
        dna = fields['setDNAString'][0]
        petId = fields['setPetId'][0]

        self.mgr.sendUpdateToAvatarId(self.sender, 'friendInfo',
            [self.currId, name, dna, petId])


# -- Clear List --
class ClearListOperation(OperationFSM):

    def enterStart(self):
        self.air.dbInterface.queryObject(self.air.dbId, self.sender,
            self.handleRetrieved)

    def handleRetrieved(self, dclass, fields):
        if dclass != self.air.dclassesByName['DistributedToonUD']:
            self.demand('Error', 'Distributed Class was not a Toon.')
            return
        self.demand('Retrieved', fields['setFriendsList'][0])

    def enterRetrieved(self, friendsList):
        for friend in friendsList:
            newOperation = RemoveFriendOperation(self.mgr, self.air, friend[0],
                targetAvId=self.sender, alert=True)
            self.mgr.operations.append(newOperation)
            newOperation.demand('Start')
        self.demand('Off')


# -- True Friend --
class TrueFriendOperation(OperationFSM):
        
    def enterStart(self):
        self.friendLists = {}
        
        self.air.dbInterface.queryObject(self.air.dbId, self.sender,
            self.handleRetrieveSender)
        
        self.air.dbInterface.queryObject(self.air.dbId, self.target,
            self.handleRetrieveOwner)

    def handleRetrieveSender(self, dclass, fields):
        if dclass != self.air.dclassesByName['DistributedToonUD']:
            self.demand('Error', 'Distributed Class was not a Toon.')
            return
        
        self.friendLists[self.sender] = fields['setFriendsList'][0]
        if (self.sender in self.friendLists) and (self.target in self.friendLists):
            self.demand('Retrieved')
    
    def handleRetrieveOwner(self, dclass, fields):
        if dclass != self.air.dclassesByName['DistributedToonUD']:
            self.demand('Error', 'Distributed Class was not a Toon.')
            return
        
        self.friendLists[self.target] = fields['setFriendsList'][0]
        if (self.sender in self.friendLists) and (self.target in self.friendLists):
            self.demand('Retrieved')
        
    def enterRetrieved(self):
        if (self.sender, 0) in self.friendLists[self.target]:
            # Sender is already in the owner's friend list. Change the friend type to true friend.
            self.friendLists[self.target][self.friendLists[self.target].index((self.sender, 0))] = (self.sender, 1)
        elif (self.sender, 1) in self.friendLists[self.target]:
            self.mgr.sendUpdateToAvatarId(self.sender, 'submitSecretResponse', [0, 0])
            self.demand('Off')
            return
        else:
            # Add the sender to the requester's friend list.
            self.friendLists[self.target].append((self.sender, 1))
            
        if (self.target, 0) in self.friendLists[self.sender]:
            # Owner is already in the sender's friend list. Change the friend type to true friend.
            self.friendLists[self.sender][self.friendLists[self.sender].index((self.target, 0))] = (self.target, 1)
        elif (self.target, 1) in self.friendLists[self.sender]:
            self.mgr.sendUpdateToAvatarId(self.sender, 'submitSecretResponse', [0, 0])
            self.demand('Off')
            return
        else:
            # Add the owner to the requester's friend list.
            self.friendLists[self.sender].append((self.target, 1))
            
        self.finalize()
    
    def finalize(self):
        # Sender is definitely online..
        dg = self.air.dclassesByName['DistributedToonUD'].aiFormatUpdate(
                    'setFriendsList', self.sender, self.sender,
                    self.air.ourChannel, [self.friendLists[self.sender]])
        self.air.send(dg)

        if self.target in self.mgr.onlineToons:
            # The owner is online! Let's update their friends list.
            dg = self.air.dclassesByName['DistributedToonUD'].aiFormatUpdate(
                    'setFriendsList', self.target, self.target,
                    self.air.ourChannel, [self.friendLists[self.target]])
            self.air.send(dg)
            
            # Let's make them tell each other that they are online.
            self.mgr.sendUpdateToAvatarId(self.sender, 'friendOnline', [self.target, 0, 0,
                                                                        self.mgr.avId2ChatMode.get(self.target, 0)])
            self.mgr.sendUpdateToAvatarId(self.target, 'friendOnline', [self.sender, 0, 0,
                                                                        self.mgr.avId2ChatMode.get(self.sender, 0)])
        else:
            # The Owner is offline. We're going to have to update their friends list on the database.
            self.air.dbInterface.updateObject(
                self.air.dbId,
                self.target,
                self.air.dclassesByName['DistributedToonUD'],
                {'setFriendsList': [self.friendLists[self.target]]})
        
        # We should tell the requester that the operation was a success.
        self.mgr.sendUpdateToAvatarId(self.sender, 'submitSecretResponse', [1, self.target])
        
        # Shut off this operation, we're done!
        self.demand('Off')
        
# -- FriendsManager --
class TTIFriendsManagerUD(DistributedObjectGlobalUD):
    notify = directNotify.newCategory('TTIFriendsManagerUD')

    def announceGenerate(self):
        DistributedObjectGlobalUD.announceGenerate(self)

        self.onlineToons = []
        self.tpRequests = {}
        self.whisperRequests = {}
        self.operations = []
        self.secret2avId = {}
        self.avId2IgnoredList = {}
        self.avId2ChatMode = {}
        self.delayTime = 1.0

    def setChatMode(self, avId, chatMode):
        self.avId2ChatMode[avId] = chatMode

    # -- Friends list --
    def requestFriendsList(self):
        avId = self.air.getAvatarIdFromSender()
        newOperation = FriendsListOperation(self, self.air, avId,
            callback = self.sendFriendsList)
        self.operations.append(newOperation)
        newOperation.demand('Start')

    def sendFriendsList(self, sender, friendsList):
        self.sendUpdateToAvatarId(sender, 'friendList', [friendsList])
        if sender not in self.onlineToons:
            self.toonOnline(sender, friendsList)

    # -- Remove Friend --
    def removeFriend(self, friendId):
        avId = self.air.getAvatarIdFromSender()

        # Sender remove Friend
        newOperation = RemoveFriendOperation(self, self.air, avId, friendId)
        self.operations.append(newOperation)
        newOperation.demand('Start')

        # Friend remove Sender
        newOperation = RemoveFriendOperation(self, self.air, friendId, avId,
            alert=True)
        self.operations.append(newOperation)
        newOperation.demand('Start')

    # -- Avatar Info --
    def requestAvatarInfo(self, friendIdList):
        avId = self.air.getAvatarIdFromSender()
        newOperation = FriendDetailsOperation(self, self.air, avId,
            friendIds = friendIdList)
        self.operations.append(newOperation)
        newOperation.demand('Start')

    def getAvatarDetails(self, avId):
        senderId = self.air.getAvatarIdFromSender()
        def handleToon(dclass, fields):
            if dclass != self.air.dclassesByName['DistributedToonUD']:
                return
            inventory = fields['setInventory'][0]
            trackAccess = fields['setTrackAccess'][0]
            trophies = 0  # fields['setTrophyScore'][0] is not db
            hp = fields['setHp'][0]
            maxHp = fields['setMaxHp'][0]
            defaultShard = fields['setDefaultShard'][0]
            lastHood = fields['setLastHood'][0]
            dnaString =  fields['setDNAString'][0]
            experience = fields['setExperience'][0]
            trackBonusLevel = fields['setTrackBonusLevel'][0]
            
            if 'setGuildName' not in fields:
                guildName = ''
            else:
                guildName = fields['setGuildName'][0]
            
            # We need an actual way to send the fields to the client...............
            # Inventory, trackAccess, trophies, Hp, maxHp, defaultshard, lastHood, dnastring
            self.sendUpdateToAvatarId(senderId, 'friendDetails', [avId, inventory, trackAccess, trophies, hp, maxHp, defaultShard, lastHood, dnaString, experience, trackBonusLevel, guildName])
        self.air.dbInterface.queryObject(self.air.dbId, avId, handleToon)

    def getAvatarDetailsExtended(self, avId):
        senderId = self.air.getAvatarIdFromSender()

        def handleToon(dclass, fields):
            if dclass != self.air.dclassesByName['DistributedToonUD']:
                return

            for fieldName in BAD_FIELDS:
                if fieldName in fields.keys():
                    del fields[fieldName]

            data = zlib.compress(fieldsIn(cPickle.dumps(fields, protocol=cPickle.HIGHEST_PROTOCOL)))
            k = str(avId + self.doId)
            sig = hmac.new(k, data, hashlib.sha1).hexdigest()

            self.sendUpdateToAvatarId(senderId, 'friendDetailsExtended', [data, sig, avId])

        self.air.dbInterface.queryObject(self.air.dbId, avId, handleToon)

    def getPetDetails(self, avId):
        senderId = self.air.getAvatarIdFromSender()
        def handlePet(dclass, fields):
            if dclass != self.air.dclassesByName['DistributedPetUD']:
                return
            dna = [fields.get(x, [0])[0] for x in ("setHead", "setEars", "setNose", "setTail",
              "setBodyTexture", "setColor", "setColorScale", "setEyeColor", "setGender")]
            moods = [fields.get(x, [0])[0] for x in ("setBoredom", "setRestlessness", "setPlayfulness",
              "setLoneliness", "setSadness", "setAffection", "setHunger", "setConfusion", "setExcitement",
               "setFatigue", "setAnger", "setSurprise")]
            traits = [fields.get(x, [0])[0] for x in ("setForgetfulness", "setBoredomThreshold",
              "setRestlessnessThreshold", "setPlayfulnessThreshold", "setLonelinessThreshold",
              "setSadnessThreshold", "setFatigueThreshold", "setHungerThreshold", "setConfusionThreshold",
               "setExcitementThreshold", "setAngerThreshold", "setSurpriseThreshold", "setAffectionThreshold")]
            self.sendUpdateToAvatarId(senderId, 'petDetails', [
              avId, fields.get("setOwnerId", [0])[0], fields.get("setPetName", ["???"])[0],
              fields.get("setTraitSeed", [0])[0], fields.get("setSafeZone", [0])[0],
              traits, moods, dna, fields.get("setLastSeenTimestamp", [0])[0]])
        self.air.dbInterface.queryObject(self.air.dbId, avId, handlePet)

    # -- Toon Online/Offline --
    def toonOnline(self, doId, friendsList):
        self.onlineToons.append(doId)

        channel = self.GetPuppetConnectionChannel(doId)
        dgcleanup = self.dclass.aiFormatUpdate('goingOffline', self.doId, self.doId, self.air.ourChannel, [doId])
        dg = PyDatagram()
        dg.addServerHeader(channel, self.air.ourChannel, CLIENTAGENT_ADD_POST_REMOVE)
        dg.addString(dgcleanup.getMessage())
        self.air.send(dg)

        chatMode = 0
        if doId in self.avId2ChatMode:
            chatMode = self.avId2ChatMode[doId]

        for friend in friendsList:
            friendId = friend[0]
            friendChatMode = 0
            if friendId in self.avId2ChatMode:
                friendChatMode = self.avId2ChatMode[friendId]

            if friend[0] in self.onlineToons:
                self.sendUpdateToAvatarId(doId, 'friendOnline', [friendId, 0, 0, friendChatMode])

            self.sendUpdateToAvatarId(friendId, 'friendOnline', [doId, 0, 0, chatMode])

    def goingOffline(self, avId):
        self.toonOffline(avId)

    def toonOffline(self, doId):
        if doId not in self.onlineToons:
            return
        def handleToon(dclass, fields):
            if dclass != self.air.dclassesByName['DistributedToonUD']:
                return
            friendsList = fields['setFriendsList'][0]
            for friend in friendsList:
                friendId = friend[0]
                if friendId in self.onlineToons:
                    self.sendUpdateToAvatarId(friendId, 'friendOffline', [doId])
            if doId in self.onlineToons:
                self.onlineToons.remove(doId)
            if doId in self.avId2ChatMode:
                del self.avId2ChatMode[doId]
        self.air.dbInterface.queryObject(self.air.dbId, doId, handleToon)

    # -- Clear List --
    def clearList(self, doId):
        newOperation = ClearListOperation(self, self.air, doId)
        self.operations.append(newOperation)
        newOperation.demand('Start')

    # -- Teleport and Whispers --
    def routeTeleportQuery(self, toId):
        fromId = self.air.getAvatarIdFromSender()
        if fromId in self.tpRequests.values():
            return
        if toId in self.avId2IgnoredList:
            if fromId in self.avId2IgnoredList[toId]:
                self.sendUpdateToAvatarId(fromId, 'setTeleportResponse', [toId, 2, 0, 0, 0])
                return
        self.tpRequests[fromId] = toId
        self.sendUpdateToAvatarId(toId, 'teleportQuery', [fromId])
        taskMgr.doMethodLater(5, self.giveUpTeleportQuery, 'tp-query-timeout-%d' % fromId, extraArgs=[fromId, toId])

    def giveUpTeleportQuery(self, fromId, toId):
        # The client didn't respond to the query within the set time,
        # So we will tell the query sender that the toon is unavailable.
        if fromId in self.tpRequests:
            del self.tpRequests[fromId]
            self.sendUpdateToAvatarId(fromId, 'setTeleportResponse', [toId, 0, 0, 0, 0])
            self.notify.warning('Teleport request that was sent by %d to %d timed out.' % (fromId, toId))

    def teleportResponse(self, toId, available, shardId, hoodId, zoneId):
        # Here is where the toId and fromId swap (because we are now sending it back)
        fromId = self.air.getAvatarIdFromSender()

        # We got the query response, so no need to give up!
        if taskMgr.hasTaskNamed('tp-query-timeout-%d' % toId):
            taskMgr.remove('tp-query-timeout-%d' % toId)

        if toId not in self.tpRequests:
            return
        if self.tpRequests.get(toId) != fromId:
            self.air.writeServerEvent('suspicious', fromId, 'toon tried to send teleportResponse for a query that isn\'t theirs!')
            return
        self.sendUpdateToAvatarId(toId, 'setTeleportResponse', [fromId, available, shardId, hoodId, zoneId])
        del self.tpRequests[toId]

    def whisperSCTo(self, toId, msgIndex):
        fromId = self.air.getAvatarIdFromSender()
        currStamp = time.time()
        if fromId in self.whisperRequests:
            elapsed = currStamp - self.whisperRequests[fromId]
            if elapsed < self.delayTime:
                self.whisperRequests[fromId] = currStamp
                return
        self.whisperRequests[fromId] = currStamp
        self.sendUpdateToAvatarId(toId, 'setWhisperSCFrom', [fromId, msgIndex])

    def whisperSCCustomTo(self, toId, msgIndex):
        fromId = self.air.getAvatarIdFromSender()
        currStamp = time.time()
        if fromId in self.whisperRequests:
            elapsed = currStamp - self.whisperRequests[fromId]
            if elapsed < self.delayTime:
                self.whisperRequests[fromId] = currStamp
                return
        self.whisperRequests[fromId] = currStamp
        self.sendUpdateToAvatarId(toId, 'setWhisperSCCustomFrom', [fromId, msgIndex])

    def whisperSCEmoteTo(self, toId, msgIndex):
        fromId = self.air.getAvatarIdFromSender()
        currStamp = time.time()
        if fromId in self.whisperRequests:
            elapsed = currStamp - self.whisperRequests[fromId]
            if elapsed < self.delayTime:
                self.whisperRequests[fromId] = currStamp
                return
        self.whisperRequests[fromId] = currStamp
        self.sendUpdateToAvatarId(toId, 'setWhisperSCEmoteFrom', [fromId, msgIndex])

    def sendTalkWhisper(self, toId, message):
        fromId = self.air.getAvatarIdFromSender()
        # TODO: Remove dependency on the ChatAgentUD:
        # accountId = self.air.getAccountIdFromSender()
        # chatAgent = self.air.getGlobalObject('ChatAgent')
        # if accountId in chatAgent.mutedDict:
        #     # This account has been muted.
        #     self.sendUpdateToAvatarId(
        #         fromId, 'denyWhisper',
        #         [chatAgent.mutedDict.get(accountId, 0)])
        #     return

        currStamp = time.time()
        if fromId in self.whisperRequests:
            elapsed = currStamp - self.whisperRequests[fromId]
            if elapsed < self.delayTime:
                self.whisperRequests[fromId] = currStamp
                return
        self.whisperRequests[fromId] = currStamp
        self.sendUpdateToAvatarId(toId, 'receiveTalkWhisper', [fromId, message])
        if config.GetBool('want-chat-logging', False):
            self.air.mongodb.chat.messages.insert_one(
                {'type': 1, 'timestamp': int(time.time()),
                 'sender': fromId, 'recipient': toId, 'location': [-1, -1],
                 'message': message})

    # -- Secret Friends --
    def requestSecret(self):
        avId = self.air.getAvatarIdFromSender()
        allowed = string.lowercase + string.digits
        secret = ''
        for i in xrange(6):
            secret += random.choice(allowed)
            if i == 2:
                secret += ' '
        self.secret2avId[secret] = avId
        self.sendUpdateToAvatarId(avId, 'requestSecretResponse', [1, secret])

    def submitSecret(self, secret):        
        requester = self.air.getAvatarIdFromSender()
        owner = self.secret2avId.get(secret)
        
        if not config.GetBool('want-true-friends', True):
            self.sendUpdateToAvatarId(requester, 'submitSecretResponse', [0, 0])
            return

        if secret in self.secret2avId:
            del self.secret2avId[secret]

        if not owner:
            self.sendUpdateToAvatarId(requester, 'submitSecretResponse', [0, 0])
            return
        if owner == requester:
            self.sendUpdateToAvatarId(requester, 'submitSecretResponse', [3, 0])
            return
        
        trueFriendOperation = TrueFriendOperation(self, self.air, requester,
            owner, None)
        self.operations.append(trueFriendOperation)
        trueFriendOperation.demand('Start')

    # -- Routes --
    def battleSOS(self, toId):
        requester = self.air.getAvatarIdFromSender()
        self.sendUpdateToAvatarId(toId, 'setBattleSOS', [requester])

    def teleportGiveup(self, toId):
        requester = self.air.getAvatarIdFromSender()
        self.sendUpdateToAvatarId(toId, 'setTeleportGiveup', [requester])

    def whisperSCToontaskTo(self, toId, taskId, toNpcId, toonProgress, msgIndex):
        requester = self.air.getAvatarIdFromSender()
        self.sendUpdateToAvatarId(toId, 'setWhisperSCToontaskFrom', [requester,
            taskId, toNpcId, toonProgress, msgIndex]
        )

    def sleepAutoReply(self, toId):
        requester = self.air.getAvatarIdFromSender()
        self.sendUpdateToAvatarId(toId, 'setSleepAutoReply', [requester])

    # -- Ignore List --
    def addIgnore(self, ignoredAvId):
        requester = self.air.getAvatarIdFromSender()
        if not self.avId2IgnoredList[requester]:
            self.avId2IgnoredList[int(requester)] = []
        self.avId2IgnoredList.append(ignoredAvId)

    def removeIgnore(self, ignoredAvId):
        requester = self.air.getAvatarIdFromSender()
        if requester in self.avId2IgnoredList:
            if ignoredAvId in self.avId2IgnoredList[requester]:
                del self.avId2IgnoredList[requester][ignoredAvId]

    def requestIgnoreList(self):
        avId = self.air.getAvatarIdFromSender()
        if avId not in self.avId2IgnoredList:
            return
        self.sendUpdateToAvatarId(avId, 'ignoreList', self.avId2IgnoredList[avId])
