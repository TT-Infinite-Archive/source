from datetime import datetime

from toontown.parties.ToontownTimeZone import ToontownTimeZone


class ToontownTimeManagerAI:
    ClockFormat = '%I:%M:%S %p'
    formatStr = '%Y-%m-%d %H:%M:%S'

    def __init__(self):
        self.serverTimeZone = ToontownTimeZone()

    def getCurServerDateTime(self):
        return datetime.now(self.serverTimeZone)
