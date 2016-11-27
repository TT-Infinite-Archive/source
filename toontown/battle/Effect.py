class Effect:
    def __init__(self, uid):
        self.uid = uid

    def applyTo(self, av):
        pass

    def applyToQuietly(self, av):
        pass


class HealEffect(Effect):
    def __init__(self, uid, amount):
        Effect.__init__(self, uid)
        self.amount = amount

    def applyTo(self, av):
        av.toonUp(self.amount)

    def applyToQuietly(self, av):
        av.setHp(av.getHp() + self.amount)


class DamageEffect(Effect):
    def __init__(self, uid, amount):
        Effect.__init__(self, uid)
        self.amount = amount

    def applyTo(self, av):
        av.takeDamage(self.amount)

    def applyToQuietly(self, av):
        av.setHp(av.getHp() - self.amount)
