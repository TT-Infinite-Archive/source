from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectAI import DistributedObjectAI
from direct.fsm.FSM import FSM
from toontown.estate.DistributedHouseAI import DistributedHouseAI
import HouseGlobals
import functools
import time



class LoadHouseFSM(FSM):
    def __init__(self, mgr, estate, houseIndex, toon, callback):
        FSM.__init__(self, 'LoadHouseFSM')
        self.mgr = mgr
        self.estate = estate
        self.houseIndex = houseIndex
        self.toon = toon
        self.callback = callback

        self.done = False

    def start(self):
        # We have a few different cases here:
        if self.toon is None:
            # Case #1: There isn't a Toon in that estate slot. Make a blank house.

            # Because this state completes so fast, we'll use taskMgr to delay
            # it until the next iteration. This solves re-entrancy problems.
            taskMgr.doMethodLater(0.0, self.demand,
                                  'makeBlankHouse-%s' % id(self),
                                  extraArgs=['MakeBlankHouse'])
            return

        self.houseId = self.toon.get('setHouseId', [0])[0]
        if self.houseId  == 0:
            # Case #2: There is a Toon, but no setHouseId. Gotta make one.
            self.demand('CreateHouse')
        else:
            # Case #3: Toon with a setHouseId. Load it.
            self.demand('LoadHouse')

    def enterMakeBlankHouse(self):
        self.house = DistributedHouseAI(self.mgr.air)
        self.house.setHousePos(self.houseIndex)
        self.house.setColor(self.houseIndex)
        self.house.generateWithRequired(self.estate.zoneId)
        self.estate.houses[self.houseIndex] = self.house
        self.demand('Off')

    def enterCreateHouse(self):
        self.mgr.air.dbInterface.createObject(
            self.mgr.air.dbId,
            self.mgr.air.dclassesByName['DistributedHouseAI'],
            {
                'setName' : [self.toon['setName'][0]],
                'setAvatarId' : [self.toon['ID']],
            },
            self.__handleCreate)

    def __handleCreate(self, doId):
        if self.state != 'CreateHouse':
            return

        # Update the avatar's houseId:
        av = self.mgr.air.doId2do.get(self.toon['ID'])
        if av:
            av.b_setHouseId(doId)
        else:
            self.mgr.air.dbInterface.updateObject(
                self.mgr.air.dbId,
                self.toon['ID'],
                self.mgr.air.dclassesByName['DistributedToonAI'],
                {'setHouseId': [doId]})

        self.houseId = doId
        self.demand('LoadHouse')

    def enterLoadHouse(self):
        # Activate the house:
        self.mgr.air.sendActivate(self.houseId, self.mgr.air.districtId, self.estate.zoneId,
                                  self.mgr.air.dclassesByName['DistributedHouseAI'],
                                  {'setHousePos': [self.houseIndex],
                                   'setColor': [self.houseIndex],
                                   'setName': [self.toon['setName'][0]],
                                   'setAvatarId': [self.toon['ID']]})

        # Now we wait for the house to show up... We do this by hanging a messenger
        # hook which the DistributedHouseAI throws once it spawns.
        self.acceptOnce('generate-%d' % self.houseId, self.__gotHouse)

    def __gotHouse(self, house):
        self.house = house
        if self.mgr.air.wantPets:
            house.generatePet(self.toon.get('setPetId')[0])
        self.estate.houses[self.houseIndex] = house
        self.demand('Off')

    def exitLoadHouse(self):
        self.ignore('generate-%d' % self.houseId)

    def enterOff(self):
        self.done = True
        self.callback(self.house)


