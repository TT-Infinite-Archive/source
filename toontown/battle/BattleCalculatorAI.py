from toontown.battle import BattleAttack
from toontown.toon import InventoryGlobals
from direct.directnotify.DirectNotifyGlobal import directNotify
import random


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
            gag = InventoryGlobals.Gags.get(ta.attackId)
            # Check if its a real gag
            if gag is not None:
                # Check if this hit
                if gag.isTargeted() and gag.accuracy > random.uniform(0, 1):
                    # It hit, set our movie attack
                    tma.hit = True
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
                if attack.accuracy > random.uniform(0, 1):
                    sma.hit = True
                smas.append(sma)
            else:
                self.notify.warning('Invalid suit attack %s' % sa.attackId)
        return smas
