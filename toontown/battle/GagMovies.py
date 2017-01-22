from direct.interval.IntervalGlobal import *
from panda3d.core import Point3

import MovieUtil
from toontown.data import Sound, Gag, Model
from toontown.toonbase import TTLocalizer
from toontown.util import PointLib


def singleTargetThrowMovie(battle, tma):
    toon = battle.findToon(tma.attackerId)
    suit = battle.findSuit(tma.targetId)
    attack = Gag.Gags[tma.attackId]
    missile = Gag.GagToMissile.get(tma.attackId)
    prop = missile.model.getActor()
    hand = toon.getRightHand()
    suitPos = suit.getPos(battle)
    suitHeadPos = Point3(suitPos[0], suitPos[1], suitPos[2] + suit.getHeight())
    origHpr = toon.getHpr(battle)
    toonTrack = Sequence(
        # Make toon look at target
        Func(toon.headsUp, battle, suitHeadPos),
        # Make toon animate throw
        MovieUtil.animateAv(toon, 'throw'),
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
        Func(MovieUtil.unloadProp, prop)
    )
    if tma.hit:
        # Splat if hit
        propTrack.append(
            Func(missile.die, battle, suitHeadPos)
        )
    suitTrack = Sequence()
    if tma.hit:
        # Wait until the missile hits the suit
        suitTrack.append(Wait(3))
        suitTrack.append(
            Parallel(
                # Make the suit react to the hit
                MovieUtil.animateAv(suit, 'pie-small-react'),
                # Apply the effects to the target
                Func(attack.effect.applyTo, suit),
                # Update health bar
                Func(suit.updateHealthBar)
            )
        )
    else:
        # Wait until the missile is fired
        suitTrack.append(Wait(2.2))
        # Show missed text
        suitTrack.append(Func(suit.displayText, TTLocalizer.AttackMissed))
        # Make the suit(s) dodge
        suitTrack.append(MovieUtil.doSuitDodge(suit, battle))
        # Pause the track until the dodge is done
        suitTrack.append(Func(suitTrack.pause))

    return Parallel(toonTrack, propTrack, suitTrack)


def multiTargetThrowMovie(battle, tma):
    toon = battle.findToon(tma.attackerId)
    suits = battle.activeSuits
    attack = Gag.Gags[tma.attackId]
    missile = Gag.GagToMissile.get(tma.attackId)
    prop = missile.model.getActor()
    hand = toon.getRightHand()
    toonTrack = Sequence(
        # Make toon animate throw
        MovieUtil.animateAv(toon, 'throw'),
    )
    missileTracks = Parallel()
    if tma.hit:
        for suit in suits:
            suitPos = suit.getPos(battle)
            suitHeadPos = Point3(suitPos[0], suitPos[1], suitPos[2] + suit.getHeight())
            p = missile.model.getActor()
            missileTracks.append(Sequence(
                Func(p.reparentTo, hand),
                Func(p.show),
                Func(p.wrtReparentTo, battle),
                # Make missile look at target point
                Func(p.lookAt, suitHeadPos),
                Func(p.setP, p.getHpr()[1] - 90),
                # Make missile move to point
                Parallel(
                    LerpPosInterval(p, 0.5, suitHeadPos),
                    Func(Sound.ThrowSound.playSound)
                ),
                # Unload missile
                Func(MovieUtil.unloadProp, p)
            ))
    else:
        for suit in suits:
            suitPos = suit.getPos(battle)
            suitHeadPos = Point3(suitPos[0], suitPos[1], suitPos[2] + suit.getHeight())
            midPoint = PointLib.pointBetween(hand.getPos(battle), suitHeadPos)
            # groundPoint = Point3(midPoint[0], midPoint[1], midPoint[2] - 3.6)
            '''
            Parallel(
                # Make the missile drop because it missed
                LerpHprInterval(p, 0.2, Point3(p.getHpr()[0], p.getHpr()[1] - 170, p.getHpr()[2])),
                LerpPosInterval(p, 0.3, groundPoint)
            ),
            '''
            p = missile.model.getActor()
            missileTracks.append(Sequence(
                Func(p.reparentTo, hand),
                Func(p.show),
                Func(p.wrtReparentTo, battle),
                # Make missile look at target point
                Func(p.lookAt, suitHeadPos),
                Func(p.setP, p.getHpr()[1] - 90),
                # Make missile move to point but fall
                Parallel(
                    LerpPosInterval(p, 0.3, midPoint, None, None, 'easeOut'),
                    Func(Sound.ThrowSound.playSound)
                ),
                Func(missile.die, battle, midPoint),
                # Unload missile
                Func(MovieUtil.unloadProp, p),
                # Show miss text on each suit
                Func(suit.displayText, TTLocalizer.AttackMissed)
            ))

    propTrack = Sequence(
        # Reparent missile to hand
        Func(prop.reparentTo, hand),
        Func(prop.show),
        # Make missile grow
        LerpScaleInterval(prop, 1.0, prop.getScale(), 0.1),
        # Wait for toon animation to get to the throw part of the animation
        Wait(1.5),
        # Cleanup prop in hand
        Func(MovieUtil.unloadProp, prop),
        # Do missile tracks
        missileTracks
    )
    if tma.hit:
        # Splat if hit
        splatTrack = Parallel()
        for suit in suits:
            suitPos = suit.getPos(battle)
            suitHeadPos = Point3(suitPos[0], suitPos[1], suitPos[2] + suit.getHeight())
            splatTrack.append(
                Func(missile.die, battle, suitHeadPos)
            )
        propTrack.append(splatTrack)
    suitTrack = Sequence()
    if tma.hit:
        # Wait until the missile hits the suit
        suitTrack.append(Wait(3))
        hitTracks = Parallel()
        for suit in suits:
            hitTracks.append(
                Parallel(
                    # Make the suit react to the hit
                    MovieUtil.animateAv(suit, 'pie-small-react'),
                    # Apply the effects to the target
                    Func(attack.effect.applyTo, suit),
                    # Update health bar
                    Func(suit.updateHealthBar)
                )
            )
        suitTrack.append(hitTracks)

    return Parallel(toonTrack, propTrack, suitTrack)


