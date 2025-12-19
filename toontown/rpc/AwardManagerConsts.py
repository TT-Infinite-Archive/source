import enum


class GiveAwardError(enum.IntEnum):
    SUCCESS = 0
    WRONG_GENDER = 1
    NOT_GIFTABLE = 2
    FULL_MAILBOX = 3
    FULL_AWARD_MAILBOX = 4
    ALREADY_IN_MAILBOX = 5
    ALREADY_IN_GIFT_QUEUE = 6
    ALREADY_IN_ORDERED_QUEUE = 7
    ALREADY_IN_CLOSET = 8
    ALREADY_BEING_WORN = 9
    ALREADY_IN_AWARD_MAILBOX = 10
    ALREADY_IN_THIRTY_MINUTE_QUEUE = 11
    ALREADY_IN_MY_PHRASES = 12
    ALREADY_KNOW_DOODLE_TRAINING = 13
    ALREADY_RENTED = 14
    GENERIC_ALREADY_HAVE_ERROR = 15
    UNKNOWN_ERROR = 16
    UNKNOWN_TOON = 17
    NON_TOON = 18


GiveAwardErrorStrings: dict[GiveAwardError, str] = {
    GiveAwardError.SUCCESS: 'success',
    GiveAwardError.NOT_GIFTABLE: 'item is not giftable',
    GiveAwardError.FULL_MAILBOX: 'mailbox is full',
    GiveAwardError.FULL_AWARD_MAILBOX: 'award mailbox is full',
    GiveAwardError.ALREADY_IN_MAILBOX: 'award already in mailbox',
    GiveAwardError.ALREADY_IN_GIFT_QUEUE: 'award already in gift queue',
    GiveAwardError.ALREADY_IN_ORDERED_QUEUE: 'award already in ordered queue',
    GiveAwardError.ALREADY_IN_CLOSET: 'award already in closet',
    GiveAwardError.ALREADY_BEING_WORN: 'award already being worn',
    GiveAwardError.ALREADY_IN_AWARD_MAILBOX: 'award already in award mailbox',
    GiveAwardError.ALREADY_IN_THIRTY_MINUTE_QUEUE: 'award already in 30 minute queue',
    GiveAwardError.ALREADY_IN_MY_PHRASES: 'speed chat award already in my phrases',
    GiveAwardError.ALREADY_KNOW_DOODLE_TRAINING: 'doodle training award already known',
    GiveAwardError.ALREADY_RENTED: 'award is already rented',
    GiveAwardError.GENERIC_ALREADY_HAVE_ERROR: 'generic-already-have error',
    GiveAwardError.UNKNOWN_ERROR: 'unknown error',
    GiveAwardError.UNKNOWN_TOON: 'toon not in database',
    GiveAwardError.NON_TOON: 'this is not a toon'
}
