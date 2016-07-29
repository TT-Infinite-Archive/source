from toontown.classicchars import CCharPaths
from toontown.safezone import Playground
from toontown.toonbase import TTLocalizer
from toontown.distributed import ShardTimeManagerGlobals


class DLPlayground(Playground.Playground):
    def showPaths(self):
        self.showPathPoints(CCharPaths.getPaths(TTLocalizer.Donald))

    def enableTimeEffects(self):
        render.setColorScale(ShardTimeManagerGlobals.NIGHT_COLOR_SCALE)

    def disableTimeEffects(self):
        render.setColorScale(ShardTimeManagerGlobals.MIDDAY_COLOR_SCALE)
