from direct.directnotify import DirectNotifyGlobal
from toontown.battle import BehaviorGlobals


class BehaviorManagerAI:
    notify = DirectNotifyGlobal.directNotify.newCategory('BehaviorManagerAI')

    def __init__(self, air):
        self.air = air

    def applyBehavior(self, behaviorId, avId):
        # Get the avatar
        av = self.air.doId2do.get(avId)
        if av is None:
            return

        # Get the behavior object
        behavior = BehaviorGlobals.BehaviorDict.get(behaviorId)
        if behavior is None:
            return

        # Apply this behavior to the avatar
        behavior.applyTo(av)

    def removeBehavior(self, behaviorId, avId):
        # Get the avatar
        av = self.air.doId2do.get(avId)
        if av is None:
            return

        # Get the behavior object
        behavior = BehaviorGlobals.BehaviorDict.get(behaviorId)
        if behavior is None:
            return

        # Remove this behavior from the avatar
        behavior.removeFrom(av)
