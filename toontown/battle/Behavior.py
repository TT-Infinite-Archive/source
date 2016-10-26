from toontown.battle.EffectGlobals import EffectDict


# Behaviors are persistent objects we place on avatars
class Behavior:
    def __init__(self, uid, name):
        self.uid = uid
        self.name = name

    def applyTo(self, av):
        pass

    def getUniqueName(self):
        return 'Behavior-%s' % id(self)


# Periodic behaviors do effects on intervals to its applied avatar
class PeriodicBehavior(Behavior):
    def __init__(self, uid, name, interval, intEffectId):
        Behavior.__init__(self, uid, name)
        self.interval = interval
        self.intervalEffect = EffectDict[intEffectId]

    def applyTo(self, av):
        self.doTask(av)

    def doIntervalEffect(self, av):
        self.intervalEffect.applyTo(av)
        self.doTask(av)

    def removeFrom(self, av):
        taskMgr.remove(self.getIntervalUniqueName(av))

    def doTask(self, av):
        taskMgr.doMethodLater(self.interval, self.doIntervalEffect, self.getIntervalUniqueName(av), extraArgs=[av])

    def getIntervalUniqueName(self, av):
        return 'Interval-%s-%s' % (self.getUniqueName(), av.doId)
