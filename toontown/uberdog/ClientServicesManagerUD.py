import semidbm
from direct.distributed.DistributedObjectGlobalUD import DistributedObjectGlobalUD
from direct.distributed.PyDatagram import *
from direct.fsm.FSM import FSM
from pandac.PandaModules import *
from datetime import datetime
import time
import random

from otp.ai.MagicWordGlobal import *
from otp.distributed import OtpDoGlobals
from toontown.makeatoon.NameGenerator import NameGenerator
from toontown.toon import ToonDNA
from toontown.toonbase import TTLocalizer
from toontown.uberdog.ClientServicesManager import generateLookupTable, encodeHexString


# Some constants for the operations we perform
NAME_APPROVED = 0
NAME_SUBMITTED = 1
NAME_SUBMISSION_ERROR = 2


accountdbType = simbase.config.GetString('accountdb-type', 'developer')

# If this config variable is set. All accounts new and old will use
# the specified access level.  It is meant to be used temporarily.
# NOTE: It doesn't replace the old account's access level, except for new ones.
forceAccessLevel = simbase.config.GetInt('force-access-level', 0)

accessLevelClamp = ConfigVariableString(
    'access-level-clamp', '100 700',
    "Specifies the range in which every user's access level will be confined to.").getValue()
accessLevelMin = int(accessLevelClamp.split(' ', 1)[0])
accessLevelMax = int(accessLevelClamp.split(' ', 1)[1])


# --- ACCOUNT DATABASES ---
# These classes make up the available account databases for Toontown Infinite.
# DeveloperAccountDB is a special database that accepts a username, and assigns
# each user with 700 access automatically upon login.

class AccountDB:
    notify = directNotify.newCategory('AccountDB')

    def __init__(self, csm):
        self.csm = csm

    def submitNameRequest(self, avId, name, callback, errback):
        callback(NAME_APPROVED)

    def isNameAcceptable(self, name, callback, errback):
        callback(True)

    def lookup(self, username, callback):
        pass  # Inheritors should override this.


class DeveloperAccountDB(AccountDB):
    notify = directNotify.newCategory('DeveloperAccountDB')
    
    def __init__(self, csm):
        AccountDB.__init__(self, csm)
        self.accessLevel = 700
        self.csm.air.dbAstronCursor.objects.create_index([('fields.ACCOUNT_ID', 1)])
    
    def lookupUserId(self, userId):
        document = self.csm.air.dbAstronCursor.objects.find_one({'fields.ACCOUNT_ID': userId})
        dict = {'userId': userId, 'success': True}
        
        if not document or 'dclass' not in document or document['dclass'] != 'Account':
            dict['accessLevel'] = self.accessLevel
            dict['accountId'] = 0
        else:
            dict['accessLevel'] = document['fields']['ACCESS_LEVEL']
            dict['accountId'] = document['_id']

        return dict
    
    def lookup(self, userId, callback):
        dict = self.lookupUserId(userId)
        callback(dict)
        return dict


class ProductionDB(AccountDB):
    notify = directNotify.newCategory('ProductionDB')

    def __init__(self, csm):
        AccountDB.__init__(self, csm)
        if simbase.isSinglePlayer:
            self.accessLevel = 700
        else:
            self.accessLevel = 100 # We set everyone in MP to 100 access by default. The host will need to set their access to 700 via mongo compass or rpc.
        self.csm.air.dbAstronCursor.objects.create_index([('fields.ACCOUNT_ID', 1)])

    def lookupUserId(self, userId):
        document = self.csm.air.dbAstronCursor.objects.find_one({'fields.ACCOUNT_ID': userId})
        dict = {'userId': userId, 'success': True}

        if not document or 'dclass' not in document or document['dclass'] != 'Account':
            dict['accessLevel'] = self.accessLevel
            dict['accountId'] = 0
        else:
            dict['accessLevel'] = document['fields']['ACCESS_LEVEL']
            dict['accountId'] = document['_id']

        return dict

    def lookup(self, userId, callback):
        dict = self.lookupUserId(userId)
        callback(dict)
        return dict

# Kaldron Network ProductionDB
"""
class ProductionDB(AccountDB):
    notify = directNotify.newCategory('ProductionDB')

    def submitNameRequest(self, avId, name, callback, errback):
        payload = {'distribution': config.GetString('distribution'), 'name': name}
        self.csm.air.webApi.execute('names/%d' % avId, payload, 'post', callback=callback, errback=errback)

    def isNameAcceptable(self, name, callback, errback):
        payload = {'name': name}
        self.csm.air.webApi.execute('acceptable-name', payload, 'get', callback=callback, errback=errback)

    def lookup(self, cookie, callback):
        payload = {'distribution': config.GetString('distribution'), 'cookie': cookie}
        self.csm.air.webApi.execute('cookies/consume', payload, 'delete', callback=self.lookupCallback,
                                    errback=self.lookupErrback, extraArgs=[callback])

    def lookupCallback(self, result, callback):
        response = {'success': False}

        if result['success'] is False:
            response['reason'] = 'Failed to authenticate login credentials.'
        else:
            response['success'] = True
            response['userId'] = result['userId']
            response['accessLevel'] = min(max(result['accessLevel'], accessLevelMin), accessLevelMax)

            lookup = self.lookupUserId(result['userId'])
            response['accountId'] = lookup['accountId']

        callback(response)

    def lookupErrback(self, callback):
        response = {
            'success': False,
            'reason': 'Failed to contact the account server.'
        }

        callback(response)
"""

