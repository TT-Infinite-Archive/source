import urllib.parse

from direct.distributed.AstronInternalRepository import AstronInternalRepository
from direct.distributed.PyDatagram import PyDatagram
from panda3d.core import loadPrcFile
from panda3d.direct import DCPacker

from toontown.toonbase import EventGlobals
from otp.distributed.OtpDoGlobals import *

from toontown.distributed.ToontownNetMessengerAI import ToontownNetMessengerAI

import pymongo

if config.GetBool('want-web-api', False):
    from toontown.web.WebserverAPIClient import WebserverAPIClient


class ToontownInternalRepository(AstronInternalRepository):
    GameGlobalsId = OTP_DO_ID_TOONTOWN
    dbId = 4003

    def __init__(self, baseChannel, serverId=None, dcFileNames=None,
                 dcSuffix='AI', connectMethod=None, threadedNet=None):
        AstronInternalRepository.__init__(
            self, baseChannel, serverId=serverId, dcFileNames=dcFileNames,
            dcSuffix=dcSuffix, connectMethod=connectMethod,
            threadedNet=threadedNet)

        self.__callbacks = {}

        url = config.GetString('mongodb-url', 'mongodb://localhost')
        replicaset = config.GetString('mongodb-replicaset', '')
        if replicaset:
            self.mongo = pymongo.MongoClient(url, replicaset=replicaset)
        else:
            self.mongo = pymongo.MongoClient(url)
        db = (urllib.parse.urlparse(url).path or '/game')[1:]
        self.mongodb = self.mongo[db]
        self.dbAstronCursor = self.mongodb.astron

        if config.GetBool('want-web-api', False):
            endpoint = config.GetString(
                'web-api-endpoint', 'https://localhost:8000/api/')
            token = config.GetString('web-api-token', '')
            self.webApi = WebserverAPIClient(endpoint, token)
        else:
            self.webApi = None

        self.netMessenger = ToontownNetMessengerAI(self)

    def handleConnected(self):
        self.netMessenger.register()

        self.accept('reloadConfig', self.handleReloadConfig)

    def getAvatarIdFromSender(self):
        return int(self.getMsgSender() & 0xFFFFFFFF)

    def getAccountIdFromSender(self):
        return int((self.getMsgSender() >> 32) & 0xFFFFFFFF)

    def createDgUpdateToDoId(self, dclassName, fieldName, doId, args,
                             channelId=None):
        """
        channelId can be used as a recipient if you want to bypass the normal
        airecv, ownrecv, broadcast, etc.  If you don't include a channelId
        or if channelId == doId, then the normal broadcast options will
        be used.
        This is just like sendUpdateToDoId, but just returns
        the datagram instead of immediately sending it.
        """
        result = None

        dclass = self.dclassesByName.get(dclassName+self.dcSuffix)

        assert dclass is not None

        if channelId is None:
            channelId = doId

        if dclass is not None:
            dg = dclass.aiFormatUpdate(fieldName, doId, channelId, self.ourChannel, args)
            result = dg

        return result

    def sendUpdateToDoId(self, dclassName, fieldName, doId, args, channelId=None):
        """
        channelId can be used as a recipient if you want to bypass the normal
        airecv, ownrecv, broadcast, etc.  If you don't include a channelId
        or if channelId == doId, then the normal broadcast options will
        be used.

        """
        dclass = self.dclassesByName.get(dclassName+self.dcSuffix)

        assert dclass is not None

        if channelId is None:
            channelId = doId

        if dclass is not None:
            dg = dclass.aiFormatUpdate(fieldName, doId, channelId, self.ourChannel, args)
            self.send(dg)

    def _isValidPlayerLocation(self, parentId, zoneId):
        if zoneId < 1000 and zoneId != 1:
            return False

        return True

    def queryObjectLocation(self, doId, callback):
        ctx = self.getContext()
        self.__callbacks[ctx] = callback

        dg = PyDatagram()
        dg.addServerHeader(doId, self.ourChannel,
                           STATESERVER_OBJECT_GET_LOCATION)
        dg.addUint32(ctx)
        self.send(dg)

    def handleQueryObjectLocationResp(self, msgType, di):
        ctx = di.getUint32()

        if ctx not in self.__callbacks:
            self.notify.warning('Received unexpected %s'
                                ' (ctx %d)' % (MsgId2Names[msgType], ctx))
            return

        di.skipBytes(4)
        parentId = di.getUint32()
        zoneId = di.getUint32()

        self.__callbacks[ctx](parentId, zoneId)
        del self.__callbacks[ctx]

    def sendNetEvent(self, message, sentArgs=[]):
        self.netMessenger.send(message, sentArgs)

    def addExitEvent(self, message, sentArgs=[]):
        dg = self.netMessenger.prepare(message, sentArgs)
        self.addPostRemove(dg)

    def handleDatagram(self, di):
        msgType = self.getMsgType()

        if msgType == self.netMessenger.msgType:
            self.netMessenger.handle(di)
            return

        AstronInternalRepository.handleDatagram(self, di)

    def handleReloadConfig(self, channel):
        if channel == self.ourChannel:
            for prc in args.config:
                loadPrcFile(prc)

            messenger.send(EventGlobals.ConfigReloaded)

    def packDclassValueDict(self, dclass, fieldDict):
        '''
        Converts {fieldName: fieldValue} dictionaries to
        {fieldName: packedFieldValue} dictionary.

        Useful for converting values returned from from Astron's Database
        interface to something more OTP compatible (for dObj.directUpdate or
        dObj.initFromServerResponse calls).
        '''

        valueDict = {}
        packer = DCPacker()

        for fieldName in fieldDict:
            field = dclass.getFieldByName(fieldName)

            packer.beginPack(field)
            field.packArgs(packer, fieldDict[fieldName])
            packer.endPack()

            valueDict[fieldName] = packer.getBytes()
            packer.clearData()

        return valueDict
