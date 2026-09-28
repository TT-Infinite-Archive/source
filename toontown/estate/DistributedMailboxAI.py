from direct.distributed import DistributedObjectAI
from . import MailboxGlobals
from toontown.catalog import CatalogItem
from toontown.catalog import CatalogItemList
from toontown.toonbase import ToontownGlobals
from toontown.parties.PartyGlobals import EInviteStatus
from direct.directnotify.DirectNotifyGlobal import *
from direct.distributed.ClockDelta import *
from direct.task import Task

class DistributedMailboxAI(DistributedObjectAI.DistributedObjectAI):

    notify = directNotify.newCategory('DistributedMailboxAI')

    def __init__(self, air, house):
        DistributedObjectAI.DistributedObjectAI.__init__(self, air)
        self.house = house
        self.fullIndicator = 0
        self.raiseFlagTask = None
        self.busy = 0
        self.av = None
        self.collisionSetup = False

    def delete(self):
        self.notify.debug("delete()")
        self.ignoreAll()
        if self.raiseFlagTask:
            taskMgr.remove(self.raiseFlagTask)
            self.raiseFlagTask = None
        del self.house
        DistributedObjectAI.DistributedObjectAI.delete(self)

    def setupPetCollision(self):
        if simbase.wantPets and not self.collisionSetup:
            # assuming houseNode exists
            houseNode = self.house.houseNode
            estate = self.air.doId2do[self.house.estateId]
            zOffset = 0
            if self.house.housePosInd == 3:
                zOffset = -1
            elif self.house.housePosInd == 2:
                zOffset = 0.5
            model = loader.loadModel('phase_5.5/models/estate/mailboxHouse')

            coll = model.find('**/mailbox_collision')
            coll.reparentTo(estate.geom)
            coll.setPos(houseNode, 19, -4, 0 + zOffset)
            coll.setH(houseNode, 90)

            model.removeNode()
            self.collisionSetup = True

    def getHouseId(self):
        return self.house.doId

    def getHousePos(self):
        return self.house.housePosInd

    def getName(self):
        return self.house.name

    def b_setFullIndicator(self, full):
        DistributedMailboxAI.notify.debug("b_setFullIndicator( full=%s )" %full)
        self.setFullIndicator(full)
        self.d_setFullIndicator(full)

    def d_setFullIndicator(self, full):
        DistributedMailboxAI.notify.debug("d_setFullIndicator( full=%s )" %full)
        self.sendUpdate("setFullIndicator", [full])

    def setFullIndicator(self, full):
        DistributedMailboxAI.notify.debug("setFullIndicator( full=%s )" %full)
        self.fullIndicator = full

    def raiseFlagLater(self, duration):
        # Sets a doLater task to raise the mailbox's flag (i.e. set
        # the full indicator to true) after the indicated number of
        # seconds have elapsed.
        DistributedMailboxAI.notify.debug("raiseFlagLater( duration=%.2f )" %duration)
        if self.raiseFlagTask:
            taskMgr.remove(self.raiseFlagTask)
        taskName = self.taskName("raiseFlag")
        self.raiseFlagTask = taskMgr.doMethodLater(
            duration,
            self.__raiseFlag,
            taskName
        )

    def __raiseFlag(self, task):
        DistributedMailboxAI.notify.debug("__raiseFlag")
        self.b_setFullIndicator(1)
        return Task.done

    def freeAvatar(self, avId):
        # Free this avatar, probably because he requested interaction while
        # I was busy. This can happen when two avatars request interaction
        # at the same time. The AI will accept the first, sending a setMovie,
        # and free the second
        DistributedMailboxAI.notify.debug("freeAvatar( avId=%d )" %avId)
        self.sendUpdateToAvatarId(avId, "freeAvatar", [])
        return

    def avatarEnter(self):
        avId = self.air.getAvatarIdFromSender()
        # this avatar has come within range
        DistributedMailboxAI.notify.debug("avatarEnter: avatarId=%d" % (avId))

        # If we are busy, free this new avatar
        if self.busy:
            DistributedMailboxAI.notify.debug("already busy with: %s" % (self.busy))
            self.freeAvatar(avId)
            return

        # Fetch the actual avatar object
        av = self.air.doId2do.get(avId)
        if not av:
            self.air.writeServerEvent('suspicious', avId, 'DistributedMailboxAI.avatarEnter unknown')
            self.notify.warning("av %s not in doId2do tried to pick up mailbox" % (avId))
            return

        # Flag us as busy with this avatar Id
        self.busy = avId
        self.av = av

        # Handle unexpected exit
        self.acceptOnce(self.air.getAvatarExitEvent(avId),
                        self.__handleUnexpectedExit, extraArgs=[avId])
        self.acceptOnce("bootAvFromEstate-"+str(avId),
                        self.__handleBootMessage, extraArgs=[avId])

        # Check the owner of the mailbox.  You shouldn't be digging
        # around in someone else's mailbox!
        if self.house.ownerId == avId:

            if len(av.mailboxContents) != 0:
                # Purchases are available!  Tell the client; he will
                # start accepting the items one at a time when he's
                # ready.
                self.sendCatalog()
            elif len(av.awardMailboxContents) != 0:
                # awards are available!  Tell the client; he will
                # start accepting the items one at a time when he's
                # ready.
                self.sendAwardCatalog()

            elif ((av.numMailItems > 0) or (av.getNumInvitesToShowInMailbox() > 0)):
                # he's got mail, tell the client
                self.sendMail()

            elif len(av.onOrder) != 0:
                self.sendUpdate("setMovie", [MailboxGlobals.MAILBOX_MOVIE_WAITING, avId])
                self.sendClearMovie()
            else:
                # The client should filter this already.
                # self.air.writeServerEvent('suspicious', avId, 'DistributedMailboxAI.avatarEnter empty')
                self.sendUpdate("setMovie", [MailboxGlobals.MAILBOX_MOVIE_EMPTY, avId])
                self.sendClearMovie()
        else:
            # Wrong mailbox.  Go away.
            # The client should filter this already.
            self.air.writeServerEvent('suspicious', avId, 'DistributedMailboxAI.avatarEnter not owner')
            self.sendUpdate("setMovie", [MailboxGlobals.MAILBOX_MOVIE_NOT_OWNER, avId])
            self.sendClearMovie()


    def sendCatalog(self):
        DistributedMailboxAI.notify.debug("sendCatalog")
        # Now open the catalog up on the client.
        self.sendUpdate("setMovie", [MailboxGlobals.MAILBOX_MOVIE_READY, self.av.doId])
        # The avatar has seen his items now.
        if self.av.mailboxNotify == ToontownGlobals.NewItems:
            self.av.b_setCatalogNotify(self.av.catalogNotify, ToontownGlobals.OldItems)

    def sendAwardCatalog(self):
        DistributedMailboxAI.notify.debug("sendCatalog")
        # Now open the catalog up on the client.
        self.sendUpdate("setMovie", [MailboxGlobals.MAILBOX_MOVIE_READY, self.av.doId])
        # The avatar has seen his items now.
        # The avatar has seen his items now.
        if self.av.awardNotify == ToontownGlobals.NewItems:
            self.av.b_setAwardNotify(ToontownGlobals.OldItems)


    def sendMail(self):
        DistributedMailboxAI.notify.debug("sendMail")
        # Now open the catalog up on the client.
        self.sendUpdate("setMovie", [MailboxGlobals.MAILBOX_MOVIE_READY, self.av.doId])
        #RAU TODO set mailNotify to oldItems
        # The avatar has seen his items now.
        #if self.av.mailNotify == ToontownGlobals.NewItems:
        #    self.av.b_setCatalogNotify(self.av.catalogNotify, ToontownGlobals.OldItems)

    def avatarExit(self):
        DistributedMailboxAI.notify.debug("avatarExit")
        self.notify.debug("avatarExit")
        avId = self.air.getAvatarIdFromSender()

        if self.busy == avId:
            self.sendExitMovie()
        self.freeAvatar(avId)

    def __handleUnexpectedExit(self, avId):
        self.notify.warning('avatar:' + str(avId) + ' has exited unexpectedly')
        self.sendClearMovie()

    def __handleBootMessage(self, avId):
        self.notify.warning('avatar:' + str(avId) + ' got booted ')
        self.sendClearMovie()

    def sendExitMovie(self):
        assert(DistributedMailboxAI.notify.debug('sendExitMovie()'))
        # Send movie to play closing sound
        self.sendUpdate("setMovie", [MailboxGlobals.MAILBOX_MOVIE_EXIT,
                                     self.busy])
        # Ignore unexpected exits on whoever I was busy with
        self.ignoreAll()
        self.busy = 0
        self.av = None

    def sendClearMovie(self):
        assert(DistributedMailboxAI.notify.debug('sendClearMovie()'))
        # Ignore unexpected exits on whoever I was busy with
        self.ignoreAll()
        self.busy = 0
        self.av = None
        self.sendUpdate("setMovie", [MailboxGlobals.MAILBOX_MOVIE_CLEAR, 0])

    def getMailboxItem(self, item, itemIndex):
        # Awards fill the first slots, then the mailbox proper. The client's
        # item only has to agree with what we hold, and ours is what's used
        awards = self.av.awardMailboxContents
        if 0 <= itemIndex < len(awards):
            stored, isAward = awards[itemIndex], True
        elif 0 <= itemIndex - len(awards) < len(self.av.mailboxContents):
            stored, isAward = self.av.mailboxContents[itemIndex - len(awards)], False
        else:
            return None, False

        if stored != item:
            return None, False

        return stored, isAward

    def removeMailboxItem(self, itemIndex, isAward):
        if isAward:
            del self.av.awardMailboxContents[itemIndex]
            self.av.b_setAwardMailboxContents(self.av.awardMailboxContents)
        else:
            del self.av.mailboxContents[itemIndex - len(self.av.awardMailboxContents)]
            self.av.b_setMailboxContents(self.av.mailboxContents)

    def acceptItemMessage(self, context, blob, itemIndex, optional):
        DistributedMailboxAI.notify.debug('acceptItemMessage()')
        # Sent from the client code to request a particular item from
        # the mailbox.
        avId = self.air.getAvatarIdFromSender()
        item = CatalogItem.getItem(blob, store = CatalogItem.Customization)
        if self.busy != avId:
            # The client should filter this already.
            self.air.writeServerEvent('suspicious', avId, 'DistributedMailboxAI.acceptItem busy with %s' % (self.busy))
            self.notify.warning("Got unexpected item request from %s while busy with %s." % (avId, self.busy))
            retcode = ToontownGlobals.P_NotAtMailbox
        else:
            stored, isAward = self.getMailboxItem(item, itemIndex)
            if stored is None:
                self.air.writeServerEvent('suspicious', avId, 'DistributedMailboxAI.acceptItem invalid index %s' % (itemIndex))
                retcode = ToontownGlobals.P_InvalidIndex
            else:
                # Give the item to the user.
                retcode = stored.recordPurchase(self.av, optional)
                if retcode >= 0:
                    self.removeMailboxItem(itemIndex, isAward)
        self.sendUpdateToAvatarId(avId, "acceptItemResponse", [context, retcode])

    def discardItemMessage(self, context, blob, itemIndex, optional):
        DistributedMailboxAI.notify.debug("discardItemMessage")
        # Sent from the client code to request a particular item from
        # the mailbox to be discarded.
        avId = self.air.getAvatarIdFromSender()
        item = CatalogItem.getItem(blob, store = CatalogItem.Customization)
        retcode = 0
        if self.busy != avId:
            # The client should filter this already.
            self.air.writeServerEvent('suspicious', avId, 'DistributedMailboxAI.acceptItem busy with %s' % (self.busy))
            DistributedMailboxAI.notify.warning("Got unexpected item discard request from %s while busy with %s." % (avId, self.busy))
            retcode = ToontownGlobals.P_NotAtMailbox
        else:
            stored, isAward = self.getMailboxItem(item, itemIndex)
            if stored is None:
                self.air.writeServerEvent('suspicious', avId, 'DistributedMailboxAI.discardItem invalid index %s' % (itemIndex))
                retcode = ToontownGlobals.P_InvalidIndex
            else:
                self.air.writeServerEvent("Discarding Item award" if isAward else "Discarding Item", avId, "discarded item %s" % (stored.getName()))
                self.removeMailboxItem(itemIndex, isAward)

        self.sendUpdateToAvatarId(avId, "discardItemResponse", [context, retcode])

    def acceptInviteMessage(self, context, inviteKey):
        DistributedMailboxAI.notify.debug("acceptInviteMessage")
        # Sent from the client code to request a particular item from
        # the mailbox.
        avId = self.air.getAvatarIdFromSender()
        validInviteKey = False
        toon = simbase.air.doId2do.get(avId)
        retcode = None
        if toon:
            for invite in toon.invites:
                if invite.inviteKey == inviteKey:
                    validInviteKey = True
                    break
        if self.busy != avId:
            # The client should filter this already.
            self.air.writeServerEvent('suspicious', avId, 'DistributedMailboxAI.acceptInvite busy with %s' % (self.busy))
            self.notify.warning("Got unexpected accept invite request from %s while busy with %s." % (avId, self.busy))
            retcode = ToontownGlobals.P_NotAtMailbox

        elif not validInviteKey:
            self.air.writeServerEvent('suspicious', avId, 'DistributedMailboxAI.acceptInvite invalid inviteKey %s' % (inviteKey))
            retcode = ToontownGlobals.P_InvalidIndex
        else:
            # hand it off to party manager
            # it's possible the party was cancelled right before he accepted
            self.air.partyManager.respondToInviteFromMailbox(context, inviteKey, EInviteStatus.ACCEPTED, self.doId)

        if not (retcode == None):
            self.sendUpdateToAvatarId(avId, "acceptItemResponse", [context, retcode])


    def respondToAcceptInviteCallback(self, context, inviteKey, retcode):
        """Tell the client the result of accepting/rejecting the invite."""
        DistributedMailboxAI.notify.debug("respondToAcceptInviteCallback")
        if self.av:
            self.sendUpdateToAvatarId(self.av.doId, "acceptItemResponse", [context, retcode])


    def markInviteReadButNotReplied(self, inviteKey):
        """Mark the invite as read but not replied in the db."""
        toon = simbase.air.doId2do.get(self.air.getAvatarIdFromSender())
        if not toon:
            return
        if any(invite.inviteKey == inviteKey and invite.status == EInviteStatus.NOT_READ
               for invite in toon.invites):
            self.air.partyManager.markInviteReadButNotReplied(inviteKey)

    def rejectInviteMessage(self, context, inviteKey):
        DistributedMailboxAI.notify.debug("rejectInviteMessage")
        # Sent from the client code to request a particular item from
        # the mailbox.
        avId = self.air.getAvatarIdFromSender()
        validInviteKey = False
        toon = simbase.air.doId2do.get(avId)
        retcode = None
        if toon:
            for invite in toon.invites:
                if invite.inviteKey == inviteKey:
                    validInviteKey = True
                    break
        if self.busy != avId:
            # The client should filter this already.
            self.air.writeServerEvent('suspicious', avId, 'DistributedMailboxAI.rejectInvite busy with %s' % (self.busy))
            DistributedMailboxAI.notify.warning("Got unexpected reject invite request from %s while busy with %s." % (avId, self.busy))
            retcode = ToontownGlobals.P_NotAtMailbox

        elif not validInviteKey:
            self.air.writeServerEvent('suspicious', avId, 'DistributedMailboxAI.rejectInvite invalid inviteKey %s' % (inviteKey))
            retcode = ToontownGlobals.P_InvalidIndex
        else:
            # hand it off to party manager
            # it's possible the party was cancelled right before he rejected
            self.air.partyManager.respondToInviteFromMailbox(context, inviteKey, EInviteStatus.REJECTED, self.doId)

        if not (retcode == None):
            self.sendUpdateToAvatarId(avId, "discardItemResponse", [context, retcode])


    def respondToRejectInviteCallback(self, context, inviteKey, retcode):
        DistributedMailboxAI.notify.debug("respondToRejectInviteCallback")
        """Tell the client the result of accepting/rejecting the invite."""
        if self.av:
            self.sendUpdateToAvatarId(self.av.doId, "discardItemResponse", [context, retcode])
        pass
