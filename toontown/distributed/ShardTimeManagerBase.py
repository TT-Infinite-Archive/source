from toontown.distributed import ShardTimeManagerGlobals


class ShardTimeManagerBase:
    def __init__(self, r):
        self.r = r
        self.timeZone = None
        self.currentTime = 0

    def incrementTimeTask(self, task):
        self.incrementTime(1)

        # Send the 'time-tick' message.
        messenger.send('time-tick')

        # Do the task again.
        taskMgr.doMethodLater(ShardTimeManagerGlobals.MINUTE, self.incrementTimeTask, 'increment-time')

    def setCurrentTime(self, currentTime):
        # Remove our current time task.
        taskMgr.remove('increment-time')

        # Get the current minute offset.
        offset = self.r.toontownTimeManager.getTimetuple().tm_sec

        # Set the current time.
        self.currentTime = currentTime

        # Send the 'time-tick' message.
        messenger.send('time-tick')

        # Start our time task.
        taskMgr.doMethodLater(ShardTimeManagerGlobals.MINUTE-offset, self.incrementTimeTask, 'increment-time')

    def setTimeZone(self, timeZone):
        # Remove our current time task.
        taskMgr.remove('increment-time')

        # Set our timeZone, current time, and send a 'time-tick' message.
        self.timeZone = timeZone
        offset = self.calculateCurrentTime()
        messenger.send('time-tick')

        # Start our time task.
        taskMgr.doMethodLater(ShardTimeManagerGlobals.MINUTE-offset, self.incrementTimeTask, 'increment-time')

    def calculateCurrentTime(self):
        timetuple = self.r.toontownTimeManager.getTimetuple()

        # Create the base time.
        self.currentTime = (timetuple.tm_hour % ShardTimeManagerGlobals.HOURS) * ShardTimeManagerGlobals.HOUR
        self.currentTime += timetuple.tm_min

        # Increment the time based on our timezone.
        shifted = ShardTimeManagerBase.shiftTime(self.timeZone) * ShardTimeManagerGlobals.HOUR
        self.incrementTime(shifted)

        # Return the offset.
        return timetuple.tm_sec

    def incrementTime(self, amount):
        self.currentTime += amount
        self.currentTime %= ShardTimeManagerGlobals.DAY

    def getCurrentPeriod(self):
        if self.currentTime < ShardTimeManagerGlobals.DAWN_START or \
                        self.currentTime >= ShardTimeManagerGlobals.NIGHT_START:
            return ShardTimeManagerGlobals.PERIOD_NIGHT
        elif self.currentTime >= ShardTimeManagerGlobals.DUSK_START and \
                        self.currentTime < ShardTimeManagerGlobals.NIGHT_START:
            return ShardTimeManagerGlobals.PERIOD_DUSK
        elif self.currentTime >= ShardTimeManagerGlobals.MIDDAY_START and \
                        self.currentTime < ShardTimeManagerGlobals.DUSK_START:
            return ShardTimeManagerGlobals.PERIOD_MIDDAY
        elif self.currentTime >= ShardTimeManagerGlobals.DAWN_START and \
                        self.currentTime < ShardTimeManagerGlobals.MIDDAY_START:
            return ShardTimeManagerGlobals.PERIOD_DAWN

    def getTimeTillNextPeriod(self):
        currentPeriod = self.getCurrentPeriod()

        if currentPeriod == ShardTimeManagerGlobals.PERIOD_NIGHT:
            if self.currentTime >= ShardTimeManagerGlobals.NIGHT_START:
                return (ShardTimeManagerGlobals.DAY - self.currentTime) + ShardTimeManagerGlobals.DAWN_START
            else:
                return ShardTimeManagerGlobals.DAWN_START - self.currentTime
        elif currentPeriod == ShardTimeManagerGlobals.PERIOD_DUSK:
            return ShardTimeManagerGlobals.NIGHT_START - self.currentTime
        elif currentPeriod == ShardTimeManagerGlobals.PERIOD_MIDDAY:
            return ShardTimeManagerGlobals.DAWN_START - self.currentTime
        elif currentPeriod == ShardTimeManagerGlobals.PERIOD_DAWN:
            return ShardTimeManagerGlobals.MIDDAY_START - self.currentTime

    @staticmethod
    def shiftTime(timeZone):
        return timeZone - 3

    @staticmethod
    def formatTimeZone(timeZone):
        shifted = ShardTimeManagerBase.shiftTime(timeZone)
        if shifted < 0:
            return '%s' % shifted
        return '+%s' % shifted


