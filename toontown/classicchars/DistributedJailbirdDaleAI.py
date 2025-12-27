"""DistributedJailbirdDaleAI module: contains the DistributedJailbirdDaleAI class"""

from toontown.classicchars import DistributedDaleAI
from direct.directnotify import DirectNotifyGlobal
from direct.fsm import ClassicFSM, State
from . import DistributedCCharBaseAI
from toontown.toonbase import TTLocalizer


class DistributedJailbirdDaleAI(DistributedDaleAI.DistributedDaleAI):
    notify = DirectNotifyGlobal.directNotify.newCategory("DistributedJailbirdDaleAI")

    def __init__(self, air, chipId):
        DistributedCCharBaseAI.DistributedCCharBaseAI.__init__(self, air, TTLocalizer.JailbirdDale)
        self.chipId = chipId
        self.chip = air.doId2do.get(chipId)
        self.fsm = ClassicFSM.ClassicFSM('DistributedJailbirdDaleAI',
                                         [State.State('Off',
                                                      self.enterOff,
                                                      self.exitOff,
                                                      ['Lonely']),
                                          State.State('Lonely',
                                                      self.enterLonely,
                                                      self.exitLonely,
                                                      ['Chatty', 'FollowChip', 'Walk', 'TransitionToCostume']),
                                          State.State('Chatty',
                                                      self.enterChatty,
                                                      self.exitChatty,
                                                      ['Lonely', 'FollowChip', 'Walk', 'TransitionToCostume']),
                                          State.State('Walk',
                                                      self.enterWalk,
                                                      self.exitWalk,
                                                      ['Lonely', 'Chatty', 'TransitionToCostume']),
                                          State.State('FollowChip',
                                                      self.enterFollowChip,
                                                      self.exitFollowChip,
                                                      ['Lonely', 'Chatty', 'FollowChip', 'TransitionToCostume']),
                                          ],
                                         # Initial State
                                         'Off',
                                         # Final State
                                         'Off',
                                         )

        # We do not want to move into the transitionCostume state unless signalled to do so.
        self.transitionToCostume = 0
        self.fsm.enterInitialState()
