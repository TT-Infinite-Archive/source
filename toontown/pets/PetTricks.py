import enum
import random

from direct.showbase.PythonUtil import invertDictLossless
from direct.interval.IntervalGlobal import *


class ETrick(enum.IntEnum):
    JUMP = 0
    BEG = 1
    PLAYDEAD = 2
    ROLLOVER = 3
    BACKFLIP = 4
    DANCE = 5
    SPEAK = 6
    BALK = 7


NonHappyMinActualTrickAptitude = 0.1
NonHappyMaxActualTrickAptitude = 0.6
MinActualTrickAptitude = 0.5
MaxActualTrickAptitude = 0.97
AptitudeIncrementDidTrick = 0.001
MaxAptitudeIncrementGotPraise = 0.001
MaxTrickFatigue = 0.45
MinTrickFatigue = 0.05
ScId2trickId = {21200: ETrick.JUMP,
 21201: ETrick.BEG,
 21202: ETrick.PLAYDEAD,
 21203: ETrick.ROLLOVER,
 21204: ETrick.BACKFLIP,
 21205: ETrick.DANCE,
 21206: ETrick.SPEAK}
TrickId2scIds = invertDictLossless(ScId2trickId)
TrickAnims = {ETrick.JUMP: 'jump',
 ETrick.BEG: ('toBeg', 'beg', 'fromBeg'),
 ETrick.PLAYDEAD: ('playDead', 'fromPlayDead'),
 ETrick.ROLLOVER: 'rollover',
 ETrick.BACKFLIP: 'backflip',
 ETrick.DANCE: 'dance',
 ETrick.SPEAK: 'speak',
 ETrick.BALK: 'neutral'}
TrickLengths = {ETrick.JUMP: 2.0,
 ETrick.BEG: 5.167,
 ETrick.PLAYDEAD: 15.21,
 ETrick.ROLLOVER: 8.0,
 ETrick.BACKFLIP: 4.88,
 ETrick.DANCE: 7.42,
 ETrick.SPEAK: 0.75,
 ETrick.BALK: 1.0}
TrickAccuracies = {ETrick.JUMP: 1.0,
 ETrick.BEG: 0.9,
 ETrick.PLAYDEAD: 0.8,
 ETrick.ROLLOVER: 0.7,
 ETrick.BACKFLIP: 0.6,
 ETrick.DANCE: 0.5,
 ETrick.SPEAK: 0.4,
 ETrick.BALK: 1.0}
TrickHeals = {ETrick.JUMP: (5, 10),
 ETrick.BEG: (6, 12),
 ETrick.PLAYDEAD: (7, 14),
 ETrick.ROLLOVER: (8, 16),
 ETrick.BACKFLIP: (9, 18),
 ETrick.DANCE: (10, 20),
 ETrick.SPEAK: (11, 22),
 ETrick.BALK: (0, 0)}
TrickSounds = {ETrick.BACKFLIP: 'phase_5/audio/sfx/backflip.ogg',
 ETrick.ROLLOVER: 'phase_5/audio/sfx/rollover.ogg',
 ETrick.PLAYDEAD: 'phase_5/audio/sfx/play_dead.ogg',
 ETrick.BEG: 'phase_5/audio/sfx/beg.ogg',
 ETrick.DANCE: 'phase_5/audio/sfx/heal_dance.ogg',
 ETrick.JUMP: 'phase_5/audio/sfx/jump.ogg',
 ETrick.SPEAK: 'phase_5/audio/sfx/speak_v1.ogg'}

def getSoundIval(trickId):
    sounds = TrickSounds.get(trickId, None)
    if sounds:
        if type(sounds) == bytes:
            sound = loader.loadSfx(sounds)
            return SoundInterval(sound)
        else:
            soundIval = Sequence()
            for s in sounds:
                sound = loader.loadSfx(s)
                soundIval.append(SoundInterval(sound))

            return soundIval
    return


def getTrickIval(pet, trickId):
    anims = TrickAnims[trickId]
    animRate = random.uniform(0.9, 1.1)
    waitTime = random.uniform(0.0, 1.0)
    if type(anims) == bytes:
        if trickId == ETrick.JUMP:
            animIval = Parallel()
            animIval.append(ActorInterval(pet, anims, playRate=animRate))
            animIval.append(Sequence(Wait(0.36), ProjectileInterval(pet, startPos=pet.getPos(), endPos=pet.getPos(), duration=1.0, gravityMult=0.5)))
        elif trickId == ETrick.ROLLOVER:
            animIval = Sequence()
            animIval.append(ActorInterval(pet, anims, playRate=animRate))
            animIval.append(ActorInterval(pet, anims, playRate=-1.0 * animRate))
        elif trickId == ETrick.SPEAK:
            animIval = ActorInterval(pet, anims, startFrame=10, playRate=animRate)
        else:
            animIval = ActorInterval(pet, anims, playRate=animRate)
    else:
        animIval = Sequence()
        for anim in anims:
            animIval.append(ActorInterval(pet, anim, playRate=animRate))

    trickIval = Parallel(animIval)
    soundIval = getSoundIval(trickId)
    if soundIval:
        trickIval.append(soundIval)
    return Sequence(Func(pet.lockPet), Wait(waitTime), trickIval, Func(pet.unlockPet))
