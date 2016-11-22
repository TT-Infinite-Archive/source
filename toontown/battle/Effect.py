class Effect:
    def __init__(self, uid):
        self.uid = uid

    def applyTo(self, av):
        pass


class HealEffect(Effect):
    def __init__(self, uid, amount):
        Effect.__init__(self, uid)
        self.amount = amount

    def applyTo(self, av):
        av.toonUp(self.amount)


class DamageEffect(Effect):
    def __init__(self, uid, amount):
        Effect.__init__(self, uid)
        self.amount = amount

    def applyTo(self, av):
        av.takeDamage(self.amount)
