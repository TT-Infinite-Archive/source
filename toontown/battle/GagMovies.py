import random

from direct.interval.IntervalGlobal import *
from panda3d.core import Point3

import MovieUtil
from toontown.data import Sound
from toontown.toon.InventoryGlobals import Gags, GagToMissile, PASS
from toontown.toonbase import TTLocalizer


def throwMovie(battle, tma):
    toon = battle.findToon(tma.attackerId)
    suit = battle.findSuit(tma.targetId)
    attack = Gags[tma.attackId]
    missile = GagToMissile.get(tma.attackId)
    prop = missile.model.getActor()
    splat = missile.deathModel.getActor()
    hand = toon.getRightHand()
    suitPos = suit.getPos(battle)
    suitHeadPos = Point3(suitPos[0], suitPos[1], suitPos[2] + suit.getHeight())
    origHpr = toon.getHpr(battle)
    toonTrack = Sequence(
        # Make toon look at target
        Func(toon.headsUp, battle, suitHeadPos),
        # Make toon animate throw
        animateAv(toon, 'throw'),
        # Make toon face original facing
        Func(toon.setHpr, battle, origHpr)
    )
    propTrack = Sequence(
        # Reparent missile to hand
        Func(prop.reparentTo, hand),
        Func(prop.show),
        # Make missile grow
        LerpScaleInterval(prop, 1.0, prop.getScale(), 0.1),
        # Wait for toon animation to get to the throw part of the animation
        Wait(1.5),
        # Parent prop to battle
        Func(prop.wrtReparentTo, battle),
        # Make missile look at target point
        Func(prop.lookAt, suitHeadPos),
        Func(prop.setP, prop.getHpr()[1] - 90),
        # Make missile move to point
        Parallel(
            LerpPosInterval(prop, 0.5, suitHeadPos),
            Func(Sound.ThrowSound.playSound)
        ),
        # Unload missile
        Func(unloadProp, prop)
    )
    if tma.hit:
        # Splat if hit
        propTrack.append(
            Sequence(
                Parallel(
                    # Load in splat animation
                    Func(splat.wrtReparentTo, battle),
                    Func(splat.setPos, suitHeadPos),
                    Func(splat.show)
                ),
                Parallel(
                    # Play splat dead animation
                    ActorInterval(splat, 'death'),
                    # Splat noise
                    Func(Sound.SplatSound.playSound),
                    # Look at camera
                    Func(splat.lookAt, base.camera)
                ),
                # Unload the splat actor
                Func(unloadProp, splat)
            )
        )
    suitTrack = Sequence()
    if tma.hit:
        # Wait until the missile hits the suit
        suitTrack.append(Wait(3))
        suitTrack.append(
            Parallel(
                # Make the suit react to the hit
                animateAv(suit, 'pie-small-react'),
                # Apply the effects to the target
                Func(attack.effect.applyTo, suit),
                # Update health bar
                Func(suit.updateHealthBar)
            )
        )
        # Play death animation if dead otherwise it wont
        if max(suit.getHp() - attack.getDamage(), 0) == 0:
            suitTrack.append(MovieUtil.suitDeath(suit, battle))
    else:
        # Wait until the missile is fired
        suitTrack.append(Wait(2.2))
        # Show missed text
        suitTrack.append(Func(suit.displayText, TTLocalizer.AttackMissed))
        # Make the suit(s) dodge
        suitTrack.append(doSuitDodge(suit, battle))
        # Pause the track until the dodge is done
        suitTrack.append(Func(suitTrack.pause))

    return Parallel(toonTrack, propTrack, suitTrack)


def animateAv(av, animName):
    # Does a toon animation then reverts to neutral
    return Sequence(
        ActorInterval(av, animName),
        Func(av.loop, 'neutral')
    )


def unloadProp(prop):
    prop.cleanup()
    prop.delete()


def getLeftSuits(suit, battle):
    suitIndex = battle.activeSuits.index(suit)
    suits = battle.activeSuits[0:suitIndex + 1]
    return suits


def getRightSuits(suit, battle):
    suitIndex = battle.activeSuits.index(suit)
    suits = battle.activeSuits[suitIndex:]
    return suits


def doSuitDodge(suit, battle):
    dodgeTrack = Parallel()
    if random.choice([0, 1]):
        for s in getLeftSuits(suit, battle):
            dodgeTrack.append(animateAv(s, 'sidestep-left'))
    else:
        for s in getRightSuits(suit, battle):
            dodgeTrack.append(animateAv(s, 'sidestep-right'))
    return dodgeTrack


GagToMovieFunc = {
    0: None,
    1: throwMovie,
    2: throwMovie,
    3: throwMovie,
    PASS: None
}
