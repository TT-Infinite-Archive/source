"""DistributedFrankenDonaldAI module: contains the DistributedFrankenDonaldAI class"""

from toontown.classicchars import DistributedChipAI
from direct.directnotify import DirectNotifyGlobal
from direct.fsm import ClassicFSM, State
from . import DistributedCCharBaseAI
from toontown.toonbase import TTLocalizer


class DistributedPoliceChipAI(DistributedChipAI.DistributedChipAI):
    notify = DirectNotifyGlobal.directNotify.newCategory("DistributedPoliceChipAI")

    def __init__(self, air):
        DistributedCCharBaseAI.DistributedCCharBaseAI.__init__(self, air, TTLocalizer.PoliceChip)
        self.fsm = ClassicFSM.ClassicFSM('DistributedPoliceChipAI',
                                         [State.State('Off',
                                                      self.enterOff,
                                                      self.exitOff,
                                                      ['Lonely', 'TransitionToCostume']),
                                          State.State('Lonely',
                                                      self.enterLonely,
                                                      self.exitLonely,
                                                      ['Chatty', 'Walk', 'TransitionToCostume']),
                                          State.State('Chatty',
                                                      self.enterChatty,
                                                      self.exitChatty,
                                                      ['Lonely', 'Walk', 'TransitionToCostume']),
                                          State.State('Walk',
                                                      self.enterWalk,
                                                      self.exitWalk,
                                                      ['Lonely', 'Chatty', 'TransitionToCostume']),
                                          ],
                                         # Initial State
                                         'Off',
                                         # Final State
                                         'Off',
                                         )

        self.fsm.enterInitialState()
        self.dale = None
