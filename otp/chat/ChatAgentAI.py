from direct.distributed.DistributedObjectGlobalAI import DistributedObjectGlobalAI
from direct.directnotify import DirectNotifyGlobal
from otp.ai.MagicWordGlobal import *
from toontown.toonbase.TTLocalizer import MutedMessage
from time import time


class ChatAgentAI(DistributedObjectGlobalAI):
    notify = DirectNotifyGlobal.directNotify.newCategory("ChatAgentAI")
    calcTime = lambda self, t: time() + t

    def d_muteAccount(self, av, time):
        if av is not None:
            accountId = av.getDISLid()
            timestamp = self.calcTime(time)
            # Saving timestamp to DB just incase.
            self.air.dbInterface.updateObject(
                self.air.dbId,
                accountId,
                self.air.dclassesByName['AccountAI'],
                {'MUTE_TIMESTAMP': timestamp})
            self.sendUpdate('muteAccount', [accountId, int(timestamp), time])
            av.d_setSystemMessage(0, MutedMessage % time)

@magicWord(category=CATEGORY_MODERATOR, types=[int])
def mute(time):
    """
    Mutes target's account for the specified time in seconds
    """
    target = spellbook.getTarget()
    if target == spellbook.getInvoker():
        return 'You can\'t mute yourself!'
    simbase.air.chatAgent.d_muteAccount(target, time)
    return 'Muting %s...' % target.getName()
