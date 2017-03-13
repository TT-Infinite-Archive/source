from toontown.strike.DistributedCorporateStrikeAI import DistributedCorporateStrikeAI
from toontown.strike.RoundManagerAI import RoundManagerAI
from toontown.strike import OperationSaveToontownGlobals


class OSTRoundManagerAI(RoundManagerAI):
    SPAWN_RANGES = (
        (6, 6),
        (6, 8),
        (7, 10),
        (8, 12)
    )

    SPAWN_SPHERES = OperationSaveToontownGlobals.SPAWN_SPHERES
    SPAWN_DELAY = (5, 12)
    MAX_ENEMIES = 14
    TIER_CHART = {1: [0, 1], 3: [1, 2, 3], 5: [2, 3], 7: [3, 4], 9: [3, 4, 5], 13: [4, 5, 6], 15: [5, 6, 7]}


class DistributedOperationSaveToontownAI(DistributedCorporateStrikeAI):
    DROP_POINTS = OperationSaveToontownGlobals.DROP_POINTS

    ROUND_MANAGER = OSTRoundManagerAI
    NAVMESH = '../resources/server/corpstrike/ost_navmesh.csv'
