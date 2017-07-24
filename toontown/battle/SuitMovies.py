from panda3d.core import Vec4, VBase3, Point3
from direct.interval.IntervalGlobal import Sequence, Wait, Func, LerpScaleInterval, LerpPosHprInterval, Parallel
from toontown.data import Model, SuitAttack, Sound
from toontown.battle import MovieUtil
from toontown.toonbase import TTLocalizer
from toontown.chat.ChatGlobals import CFSpeech, CFTimeout


def doPoundKey(battle, sma):
    suit = battle.findSuit(sma.attackerId)
    toon = battle.findToon(sma.targetId)
    attack = SuitAttack.getSuitAttack(sma.attackId)
    phone = Model.getModel(20).getActor()  # Phone Model
    receiver = Model.getModel(21).getActor()  # Receiver Model
    hangupSound = Sound.getSound(14)
    particleEffect = MovieUtil.loadParticle('poundkey')
    particles = particleEffect.getParticlesNamed('particles-1')
    particles.renderer.setColor(Vec4(0, 0, 0, 1))
    partTrack = MovieUtil.getPartTrack(particleEffect, 2.1, 1.55, [particleEffect, suit, 0])
    origHpr = suit.getHpr(battle)
    suitTrack = Sequence(
        Func(suit.setChatAbsolute, attack.getRandomTaunt(), CFSpeech | CFTimeout),
        Func(suit.headsUp, battle, toon.getPos(battle)),
        MovieUtil.animateAv(suit, 'phone'),
        Func(suit.setHpr, battle, origHpr),
        Func(suit.clearChat)
    )
    propTrack = Sequence(
        Wait(0.3),
        # Position phone
        Func(phone.reparentTo, suit.getLeftHand()),
        Func(phone.setHpr, Point3(0.23, 0.17, -0.11)),
        Func(phone.setPos, VBase3(5.939, 2.763, -177.591)),
        Func(phone.show),
        # Position receiver
        Func(receiver.reparentTo, suit.getLeftHand()),
        Func(receiver.setHpr, Point3(0.23, 0.17, -0.11)),
        Func(receiver.setPos, VBase3(5.939, 2.763, -177.591)),
        Func(receiver.show),
        # Shrink phone
        LerpScaleInterval(phone, 0.5, 1.0, 0.01),
        Wait(0.74),
        Func(receiver.wrtReparentTo, suit.getRightHand()),
        LerpPosHprInterval(receiver, 0.0001, Point3(-0.45, 0.48, -0.62), VBase3(-87.47, -18.21, 7.82)),
        Wait(3.14),
        Func(receiver.wrtReparentTo, phone),
        Wait(0.62),
        LerpScaleInterval(phone, 0.5, MovieUtil.PNT3_NEARZERO),
        Func(MovieUtil.removeProps, [receiver, phone])
    )
    toonTrack = Sequence()
    if sma.hit:
        # Wait until the missile hits the suit
        toonTrack.append(Wait(2.7))
        toonTrack.append(
            Parallel(
                # Make the suit react to the hit
                MovieUtil.animateAv(toon, 'cringe'),
                # Apply the effects to the target
                Func(attack.effect.applyTo, toon),
                # Update health bar
                Func(suit.updateHealthBar)
            )
        )
    else:
        # Wait until the missile is fired
        toonTrack.append(Wait(1.9))
        # Show missed text
        toonTrack.append(Func(toon.displayText, TTLocalizer.AttackMissed))
        # Make the toon(s) dodge
        toonTrack.append(MovieUtil.doToonDodge(toon, battle, 'sidestep'))
        # Pause the track until the dodge is done
        toonTrack.append(Func(toonTrack.pause))

    soundTrack = Sequence(
        Wait(1.3),
        Func(hangupSound.playSound)
    )
    return Parallel(suitTrack, toonTrack, propTrack, partTrack, soundTrack)


SuitAttackToMovieFunc = {
    0: None,
    1: doPoundKey
}