# --- FSMs ---
class OperationFSM(FSM):
    TARGET_CONNECTION = False

    def __init__(self, csm, target):
        self.csm = csm
        self.target = target

        FSM.__init__(self, self.__class__.__name__)

    def enterKill(self, reason=''):
        if self.TARGET_CONNECTION:
            self.csm.killConnection(self.target, reason)
        else:
            self.csm.killAccount(self.target, reason)
        self.demand('Off')

    def enterOff(self):
        if self.TARGET_CONNECTION:
            del self.csm.connection2fsm[self.target]
        else:
            del self.csm.account2fsm[self.target]


class LoginAccountFSM(OperationFSM):
    notify = directNotify.newCategory('LoginAccountFSM')
    TARGET_CONNECTION = True

    def enterStart(self, token):
        self.token = token
        self.demand('QueryAccountDB')

    def enterQueryAccountDB(self):
        self.csm.accountDB.lookup(self.token, self.__handleLookup)

    def __handleLookup(self, result):
        if not result.get('success'):
            self.csm.air.writeServerEvent('tokenRejected', self.target, self.token)
            self.demand('Kill', result.get('reason', 'The account server rejected your token.'))
            return

        self.userId = result.get('userId', 0)
        self.accountId = result.get('accountId', 0)
        self.accessLevel = forceAccessLevel if forceAccessLevel else result.get('accessLevel', 0)
        if self.accountId:
            self.demand('RetrieveAccount')
        else:
            self.demand('CreateAccount')

    def enterRetrieveAccount(self):
        self.csm.air.dbInterface.queryObject(
            self.csm.air.dbId, self.accountId, self.__handleRetrieve)

    def __handleRetrieve(self, dclass, fields):
        if dclass != self.csm.air.dclassesByName['AccountUD']:
            self.demand('Kill', 'Your account object was not found in the database!')
            return

        self.account = fields
        self.demand('SetAccount')

    def enterCreateAccount(self):
        self.account = {
            'ACCOUNT_AV_SET': [0] * 6,
            'ESTATE_ID': 0,
            'ACCOUNT_AV_SET_DEL': [],
            'CREATED': time.ctime(),
            'LAST_LOGIN': time.ctime(),
            'ACCOUNT_ID': str(self.userId),
            'ACCESS_LEVEL': self.accessLevel,
            'MONEY': 0,
            'CHAT_MODE': 1
        }
        self.csm.air.dbInterface.createObject(
            self.csm.air.dbId,
            self.csm.air.dclassesByName['AccountUD'],
            self.account,
            self.__handleCreate)

    def __handleCreate(self, accountId):
        if self.state != 'CreateAccount':
            self.notify.warning('Received a create account response outside of the CreateAccount state.')
            return

        if not accountId:
            self.notify.warning('Database failed to construct an account object!')
            self.demand('Kill', 'Your account object could not be created in the game database.')
            return

        self.accountId = accountId
        self.csm.air.writeServerEvent('accountCreated', accountId)
        self.demand('SetAccount')

    def enterSetAccount(self):
        # If necessary, update their account information:
        if self.accessLevel and not forceAccessLevel:
            self.csm.air.dbInterface.updateObject(
                self.csm.air.dbId,
                self.accountId,
                self.csm.air.dclassesByName['AccountUD'],
                {'ACCESS_LEVEL': self.accessLevel})

        # If this is a single player server, Don't allow
        # any more connections.
        if simbase.isSinglePlayer: self.csm.playerLoggedIn = True

        # If there's anybody on the account, kill them for redundant login:
        datagram = PyDatagram()
        datagram.addServerHeader(
            self.csm.GetAccountConnectionChannel(self.accountId),
            self.csm.air.ourChannel,
            CLIENTAGENT_EJECT)
        datagram.addUint16(100)
        datagram.addString('This account has been logged in from elsewhere.')
        self.csm.air.send(datagram)

        # Next, add this connection to the account channel.
        datagram = PyDatagram()
        datagram.addServerHeader(
            self.target,
            self.csm.air.ourChannel,
            CLIENTAGENT_OPEN_CHANNEL)
        datagram.addChannel(self.csm.GetAccountConnectionChannel(self.accountId))
        self.csm.air.send(datagram)

        # Add this connection to extra channels which may be useful:
        if self.accessLevel > 175:
            datagram = PyDatagram()
            datagram.addServerHeader(self.target, self.csm.air.ourChannel,
                                     CLIENTAGENT_OPEN_CHANNEL)
            datagram.addChannel(OtpDoGlobals.OTP_STAFF_CHANNEL)
            self.csm.air.send(datagram)

        # Now set their sender channel to represent their account affiliation:
        datagram = PyDatagram()
        datagram.addServerHeader(
            self.target,
            self.csm.air.ourChannel,
            CLIENTAGENT_SET_CLIENT_ID)
        # Account ID in high 32 bits, 0 in low (no avatar):
        datagram.addChannel(self.accountId << 32)
        self.csm.air.send(datagram)

        # Un-sandbox them!
        datagram = PyDatagram()
        datagram.addServerHeader(
            self.target,
            self.csm.air.ourChannel,
            CLIENTAGENT_SET_STATE)
        datagram.addUint16(2)  # ESTABLISHED
        self.csm.air.send(datagram)

        # Update the last login timestamp:
        self.csm.air.dbInterface.updateObject(
            self.csm.air.dbId,
            self.accountId,
            self.csm.air.dclassesByName['AccountUD'],
            {'LAST_LOGIN': time.ctime(),
             'ACCOUNT_ID': str(self.userId)})

        # We're done.
        self.csm.air.writeServerEvent('accountLogin', self.target, self.accountId, self.userId)
        self.csm.sendUpdateToChannel(self.target, 'acceptLogin', [int(time.time())])
        self.demand('Off')


