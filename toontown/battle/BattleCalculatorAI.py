import random

from direct.directnotify.DirectNotifyGlobal import directNotify

from toontown.battle import BattleAttack
from toontown.data import Gag, GagDefs


class BattleCalculatorAI:
    notify = directNotify.newCategory('BattleCalculatorAI')

    def __init__(self, tutorialFlag = 0):
        self.tutorialFlag = tutorialFlag

    def generateMovieAttack(self, attack):
        if attack is None:
            return None
        ma = BattleAttack.MovieAttack()
        ma.fromList(attack.toList() + [False])
        # Get the gag object for this attack id
        gag = GagDefs.Gags.get(ma.attackId)
        # Check if its a real gag
        if gag is not None:
            # Check if attack hit
            ma.hit = gag.chance >= random.uniform(0, 1)
            self.notify.debug('generatedAttack: %s' % ma.toList())
        else:
            self.notify.warning('Unknown toon attack %s' % ma.attackId)
        return ma
