from panda3d.core import Texture
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
AntiAliasing = 'anti-aliasing'
TextureQuality = 'textures-quality'
CompressTextures = 'compress-textures'
ThreadedRender = 'experimental-threaded-render'
NewFootsteps = 'surface-footsteps'

# Default controls:
ClassicKeymap = {
    "MOVE_UP": "arrow_up",
    "MOVE_DOWN": "arrow_down",
    "MOVE_LEFT": "arrow_left",
    "MOVE_RIGHT": "arrow_right",
    "JUMP": "space",
    "ACTION_BUTTON": "delete",
    "INTERACT_KEY": "shift",
    "CHAT_HOTKEY": "t",
    "OPTIONS_PAGE_HOTKEY": "escape",
    "SCREENSHOT_KEY": "f9",
    "VIEW_GAGS_KEY": "home",
    "VIEW_TASKS_KEY": "end"
}

# Default custom controls:
DefaultKeymap = dict(ClassicKeymap, **{
    "MOVE_UP": "w",
    "MOVE_LEFT": "a",
    "MOVE_DOWN": "s",
    "MOVE_RIGHT": "d"
})

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
    NewFootsteps: True,
    Keymap: dict(DefaultKeymap),
    DoorInteract: False,
    NPCInteract: False,
    TextureQuality: 3,
    CompressTextures: False,
    ThreadedRender: False,
    AntiAliasing: False
}

TextureOptionToDimension = [128, 256, 1024, 4096]

def loadInitialSettings():
    # Initializes settings if some initial options aren't in there
    for setting, default in list(InitialSettings.items()):
        if setting not in settings:
            settings[setting] = dict(default) if isinstance(default, dict) else default