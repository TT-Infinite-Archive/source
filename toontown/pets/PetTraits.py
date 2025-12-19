import enum

from direct.showbase.PythonUtil import randFloat, normalDistrib
from toontown.toonbase import TTLocalizer, ToontownGlobals
import random, copy
TraitDivisor = 10000

def getTraitNames():
    if not hasattr(PetTraits, 'TraitNames'):
        traitNames = []
        for desc in PetTraits.TraitDescs:
            traitNames.append(desc[0])
            PetTraits.TraitNames = traitNames

    return PetTraits.TraitNames


def uniform(min, max, rng):
    return randFloat(min, max, rng.random)


def gaussian(min, max, rng):
    return normalDistrib(min, max, rng.gauss)


class ETraitQuality(enum.IntEnum):
    VERY_BAD = 0
    BAD = 1
    AVERAGE = 2
    GOOD = 3
    VERY_GOOD = 4


class ETraitType(enum.IntEnum):
    INCREASING = 0
    DECREASING = 1


class TraitDistribution:
    Sz2MinMax = None
    TraitType = None
    TraitCutoffs = {ETraitType.INCREASING: {ETraitQuality.VERY_BAD: 0.1,
                             ETraitQuality.BAD: 0.25,
                             ETraitQuality.GOOD: 0.75,
                             ETraitQuality.VERY_GOOD: 0.9},
     ETraitType.DECREASING: {ETraitQuality.VERY_BAD: 0.9,
                             ETraitQuality.BAD: 0.75,
                             ETraitQuality.GOOD: 0.25,
                             ETraitQuality.VERY_GOOD: 0.1}}

    def __init__(self, rndFunc = gaussian):
        self.rndFunc = rndFunc
        if not hasattr(self.__class__, 'GlobalMinMax'):
            _min = 1.0
            _max = 0.0
            minMax = self.Sz2MinMax
            for sz in minMax:
                thisMin, thisMax = minMax[sz]
                _min = min(_min, thisMin)
                _max = max(_max, thisMax)

            self.__class__.GlobalMinMax = [_min, _max]

    def getRandValue(self, szId, rng = random):
        min, max = self.getMinMax(szId)
        return self.rndFunc(min, max, rng)

    def getHigherIsBetter(self):
        return self.TraitType == ETraitType.INCREASING

    def getMinMax(self, szId):
        return (self.Sz2MinMax[szId][0], self.Sz2MinMax[szId][1])

    def getGlobalMinMax(self):
        return (self.GlobalMinMax[0], self.GlobalMinMax[1])

    def _getTraitPercent(self, traitValue):
        gMin, gMax = self.getGlobalMinMax()
        if traitValue < gMin:
            gMin = traitValue
        elif traitValue > gMax:
            gMax = traitValue
        return (traitValue - gMin) / (gMax - gMin)

    def getPercentile(self, traitValue):
        if self.TraitType is ETraitType.INCREASING:
            return self._getTraitPercent(traitValue)
        else:
            return 1.0 - self._getTraitPercent(traitValue)

    def getQuality(self, traitValue):
        ETraitQuality = ETraitQuality
        TraitCutoffs = self.TraitCutoffs[self.TraitType]
        percent = self._getTraitPercent(traitValue)
        if self.TraitType is ETraitType.INCREASING:
            if percent <= TraitCutoffs[ETraitQuality.VERY_BAD]:
                return ETraitQuality.VERY_BAD
            elif percent <= TraitCutoffs[ETraitQuality.BAD]:
                return ETraitQuality.BAD
            elif percent >= TraitCutoffs[ETraitQuality.VERY_GOOD]:
                return ETraitQuality.VERY_GOOD
            elif percent >= TraitCutoffs[ETraitQuality.GOOD]:
                return ETraitQuality.GOOD
            else:
                return ETraitQuality.AVERAGE
        elif percent <= TraitCutoffs[ETraitQuality.VERY_GOOD]:
            return ETraitQuality.VERY_GOOD
        elif percent <= TraitCutoffs[ETraitQuality.GOOD]:
            return ETraitQuality.GOOD
        elif percent >= TraitCutoffs[ETraitQuality.VERY_BAD]:
            return ETraitQuality.VERY_BAD
        elif percent >= TraitCutoffs[ETraitQuality.BAD]:
            return ETraitQuality.BAD
        else:
            return ETraitQuality.AVERAGE

    def getExtremeness(self, traitValue):
        percent = self._getTraitPercent(traitValue)
        if percent < 0.5:
            howExtreme = (0.5 - percent) * 2.0
        else:
            howExtreme = (percent - 0.5) * 2.0
        return min(max(howExtreme, 0.0), 1.0)


