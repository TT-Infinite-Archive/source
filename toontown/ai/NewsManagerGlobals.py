from toontown.toonbase.ToontownGlobals import *

# [Holiday ID, Weekday]
DEFAULT_WEEKLY_HOLIDAYS = [
    [FISH_BINGO_NIGHT, 2],  # Wednesday
    [TROLLEY_HOLIDAY, 3],  # Thursday
    [SILLY_SATURDAY_BINGO, 5],  # Saturday
]


# [Holiday ID, START [Month, Day, Hour, Minute], END [Month, Day, Hour, Minute]]
DEFAULT_YEARLY_HOLIDAYS = [
    [TOP_TOONS_MARATHON, [1, 1, 0, 0], [1, 2, 0, 0]],
    [VALENTINES_DAY, [2, 8, 0, 0], [2, 24, 0, 0]],
    [SAINT_PATRICKS_DAY, [3, 13, 0, 0], [3, 20, 0, 0]],
    [APRIL_FOOLS_DAY, [4, 1, 0, 0], [4, 15, 0, 0]],
    [JULY4_FIREWORKS, [6, 29, 0, 0], [7, 17, 0, 0]],
    [HALLOWEEN_PROPS, [10, 21, 0, 0], [11, 1, 0, 0]],
    [TRICK_OR_TREAT, [10, 21, 0, 0], [11, 1, 0, 0]],
    [HALLOWEEN, [10, 31, 0, 0], [11, 1, 0, 0]],
    [WINTER_DECORATIONS, [12, 14, 0, 0], [1, 1, 0, 0]],
    [WINTER_CAROLING, [12, 14, 0, 0], [1, 1, 0, 0]],
    [DOUBLE_PROGRESSION_HOLIDAY, [1, 29, 0, 0], [2, 1, 0, 0]],
]

HOLIDAY_SHOPKEEPER_ZONES = {
    TRICK_OR_TREAT: {
        ToontownCentral: 2626,  # Jesse's Joke Repair
        DonaldsDock: 1820,  # Hook, Line, and Sinker Prank Shop
        DaisyGardens: 5609,  # Berried Treasure
        MinniesMelodyland: 4625,  # Tuba Toothpaste
        TheBrrrgh: 3653,  # Ice House Jewelry
        DonaldsDreamland: 9759  # Sleeping Beauty Parlor
    },
    WINTER_CAROLING: {
        ToontownCentral: 2659,
        DonaldsDock: 1707,
        DaisyGardens: 5626,
        MinniesMelodyland: 4614,
        TheBrrrgh: 3828,
        DonaldsDreamland: 9720
    }
}