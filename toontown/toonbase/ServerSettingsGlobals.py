EnabledZones = 'wanted-zones'
ExpMultiplier = 'exp-multiplier'
YinYang = 'want-yin-yang'
WantRacing = 'want-racing'
WantGolf = 'want-golf'
TTCJukebox = 'want-ttc-jukebox'
WantSinglePlayer = 'want-singleplayer'
WantCheats = 'want-cheats'

InitialSettings = {
    EnabledZones: {
        "ToontownCentral": True,
        "TheHarbor": True,
        "DaisyGardens": True,
        "Melodyland": True,
        "TheBrrrgh": True,
        "Dreamland": True,
        "Speedway": True,
        "AcornAcres": True,
        "Minigolf": True,
        "SellbotHQ": True,
        "LawbotHQ": True,
        "CashbotHQ": True,
        "BossbotHQ": True
        },
    ExpMultiplier: 1,
    YinYang: True,
    WantRacing: True,
    WantGolf: True,
    TTCJukebox: True,
    WantSinglePlayer: False,
    WantCheats: False,
}
    
def loadInitialSettings():
    # Initializes settings if some initial options aren't in there
    for setting, default in InitialSettings.items():
        if setting not in serverSettings:
            serverSettings[setting] = default
