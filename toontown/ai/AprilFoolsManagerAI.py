import random
import time

from direct.directnotify import DirectNotifyGlobal
from otp.otpbase import OTPGlobals
from toontown.ai import CostumeManagerAI
from toontown.toon import ToonDNA
from toontown.toon.DistributedToonAI import DistributedToonAI


class AprilFoolsManagerAI(CostumeManagerAI.CostumeManagerAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('AprilFoolsManagerAI')
    PrankTask = 'aprilToonsPranks'
    PrankDelay = 30
    RandomCheesyList = (
        OTPGlobals.CEBigHead, OTPGlobals.CEBigHead,
        OTPGlobals.CESmallHead,
        OTPGlobals.CEBigLegs, OTPGlobals.CEBigLegs,
        OTPGlobals.CESmallLegs,
        OTPGlobals.CEBigToon, OTPGlobals.CEBigToon,
        OTPGlobals.CESmallToon, OTPGlobals.CESmallToon,
        OTPGlobals.CEFlatPortrait, OTPGlobals.CEFlatPortrait,
        OTPGlobals.CEFlatProfile, OTPGlobals.CEFlatProfile,
        OTPGlobals.CETransparent, OTPGlobals.CETransparent,
        OTPGlobals.CEInvisible, OTPGlobals.CEInvisible,
    )
    RandomCheesyMinTime = 3
    RandomCheesyMaxTime = 60

    def __init__(self, air, holidayId):
        CostumeManagerAI.CostumeManagerAI.__init__(self, air, holidayId)
        self.nextEffectTimes = {}
        self.savedEffects = {}

    def start(self):
        CostumeManagerAI.CostumeManagerAI.start(self)
        taskMgr.doMethodLater(self.PrankDelay, self.__prankToons, self.PrankTask)

    def goingToStop(self, stopForever=False):
        CostumeManagerAI.CostumeManagerAI.goingToStop(self, stopForever)
        self.__stopPranks()

    def stop(self):
        CostumeManagerAI.CostumeManagerAI.stop(self)
        self.__stopPranks()

    def __stopPranks(self):
        taskMgr.remove(self.PrankTask)

        for av in self.__getToons():
            if av.doId in self.savedEffects:
                av.b_setAnimalSound(self.__getSpecies(av))
                av.b_setCheesyEffect(*self.savedEffects[av.doId])

        self.nextEffectTimes = {}
        self.savedEffects = {}

    def __getToons(self):
        return [av for av in self.air.doFindAllInstances(DistributedToonAI) if av.isPlayerControlled()]

    def __getSpecies(self, av):
        return ToonDNA.toonSpeciesTypes.index(av.dna.head[0])

    def __prankToons(self, task):
        now = time.time()
        nextEffectTimes = {}

        for av in self.__getToons():
            nextTime = self.nextEffectTimes.get(av.doId)

            if av.doId not in self.savedEffects:
                self.savedEffects[av.doId] = self.__getOwnEffect(av)

            if nextTime is None:
                self.__scrambleVoice(av)

            if nextTime is None or nextTime <= now:
                nextTime = self.__randomizeEffect(av, now)

            nextEffectTimes[av.doId] = nextTime

        self.nextEffectTimes = nextEffectTimes
        return task.again

    def __getOwnEffect(self, av):
        effect = av.getCheesyEffect()
        if effect[0] in self.RandomCheesyList and effect[2]:
            return (av.getEquippedCheesyEffect(), 0, 0)

        return effect

    def __scrambleVoice(self, av):
        species = self.__getSpecies(av)
        av.b_setAnimalSound(random.choice([index for index in range(len(ToonDNA.toonSpeciesTypes))
                                           if index != species]))

    def __randomizeEffect(self, av, now):
        effect = random.choice([effect for effect in self.RandomCheesyList
                                if effect != av.getCheesyEffect()[0]])
        nextTime = now + 60 * random.randint(self.RandomCheesyMinTime, self.RandomCheesyMaxTime)

        av.b_setCheesyEffect(effect, 0, int(nextTime / 60) + 2, syncCollectible=False)
        return nextTime
