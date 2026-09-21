from toontown.battle.Behavior import PeriodicBehavior
from toontown.battle import EffectGlobals
from toontown.toonbase import TTLocalizerServer as TTLocalizer

BehaviorPicnicHeal = 1

BehaviorDict = {
    0: None,
    BehaviorPicnicHeal: PeriodicBehavior(BehaviorPicnicHeal, TTLocalizer.BehaviorName[1], 5, EffectGlobals.PicnicHeal)
}
