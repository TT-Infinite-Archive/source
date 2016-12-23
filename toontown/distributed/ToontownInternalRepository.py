import urlparse

from direct.distributed.AstronInternalRepository import AstronInternalRepository
from direct.distributed.PyDatagram import PyDatagram
from panda3d.core import loadPrcFile

from toontown.toonbase import EventGlobals
from otp.distributed.OtpDoGlobals import *

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
        db = (urlparse.urlparse(url).path or '/game')[1:]
        self.mongodb = self.mongo[db]
        self.dbAstronCursor = self.mongodb.astron

        if config.GetBool('want-web-api', False):
            endpoint = config.GetString(
                'web-api-endpoint', 'https://localhost:8000/api/')
            token = config.GetString('web-api-token', '')
            self.webApi = WebserverAPIClient(endpoint, token)
        else:
            self.webApi = None

        self.netMessenger.register(0, 'shardStatus')
        self.netMessenger.register(1, 'queryShardStatus')
        self.netMessenger.register(2, 'startInvasion')
        self.netMessenger.register(3, 'stopInvasion')
        self.netMessenger.register(4, 'reloadConfig')

    def handleConnected(self):
        self.netMessenger.accept('reloadConfig', self, self.handleReloadConfig)

    def getAvatarIdFromSender(self):
        return int(self.getMsgSender() & 0xFFFFFFFF)

    def getAccountIdFromSender(self):
        return int((self.getMsgSender() >> 32) & 0xFFFFFFFF)

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

    def handleDatagram(self, di):
        msgType = self.getMsgType()

        if msgType in (STATESERVER_OBJECT_ENTER_AI_WITH_REQUIRED,
                       STATESERVER_OBJECT_ENTER_AI_WITH_REQUIRED_OTHER):
            self.handleObjEntry(di,
                                msgType == STATESERVER_OBJECT_ENTER_AI_WITH_REQUIRED_OTHER)
        elif msgType in (STATESERVER_OBJECT_CHANGING_AI,
                         STATESERVER_OBJECT_DELETE_RAM):
            self.handleObjExit(di)
        elif msgType == STATESERVER_OBJECT_CHANGING_LOCATION:
            self.handleObjLocation(di)
        elif msgType in (DBSERVER_CREATE_OBJECT_RESP,
                         DBSERVER_OBJECT_GET_ALL_RESP,
                         DBSERVER_OBJECT_GET_FIELDS_RESP,
                         DBSERVER_OBJECT_GET_FIELD_RESP,
                         DBSERVER_OBJECT_SET_FIELD_IF_EQUALS_RESP,
                         DBSERVER_OBJECT_SET_FIELDS_IF_EQUALS_RESP):
            self.dbInterface.handleDatagram(msgType, di)
        elif msgType == DBSS_OBJECT_GET_ACTIVATED_RESP:
            self.handleGetActivatedResp(di)
        elif msgType == STATESERVER_OBJECT_GET_LOCATION_RESP:
            self.handleQueryObjectLocationResp(msgType, di)
        elif msgType >= 20000:
            # These messages belong to the NetMessenger:
            self.netMessenger.handle(msgType, di)
        else:
            self.notify.warning(
                'Received message with unknown MsgType=%d' % msgType)

    def handleReloadConfig(self, channel):
        if channel == self.ourChannel:
            for prc in args.config:
                loadPrcFile(prc)

            messenger.send(EventGlobals.ConfigReloaded)
