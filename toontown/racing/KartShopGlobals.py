import enum


class KartShopGlobals:
    EVENTDICT = {'guiDone': 'guiDone',
     'returnKart': 'returnKart',
     'buyKart': 'buyAKart',
     'buyAccessory': 'buyAccessory'}
    KARTCLERK_TIMER = 180
    MAX_KART_ACC = 16


class EKartErrorCode(enum.IntEnum):
    NOT_ENOUGH_TICKETS = 0
    BOARD_OVER = 1
    NO_KART = 2
    OCCUPIED = 3
    TRACK_CLOSED = 4
    UNPAID = 5


class KartGlobals:
    ENTER_MOVIE = 1
    EXIT_MOVIE = 2
    COUNTDOWN_TIME = 30
    BOARDING_TIME = 10.0
    ENTER_RACE_TIME = 6.0
    FRONT_LEFT_SPOT = 0
    FRONT_RIGHT_SPOT = 1
    REAR_LEFT_SPOT = 2
    REAR_RIGHT_SPOT = 3
    PAD_GROUP_NUM = 4

    def getPadLocation(padId):
        return padId % KartGlobals.PAD_GROUP_NUM

    getPadLocation = staticmethod(getPadLocation)
