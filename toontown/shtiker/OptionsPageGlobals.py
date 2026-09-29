import enum
import sys

from toontown.toonbase import GraphicsSettings, SettingsGlobals, TTLocalizer

speedChatStyles = (
    (
        2000,
        (200 / 255.0, 60 / 255.0, 229 / 255.0),
        (200 / 255.0, 135 / 255.0, 255 / 255.0),
        (220 / 255.0, 195 / 255.0, 229 / 255.0)
    ),
    (
        2012,
        (142 / 255.0, 151 / 255.0, 230 / 255.0),
        (173 / 255.0, 180 / 255.0, 237 / 255.0),
        (220 / 255.0, 195 / 255.0, 229 / 255.0)
    ),
    (
        2001,
        (0 / 255.0, 0 / 255.0, 255 / 255.0),
        (140 / 255.0, 150 / 255.0, 235 / 255.0),
        (201 / 255.0, 215 / 255.0, 255 / 255.0)
    ),
    (
        2010,
        (0 / 255.0, 119 / 255.0, 190 / 255.0),
        (53 / 255.0, 180 / 255.0, 255 / 255.0),
        (201 / 255.0, 215 / 255.0, 255 / 255.0)
    ),
    (
        2014,
        (0 / 255.0, 64 / 255.0, 128 / 255.0),
        (0 / 255.0, 64 / 255.0, 128 / 255.0),
        (201 / 255.0, 215 / 255.0, 255 / 255.0)
    ),
    (
        2002,
        (90 / 255.0, 175 / 255.0, 225 / 255.0),
        (120 / 255.0, 215 / 255.0, 255 / 255.0),
        (208 / 255.0, 230 / 255.0, 250 / 255.0)
    ),
    (
        2003,
        (130 / 255.0, 235 / 255.0, 235 / 255.0),
        (120 / 255.0, 225 / 255.0, 225 / 255.0),
        (234 / 255.0, 255 / 255.0, 255 / 255.0)
    ),
    (
        2004,
        (0 / 255.0, 200 / 255.0, 70 / 255.0),
        (0 / 255.0, 200 / 255.0, 80 / 255.0),
        (204 / 255.0, 255 / 255.0, 204 / 255.0)
    ),
    (
        2015,
        (13 / 255.0, 255 / 255.0, 100 / 255.0),
        (64 / 255.0, 255 / 255.0, 131 / 255.0),
        (204 / 255.0, 255 / 255.0, 204 / 255.0)
    ),
    (
        2005,
        (235 / 255.0, 230 / 255.0, 0 / 255.0),
        (255 / 255.0, 250 / 255.0, 100 / 255.0),
        (255 / 255.0, 250 / 255.0, 204 / 255.0)
    ),
    (
        2006,
        (255 / 255.0, 153 / 255.0, 0 / 255.0),
        (229 / 255.0, 147 / 255.0, 0 / 255.0),
        (255 / 255.0, 234 / 255.0, 204 / 255.0)
    ),
    (
        2011,
        (255 / 255.0, 177 / 255.0, 62 / 255.0),
        (255 / 255.0, 200 / 255.0, 117 / 255.0),
        (255 / 255.0, 234 / 255.0, 204 / 255.0)
    ),
    (
        2007,
        (255 / 255.0, 0 / 255.0, 50 / 255.0),
        (229 / 255.0, 0 / 255.0, 50 / 255.0),
        (255 / 255.0, 204 / 255.0, 204 / 255.0)
    ),
    (
        2013,
        (130 / 255.0, 0 / 255.0, 26 / 255.0),
        (179 / 255.0, 0 / 255.0, 50 / 255.0),
        (255 / 255.0, 204 / 255.0, 204 / 255.0)
    ),
    (
        2016,
        (176 / 255.0, 35 / 255.0, 0 / 255.0),
        (240 / 255.0, 48 / 255.0, 0 / 255.0),
        (255 / 255.0, 204 / 255.0, 204 / 255.0)
    ),
    (
        2008,
        (255 / 255.0, 153 / 255.0, 193 / 255.0),
        (240 / 255.0, 157 / 255.0, 192 / 255.0),
        (255 / 255.0, 215 / 255.0, 238 / 255.0)
    ),
    (
        2009,
        (170 / 255.0, 120 / 255.0, 20 / 255.0),
        (165 / 255.0, 120 / 255.0, 50 / 255.0),
        (210 / 255.0, 200 / 255.0, 180 / 255.0)
    )
)

class ECategory(enum.Enum):
    VIDEO = 0
    SOUND = 1
    GAMEPLAY = 2
    SOCIAL = 3
    CODES = 4


Categories = (
    (ECategory.VIDEO, TTLocalizer.OptionsPageVideo),
    (ECategory.SOUND, TTLocalizer.OptionsPageSound),
    (ECategory.GAMEPLAY, TTLocalizer.OptionsPageGameplay),
    (ECategory.SOCIAL, TTLocalizer.OptionsPageSocial)
)


class ERowKind(enum.Enum):
    TOGGLE = 0
    CHOICE = 1
    SLIDER = 2
    HEADING = 3


