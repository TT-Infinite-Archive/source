from otp.ai.AIBase import *
from toontown.toonbase.ToontownGlobals import *
from toontown.racing.KartDNA import *
from direct.distributed.ClockDelta import *
from direct.distributed import DistributedSmoothNodeAI
from direct.fsm import FSM

from direct.distributed.MsgTypes import STATESERVER_OBJECT_SET_OWNER
from direct.distributed.PyDatagram import *


class DistributedVehicleAI(DistributedSmoothNodeAI.DistributedSmoothNodeAI, FSM.FSM):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedVehicleAI')

    def __init__(self, air, avId):
        self.ownerId = avId
        DistributedSmoothNodeAI.DistributedSmoothNodeAI.__init__(self, air)
        FSM.FSM.__init__(self, 'DistributedVehicleAI')

        self.driverId = 0

        # Initialize default Kart DNA List, then update it based on the
        # actual DNA found on the distributed toon.
        self.kartDNA = [-1] * getNumFields()

        self.__initDNA()
        self.request('Off')

    def __initDNA(self):
        # Retrieve the Distributed Object of the owner in order to set
        # each of the kart dna fields.
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
        # A client wants to start controlling the car.
        avId = self.air.getAvatarIdFromSender()
        accId = self.air.getAccountIdFromSender()
        if self.driverId == 0:
            self.request('Controlled', avId, accId)

    def requestParked(self):
        # A client wants to stop controlling the car.
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
        """
        Purpose: The getBodyType Method obtains the local AI side
        body type of the kart that the toon currently owns.

        Params: None
        Return: bodyType - the body type of the kart.
        """
        return self.kartDNA[EKartDNA.BODY_TYPE]

    def getBodyColor(self):
        """
        Purpose: The getBodyColor Method obtains the current
        body color of the kart.

        Params: None
        Return: bodyColor - the color of the kart body.
        """
        return self.kartDNA[EKartDNA.BODY_COLOR]

    def getAccessoryColor(self):
        """
        Purpose: The getAccessoryColor Method obtains the
        accessory color for the kart.

        Params: None
        Return: accColor - the color of the accessories
        """
        return self.kartDNA[EKartDNA.ACC_COLOR]

    def getEngineBlockType(self):
        """
        Purpose: The getEngineBlockType Method obtains the engine
        block type accessory for the kart by accessing the
        current Kart DNA.

        Params: None
        Return: ebType - the type of engine block accessory.
        """
        return self.kartDNA[EKartDNA.EB_TYPE]

    def getSpoilerType(self):
        """
        Purpose: The getSpoilerType Method obtains the spoiler
        type accessory for the kart by accessing the current Kart DNA.

        Params: None
        Return: spType - the type of spoiler accessory
        """
        return self.kartDNA[EKartDNA.SP_TYPE]

    def getFrontWheelWellType(self):
        """
        Purpose: The getFrontWheelWellType Method obtains the
        front wheel well accessory for the kart accessing the
        Kart DNA.

        Params: None
        Return: fwwType - the type of Front Wheel Well accessory
        """
        return self.kartDNA[EKartDNA.FWW_TYPE]

    def getBackWheelWellType(self):
        """
        Purpose: The getWheelWellType Method gets the Back
        Wheel Wheel accessory for the kart by updating the Kart DNA.

        Params: bwwType - the type of Back Wheel Well accessory.
        Return: None
        """
        return self.kartDNA[EKartDNA.BWW_TYPE]

    def getRimType(self):
        """
        Purpose: The setRimType Method sets the rims accessory
        for the karts tires by accessing the Kart DNA.

        Params: None
        Return: rimsType - the type of rims for the kart tires.
        """
        return self.kartDNA[EKartDNA.RIMS_TYPE]

    def getDecalType(self):
        """
        Purpose: The getDecalType Method obtains the decal
        accessory of the kart by accessing the Kart DNA.

        Params: None
        Return: decalType - the type of decal set for the kart.
        """
        return self.kartDNA[EKartDNA.DECAL_TYPE]

    def getOwner(self):
        return self.ownerId
