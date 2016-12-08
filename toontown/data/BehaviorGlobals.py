from toontown.data import EffectGlobals
from toontown.data.Behavior import PeriodicBehavior
from toontown.toonbase import TTLocalizer

BehaviorPicnicHeal = 1

BehaviorDict = {
    0: None,
    BehaviorPicnicHeal: PeriodicBehavior(BehaviorPicnicHeal, TTLocalizer.BehaviorName[1], 5, EffectGlobals.PicnicHeal)
}
