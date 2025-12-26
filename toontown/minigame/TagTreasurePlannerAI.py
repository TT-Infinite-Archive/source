from direct.directnotify import DirectNotifyGlobal
from toontown.toonbase.ToontownGlobals import *
from toontown.safezone.RegenTreasurePlannerAI import RegenTreasurePlannerAI
from toontown.safezone.SZTreasureGlobals import ETreasureType

class TagTreasurePlannerAI(RegenTreasurePlannerAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('TagTreasurePlannerAI')
    SPAWN_POINTS: tuple[tuple[float, float, float], ...] = (
        (0, 0, 0.1),
        (5, 20, 0.1),
        (0, 40, 0.1),
        (-5, -20, 0.1),
        (0, -40, 0.1),
        (20, 0, 0.1),
        (40, 5, 0.1),
        (-20, -5, 0.1),
        (-40, 0, 0.1),
        (22, 20, 0.1),
        (-20, 22, 0.1),
        (20, -20, 0.1),
        (-25, -20, 0.1),
        (20, 40, 0.1),
        (20, -44, 0.1),
        (-24, 40, 0.1),
        (-20, -40, 0.1)
    )

    def __init__(self, zoneId, game, callback):
        self.numPlayers = 0
        self.game = game
        RegenTreasurePlannerAI.__init__(self, zoneId, ETreasureType.TOONTOWN_CENTRAL,
                                        self.SPAWN_POINTS, 'TagTreasurePlanner-' + str(zoneId), 3, 4, callback)

    def validAvatar(self, av):
        return av.doId != self.game.itAvId
