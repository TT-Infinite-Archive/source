from direct.interval.IntervalGlobal import *
from panda3d.core import Vec3, Point3
from toontown.toon import InventoryGlobals
from toontown.battle import Sound, BattleParticles
import MovieUtil


def cupcakeMovie(battle, tma):
    toon = battle.findToon(tma.attackerId)
    suit = battle.findSuit(tma.targetId)
    attack = InventoryGlobals.Gags[tma.attackId]
    missile = InventoryGlobals.GagToMissile.get(tma.attackId)
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
                # Play splat dead animation
                ActorInterval(splat, 'death'),
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
        # Play death effect if dead otherwise it wont
        if max(suit.getHp() - attack.getDamage(), 0) == 0:
            suitTrack.append(MovieUtil.suitDeath(suit, battle))
        else:
            battle.notify.debug('%s - %s != 0, not killing' % (suit.getHp(), attack.getDamage()))
    else:
        # 'sidestep-left', 'sidestep-right'
        # Wait until the missile is fired
        suitTrack.append(Wait(2.2))
        # Make the suit dodge
        suitTrack.append(animateAv(suit, 'sidestep-left'))
    return Parallel(toonTrack, propTrack, suitTrack)

GagToMovieFunc = {
    0: None,
    1: cupcakeMovie,
    2: cupcakeMovie,
    3: cupcakeMovie,
    InventoryGlobals.PASS: None
}


def animateAv(av, animName):
    # Does a toon animation then reverts to neutral
    return Sequence(
        ActorInterval(av, animName),
        Func(av.loop, 'neutral')
    )


def fireMissile(prop, missile, toPos):
    # Fires a missile to a point
    splat = missile.deathModel.getActor()
    return Sequence


def unloadProp(prop):
    prop.cleanup()
    prop.delete()