class LoadEstateFSM(FSM):
    def __init__(self, mgr, callback):
        FSM.__init__(self, 'LoadEstateFSM')
        self.mgr = mgr
        self.callback = callback

        self.estate = None

    def start(self, accountId, zoneId):
        self.accountId = accountId
        self.zoneId = zoneId
        self.demand('QueryAccount')

    def enterQueryAccount(self):
        self.mgr.air.dbInterface.queryObject(self.mgr.air.dbId, self.accountId,
                                             self.__gotAccount)

    def __gotAccount(self, dclass, fields):
        if self.state != 'QueryAccount':
            return # We must have aborted or something...

        if dclass != self.mgr.air.dclassesByName['AccountAI']:
            self.mgr.notify.warning('Account %d has non-account dclass %d!' %
                                    (self.accountId, dclass))
            self.demand('Failure')
            return

        self.accountFields = fields

        self.estateId = fields.get('ESTATE_ID', 0)
        self.demand('QueryToons')

    def enterQueryToons(self):
        self.toonIds = self.accountFields.get('ACCOUNT_AV_SET', [0]*6)
        self.toons = {}

        for index, toonId in enumerate(self.toonIds):
            if toonId == 0:
                self.toons[index] = None
                continue
            self.mgr.air.dbInterface.queryObject(
                self.mgr.air.dbId, toonId,
                functools.partial(self.__gotToon, index=index))

    def __gotToon(self, dclass, fields, index):
        if self.state != 'QueryToons':
            return # We must have aborted or something...

        if dclass != self.mgr.air.dclassesByName['DistributedToonAI']:
            self.mgr.notify.warning('Account %d has avatar %d with non-Toon dclass %d!' %
                                    (self.accountId, self.toonIds[index], dclass))
            self.demand('Failure')
            return

        fields['ID'] = self.toonIds[index]
        self.toons[index] = fields
        if len(self.toons) == 6:
            self.__gotAllToons()

    def __gotAllToons(self):
        # Okay, we have all of our Toons, now we can proceed with estate!
        if self.estateId:
            # We already have an estate, load it!
            self.demand('LoadEstate')
        else:
            # We don't have one yet, make one!
            self.demand('CreateEstate')

    def enterCreateEstate(self):
        # We have to ask the DB server to construct a blank estate object...
        self.mgr.air.dbInterface.createObject(
            self.mgr.air.dbId,
            self.mgr.air.dclassesByName['DistributedEstateAI'],
            {},
            self.__handleEstateCreate)

    def __handleEstateCreate(self, estateId):
        if self.state != 'CreateEstate':
            return  # We must have aborted or something...
        self.estateId = estateId

        # Update our account so we can store this new estate object.
        self.mgr.air.dbInterface.updateObject(
            self.mgr.air.dbId,
            self.accountId,
            self.mgr.air.dclassesByName['AccountAI'],
            {'ESTATE_ID': self.estateId}
        )

        self.demand('LoadEstate')

    def enterLoadEstate(self):
        # Activate the estate:
        self.mgr.air.sendActivate(self.estateId, self.mgr.air.districtId, self.zoneId)

        # Now we wait for the estate to show up... We do this by hanging a messenger
        # hook which the DistributedEstateAI throws once it spawns.
        self.acceptOnce('generate-%d' % self.estateId, self.__gotEstate)

    def __gotEstate(self, estate):
        self.estate = estate
        
        self.estate.toons = self.toonIds
        self.estate.updateToons()

        # Gotcha! Now we need to load houses:
        self.demand('LoadHouses')

    def exitLoadEstate(self):
        self.ignore('generate-%d' % self.estateId)

    def enterLoadHouses(self):
        self.houseFSMs = []

        for houseIndex in xrange(6):
            fsm = LoadHouseFSM(self.mgr, self.estate, houseIndex,
                               self.toons[houseIndex], self.__houseDone)
            self.houseFSMs.append(fsm)
            fsm.start()

    def __houseDone(self, house):
        if self.state != 'LoadHouses':
            # We aren't loading houses, so we probably got cancelled. Therefore,
            # the only sensible thing to do is simply destroy the house.
            house.requestDelete()
            return

        # A houseFSM just finished! Let's see if all of them are done:
        if all(houseFSM.done for houseFSM in self.houseFSMs):
            self.demand('Finished')

    def enterFinished(self):
        self.callback(True)

    def enterFailure(self):
        self.cancel()

        self.callback(False)

    def cancel(self):
        if self.estate:
            self.estate.destroy()
            self.estate = None

        self.demand('Off')


