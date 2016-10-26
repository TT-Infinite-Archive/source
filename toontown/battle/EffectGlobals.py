from toontown.battle.Effect import Effect, HealEffect
from toontown.toonbase import TTLocalizer

PicnicHeal = 1

EffectDict = {
    0: Effect(0, TTLocalizer.EffectName[0]),
    PicnicHeal: HealEffect(PicnicHeal, TTLocalizer.EffectName[1], amount=5),
}