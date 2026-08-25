_catalogNodePath = None


def getCatalogNodePath():
    # Loaded on demand rather than at import: the AI reaches this module through
    # TTCodeRedemptionMgrAI, and a server has no art to load it from
    global _catalogNodePath
    if _catalogNodePath is None:
        _catalogNodePath = loader.loadModel('phase_3/models/gui/catalog_gui')
    return _catalogNodePath


CatalogBKGDScale = 0.60
ItemPageTextLoc = (-1.7, 0.0, 1.36)
ItemPageTextScale = 0.1

CatalogNumWeeks = 78

CatalogNumWeeksPerSeries = 13

CatalogPropPos = [
  (-1.3, 0.0, 0.8),
  (-0.6, 0.0, 0.8),
  (-1.3, 0.0, 0.1),
  (-0.6, 0.0, 0.1),
  (-1.3, 0.0, -0.6),
  (-0.6, 0.0, -0.6),
  (0.45, 0.0, 0.8),
  (1.15, 0.0, 0.8),
  (0.45, 0.0, 0.1),
  (1.15, 0.0, 0.1),
  (0.45, 0.0, -0.6),
  (1.15, 0.0, -0.6)
]

NoItems = 0
NewItems = 1
OldItems = 2

P_NoTrunk = -28
P_AlreadyOwnBiggerCloset = -27
P_ItemAlreadyRented = -26
P_OnAwardOrderListFull = -25
P_AwardMailboxFull = -24
P_ItemInPetTricks = -23
P_ItemInMyPhrases = -22
P_ItemOnAwardOrder = -21
P_ItemInAwardMailbox = -20
P_ItemAlreadyWorn = -19
P_ItemInCloset = -18
P_ItemOnGiftOrder = -17
P_ItemOnOrder = -16
P_ItemInMailbox = -15
P_PartyNotFound = 14
P_WillNotFit = -13
P_NotAGift = -12
P_OnOrderListFull = -11
P_MailboxFull = -10
P_NoPurchaseMethod = -9
P_ReachedPurchaseLimit = -8
P_NoRoomForItem = -7
P_NotShopping = -6
P_NotAtMailbox = -5
P_NotInCatalog = -4
P_NotEnoughMoney = -3
P_InvalidIndex = -2
P_UserCancelled = -1
P_ItemAvailable = 1
P_ItemOnOrder = 2
P_ItemUnneeded = 3
RentalCannon = 1
RentalGameTable = 2
GIFT_user = 0
GIFT_admin = 1
GIFT_RAT = 2
GIFT_mobile = 3
GIFT_cogs = 4
GIFT_partyrefund = 5
MaxHouseItems = 45
MaxCustomMessages = 25
MaxMailboxContents = 30
FM_InvalidItem = -7
FM_NondeletableItem = -6
FM_InvalidIndex = -5
FM_NotOwner = -4
FM_NotDirector = -3
FM_RoomFull = -2
FM_HouseFull = -1
FM_MovedItem = 1
FM_SwappedItem = 2
FM_DeletedItem = 3
FM_RecoveredItem = 4
