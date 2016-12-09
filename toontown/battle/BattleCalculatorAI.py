from DistributedBattleAI import *
from toontown.toonbase.ToontownBattleGlobals import *
import SuitBattleGlobals
import BattleExperienceAI
from toontown.toon import InventoryGlobals
from toontown.suit.SuitBuffGlobals import SuitBuffStable
from toontown.toon import NPCToons
from toontown.pets import PetTricks
from toontown.hood import ZoneUtil
from direct.showbase.PythonUtil import lerp
from direct.directnotify.DirectNotifyGlobal import directNotify
import random


class BattleCalculatorAI:
    notify = directNotify.newCategory('BattleCalculatorAI')
    AccuracyBonuses = [0, 20, 40, 60]
    DamageBonuses = [0,
     20,
     20,
     20]
    AttackExpPerTrack = [0,
     10,
     20,
     30,
     40,
     50,
     60]
    TRAP_CONFLICT = -2
    APPLY_HEALTH_ADJUSTMENTS = 1
    TOONS_TAKE_NO_DAMAGE = 0
    CAP_HEALS = 1
    CLEAR_SUIT_ATTACKERS = 1
    CLEAR_MULTIPLE_TRAPS = 0
    toonsAlwaysHit = simbase.config.GetBool('toons-always-hit', 0)
    toonsAlwaysMiss = simbase.config.GetBool('toons-always-miss', 0)
    toonsAlways5050 = simbase.config.GetBool('toons-always-5050', 0)
    suitsAlwaysHit = simbase.config.GetBool('suits-always-hit', 0)
    suitsAlwaysMiss = simbase.config.GetBool('suits-always-miss', 0)
    immortalSuits = simbase.config.GetBool('immortal-suits', 0)
    propAndOrganicBonusStack = simbase.config.GetBool('prop-and-organic-bonus-stack', 0)

    def __init__(self, battle, tutorialFlag = 0):
        self.battle = battle
        self.SuitAttackers = {}
        self.toonAtkOrder = []
        self.toonHPAdjusts = {}
        self.toonSkillPtsGained = {}
        self.traps = {}
        self.npcTraps = {}
        self.suitAtkStats = {}
        self.__clearBonuses(hp=1)
        self.__clearBonuses(hp=0)
        self.__skillCreditMultiplier = simbase.air.baseXpMultiplier
        self.tutorialFlag = tutorialFlag
        self.trainTrapTriggered = False

    def setSkillCreditMultiplier(self, mult):
        self.__skillCreditMultiplier = simbase.air.baseXpMultiplier * mult

    def getSkillCreditMultiplier(self):
        return self.__skillCreditMultiplier

    def cleanup(self):
        self.battle = None

    def generateMovieAttacks(self):
        self.notify.debug('Generating movie attacks...')
        # Fill toon movie and suit movie attacks
        tmas = self.__generateToonMovieAttacks()
        smas = self.__generateSuitMovieAttacks()
        self.battle.b_setMovieAttacks(tmas, smas)
        self.notify.debug(
            'Movie attacks generated:\n Toons: %s\nSuits: %s' % (self.battle.toonAttacks, self.battle.suitAttacks))

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

    def applyAttacks(self):
        self.notify.debug('Applying attacks...')
        for tma in self.battle.toonMovieAttacks:
            if not tma.hit:
                continue
            target = self.battle.findSuit(tma.targetId)
            gag = InventoryGlobals.Gags.get(tma.attackId)
            if target is None or gag is None:
                continue
            if gag.isTargeted():
                gag.effect.b_applyTo(target)
        # TODO: Do suit movie attacks here
