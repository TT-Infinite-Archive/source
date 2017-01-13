import random

from direct.directnotify.DirectNotifyGlobal import directNotify

from toontown.battle import BattleAttack
from toontown.data import Gag


class BattleCalculatorAI:
    notify = directNotify.newCategory('BattleCalculatorAI')

    def __init__(self, battle, tutorialFlag = 0):
        self.battle = battle
        self.tutorialFlag = tutorialFlag

    def cleanup(self):
        self.battle = None

    def generateMovieAttacks(self):
        self.notify.debug('Generating movie attacks...')
        # Fill toon movie and suit movie attacks
        tmas = self.__generateToonMovieAttacks()
        smas = self.__generateSuitMovieAttacks()
        return tmas, smas

    def __generateToonMovieAttacks(self):
        # Go through each toon attack
        tmas = []
        for ta in self.battle.toonAttacks.values():
            tma = BattleAttack.MovieAttack()
            tma.fromList(ta.toList() + [False])
            # Get the gag object for this attack id
            gag = Gag.Gags.get(ta.attackId)
            # Check if its a real gag
            if gag is not None:
                # Check if attack hit
                tma.hit = gag.chance >= random.uniform(0, 1)
                self.notify.debug('generatedToonAttack: %s' % tma.toList())
                tmas.append(tma)
            else:
                self.notify.warning('Unknown toon attack %s' % ta.attackId)
        return tmas

    def __generateSuitMovieAttacks(self):
        smas = []
        for sa in self.battle.suitAttacks:
            sma = BattleAttack.MovieAttack()
            sma.fromList(sa.toList() + [False])
            attack = BattleAttack.SuitAttacks.get(sa.attackId)
            if attack is not None:
                # Check if attack hit
                sma.hit = attack.chance >= random.uniform(0, 1)
                smas.append(sma)
            else:
                self.notify.warning('Invalid suit attack %s' % sa.attackId)
        return smas