class CreateAvatarFSM(OperationFSM):
    notify = directNotify.newCategory('CreateAvatarFSM')

    def enterStart(self, dna, index):
        # Basic sanity-checking:
        if index >= 6:
            self.demand('Kill', 'Invalid index specified!')
            return

        if not ToonDNA.ToonDNA.isValidNetString(dna):
            self.demand('Kill', 'Invalid DNA specified!')
            return

        self.index = index
        self.dna = dna

        # Okay, we're good to go, let's query their account.
        self.demand('RetrieveAccount')

    def enterRetrieveAccount(self):
        self.csm.air.dbInterface.queryObject(
            self.csm.air.dbId, self.target, self.__handleRetrieve)

    def __handleRetrieve(self, dclass, fields):
        if dclass != self.csm.air.dclassesByName['AccountUD']:
            self.demand('Kill', 'Your account object was not found in the database!')
            return

        self.account = fields

        self.avList = self.account['ACCOUNT_AV_SET']
        # Sanitize:
        self.avList = self.avList[:6]
        self.avList += [0] * (6-len(self.avList))

        # Make sure the index is open:
        if self.avList[self.index]:
            self.demand('Kill', 'This avatar slot is already taken by another avatar!')
            return

        # Okay, there's space. Let's create the avatar!
        self.demand('CreateAvatar')

    def enterCreateAvatar(self):
        dna = ToonDNA.ToonDNA()
        dna.makeFromNetString(self.dna)
        colorId = ToonDNA.getColorIdFromColorDna(dna.colorDNA.headColor)
        colorString = TTLocalizer.getColorString(colorId)
        animalType = TTLocalizer.AnimalToSpecies[dna.getAnimal()]
        name = ' '.join((colorString, animalType))
        toonFields = {
            'setPatchVersion': (config.GetInt('toon-patch-version', 0),),
            'setName': (name,),
            'WishNameState': ('OPEN',),
            'WishName': ('',),
            'setDNAString': (self.dna,),
            'setDISLid': (self.target,),
            'setGuildId': (0,)
        }
        self.csm.air.dbInterface.createObject(
            self.csm.air.dbId,
            self.csm.air.dclassesByName['DistributedToonUD'],
            toonFields,
            self.__handleCreate)

    def __handleCreate(self, avId):
        if not avId:
            self.demand('Kill', 'Database failed to create the new avatar object!')
            return

        self.avId = avId
        self.demand('StoreAvatar')

    def enterStoreAvatar(self):
        # Associate the avatar with the account...
        self.avList[self.index] = self.avId
        self.csm.air.dbInterface.updateObject(
            self.csm.air.dbId,
            self.target,
            self.csm.air.dclassesByName['AccountUD'],
            {'ACCOUNT_AV_SET': self.avList},
            {'ACCOUNT_AV_SET': self.account['ACCOUNT_AV_SET']},
            self.__handleStoreAvatar)

    def __handleStoreAvatar(self, fields):
        if fields:
            self.demand('Kill', 'Database failed to associate the new avatar to your account!')
            return

        # Otherwise, we're done!
        self.csm.air.writeServerEvent('avatarCreated', self.avId, self.target, self.dna.encode('hex'), self.index)
        self.csm.sendUpdateToAccountId(self.target, 'createAvatarResp', [self.avId])
        self.demand('Off')


