"""
The settings a host chooses for their server and where they live on disk.
"""
from panda3d.core import ConfigVariableString
import os


EnabledZones = 'wanted-zones'
ExpMultiplier = 'exp-multiplier'
YinYang = 'want-yin-yang'
WantRacing = 'want-racing'
WantGolf = 'want-golf'
TTCJukebox = 'want-ttc-jukebox'
# WantSinglePlayer = 'want-singleplayer'
WantCheats = 'want-cheats'

# The launcher's Hosting screen writes these into the settings file too.
DistrictName = 'district-name'
HostPort = 'host-port'
SettingsFile = 'host-settings-file'
StatusFile = 'host-status-file'
DefaultSettingsFile = 'server-settings.json'
DefaultStatusFile = 'server-status.json'

def settingsPath():
    """
    The host's settings: district name, port, which zones are open.

    Read by every process in the server stack.
    """
    path = ConfigVariableString(
        SettingsFile, DefaultSettingsFile).getValue() or DefaultSettingsFile

    return os.path.abspath(path)


def statusPath():
    """
    Where the district reports who is online, or None to not report at all.
    """
    path = ConfigVariableString(StatusFile, '').getValue()

    return os.path.abspath(path) if path else None


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
    YinYang: False,
    WantRacing: True,
    WantGolf: True,
    TTCJukebox: False,
    # WantSinglePlayer: False,
    WantCheats: False,
    DistrictName: 'Kookyboro',
    HostPort: 7000,
}
    
def loadInitialSettings():
    # Initializes settings if some initial options aren't in there
    for setting, default in list(InitialSettings.items()):
        if setting not in serverSettings:
            serverSettings[setting] = default