class Option:
    def __init__(self, key = None, label = '', kind = ERowKind.TOGGLE, values = (),
                 valueLabels = (), requiresRestart = False, apply = None, getter = None, setter = None,
                 available = None):
        self.key = key
        self.label = label
        self.kind = kind
        self.values = values
        self.valueLabels = valueLabels
        self.requiresRestart = requiresRestart
        self.apply = apply
        self.getter = getter
        self.setter = setter
        self.available = available

    def isAvailable(self):
        return self.available is None or self.available()

    def getValue(self):
        if self.getter is not None:
            return self.getter()
        return settings[self.key]

    def setValue(self, value):
        if self.setter is not None:
            self.setter(value)
        else:
            settings[self.key] = value
        if self.apply is not None:
            self.apply(value)


def heading(label):
    return Option(label = label, kind = ERowKind.HEADING)


VideoOptions = (
    Option(
        key = SettingsGlobals.ShowFps,
        label = TTLocalizer.OptionsPageShowFps,
        apply = lambda value: base.setFrameRateMeter(value)
    ),
    Option(
        key = SettingsGlobals.VSync,
        label = TTLocalizer.OptionsPageVSync,
        requiresRestart = sys.platform != 'darwin',
        apply = GraphicsSettings.applyVSync
    ),
    Option(
        key = SettingsGlobals.RetinaMode,
        label = TTLocalizer.OptionsPageRetinaMode,
        requiresRestart = True,
        available = SettingsGlobals.retinaModeAvailable
    ),
    heading(TTLocalizer.OptionsPageQuality),
    Option(
        key = SettingsGlobals.AntiAliasing,
        label = TTLocalizer.OptionsPageAntiAliasing,
        kind = ERowKind.CHOICE,
        values = GraphicsSettings.AntiAliasingSamples,
        valueLabels = TTLocalizer.OptionsPageAntiAliasingValues[:len(GraphicsSettings.AntiAliasingSamples)],
        requiresRestart = True,
        getter = GraphicsSettings.antiAliasingSamples,
        setter = GraphicsSettings.setAntiAliasingSamples
    ),
    Option(
        key = SettingsGlobals.AnisotropicFiltering,
        label = TTLocalizer.OptionsPageAnisotropicFiltering,
        kind = ERowKind.CHOICE,
        values = GraphicsSettings.AnisotropicDegrees,
        valueLabels = TTLocalizer.OptionsPageAnisotropicFilteringValues,
        apply = GraphicsSettings.applyAnisotropicDegree
    ),
    Option(
        key = SettingsGlobals.FrameRateLimit,
        label = TTLocalizer.OptionsPageFrameRateLimit,
        kind = ERowKind.CHOICE,
        values = GraphicsSettings.FrameRateLimits,
        valueLabels = TTLocalizer.OptionsPageFrameRateLimitValues,
        apply = GraphicsSettings.applyFrameRateLimit
    ),
    Option(
        key = SettingsGlobals.LodDistance,
        label = TTLocalizer.OptionsPageLodDistance,
        kind = ERowKind.CHOICE,
        values = GraphicsSettings.LodScales,
        valueLabels = TTLocalizer.OptionsPageLodDistanceValues,
        apply = GraphicsSettings.applyLodScale
    ),
    Option(
        key = SettingsGlobals.FontQuality,
        label = TTLocalizer.OptionsPageFontQuality,
        kind = ERowKind.CHOICE,
        values = GraphicsSettings.FontQualities,
        valueLabels = TTLocalizer.OptionsPageFontQualityValues,
        apply = GraphicsSettings.applyFontQuality
    ),
    Option(
        key = SettingsGlobals.AnimationSmoothing,
        label = TTLocalizer.OptionsPageAnimationSmoothing,
        apply = GraphicsSettings.applyAnimationSmoothing
    )
)

SoundOptions = (
    Option(
        key = SettingsGlobals.Music,
        label = TTLocalizer.OptionsPageEnableMusic,
        apply = lambda value: base.enableMusic(value)
    ),
    Option(
        key = SettingsGlobals.MusicVolume,
        label = TTLocalizer.OptionsPageMusicVolume,
        kind = ERowKind.SLIDER,
        apply = lambda value: base.musicManager.setVolume(value)
    ),
    Option(
        key = SettingsGlobals.Sound,
        label = TTLocalizer.OptionsPageEnableSound,
        apply = lambda value: base.enableSoundEffects(value)
    ),
    Option(
        key = SettingsGlobals.SoundVolume,
        label = TTLocalizer.OptionsPageSoundVolume,
        kind = ERowKind.SLIDER,
        apply = lambda value: base.setSfxVolume(value)
    ),
    Option(
        key = SettingsGlobals.ClassicMusic,
        label = TTLocalizer.OptionsPageClassicMusic,
        apply = lambda value: setattr(base, 'wantClassicMusic', value)
    ),
    Option(
        key = SettingsGlobals.NewFootsteps,
        label = TTLocalizer.OptionsPageSurfaceFootsteps,
    )
)

CustomControlsOptions = (
    Option(
        key = SettingsGlobals.WantCustomControls,
        label = TTLocalizer.OptionsPageCustomControls,
    ),
)

InteractionOptions = (
    Option(
        key = SettingsGlobals.DoorInteract,
        label = TTLocalizer.OptionsPageDoorInteract,
        apply = lambda value: setattr(base, 'wantDoorInteract', value)
    ),
    Option(
        key = SettingsGlobals.NPCInteract,
        label = TTLocalizer.OptionsPageNpcInteract,
        apply = lambda value: setattr(base, 'wantNpcInteract', value)
    )
)
