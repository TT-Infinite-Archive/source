from toontown.distributed.ShardTimeManagerBase import ShardTimeManagerBase
from toontown.distributed import ShardTimeManagerGlobals

from otp.ai.MagicWordGlobal import *


class ShardTimeManager(ShardTimeManagerBase):
    def getTimedColorScale(self):
        currentPeriod = self.getCurrentPeriod()

        if currentPeriod == ShardTimeManagerGlobals.PERIOD_DAWN:
            colorScale = [1, 1, 1, 1]
            dawnLength = ShardTimeManagerGlobals.MIDDAY_START - ShardTimeManagerGlobals.DAWN_START

            # Get the time of how long we have been in this period.
            minutes = dawnLength - self.getTimeTillNextPeriod()

            # Loop through the r, g, b values:
            for i in xrange(3):
                # Get the difference between NIGHT and MIDDAY color:
                difference = ShardTimeManagerGlobals.MIDDAY_COLOR_SCALE[i] - ShardTimeManagerGlobals.NIGHT_COLOR_SCALE[i]

                # Divide the difference by the length of the DAWN period:
                difference /= dawnLength

                # Multiply the difference by the number of minutes we have been in the DAWN period and set our
                # colorScale index to our value + night color scale.
                colorScale[i] = ShardTimeManagerGlobals.NIGHT_COLOR_SCALE[i] + (difference * minutes)

            # Return the colorScale:
            return tuple(colorScale)
        elif currentPeriod == ShardTimeManagerGlobals.PERIOD_MIDDAY:
            return ShardTimeManagerGlobals.MIDDAY_COLOR_SCALE
        elif currentPeriod == ShardTimeManagerGlobals.PERIOD_DUSK:
            colorScale = [1, 1, 1, 1]
            duskLength = ShardTimeManagerGlobals.NIGHT_START - ShardTimeManagerGlobals.DUSK_START

            # Get the time of how long we have been in this period.
            minutes = duskLength - self.getTimeTillNextPeriod()

            # Loop through the r, g, b values:
            for i in xrange(3):
                # Get the difference between NIGHT and MIDDAY color:
                difference = ShardTimeManagerGlobals.MIDDAY_COLOR_SCALE[i] - ShardTimeManagerGlobals.NIGHT_COLOR_SCALE[i]

                # Divide the difference by the length of the DUSK period:
                difference /= duskLength

                # Multiply the difference by the number of minutes we have been in the DUSK period and set our
                # colorScale index to our value - midday color scale.
                colorScale[i] = ShardTimeManagerGlobals.MIDDAY_COLOR_SCALE[i] - (difference * minutes)

            # Return the colorScale:
            return tuple(colorScale)
        elif currentPeriod == ShardTimeManagerGlobals.PERIOD_NIGHT:
            return ShardTimeManagerGlobals.NIGHT_COLOR_SCALE


@magicWord(category=CATEGORY_CREATIVE, types=[int])
def timeZone(tz):
    base.cr.shardTimeManager.setTimeZone(tz)


@magicWord(category=CATEGORY_CREATIVE, types=[int])
def time(minutes):
    # Set the current time, disregards time zone.
    base.cr.shardTimeManager.setCurrentTime(minutes)
