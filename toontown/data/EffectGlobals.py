from toontown.data.Effect import Effect, HealEffect, DamageEffect

PicnicHeal = 1
CupcakeDamage = 2

DefaultEffect = Effect(0)
EffectDict = {
    PicnicHeal: HealEffect(PicnicHeal, 5),
    CupcakeDamage: DamageEffect(CupcakeDamage, 6)
}


def getEffect(effectId):
    return EffectDict.get(effectId, DefaultEffect)