class EstateManagerAI(DistributedObjectAI):
    notify = DirectNotifyGlobal.directNotify.newCategory("EstateManagerAI")

    def __init__(self, air):
        DistributedObjectAI.__init__(self, air)

        self.estate2toons = {}
        self.toon2estate = {}
        self.estate2timeout = {}
        self.estate2pets = {}

    def getEstateZone(self, avId):
        senderId = self.air.getAvatarIdFromSender()
        accId = self.air.getAccountIdFromSender()

        toon = self.air.doId2do.get(senderId)
        if not toon:
            self.air.writeServerEvent('suspicious', senderId, 'Sent getEstateZone() but not on district!')
            return

        # If there's an avId included, then the Toon is interested in visiting a
        # friend. We do NOT load the estate, we simply see if it's already up...
        if avId and avId != senderId:
            av = self.air.doId2do.get(avId)
            if av and av.dclass == self.air.dclassesByName['DistributedToonAI']:
                estate = self._lookupEstate(av)
                if estate:
                    # Yep, there it is!
                    avId = estate.owner.doId
                    zoneId = estate.zoneId
                    self._mapToEstate(toon, estate)
                    self._unloadEstate(toon) # In case they're doing estate->estate TP.
                    if self.air.wantPets:
                        self.loadPet(avId, toon, zoneId, estate)

                    self.sendUpdateToAvatarId(senderId, 'setEstateZone', [avId, zoneId, 0])
            else:
                toon.queryEstateFSM = QueryEstateFSM(self, self.air, avId, senderId, toon,
                                                     self.__handleEstateQueryResponse)
                toon.queryEstateFSM.start()
                return

            # Bummer, couldn't find avId at an estate...
            self.sendUpdateToAvatarId(senderId, 'setEstateZone', [0, 0, 0])
            return

        # The Toon definitely wants to go to his own estate...

        estate = getattr(toon, 'estate', None)
        if estate:
            if self.air.wantPets:
                if hasattr(toon, 'loadPetFSM') and toon.getPetId():
                    toon.loadPetFSM.demand('Cancel')
                    del toon.loadPetFSM

                if toon.getPetId():
                    pet = self.air.doId2do.get(toon.getPetId())
                    if pet:
                        pet.requestDelete()

            # They already have an estate loaded, so let's just return it:
            self._mapToEstate(toon, toon.estate)
            self.sendUpdateToAvatarId(senderId, 'setEstateZone', [senderId, estate.zoneId, 0])

            # If a timeout is active, cancel it:
            if estate in self.estate2timeout:
                self.estate2timeout[estate].remove()
                del self.estate2timeout[estate]

            return

        if getattr(toon, 'loadEstateFSM', None):
            # We already have a loading operation underway; ignore this second
            # request since the first operation will setEstateZone() when it
            # finishes anyway.
            return

        zoneId = self.air.allocateZone()

        def estateLoaded(success):
            if success:
                toon.estate = toon.loadEstateFSM.estate
                toon.estate.owner = toon
                self._mapToEstate(toon, toon.estate)
                self.sendUpdateToAvatarId(senderId, 'setEstateZone', [senderId, zoneId, 0])
                if self.air.wantPets:
                    toon.enterEstate(toon.doId, zoneId)
            else:
                # Estate loading failed??!
                self.sendUpdateToAvatarId(senderId, 'setEstateZone', [0, 0, 0])

                # And I guess we won't need our zoneId anymore...
                self.air.deallocateZone(zoneId)

            toon.loadEstateFSM = None

        self.acceptOnce(self.air.getAvatarExitEvent(toon.doId), self._unloadEstate, extraArgs=[toon])

        toon.loadEstateFSM = LoadEstateFSM(self, estateLoaded)
        toon.loadEstateFSM.start(accId, zoneId)

    def exitEstate(self):
        senderId = self.air.getAvatarIdFromSender()
        toon = self.air.doId2do.get(senderId)

        if not toon:
            self.air.writeServerEvent('suspicious', senderId, 'Sent exitEstate() but not on district!')
            return

        self._unmapFromEstate(toon)
        self._unloadEstate(toon)

    def mapAvatar(self, ownerId):
        avId = self.air.getAvatarIdFromSender()
        toon = self.air.doId2do.get(avId)
        if not toon:
            self.air.writeServerEvent('suspicious', avId, 'Sent mapAvatar() but not on district!')
            return

        owner = self.air.doId2do.get(ownerId)
        if not owner:
            self.air.writeServerEvent('suspicious', avId, 'Sent mapAvatar() but Estate owner not on district!')
            return

        estate = self._lookupEstate(owner)
        if not estate:
            self.air.writeServerEvent('suspicious', avId, 'Sent mapAvatar() but no estate on district!')
            return

        self._mapToEstate(toon, estate)
        if self.air.wantPets:
            self.loadPet(ownerId, toon, estate.zoneId, estate)

    def __handleEstateQueryResponse(self, success=False, location=None, sender=None, avId=None):
        if success:
            self._unloadEstate(sender)  # In case they're doing estate->estate TP.
            shardId = location[0]
            zoneId = location[1]
            if self.air.wantPets:
                self.loadPet(avId, sender, zoneId, None)
            self.sendUpdateToAvatarId(sender.doId, 'setEstateZone', [avId, zoneId, shardId])
        elif sender:
            self.sendUpdateToAvatarId(sender.doId, 'setEstateZone', [0, 0, 0])

    def _unloadEstate(self, toon):
        if getattr(toon, 'estate', None):
            estate = toon.estate

            # Don't use a boot delay if only the owner is in the estate.
            delay = HouseGlobals.BOOT_GRACE_PERIOD if len(self.estate2toons.get(estate, [])) > 1\
                else HouseGlobals.CLEANUP_DELAY_AFTER_BOOT


            if estate not in self.estate2timeout:
                self.estate2timeout[estate] = \
                    taskMgr.doMethodLater(delay,
                                          self._cleanupEstate,
                                          estate.uniqueName('emai-cleanup-task'),
                                          extraArgs=[estate])
            self._sendToonsToPlayground(toon.estate, 0)  # This is a warning only...
            if self.air.wantPets:
                toon.exitEstate(toon.doId, estate.zoneId)

        if getattr(toon, 'loadEstateFSM', None):
            self.air.deallocateZone(toon.loadEstateFSM.zoneId)
            toon.loadEstateFSM.cancel()
            toon.loadEstateFSM = None

        self.ignore(self.air.getAvatarExitEvent(toon.doId))

    def _cleanupEstate(self, estate):
        # Boot all Toons from estate:
        self._sendToonsToPlayground(estate, 1)

        if self.air.wantPets:
            for pet in self.estate2pets.get(estate, []):
                try:
                    pet.requestDelete()
                    del self.estate2pets[pet]
                except KeyError:
                    pass
            try:
                del self.estate2pets[estate]
            except KeyError:
                pass


        # Clean up toon<->estate mappings...
        for toon in self.estate2toons.get(estate, []):
            try:
                if self.air.wantPets:
                    toon.exitEstate(estate.owner.doId, estate.zoneId)
                del self.toon2estate[toon]
            except KeyError:
                pass
        try:
            del self.estate2toons[estate]
        except KeyError:
            pass

        # Clean up timeout, if it exists:
        if estate in self.estate2timeout:
            del self.estate2timeout[estate]

        # Destroy estate and unmap from owner:
        estate.destroy()
        estate.owner.estate = None

        # Free estate's zone:
        self.air.deallocateZone(estate.zoneId)

    def _sendToonsToPlayground(self, estate, reason):
        for toon in self.estate2toons.get(estate, []):
            self.sendUpdateToAvatarId(toon.doId, 'sendAvToPlayground',
                                      [toon.doId, reason])

    def _mapToEstate(self, toon, estate):
        self._unmapFromEstate(toon)

        self.estate2toons.setdefault(estate, []).append(toon)
        self.toon2estate[toon] = estate

    def _unmapFromEstate(self, toon):
        estate = self.toon2estate.get(toon)
        if not estate: return
        del self.toon2estate[toon]

        if self.air.wantPets:
            petId = toon.getPetId()
            pet = None
            if petId:
                pet = self.air.doId2do.get(petId)

            try:
                if pet:
                    if estate in self.estate2pets:
                        self.estate2pets[estate].remove(pet)
                    pet.requestDelete()

            except (KeyError, ValueError):
                pass

        try:
            self.estate2toons[estate].remove(toon)
        except (KeyError, ValueError):
            pass

    def _lookupEstate(self, toon):
        return self.toon2estate.get(toon)

    def getOwnerFromZone(self, avId):
        return False

    def getEstateZones(self, avId):
        # Used for PetLookerAI
        estateZone = None
        av = self.air.doId2do.get(avId)
        if av and av.dclass == self.air.dclassesByName['DistributedToonAI']:
            estate = self._lookupEstate(av)
            if estate:
                estateZone = estate.zoneId
        return [estateZone]

    def getEstateHouseZones(self, avId):
        # Used for PetLookerAI
        houseZones = []
        av = self.air.doId2do.get(avId)
        if av and av.dclass == self.air.dclassesByName['DistributedToonAI']:
            estate = self._lookupEstate(av)
            if estate:
                for house in estate.houses:
                    houseZones.append(house.interiorZone)
        return houseZones

    def loadPet(self, ownerId, toon, zoneId, estate):
        if not toon.doId == ownerId:
            toon.enterEstate(ownerId, zoneId)
            if hasattr(toon, 'loadPetFSM') and toon.getPetId():
                toon.loadPetFSM.demand('Cancel')
                del toon.loadPetFSM

            pet = simbase.air.doId2do.get(toon.getPetId())
            if pet:
                pet.requestDelete()

            toon.loadPetFSM = LoadPetFSM(self, self.air, ownerId, toon, estate, zoneId)
            toon.loadPetFSM.request('LoadPet')


