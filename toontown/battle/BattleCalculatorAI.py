import random

from direct.directnotify.DirectNotifyGlobal import directNotify

from toontown.battle import BattleAttack
from toontown.data import Gag, GagDefs, SuitAttack


class BattleCalculatorAI:
    notify = directNotify.newCategory('BattleCalculatorAI')

    def __init__(self, battle, tutorialFlag = 0):
        self.tutorialFlag = tutorialFlag
        self.battle = battle

    def cleanup(self):
        self.battle = 0

    def generateMovieAttack(self, attack):
        if attack is None:
            return None
        ma = BattleAttack.MovieAttack()
        ma.fromList(attack.toList() + [False])
        # Get the attack object for this attack id
        if ma.attackerId in self.battle.activeToons:
            # Toon is attacking; they use gags
            gag = GagDefs.Gags.get(ma.attackId)
            # Check if its a real gag
            if gag is not None:
                # Check if attack hit
                ma.hit = gag.chance >= random.uniform(0, 1)
        else:
            # Suit is attacking
            sa = SuitAttack.getSuitAttack(ma.attackId)
            # Check if attack hit
            ma.hit = sa.accuracy >= random.uniform(0, 1)
        self.notify.debug('generatedAttack: %s' % ma.toList())
        return ma

    def makeSuitAttack(self, suit):
        sa = random.choice(SuitAttack.SuitAttacks.values()[1:])
        ba = BattleAttack.BattleAttack(suit.doId, sa.attackId, targetId=0)
        if sa.targetsAlly():
            # Choose a suit to attack
            potentialSuits = self.battle.activeSuits
            target = random.choice(potentialSuits)
            ba.targetId = target.doId
        elif sa.targetsEnemy():
            # Choose a toon to attack
            potentialToons = self.battle.activeToons
            ba.targetId = random.choice(potentialToons)
        self.notify.debug('Made suit attack %s' % sa)
        return ba