class AvatarOperationFSM(OperationFSM):
    POST_ACCOUNT_STATE = 'Off'  # This needs to be overridden.

    def enterRetrieveAccount(self):
        # Query the account:
        self.csm.air.dbInterface.queryObject(
            self.csm.air.dbId, self.target, self.__handleRetrieve)

    def __handleRetrieve(self, dclass, fields):
        if dclass != self.csm.air.dclassesByName['AccountUD']:
            self.demand('Kill', 'Your account object was not found in the database!')
            return

        self.account = fields

        # Check if the server might be locked:
        if config.GetBool('want-unlock-timer', False):
            # Get the unlock time:
            dt = datetime.strptime(config.GetString('unlock-time', ''), '%a %b %d %H:%M:%S %Y')
            ts = int(time.mktime(dt.timetuple()))

            # Check if the client should be locked out:
            if time.time() < ts and self.account['ACCESS_LEVEL'] < 175:
                self.csm.sendUpdateToAccountId(self.target, 'lockClient', [ts, config.GetString('unlock-text', '')])
                self.demand('Off')
                return

        self.avList = self.account['ACCOUNT_AV_SET']

        # Sanitize:
        self.avList = self.avList[:6]
        self.avList += [0] * (6-len(self.avList))

        self.demand(self.POST_ACCOUNT_STATE)


class GetAvatarsFSM(AvatarOperationFSM):
    notify = directNotify.newCategory('GetAvatarsFSM')
    POST_ACCOUNT_STATE = 'QueryAvatars'

    def enterStart(self):
        self.demand('RetrieveAccount')

    def enterQueryAvatars(self):
        self.pendingAvatars = set()
        self.avatarFields = {}
        for avId in self.avList:
            if avId:
                self.pendingAvatars.add(avId)

                def response(dclass, fields, avId=avId):
                    if self.state != 'QueryAvatars':
                        return
                    if dclass != self.csm.air.dclassesByName['DistributedToonUD']:
                        self.demand('Kill', "One of the account's avatars is invalid!")
                        return
                    self.avatarFields[avId] = fields
                    self.pendingAvatars.remove(avId)
                    if not self.pendingAvatars:
                        self.demand('SendAvatars')

                self.csm.air.dbInterface.queryObject(
                    self.csm.air.dbId,
                    avId,
                    response)

        if not self.pendingAvatars:
            self.demand('SendAvatars')

    def enterSendAvatars(self):
        potentialAvs = []

        for avId, fields in self.avatarFields.items():
            index = self.avList.index(avId)
            wishNameState = fields.get('WishNameState', [''])[0]
            name = fields['setName'][0]
            if fields.get('setGuildId') is None:
                # This toon is an older toon, it doesn't have this field
                guildId = 0
            else:
                guildId = fields['setGuildId'][0]

            nameState = 0

            if wishNameState == 'OPEN':
                nameState = 1
            elif wishNameState == 'PENDING':
                nameState = 2
            elif wishNameState == 'APPROVED':
                nameState = 3
            elif wishNameState == 'REJECTED':
                nameState = 4

            potentialAvs.append([avId, name, fields['setDNAString'][0],
                                 index, nameState, guildId])

        self.csm.sendUpdateToAccountId(self.target, 'setAvatars', [potentialAvs])
        self.demand('Off')


# This inherits from GetAvatarsFSM, because the delete operation ends in a
# setAvatars message being sent to the client.
class DeleteAvatarFSM(GetAvatarsFSM):
    notify = directNotify.newCategory('DeleteAvatarFSM')
    POST_ACCOUNT_STATE = 'ProcessDelete'

    def enterStart(self, avId):
        self.avId = avId
        GetAvatarsFSM.enterStart(self)

    def enterProcessDelete(self):
        self.notify.debug('enterProcessDelete %s' % self.avId)
        if self.avId not in self.avList:
            self.notify.debug('Kill, tried to delete av %s not in the account!' % self.avId)
            self.demand('Kill', 'Tried to delete an avatar not in the account!')
            return

        def handleRetrieved(dclass, fields):
            if dclass != self.csm.air.dclassesByName['DistributedToonUD']:
                self.notify.debug('Kill, tried to delete non av %s' % self.avId)
                self.demand('Kill', 'Tried to delete a non toon object!')
                return

            if 'setGuildId' not in fields:
                guildId = 0
            else:
                guildId = fields['setGuildId'][0]

            if guildId != 0:
                self.notify.debug('Kill, tried to delete av %s in a guild %d' % self.avId, guildId)
                self.demand('Kill', 'Tried to delete an avatar that is in a guild!')
                return

            index = self.avList.index(self.avId)
            self.avList[index] = 0

            avsDeleted = list(self.account.get('ACCOUNT_AV_SET_DEL', []))
            avsDeleted.append((self.avId, int(time.time())))

            estateId = self.account.get('ESTATE_ID', 0)

            if estateId != 0:
                # This assumes that the house already exists, but it shouldn't
                # be a problem if it doesn't.
                self.csm.air.dbInterface.updateObject(
                    self.csm.air.dbId,
                    estateId,
                    self.csm.air.dclassesByName['DistributedEstateAI'],
                    {'setSlot%dToonId' % index: [0]}
                )

            newFields = {
                'ACCOUNT_AV_SET': self.avList,
                'ACCOUNT_AV_SET_DEL': avsDeleted
            }

            self.notify.debug('Updating Account %s with newFields: %s' %
                              (self.target, newFields))

            self.csm.air.dbInterface.updateObject(
                self.csm.air.dbId,
                self.target,
                self.csm.air.dclassesByName['AccountUD'],
                newFields,
                callback=self.__handleDelete
            )

        # Check the guildId in the db first.
        # If they are in a guild we cannot allow them to delete their toon.
        self.csm.air.dbInterface.queryObject(self.csm.air.dbId, self.avId, handleRetrieved)

    def __handleDelete(self, fields):
        self.notify.debug('__handleDelete %s' % repr(fields))

        if fields:
            self.notify.debug('Kill, failed to mark avatar %s as deleted' % self.avId)
            self.demand('Kill', 'Database failed to mark the avatar as deleted!')
            return

        friendsManager = self.csm.air.getGlobalObject('TTIFriendsManager')
        friendsManager.clearList(self.avId)
        self.csm.air.writeServerEvent('avatarDeleted', self.avId, self.target)
        self.demand('QueryAvatars')

