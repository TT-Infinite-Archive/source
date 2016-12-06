from direct.interval.IntervalGlobal import Sequence, ActorInterval, Func


def cupcakeMovie(battle, tma):
    toon = battle.findToon(tma.attackerId)
    suit = battle.findSuit(tma.targetId)
    attackTrack = Sequence(
        getToonAnimation(toon, 'throw')
    )
    return attackTrack

GagToGagMovie = {
    0: None,
    1: cupcakeMovie,
}


def getToonAnimation(toon, animName):
    # Does a toon animation then reverts to neutral
    return Sequence(
        ActorInterval(toon, animName),
        Func(toon.loop, 'neutral')
    )