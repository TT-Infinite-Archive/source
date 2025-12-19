from typing import TYPE_CHECKING
from direct.directnotify import DirectNotifyGlobal
from toontown.coghq import DistributedCogHQDoor
from toontown.toonbase import TTLocalizer
from .CogDisguiseGlobals import EPlayerSuitType

if TYPE_CHECKING:
    from ..toonbase.ToonBase import ToonBase
    base: ToonBase


class DistributedSellbotHQDoor(DistributedCogHQDoor.DistributedCogHQDoor):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedSellbotHQDoor')

    def __init__(self, cr):
        DistributedCogHQDoor.DistributedCogHQDoor.__init__(self, cr)

    def informPlayer(self, suitType: EPlayerSuitType):
        self.notify.debugStateCall(self)
        match suitType:
            case EPlayerSuitType.NO_SUIT:
                popupMsg = TTLocalizer.SellbotRentalSuitMessage
            case EPlayerSuitType.NO_MERITS:
                popupMsg = TTLocalizer.SellbotCogSuitNoMeritsMessage
            case EPlayerSuitType.FULL_SUIT:
                popupMsg = TTLocalizer.SellbotCogSuitHasMeritsMessage
            case _:
                popupMsg = TTLocalizer.FADoorCodes_SB_DISGUISE_INCOMPLETE
        base.localAvatar.elevatorNotifier.showMeWithoutStopping(popupMsg, pos=(0, 0, 0.26), ttDialog=True)
        base.localAvatar.elevatorNotifier.setOkButton()
        base.localAvatar.elevatorNotifier.doneButton.setZ(-0.3)