class SetNameTypedFSM(AvatarOperationFSM):
    notify = directNotify.newCategory('SetNameTypedFSM')
    POST_ACCOUNT_STATE = 'RetrieveAvatar'

    def enterStart(self, avId, name):
        self.avId = avId
        self.name = name

        if self.avId:
            self.demand('RetrieveAccount')
            return

        # Hmm, self.avId was 0. Okay, let's just cut to the judging:
        self.demand('JudgeName')

    def enterRetrieveAvatar(self):
        if self.avId and self.avId not in self.avList:
            self.demand('Kill', 'Tried to name an avatar not in the account!')
            return

        self.csm.air.dbInterface.queryObject(self.csm.air.dbId, self.avId,
                                             self.__handleAvatar)

    def __handleAvatar(self, dclass, fields):
        if dclass != self.csm.air.dclassesByName['DistributedToonUD']:
            self.demand('Kill', "One of the account's avatars is invalid!")
            return

        if fields['WishNameState'][0] != 'OPEN':
            self.demand('Kill', 'Avatar is not in a nameable state!')
            return

        self.demand('JudgeName')

    def enterJudgeName(self):
        chatAgent = self.csm.air.getGlobalObject('ChatAgent')
        badName = chatAgent.checkBadNames(self.name, nameCheck=True)
        if badName:
            self.csm.sendUpdateToAccountId(self.target, 'setNameTypedResp', [self.avId, 0])
        else:
            self.csm.air.dbInterface.updateObject(
                self.csm.air.dbId,
                self.avId,
                self.csm.air.dclassesByName['DistributedToonUD'],
                {'WishNameState': ('APPROVED',),
                 'WishName': (self.name,),
                 'setName': (self.name,)})
            self.csm.sendUpdateToAccountId(self.target, 'setNameTypedResp', [self.avId, 1])
        self.demand('Off')


class SetNamePatternFSM(AvatarOperationFSM):
    notify = directNotify.newCategory('SetNamePatternFSM')
    POST_ACCOUNT_STATE = 'RetrieveAvatar'

    def enterStart(self, avId, pattern):
        self.avId = avId
        self.pattern = pattern

        self.demand('RetrieveAccount')

    def enterRetrieveAvatar(self):
        if self.avId and self.avId not in self.avList:
            self.demand('Kill', 'Tried to name an avatar not in the account!')
            return

        self.csm.air.dbInterface.queryObject(self.csm.air.dbId, self.avId,
                                             self.__handleAvatar)

    def __handleAvatar(self, dclass, fields):
        if dclass != self.csm.air.dclassesByName['DistributedToonUD']:
            self.demand('Kill', "One of the account's avatars is invalid!")
            return

        if fields['WishNameState'][0] != 'OPEN':
            self.demand('Kill', 'Avatar is not in a namable state!')
            return

        self.demand('SetName')

    def enterSetName(self):
        # Render the pattern into a string:
        parts = []
        for p, f in self.pattern:
            part = self.csm.nameGenerator.nameDictionary.get(p, ('', ''))[1]
            if f:
                part = part[:1].upper() + part[1:]
            else:
                part = part.lower()
            parts.append(part)

        parts[2] += parts.pop(3)  # Merge 2&3 (the last name) as there should be no space.
        while '' in parts:
            parts.remove('')
        name = ' '.join(parts)

        if name == '':
            name = 'Toon'

        self.csm.air.dbInterface.updateObject(
            self.csm.air.dbId,
            self.avId,
            self.csm.air.dclassesByName['DistributedToonUD'],
            {'WishNameState': ('',),
             'WishName': ('',),
             'setName': (name,)})

        self.csm.air.writeServerEvent('avatarNamed', self.avId, name)
        self.csm.sendUpdateToAccountId(self.target, 'setNamePatternResp', [self.avId, 1])
        self.demand('Off')


