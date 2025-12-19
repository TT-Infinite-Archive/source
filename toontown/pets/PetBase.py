from toontown.pets.PetConstants import EAnimMood
from toontown.pets import PetMood

class PetBase:

    def getSetterName(self, valueName, prefix = 'set'):
        return '%s%s%s' % (prefix, valueName[0].upper(), valueName[1:])

    def getAnimMood(self):
        if self.mood.getDominantMood() in PetMood.PetMood.ExcitedMoods:
            return EAnimMood.EXCITED
        elif self.mood.getDominantMood() in PetMood.PetMood.UnhappyMoods:
            return EAnimMood.SAD
        else:
            return EAnimMood.NEUTRAL

    def isExcited(self):
        return self.getAnimMood() == EAnimMood.EXCITED

    def isSad(self):
        return self.getAnimMood() == EAnimMood.SAD
