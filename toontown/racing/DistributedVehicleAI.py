from panda3d.core import Datagram
from otp.ai.AIBase import *
from toontown.toonbase.ToontownGlobals import *
from toontown.racing.KartDNA import *
from direct.distributed.ClockDelta import *
from direct.distributed import DistributedSmoothNodeAI
from direct.fsm import FSM
from direct.task import Task

from direct.distributed.PyDatagram import *


if (__debug__):
    import pdb

class DistributedVehicleAI(DistributedSmoothNodeAI.DistributedSmoothNodeAI, FSM.FSM):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedVehicleAI')

    def __init__(self, air, avId):
        self.ownerId = avId
        DistributedSmoothNodeAI.DistributedSmoothNodeAI.__init__(self, air)
        FSM.FSM.__init__(self, 'DistributedVehicleAI')
        self.driverId = 0
        self.kartDNA = [-1] * getNumFields()
        self.__initDNA()
        self.request('Off')

    def generate(self):
        DistributedSmoothNodeAI.DistributedSmoothNodeAI.generate(self)

    def delete(self):
        DistributedSmoothNodeAI.DistributedSmoothNodeAI.delete(self)

    def __initDNA(self):
        owner = self.air.doId2do.get(self.ownerId)
        if owner:
            self.kartDNA[EKartDNA.BODY_TYPE] = owner.getKartBodyType()
            self.kartDNA[EKartDNA.BODY_COLOR] = owner.getKartBodyColor()
            self.kartDNA[EKartDNA.ACC_COLOR] = owner.getKartAccessoryColor()
            self.kartDNA[EKartDNA.EB_TYPE] = owner.getKartEngineBlockType()
            self.kartDNA[EKartDNA.SP_TYPE] = owner.getKartSpoilerType()
            self.kartDNA[EKartDNA.FWW_TYPE] = owner.getKartFrontWheelWellType()
            self.kartDNA[EKartDNA.BWW_TYPE] = owner.getKartBackWheelWellType()
            self.kartDNA[EKartDNA.RIMS_TYPE] = owner.getKartRimType()
            self.kartDNA[EKartDNA.DECAL_TYPE] = owner.getKartDecalType()
        else:
            self.notify.warning('__initDNA - OWNER %s OF KART NOT FOUND!' % self.ownerId)

    def d_setState(self, state, avId):
        self.sendUpdate('setState', [state, avId])

    def requestControl(self):
        avId = self.air.getAvatarIdFromSender()
        accId = self.air.getAccountIdFromSender()
        if self.driverId == 0:
            self.request('Controlled', avId, accId)

    def requestParked(self):
        avId = self.air.getAvatarIdFromSender()
        if avId == self.driverId:
            self.request('Parked')

    def start(self):
        self.request('Parked')

    def enterOff(self):
        return None

    def exitOff(self):
        return None

    def enterParked(self):
        self.driverId = 0
        self.d_setState('P', 0)
        return None

    def exitParked(self):
        return None

    def enterControlled(self, avId, accId):
        self.driverId = avId
        fieldList = ['setComponentL',
         'setComponentX',
         'setComponentY',
         'setComponentZ',
         'setComponentH',
         'setComponentP',
         'setComponentR',
         'setComponentT',
         'setSmStop',
         'setSmH',
         'setSmZ',
         'setSmXY',
         'setSmXZ',
         'setSmPos',
         'setSmHpr',
         'setSmXYH',
         'setSmXYZH',
         'setSmPosHpr',
         'setSmPosHprL',
         'clearSmoothing',
         'suggestResync',
         'returnResync']
        #self.air.setAllowClientSend(avId, self, fieldList, accId)
        #hack until CLIENTAGENT_SET_FIELDS_SENDABLE works
        #probably should not be kept for any longer than it needs to
        dg = PyDatagram()
        dg.addServerHeader(self.doId, self.air.ourChannel, STATESERVER_OBJECT_SET_OWNER)
        dg.addUint64(accId << 32 | avId)
        self.air.send(dg)
        self.d_setState('C', self.driverId)

    def exitControlled(self):
        pass

    def handleUnexpectedExit(self):
        self.notify.warning('toon: %d exited unexpectedly, resetting vehicle %d' % (self.driverId, self.doId))
        self.request('Parked')
        self.requestDelete()

    def getBodyType(self):
        return self.kartDNA[EKartDNA.BODY_TYPE]

    def getBodyColor(self):
        return self.kartDNA[EKartDNA.BODY_COLOR]

    def getAccessoryColor(self):
        return self.kartDNA[EKartDNA.ACC_COLOR]

    def getEngineBlockType(self):
        return self.kartDNA[EKartDNA.EB_TYPE]

    def getSpoilerType(self):
        return self.kartDNA[EKartDNA.SP_TYPE]

    def getFrontWheelWellType(self):
        return self.kartDNA[EKartDNA.FWW_TYPE]

    def getBackWheelWellType(self):
        return self.kartDNA[EKartDNA.BWW_TYPE]

    def getRimType(self):
        return self.kartDNA[EKartDNA.RIMS_TYPE]

    def getDecalType(self):
        return self.kartDNA[EKartDNA.DECAL_TYPE]

    def getOwner(self):
        return self.ownerId