class AcknowledgeNameFSM(AvatarOperationFSM):
    notify = directNotify.newCategory('AcknowledgeNameFSM')
    POST_ACCOUNT_STATE = 'GetTargetAvatar'

    def enterStart(self, avId):
        self.avId = avId
        self.demand('RetrieveAccount')

    def enterGetTargetAvatar(self):
        # Make sure the target avatar is part of the account:
        if self.avId not in self.avList:
            self.demand('Kill', 'Tried to acknowledge name on an avatar not in the account!')
            return

        self.csm.air.dbInterface.queryObject(self.csm.air.dbId, self.avId,
                                             self.__handleAvatar)

    def __handleAvatar(self, dclass, fields):
        if dclass != self.csm.air.dclassesByName['DistributedToonUD']:
            self.demand('Kill', "One of the account's avatars is invalid!")
            return

        # Process the WishNameState change.
        wishNameState = fields['WishNameState'][0]
        wishName = fields['WishName'][0]
        name = fields['setName'][0]

        if wishNameState == 'APPROVED':
            wishNameState = ''
            name = wishName
            wishName = ''
        elif wishNameState == 'REJECTED':
            wishNameState = 'OPEN'
            wishName = ''
        else:
            self.demand('Kill', "Tried to acknowledge name on an avatar in %s state!" % wishNameState)
            return

        # Push the change back through:
        self.csm.air.dbInterface.updateObject(
            self.csm.air.dbId,
            self.avId,
            self.csm.air.dclassesByName['DistributedToonUD'],
            {'WishNameState': (wishNameState,),
             'WishName': (wishName,),
             'setName': (name,)},
            {'WishNameState': fields['WishNameState'],
             'WishName': fields['WishName'],
             'setName': fields['setName']})

        self.csm.sendUpdateToAccountId(self.target, 'acknowledgeAvatarNameResp', [])
        self.demand('Off')


class LoadAvatarFSM(AvatarOperationFSM):
    notify = directNotify.newCategory('LoadAvatarFSM')
    POST_ACCOUNT_STATE = 'GetTargetAvatar'

    def enterStart(self, avId):
        self.avId = avId
        self.demand('RetrieveAccount')

    def enterGetTargetAvatar(self):
        # Make sure the target avatar is part of the account:
        if self.avId not in self.avList:
            self.demand('Kill', 'Tried to play an avatar not in the account!')
            return

        self.csm.air.dbInterface.queryObject(self.csm.air.dbId, self.avId,
                                             self.__handleAvatar)

    def __handleAvatar(self, dclass, fields):
        if dclass != self.csm.air.dclassesByName['DistributedToonUD']:
            self.demand('Kill', "One of the account's avatars is invalid!")
            return

        # DNA patch below for black and white toons.
        dna = ToonDNA.ToonDNA()
        dna.makeFromNetString(fields['setDNAString'][0])
        if dna.getAnimal() not in ('bear', 'cat'):
            if dna.colorDNA is not None:
                modified = False
                for part in (dna.colorDNA.headColor, dna.colorDNA.armColor, dna.colorDNA.legColor):
                    currColor = part.get()
                    newColor = list(currColor)
                    # Color legitimacy checks
                    if currColor[0] > 1.0:
                        newColor[0] = min(currColor[0], 1.0)
                        modified = True
                    if currColor[1] < .2 or currColor[1] > .88:
                        newColor[1] = min(max(currColor[1], .2), .88)
                        modified = True
                    if currColor[2] < .55 or currColor[2] > .9:
                        newColor[2] = min(max(currColor[2], .55), .90)
                        modified = True
                    if modified:
                        part.reset(*newColor)
                if modified:
                    dna.colorDNA.dna = (dna.colorDNA.headColor, dna.colorDNA.armColor, dna.colorDNA.legColor)
                    self.dnaPatch = dna.makeNetString()
                    fields['setDNAString'] = (self.dnaPatch,)

        self.avatar = fields
        self.demand('SetAvatar')

    def enterSetAvatarTask(self, channel, task):
        # Finally, grant ownership and shut down.
        datagram = PyDatagram()
        datagram.addServerHeader(
            self.avId,
            self.csm.air.ourChannel,
            STATESERVER_OBJECT_SET_OWNER)
        datagram.addChannel(self.target<<32 | self.avId)
        self.csm.air.send(datagram)

        # Tell the Managers as well:
        globalPartyMgr = self.csm.air.getGlobalObject('GlobalPartyManager')
        globalPartyMgr.avatarJoined(self.avId)
        guildManager = self.csm.air.getGlobalObject('GuildManager')
        guildManager.toonOnline(
            self.avId, self.avatar.get('setGuildId', [0])[0])

        self.csm.air.writeServerEvent('avatarChosen', self.avId, self.target)
        self.demand('Off')
        return task.done

    def enterSetAvatar(self):
        channel = self.csm.GetAccountConnectionChannel(self.target)

        # First, give them a POSTREMOVE to unload the avatar, just in case they
        # disconnect while we're working.
        datagramCleanup = PyDatagram()
        datagramCleanup.addServerHeader(
            self.avId,
            channel,
            STATESERVER_OBJECT_DELETE_RAM)
        datagramCleanup.addUint32(self.avId)
        datagram = PyDatagram()
        datagram.addServerHeader(
            channel,
            self.csm.air.ourChannel,
            CLIENTAGENT_ADD_POST_REMOVE)
        datagram.addString(datagramCleanup.getMessage())
        self.csm.air.send(datagram)

        # Activate the avatar on the DBSS:
        self.csm.air.sendActivate(
            self.avId, 0, 0, self.csm.air.dclassesByName['DistributedToonUD'],
            {'setAdminAccess': [forceAccessLevel if forceAccessLevel else self.account.get('ACCESS_LEVEL', 100)],
             'setBankMoney': [self.account.get('MONEY', 0)],
             'setChatMode': [self.account.get('CHAT_MODE', 1)]})

        # Let the TTIFriendsManager know about the account's chat mode.
        friendsManager = self.csm.air.getGlobalObject('TTIFriendsManager')
        friendsManager.setChatMode(self.avId, self.account.get('CHAT_MODE', 1))

        if hasattr(self, 'dnaPatch'):
            self.csm.air.dbInterface.updateObject(
                self.csm.air.dbId,
                self.avId,
                self.csm.air.dclassesByName['DistributedToonUD'],
                {'setDNAString': (self.dnaPatch,)})

        # Next, add them to the avatar channel:
        datagram = PyDatagram()
        datagram.addServerHeader(
            channel,
            self.csm.air.ourChannel,
            CLIENTAGENT_OPEN_CHANNEL)
        datagram.addChannel(self.csm.GetPuppetConnectionChannel(self.avId))
        self.csm.air.send(datagram)

        # Now set their sender channel to represent their account affiliation:
        datagram = PyDatagram()
        datagram.addServerHeader(
            channel,
            self.csm.air.ourChannel,
            CLIENTAGENT_SET_CLIENT_ID)
        datagram.addChannel(self.target<<32 | self.avId)
        self.csm.air.send(datagram)

        # Eliminate race conditions.
        taskMgr.doMethodLater(0.2, self.enterSetAvatarTask,
                              'avatarTask-%s' % self.avId, extraArgs=[channel],
                              appendTask=True)