class LoadPetFSM(FSM):
    def __init__(self, mgr, air, estateOwnerId, toon, estate, zoneId):
        FSM.__init__(self, 'LoadPetFSM')
        self.mgr = mgr
        self.air = air
        self.estateOwnerId = estateOwnerId
        self.toon = toon
        self.estate = estate
        self.zoneId = zoneId

    def enterLoadPet(self):
        if self.toon.getPetId() > 0:
            self.air.sendActivate(self.toon.getPetId(), self.air.districtId, self.zoneId,
                                  self.air.dclassesByName['DistributedPetAI'],
                                  {"setOwnerId": [self.toon.doId],})

            self.acceptOnce('generate-%d' % self.toon.getPetId(), self.__gotPet)

    def exitLoadPet(self):
        self.ignore('generate-%d' % self.toon.getPetId())

    def __gotPet(self, pet):
        self.request('GotPet', pet)

    def enterGotPet(self, pet):
        if not self.estate:
            self.pet = pet
            return
        if self.estate not in self.mgr.estate2pets:
            self.mgr.estate2pets[self.estate] = []
        self.mgr.estate2pets[self.estate].append(pet)
        self.pet = pet

    def enterCancel(self):
        self.ignore('generate-%d' % self.toon.getPetId())
        try:
            if hasattr(self, 'pet') and self.estate in self.mgr.estate2pets:
                if self.pet in self.mgr.estate2pets[self.estate]:
                    self.mgr.estate2pets[self.estate].remove(self.pet)
        except:
            pass



