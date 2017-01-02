from toontown.toonbase import TTLocalizer


class Track:
    def __init__(self, idn, name):
        self.idn = idn
        self.name = name

TrackNone = 0
TrackToonUp = 1
TrackLure = 2
TrackTrap = 3
TrackSound = 4
TrackSquirt = 5
TrackThrow = 6
TrackDrop = 7

Tracks = [
    Track(0, TTLocalizer.lNone),
    Track(1, TTLocalizer.TrackToonUp),
    Track(2, TTLocalizer.TrackLure),
    Track(3, TTLocalizer.TrackTrap),
    Track(4, TTLocalizer.TrackSound),
    Track(5, TTLocalizer.TrackSquirt),
    Track(6, TTLocalizer.TrackThrow),
    Track(7, TTLocalizer.TrackDrop)
]