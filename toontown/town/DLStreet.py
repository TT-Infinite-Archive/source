from toontown.town import Street
from toontown.distributed import ShardTimeManagerGlobals


class DLStreet(Street.Street):
    def enableTimeEffects(self):
        render.setColorScale(ShardTimeManagerGlobals.NIGHT_COLOR_SCALE)

    def disableTimeEffects(self):
        render.setColorScale(ShardTimeManagerGlobals.MIDDAY_COLOR_SCALE)
