class Effect:
    def __init__(self, uid, name):
        self.uid = uid
        self.name = name

    def applyTo(self, av):
        pass


class HealEffect(Effect):
    def __init__(self, uid, name, amount):
        Effect.__init__(self, uid, name)
        self.amount = amount

    def applyTo(self, av):
        av.toonUp(self.amount)