class QueryEstateFSM(FSM):
    def __init__(self, mgr, air, avId, senderId, sender, callback):
        FSM.__init__(self, 'QueryEstateFSM')
        self.mgr = mgr
        self.air = air
        self.avId = avId
        self.senderId = senderId
        self.sender = sender
        self.callback = callback
        self.houseId = None
        self.houseLocation = None
        self.avLocation = None

    def start(self):
        self.demand('QueryToon')

    def enterQueryToon(self):
        self.air.dbInterface.queryObject(
            self.air.dbId, self.avId, self.__handleRetrieve)

    def enterQueryEstate(self):
        self.air.getActivated(self.houseId, self.__handleGetActivated)

    def enterDone(self):
        if self.avLocation is None or self.houseLocation is None:
            self.demand('Error', 'Locations are None.')
            return

        if self.avLocation == self.houseLocation:
            # We found the estate zone!
            self.callback(True, self.houseLocation, self.sender, self.avId)
            self.demand('Off')
            return

        self.demand('Error', 'Locations do not match. %s %s' % (self.avLocation, self.houseLocation))
        return

    def enterError(self, error=''):
        self.mgr.notify.warning('QueryEstateFSM Error: %s' % error)
        self.callback(False, sender=self.sender)
        return

    def enterOff(self):
        pass

    def __handleRetrieve(self, dclass, fields):
        if dclass == self.air.dclassesByName['DistributedToonAI']:
            self.houseId = fields['setHouseId'][0]
            if not self.houseId:
                self.demand('Error', 'Recieved invalid houseId when querying toon %s.' % self.avId)
                return

            self.air.getActivated(self.avId, self.__handleGetActivated)
            return

        self.demand('Error', 'Recieved invalid dclass when querying toon %s.' % self.avId)
        return

    def __handleGetActivated(self, doId, isActivated):
        if not isActivated:
            self.demand('Error', 'Object %s is not activated.' % doId)
            return

        if isActivated and doId == self.avId:
            self.air.queryObjectLocation(self.avId, self.__handleLocationQuery)
            return

        if isActivated and doId == self.houseId:
            self.air.queryObjectLocation(self.houseId, self.__handleLocationQuery)
            return

    def __handleLocationQuery(self, parentId, zoneId):
        if self.state == 'QueryToon':
            self.avLocation = (parentId, zoneId)
            self.demand('QueryEstate')
            return

        if self.state == 'QueryEstate':
            self.houseLocation = (parentId, zoneId)
            self.demand('Done')
            return

        self.demand('Error', 'Invalid state %s while querying location.' % self.state)
        return