def cannonAttack(battle, tma):
    toon = battle.findToon(tma.attackerId)
    suit = battle.findSuit(tma.targetId)
    suitHeadPos = MovieUtil.getSuitHeadPos(suit, battle)
    origHpr = toon.getHpr(battle)
    suitColorScale = suit.getColorScale()
    attack = Gag.Gags[tma.attackId]
    if not toon or not suit:
        return Sequence()
    toonTrack = Sequence(
        # Make toon look at target
        Func(toon.headsUp, battle, suitHeadPos),
        # Make toon press the button
        MovieUtil.toonButtonTrack(toon),
        # Make toon face original facing
        Func(toon.setHpr, battle, origHpr)
    )

    cannon = Model.CannonModel.getActor()
    cannon.reparentTo(battle)
    cannonPos = cannon.getPos()
    cannonPos = (cannonPos[0], cannonPos[1] - 2, cannonPos[2] - 8)
    cannonToPos = (cannonPos[0], cannonPos[1], cannonPos[2] + 8)

    cannon.setScale(0.55)
    cannon.hide()
    kapow = Model.KapowModel.getActor()
    kapow.setBillboardPointEye()
    barrel = cannon.find('**/cannon')
    kapowPoint = barrel.attachNewNode('kapowPoint')
    kapowPoint.setPos(0, 6.7, 0)
    shadow = cannon.find('**/square_drop_shadow')
    shadow.hide()
    barrelPos = barrel.getPos()

    cannonTrack = Sequence(
        # Initialize cannon and barrel
        Func(cannon.show),
        Func(cannon.headsUp, suit),
        Func(cannon.setPos, cannonPos),
        Func(barrel.setPos, barrelPos),
        Func(barrel.setHpr, 0, 90, 0),
        # Make cannon raise from floor
        Parallel(
            LerpPosInterval(cannon, 0.4, cannonToPos, blendType='easeOut'),
            SoundInterval(Sound.CannonAdjustSound.getSound(), duration=1, node=cannon),
            Sequence(
                Wait(0.2),
                LerpHprInterval(barrel, 0.6, (0, 25, 0), blendType='easeInOut')
            )
        ),
        # Initialize kapow
        Func(kapow.reparentTo, kapowPoint),
        # Fire the cannon
        Parallel(
            # Kapow!
            ActorInterval(kapow, 'kapow', playRate=1.5),
            SoundInterval(Sound.CannonFireSound.getSound(), node=cannon),
            # Barrel movement
            Sequence(
                Parallel(
                    LerpPosInterval(barrel, 0.2, (barrelPos[0], barrelPos[1] - 1.25, barrelPos[2]), blendType='easeInOut'),
                    LerpHprInterval(barrel, 0.25, (0, 15, 0), blendType='easeInOut')
                ),
                Wait(0.1),
                Parallel(
                    LerpPosInterval(barrel, 0.2, barrelPos, blendType='easeInOut'),
                    LerpHprInterval(barrel, 0.25, (0, 20, 0), blendType='easeInOut')
                )
            )
        ),
        Func(kapow.hide),
        Func(kapow.destroy),
        # Make cannon hide in floor
        Parallel(
            LerpHprInterval(barrel, 0.4, (0, 90, 0), blendType='easeInOut'),
            Sequence(
                Wait(0.2),
                LerpPosInterval(cannon, 0.6, cannonPos, blendType='easeIn'),
            )
        ),
    )

    suitTrack = Sequence()
    if tma.hit:
        # Wait until the cannon fires at the suit
        suitTrack = Sequence(
            Wait(1),
            Func(suit.setColorScale, 0, 0, 0, suit.getColorScale()[3]),
            Parallel(
                # Make the suit react to the hit
                MovieUtil.animateAv(suit, 'pie-small-react'),
                # Apply the effects to the target
                Func(attack.effect.applyTo, suit),
                # Update health bar
                Func(suit.updateHealthBar),
                # Fade out the color scale
                Sequence(
                    Wait(0.25),
                    LerpColorScaleInterval(suit, 0.5, suitColorScale, blendType='easeOut')
                )
            ),
        )
    return Parallel(
        toonTrack,
        Sequence(
            Wait(2.5),
            Parallel(
                cannonTrack,
                suitTrack
            )
        )
    )


GagToMovieFunc = {
    0: None,
    1: singleTargetThrowMovie,
    2: singleTargetThrowMovie,
    3: multiTargetThrowMovie,
    4: multiTargetThrowMovie,
    5: singleTargetThrowMovie,
    6: singleTargetThrowMovie,
    7: singleTargetThrowMovie,
    8: singleTargetThrowMovie,
    9: cannonAttack,
    Gag.PASS: None
}
