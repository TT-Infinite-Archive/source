"""DistributedDaleAI module: contains the DistributedDaleAI class"""

from . import DistributedCCharBaseAI
from direct.directnotify import DirectNotifyGlobal
from direct.fsm import ClassicFSM
from direct.fsm import State
from direct.task import Task
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import TTLocalizer
from . import CharStateDatasAI


class DistributedDaleAI(DistributedCCharBaseAI.DistributedCCharBaseAI):
    notify = DirectNotifyGlobal.directNotify.newCategory("DistributedDaleAI")

    def __init__(self, air, chipId):
        DistributedCCharBaseAI.DistributedCCharBaseAI.__init__(self, air, TTLocalizer.Dale)
        self.chipId = chipId
        self.chip = air.doId2do.get(chipId)
        self.fsm = ClassicFSM.ClassicFSM('DistributedDaleAI',
                                         [State.State('Off',
                                                      self.enterOff,
                                                      self.exitOff,
                                                      ['FollowChip']),
                                          State.State('FollowChip',
                                                      self.enterFollowChip,
                                                      self.exitFollowChip,
                                                      ['FollowChip', 'TransitionToCostume']),
                                          ],
                                         # Initial State
                                         'Off',
                                         # Final State
                                         'Off',
                                         )

        self.fsm.enterInitialState()
        self.handleHolidays()

    def delete(self):
        self.fsm.requestFinalState()
        DistributedCCharBaseAI.DistributedCCharBaseAI.delete(self)

        self.lonelyDoneEvent = None
        self.lonely = None
        self.chattyDoneEvent = None
        self.chatty = None
        self.walkDoneEvent = None
        self.walk = None

    def generate(self):
        # all state data's that Dale will need
        #
        DistributedCCharBaseAI.DistributedCCharBaseAI.generate(self)

        # self.followChipDoneEvent = self.taskName(name + '-follow-done')        
        self.followChip = CharStateDatasAI.CharFollowChipStateAI(
            None, self, self.chip)

    def walkSpeed(self):
        return ToontownGlobals.DaleSpeed

    # this function kicks off Dale
    def start(self):
        # poor Dale, having to endure Chip
        self.fsm.request('FollowChip')

    ### Off state ###
    def enterOff(self):
        pass

    def exitOff(self):
        DistributedCCharBaseAI.DistributedCCharBaseAI.exitOff(self)

    ### Follow Chip state ###
    def enterFollowChip(self):
        self.notify.debug("enterFollowChip")
        walkState = self.chip.walk
        destNode = walkState.getDestNode()
        self.followChip.enter(destNode)

    def exitFollowChip(self):
        self.notify.debug('exitFollowChip')
        self.followChip.exit()

    def avatarEnterNextState(self):
        """
        decide what to do with the state machine when
        a toon gets near Dale
        """
        self.notify.debug("avatarEnterNextState: num avatars: " + str(len(self.nearbyAvatars)))

    def avatarExitNextState(self):
        """
        decide what to do with the state machine when a
        toon is no longer near Dale
        """
        pass

    def chipEnteringState(self, newState):
        """Handle chip entering a new state."""
        assert self.notify.debugStateCall(self)
        if newState == 'Walk':
            self.doFollowChip()

    def chipLeavingState(self, oldState):
        """Handle chip leaving his state."""
        assert self.notify.debugStateCall(self)

    def doFollowChip(self):
        """Actually make dale follow chip."""
        walkState = self.chip.walk
        destNode = walkState.getDestNode()
        # import pdb; pdb.set_trace()
        self.fsm.request('FollowChip')

    def getWalk(self):
        """
        Sync Dale with Chip's Walk
        """
        return self.chip.getWalk()

    def getChipId(self):
        """Return chip's doId."""
        return self.chipId