class PetTraits:

    class StdIncDistrib(TraitDistribution):
        TraitType = ETraitType.INCREASING
        Sz2MinMax = {ToontownGlobals.ToontownCentral: (0.2, 0.65),
         ToontownGlobals.DonaldsDock: (0.3, 0.7),
         ToontownGlobals.DaisyGardens: (0.4, 0.75),
         ToontownGlobals.MinniesMelodyland: (0.5, 0.8),
         ToontownGlobals.TheBrrrgh: (0.6, 0.85),
         ToontownGlobals.DonaldsDreamland: (0.7, 0.9)}

    class StdDecDistrib(TraitDistribution):
        TraitType = ETraitType.DECREASING
        Sz2MinMax = {ToontownGlobals.ToontownCentral: (0.35, 0.8),
         ToontownGlobals.DonaldsDock: (0.3, 0.7),
         ToontownGlobals.DaisyGardens: (0.25, 0.6),
         ToontownGlobals.MinniesMelodyland: (0.2, 0.5),
         ToontownGlobals.TheBrrrgh: (0.15, 0.4),
         ToontownGlobals.DonaldsDreamland: (0.1, 0.3)}

    class ForgetfulnessDistrib(TraitDistribution):
        TraitType = ETraitType.DECREASING
        Sz2MinMax = {ToontownGlobals.ToontownCentral: (0.0, 1.0),
         ToontownGlobals.DonaldsDock: (0.0, 0.9),
         ToontownGlobals.DaisyGardens: (0.0, 0.8),
         ToontownGlobals.MinniesMelodyland: (0.0, 0.7),
         ToontownGlobals.TheBrrrgh: (0.0, 0.6),
         ToontownGlobals.DonaldsDreamland: (0.0, 0.5)}

    class BoredomDistrib(TraitDistribution):
        TraitType = ETraitType.INCREASING
        Sz2MinMax = {ToontownGlobals.ToontownCentral: (0.1, 0.35),
         ToontownGlobals.DonaldsDock: (0.2, 0.55),
         ToontownGlobals.DaisyGardens: (0.3, 0.65),
         ToontownGlobals.MinniesMelodyland: (0.4, 0.75),
         ToontownGlobals.TheBrrrgh: (0.5, 0.85),
         ToontownGlobals.DonaldsDreamland: (0.5, 1.0)}

    TraitDescs = (('forgetfulness', ForgetfulnessDistrib(), True),
     ('boredomThreshold', BoredomDistrib(), True),
     ('restlessnessThreshold', StdIncDistrib(), True),
     ('playfulnessThreshold', StdDecDistrib(), True),
     ('lonelinessThreshold', StdIncDistrib(), True),
     ('sadnessThreshold', StdIncDistrib(), True),
     ('fatigueThreshold', StdIncDistrib(), True),
     ('hungerThreshold', StdIncDistrib(), True),
     ('confusionThreshold', StdIncDistrib(), True),
     ('excitementThreshold', StdDecDistrib(), True),
     ('angerThreshold', StdIncDistrib(), True),
     ('surpriseThreshold', StdIncDistrib(), False),
     ('affectionThreshold', StdDecDistrib(), True))
    NumTraits = len(TraitDescs)

    class Trait:

        def __init__(self, index, traitsObj, value = None):
            self.name, distrib, self.hasWorth = PetTraits.TraitDescs[index]
            if value is not None:
                self.value = value
            else:
                szId = traitsObj.safeZoneId
                self.value = distrib.getRandValue(szId, traitsObj.rng)
                self.value = int(self.value * TraitDivisor) / float(TraitDivisor)
            self.higherIsBetter = distrib.getHigherIsBetter()
            self.percentile = distrib.getPercentile(self.value)
            self.quality = distrib.getQuality(self.value)
            self.howExtreme = distrib.getExtremeness(self.value)
            return

        def __repr__(self):
            return 'Trait: %s, %s, %s, %s' % (self.name,
             self.value,
             ETraitQuality.getString(self.quality),
             self.howExtreme)

    def __init__(self, traitSeed, safeZoneId, traitValueList = []):
        self.traitSeed = traitSeed
        self.safeZoneId = safeZoneId
        self.rng = random.Random(self.traitSeed)
        self.traits = {}
        for i in range(len(PetTraits.TraitDescs)):
            if i < len(traitValueList) and traitValueList[i] > 0.0:
                trait = PetTraits.Trait(i, self, traitValueList[i])
            else:
                trait = PetTraits.Trait(i, self)
            self.traits[trait.name] = trait
            self.__dict__[trait.name] = trait.value

        extremeTraits = []
        for trait in list(self.traits.values()):
            if not trait.hasWorth:
                continue
            if trait.quality == ETraitQuality.AVERAGE:
                continue
            i = 0
            while i < len(extremeTraits) and extremeTraits[i].howExtreme > trait.howExtreme:
                i += 1

            extremeTraits.insert(i, trait)

        self.extremeTraits = []
        for trait in extremeTraits:
            self.extremeTraits.append((trait.name, trait.quality))

    def getValueList(self):
        traitValues = []
        for desc in PetTraits.TraitDescs:
            traitName = desc[0]
            traitValues.append(self.traits[traitName].value)

        return traitValues

    def getTraitValue(self, traitName):
        return self.traits[traitName].value

    def getExtremeTraits(self):
        return copy.copy(self.extremeTraits)

    def getOverallValue(self):
        total = 0
        numUsed = 0
        for trait in list(self.traits.values()):
            if trait.hasWorth:
                if trait.higherIsBetter:
                    value = trait.value
                else:
                    value = 1.0 - trait.value
                total += value
                numUsed += 1

        value = total / len(list(self.traits.values()))
        return value

    def getExtremeTraitDescriptions(self):
        descs = []
        ETraitQuality = ETraitQuality
        Quality2index = {ETraitQuality.VERY_BAD: 0,
         ETraitQuality.BAD: 1,
         ETraitQuality.GOOD: 2,
         ETraitQuality.VERY_GOOD: 3}
        for name, quality in self.extremeTraits:
            descs.append(TTLocalizer.PetTrait2descriptions[name][Quality2index[quality]])

        return descs
