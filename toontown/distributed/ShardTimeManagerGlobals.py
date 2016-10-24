import math


# This is how often the world gets updated. Its in real world seconds.
# Increasing the value will cause time to slow down, decreasing it will cause time to speed up.
# 60 should always be used, this keeps the game's clock in-sync with the real world.
MINUTE = 60

HOUR = 20  # A Toontown hour is 20 minutes
HOURS = 2  # A full Toontown day is 2 hours.
DAY = HOURS * HOUR  # The total length of a Toontown day in minutes

TRANSITION_LENGTH = (9/2.0)
SEGMENT_LENGTH = TRANSITION_LENGTH * 3

DAWN_START_PERIOD = (SEGMENT_LENGTH/36.0)  # This is how far we get into the day before dawn starts
MIDDAY_START_PERIOD = ((DAWN_START_PERIOD*36.0+TRANSITION_LENGTH)/36.0)  # This is how far we get into the day before midday starts
DUSK_START_PERIOD = ((MIDDAY_START_PERIOD*36.0+SEGMENT_LENGTH)/36.0)  # This is how far we get into the day before dusk starts
NIGHT_START_PERIOD = ((DUSK_START_PERIOD*36.0+TRANSITION_LENGTH)/36.0)  # This is how far we get into the day before night starts

# All of the different parts of the day and when they start in toontown minutes.
# A toontown minute is defined in real world seconds at the top of the file.
DAWN_START = math.floor(DAY * DAWN_START_PERIOD)  # Dawn is the start of the transition from night to day
MIDDAY_START = math.floor(DAY * MIDDAY_START_PERIOD)
DUSK_START = math.floor(DAY * DUSK_START_PERIOD)  # Dusk is the transition from day to night
NIGHT_START = math.floor(DAY * NIGHT_START_PERIOD)

# Constants representing the current part of the day.
PERIOD_DAWN = 0
PERIOD_MIDDAY = 1
PERIOD_DUSK = 2
PERIOD_NIGHT = 3

MIDDAY_COLOR_SCALE = (1, 1, 1, 1)
NIGHT_COLOR_SCALE = (0.50, 0.50, 0.60, 1)
