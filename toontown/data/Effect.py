class Effect:
    def __init__(self, uid):
        self.uid = uid

    def applyTo(self, av):
        pass

    def applyToQuietly(self, av):
        pass

    def b_applyTo(self, av):
        pass

    @property
    def description(self):
        return ''


class HealEffect(Effect):
    def __init__(self, uid, amount):
        Effect.__init__(self, uid)
        self.amount = amount

    def applyTo(self, av):
        av.toonUp(self.amount)

    def applyToQuietly(self, av):
        av.setHp(av.getHp() + self.amount)

    def b_applyTo(self, av):
        av.b_setHp(av.getHp() + self.amount)

    @property
    def description(self):
        return 'Toon-Up: %d' % self.amount


class DamageEffect(Effect):
    def __init__(self, uid, amount):
        Effect.__init__(self, uid)
        self.amount = amount

    def applyTo(self, av):
        av.takeDamage(self.amount)

    def applyToQuietly(self, av):
        av.setHp(av.getHp() - self.amount)

    def b_applyTo(self, av):
        av.b_setHp(av.getHp() - self.amount)

    @property
    def description(self):
        return 'Damage: %d' % self.amount
