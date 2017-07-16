Music = 'music'
MusicVolume = 'music-volume'
Sound = 'sfx'
SoundVolume = 'sound-volume'
WantWhispers = 'want-whispers'
WantFriendWhispers = 'want-friend-whispers'
WantNonFriendWhispers = 'want-non-friend-whispers'  # Dict of toonId to boolean
WantFriends = 'want-friends'
WantCustomControls = 'want-custom-controls'
LoadDisplay = 'loadDisplay'
Keymap = 'keymap'
ShowFps = 'show-fps'
VSync = 'vsync'
Resolution = 'res'
Fullscreen = 'fullscreen'
AnimationSmoothing = 'animation-smoothing'
ProcessFailback = 'process-failback'
ClassicMusic = 'classic-music'
DoorInteract = 'door-interaction-key'
NPCInteract = 'npc-interaction-key'

InitialSettings = {
    # Initial setting
    # name: default
    Music: True,
    Sound: True,
    MusicVolume: 1.0,
    SoundVolume: 1.0,
    LoadDisplay: "pandagl",
    WantCustomControls: False,
    Fullscreen: False,
    ShowFps: False,
    VSync: False,
    AnimationSmoothing: True,
    ProcessFailback: 60,
    ClassicMusic: False,
    Keymap: {
        "ACTION_BUTTON": "delete",
        "CHAT_HOTKEY": "t",
        "JUMP": "control",
        "MOVE_DOWN": "s",
        "MOVE_LEFT": "a",
        "MOVE_RIGHT": "d",
        "MOVE_UP": "w",
        "OPTIONS_PAGE_HOTKEY": "escape",
        "SCREENSHOT_KEY": "f9",
        "INTERACT_KEY": "shift"
    },
    DoorInteract: False,
    NPCInteract: False
}


def loadInitialSettings():
    # Initializes settings if some initial options aren't in there
    for setting, default in InitialSettings.items():
        if setting not in settings:
            settings[setting] = default