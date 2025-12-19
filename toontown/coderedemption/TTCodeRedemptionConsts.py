import enum
from panda3d.core import ConfigVariableInt
DefaultDbName = 'tt_code_redemption'


class ERedeemError(enum.IntEnum):
    SUCCESS = 0
    CODE_DOESNT_EXIST = 1
    CODE_IS_INACTIVE = 2
    CODE_ALREADY_REDEEMED = 3
    AWARD_COULDNT_BE_GIVEN = 4
    TOO_MANY_ATTEMPTS = 5
    SYSTEM_UNAVAILABLE = 6


RedeemErrorStrings: dict[ERedeemError, str] = {
    ERedeemError.SUCCESS: 'Success',
    ERedeemError.CODE_DOESNT_EXIST: 'Invalid code',
    ERedeemError.CODE_IS_INACTIVE: 'Code is inactive',
    ERedeemError.CODE_ALREADY_REDEEMED: 'Code has already been redeemed',
    ERedeemError.AWARD_COULDNT_BE_GIVEN: 'Award could not be given',
    ERedeemError.TOO_MANY_ATTEMPTS: 'Too many attempts, code ignored',
    ERedeemError.SYSTEM_UNAVAILABLE: 'Code redemption is currently unavailable'
}

MaxCustomCodeLen = ConfigVariableInt('tt-max-custom-code-len', 16).getValue()