class UnloadAvatarFSM(OperationFSM):
    notify = directNotify.newCategory('UnloadAvatarFSM')

    def enterStart(self, avId):
        self.avId = avId

        # We don't even need to query the account, we know the avatar is being played!
        self.demand('UnloadAvatar')

    def enterUnloadAvatar(self):
        channel = self.csm.GetAccountConnectionChannel(self.target)

        # Tell Managers somebody is logging off:
        friendsManager = self.csm.air.getGlobalObject('TTIFriendsManager')
        friendsManager.toonOffline(self.avId)
        guildManager = self.csm.air.getGlobalObject('GuildManager')
        guildManager.toonOffline(self.avId)

        # Clear off POSTREMOVE:
        datagram = PyDatagram()
        datagram.addServerHeader(
            channel,
            self.csm.air.ourChannel,
            CLIENTAGENT_CLEAR_POST_REMOVES)
        self.csm.air.send(datagram)

        # Remove avatar channel:
        datagram = PyDatagram()
        datagram.addServerHeader(
            channel,
            self.csm.air.ourChannel,
            CLIENTAGENT_CLOSE_CHANNEL)
        datagram.addChannel(self.csm.GetPuppetConnectionChannel(self.avId))
        self.csm.air.send(datagram)

        # Reset sender channel:
        datagram = PyDatagram()
        datagram.addServerHeader(
            channel,
            self.csm.air.ourChannel,
            CLIENTAGENT_SET_CLIENT_ID)
        datagram.addChannel(self.target<<32)
        self.csm.air.send(datagram)

        # Unload avatar object:
        datagram = PyDatagram()
        datagram.addServerHeader(
            self.avId,
            channel,
            STATESERVER_OBJECT_DELETE_RAM)
        datagram.addUint32(self.avId)
        self.csm.air.send(datagram)

        # Done!
        self.csm.air.writeServerEvent('avatarUnload', self.avId)
        self.demand('Off')


