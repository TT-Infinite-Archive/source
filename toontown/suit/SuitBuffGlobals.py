# Temporary buff global file for factory foreman until a proper buff system is implemented
import random

SuitBuffNone = 0
SuitBuffHealthy = 1
SuitBuffStable = 2
SuitBuffAvenger = 3
SuitBuffLoveStruck = 4

SuitBuffs = {
    SuitBuffNone:       'None',
    SuitBuffHealthy:    'Healthy',  # Bonus Health
    SuitBuffStable:     'Stable',   # Un-lure-able
    SuitBuffAvenger:    'Avenger',  # Gets health when other cogs in the same battle die
    SuitBuffLoveStruck: 'Love Struck'
}

ForemanBuffs = (SuitBuffHealthy, SuitBuffStable, SuitBuffAvenger)


def getRandomSuitBuff():
    return random.choice(xrange(1, len(SuitBuffs)))


def getBuffIndexFromName(buffName):
    for buffIndex in SuitBuffs:
        if SuitBuffs[buffIndex] == buffName:
            return buffIndex
    return 0

