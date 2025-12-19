from panda3d.direct import DCFile
from panda3d.core import ConfigVariableBool, ConfigVariableString, Datagram, StringStream, loadPrcFile
import builtins
import types
import urllib.parse

import pymongo
from direct.distributed.AstronInternalRepository import AstronInternalRepository
from direct.distributed.PyDatagram import PyDatagram

from otp.distributed.OtpDoGlobals import *
from toontown.distributed.ToontownNetMessengerAI import ToontownNetMessengerAI
from toontown.toonbase import EventGlobals

if ConfigVariableBool('want-web-api', False).getValue():
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

        url = ConfigVariableString('mongodb-url', 'mongodb://localhost').getValue()
        replicaset = ConfigVariableString('mongodb-replicaset', '').getValue()
        if replicaset:
            self.mongo = pymongo.MongoClient(url, replicaset=replicaset)
        else:
            self.mongo = pymongo.MongoClient(url)
        db = (urllib.parse.urlparse(url).path or '/game')[1:]
        self.mongodb = self.mongo[db]
        self.dbAstronCursor = self.mongodb.astron

        if ConfigVariableBool('want-web-api', False).getValue():
            endpoint = ConfigVariableString(
                'web-api-endpoint', 'https://localhost:8000/api/').getValue()
            token = ConfigVariableString('web-api-token', '').getValue()
            self.webApi = WebserverAPIClient(endpoint, token)
        else:
            self.webApi = None

    def readDCFile(self, dcFileNames=None):
        dcFile = self.getDcFile()
        dcFile.clear()
        self.dclassesByName = {}
        self.dclassesByNumber = {}
        self.hashVal = 0

        if isinstance(dcFileNames, (str,)):
            # If we were given a single string, make it a list.
            dcFileNames = [dcFileNames]

        if hasattr(builtins, 'dcData'):
            dcFileNames = [StringStream(dcData)]

        dcImports = {}
        if dcFileNames is None:
            readResult = dcFile.readAll()
            if not readResult:
                self.notify.error('Could not read DC file.')
        else:
            for dcFileName in dcFileNames:
                if isinstance(dcFileName, StringStream):
                    readResult = dcFile.read(dcFileName, 'DC stream')
                else:
                    readResult = dcFile.read(dcFileName)
                if not readResult:
                    self.notify.error('Could not read DC file.')

        self.hashVal = dcFile.getHash()

        # Now import all of the modules required by the DC file.
        for n in range(dcFile.getNumImportModules()):
            moduleName = dcFile.getImportModule(n)[:]

            # Maybe the module name is represented as "moduleName/AI".
            suffix = moduleName.split('/')
            moduleName = suffix[0]
            suffix=suffix[1:]
            if self.dcSuffix in suffix:
                moduleName += self.dcSuffix
            elif self.dcSuffix == 'UD' and 'AI' in suffix:  # HACK:
                moduleName += 'AI'

            importSymbols = []
            for i in range(dcFile.getNumImportSymbols(n)):
                symbolName = dcFile.getImportSymbol(n, i)

                # Maybe the symbol name is represented as "symbolName/AI".
                suffix = symbolName.split('/')
                symbolName = suffix[0]
                suffix=suffix[1:]
                if self.dcSuffix in suffix:
                    symbolName += self.dcSuffix
                elif self.dcSuffix == 'UD' and 'AI' in suffix:  # HACK:
                    symbolName += 'AI'

                importSymbols.append(symbolName)

            self.importModule(dcImports, moduleName, importSymbols)

        # Now get the class definition for the classes named in the DC
        # file.
        for i in range(dcFile.getNumClasses()):
            dclass = dcFile.getClass(i)
            number = dclass.getNumber()
            className = dclass.getName() + self.dcSuffix

            # Does the class have a definition defined in the newly
            # imported namespace?
            classDef = dcImports.get(className)
            if classDef is None and self.dcSuffix == 'UD':  # HACK:
                className = dclass.getName() + 'AI'
                classDef = dcImports.get(className)

            # Also try it without the dcSuffix.
            if classDef is None:
                className = dclass.getName()
                classDef = dcImports.get(className)
            if classDef is None:
                self.notify.debug('No class definition for %s.' % className)
            else:
                if type(classDef) == types.ModuleType:
                    if not hasattr(classDef, className):
                        self.notify.warning('Module %s does not define class %s.' % (className, className))
                        continue
                    classDef = getattr(classDef, className)

                if type(classDef) != type and type(classDef) != type:
                    self.notify.error('Symbol %s is not a class name.' % className)
                else:
                    dclass.setClassDef(classDef)

            self.dclassesByName[className] = dclass
            if number >= 0:
                self.dclassesByNumber[number] = dclass

        # Owner Views
        if self.hasOwnerView():
            ownerDcSuffix = self.dcSuffix + 'OV'
            # dict of class names (without 'OV') that have owner views
            ownerImportSymbols = {}

            # Now import all of the modules required by the DC file.
            for n in range(dcFile.getNumImportModules()):
                moduleName = dcFile.getImportModule(n)

                # Maybe the module name is represented as "moduleName/AI".
                suffix = moduleName.split('/')
                moduleName = suffix[0]
                suffix=suffix[1:]
                if ownerDcSuffix in suffix:
                    moduleName = moduleName + ownerDcSuffix

                importSymbols = []
                for i in range(dcFile.getNumImportSymbols(n)):
                    symbolName = dcFile.getImportSymbol(n, i)

                    # Check for the OV suffix
                    suffix = symbolName.split('/')
                    symbolName = suffix[0]
                    suffix=suffix[1:]
                    if ownerDcSuffix in suffix:
                        symbolName += ownerDcSuffix
                    importSymbols.append(symbolName)
                    ownerImportSymbols[symbolName] = None

                self.importModule(dcImports, moduleName, importSymbols)

            # Now get the class definition for the owner classes named
            # in the DC file.
            for i in range(dcFile.getNumClasses()):
                dclass = dcFile.getClass(i)
                if ((dclass.getName()+ownerDcSuffix) in ownerImportSymbols):
                    number = dclass.getNumber()
                    className = dclass.getName() + ownerDcSuffix

                    # Does the class have a definition defined in the newly
                    # imported namespace?
                    classDef = dcImports.get(className)
                    if classDef is None:
                        self.notify.error('No class definition for %s.' % className)
                    else:
                        if type(classDef) == types.ModuleType:
                            if not hasattr(classDef, className):
                                self.notify.error('Module %s does not define class %s.' % (className, className))
                            classDef = getattr(classDef, className)
                        dclass.setOwnerClassDef(classDef)
                        self.dclassesByName[className] = dclass

    def handleConnected(self):
        self.__messenger = ToontownNetMessengerAI(self)
        self.accept('reloadConfig', self.handleReloadConfig)

    def prepareMessage(self, message, sentArgs=[], channels=None):
        return self.__messenger.prepare(message, sentArgs, channels)

    def sendNetEvent(self, message, sentArgs=[], channels=None):
        self.__messenger.send(message, sentArgs, channels)

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
        elif msgType == self.__messenger.msgType:
            self.__messenger.handle(msgType, di)
            return
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