# --- CLIENT SERVICES MANAGER UBERDOG ---
class ClientServicesManagerUD(DistributedObjectGlobalUD):
    notify = directNotify.newCategory('ClientServicesManagerUD')

    def __init__(self, air):
        DistributedObjectGlobalUD.__init__(self, air)

        self.air.csm = self
        self.authTokens = {}

    def announceGenerate(self):
        DistributedObjectGlobalUD.announceGenerate(self)

        # These keep track of the connection/account IDs currently undergoing an
        # operation on the CSM. This is to prevent (hacked) clients from firing up more
        # than one operation at a time, which could potentially lead to exploitation
        # of race conditions.
        self.connection2fsm = {}
        self.account2fsm = {}

        # For processing name patterns.
        self.nameGenerator = NameGenerator()

        # Temporary HMAC key:
        self.key = 'bWlub3Iub3BlbmFsLmZpeC5zdGFydC5vZi5oZWFsam9rZXM='

        if simbase.isSinglePlayer:
            self.playerLoggedIn = False

        # Instantiate our account DB interface:
        if accountdbType == 'developer':
            self.accountDB = DeveloperAccountDB(self)
        elif accountdbType == 'production':
            self.accountDB = ProductionDB(self)
        else:
            self.notify.error('Invalid accountdb-type: ' + accountdbType)

    def killConnection(self, connId, reason):
        datagram = PyDatagram()
        datagram.addServerHeader(
            connId,
            self.air.ourChannel,
            CLIENTAGENT_EJECT)
        datagram.addUint16(122)
        datagram.addString(reason)
        self.air.send(datagram)

    def killConnectionFSM(self, connId):
        fsm = self.connection2fsm.get(connId)

        if not fsm:
            self.notify.warning('Tried to kill connection %d for duplicate FSM, but none exists!' % connId)
            return

        self.killConnection(connId, 'An operation is already underway: ' + fsm.name)

    def killAccount(self, accountId, reason):
        self.killConnection(self.GetAccountConnectionChannel(accountId), reason)

    def killAccountFSM(self, accountId):
        fsm = self.account2fsm.get(accountId)
        if not fsm:

            self.notify.warning('Tried to kill account %d for duplicate FSM, but none exists!' % accountId)
            return

        self.killAccount(accountId, 'An operation is already underway: ' + fsm.name)

    def runAccountFSM(self, fsmtype, *args):
        sender = self.air.getAccountIdFromSender()

        if not sender:
            self.killAccount(sender, 'Client is not logged in.')

        if sender in self.account2fsm:
            self.killAccountFSM(sender)
            return

        self.account2fsm[sender] = fsmtype(self, sender)
        self.account2fsm[sender].request('Start', *args)

    def requestAuthToken(self, mac_addr, ip_addr):
        sender = self.air.getMsgSender()
        self.air.sendNetEvent('banCheck', [sender, mac_addr, ip_addr], channels=[OtpDoGlobals.MESSENGER_CHANNEL_AI])
        self.acceptOnce('banCheckResponse-%s' % sender, self.handleResponse)

    def handleResponse(self, sender, isBanned, banLength):
        if isBanned:
            datagram = PyDatagram()
            datagram.addServerHeader(
                sender,
                self.air.ourChannel,
                CLIENTAGENT_EJECT)
            datagram.addUint16(156)
            datagram.addString(banLength)
            self.air.send(datagram)
            return

        authToken = ''.join([hex(random.randint(0, 254)) for _ in xrange(25)])

        lookupTable = generateLookupTable(authToken[::2])
        self.authTokens[sender] = encodeHexString(lookupTable, authToken)
        del lookupTable

        self.sendUpdateToChannel(sender, 'receiveAuthToken', [authToken])

    def login(self, cookie, authToken):
        self.notify.debug('Received login cookie %r from %d' % (cookie, self.air.getMsgSender()))

        sender = self.air.getMsgSender()

        if simbase.isSinglePlayer and self.playerLoggedIn:
            # Only one connection is allowed in singleplayer mode.
            self.killConnection(sender, 'Single Player servers only allows one connection.')

        # Time to check this login to see if its authentic
        if authToken == self.authTokens.get(sender):
            # This login is authentic!
            del self.authTokens[sender]
        else:
            # This login is not authentic.
            self.killConnection(sender, 'Invalid auth token.')
            return

        if sender >> 32:
            self.killConnection(sender, 'Client is already logged in.')
            return

        if sender in self.connection2fsm:
            self.killConnectionFSM(sender)
            return

        self.connection2fsm[sender] = LoginAccountFSM(self, sender)
        self.connection2fsm[sender].request('Start', cookie)

    def requestAvatars(self):
        self.notify.debug('Received avatar list request from %d' % (self.air.getMsgSender()))
        self.runAccountFSM(GetAvatarsFSM)

    def createAvatar(self, dna, index):
        self.runAccountFSM(CreateAvatarFSM, dna, index)

    def deleteAvatar(self, avId):
        self.runAccountFSM(DeleteAvatarFSM, avId)

    def setNameTyped(self, avId, name):
        self.runAccountFSM(SetNameTypedFSM, avId, name)

    def setNamePattern(self, avId, p1, f1, p2, f2, p3, f3, p4, f4):
        self.runAccountFSM(SetNamePatternFSM, avId, [(p1, f1), (p2, f2),
                                                     (p3, f3), (p4, f4)])

    def acknowledgeAvatarName(self, avId):
        self.runAccountFSM(AcknowledgeNameFSM, avId)

    def chooseAvatar(self, avId):
        currentAvId = self.air.getAvatarIdFromSender()
        accountId = self.air.getAccountIdFromSender()
        if currentAvId and avId:
            self.killAccount(accountId, 'A Toon is already chosen!')
            return
        elif not currentAvId and not avId:
            # This isn't really an error, the client is probably just making sure
            # none of its Toons are active.
            return

        if avId:
            self.runAccountFSM(LoadAvatarFSM, avId)
            chatAgent = self.air.getGlobalObject('ChatAgent')
            chatAgent.checkMuted(accountId)
        else:
            self.runAccountFSM(UnloadAvatarFSM, currentAvId)
