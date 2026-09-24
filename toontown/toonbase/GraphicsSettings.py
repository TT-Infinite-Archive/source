import sys

from panda3d.core import ClockObject, ConfigVariableBool, DynamicTextFont, TextNode, TexturePool, loadPrcFileData

from toontown.toonbase import SettingsGlobals

MaxAntiAliasingSamples = 4 if sys.platform == 'darwin' else 8
AntiAliasingSamples = tuple(samples for samples in (0, 2, 4, 8) if samples <= MaxAntiAliasingSamples)
AnisotropicDegrees = (1, 2, 4, 8, 16)
FrameRateLimits = (0, 30, 60, 120, 144, 240)
LodScales = (2.0, 1.0, 0.5)
FontQualities = (40, 128, 256, 512)


def antiAliasingSamples():
    if not settings[SettingsGlobals.AntiAliasing]:
        return 0
    return min(settings[SettingsGlobals.AntiAliasingSamples], MaxAntiAliasingSamples)


def setAntiAliasingSamples(samples):
    settings[SettingsGlobals.AntiAliasing] = bool(samples)
    if samples:
        settings[SettingsGlobals.AntiAliasingSamples] = samples


def applyAnisotropicDegree(degree):
    loadPrcFileData('Settings: Anisotropic Filtering',
                    'texture-anisotropic-degree %d' % degree)
    for texture in TexturePool.findAllTextures():
        texture.setAnisotropicDegree(degree)


def applyFrameRateLimit(fps):
    clock = ClockObject.getGlobalClock()
    if fps:
        clock.setMode(ClockObject.MLimited)
        clock.setFrameRate(fps)
    else:
        clock.setMode(ClockObject.MNormal)


def applyLodScale(scale):
    base.cam.node().setLodScale(scale)


def fontPageSize(quality):
    return max(256, quality * 4)


def fontTextureMargin(quality):
    return max(2, quality // 16)


def fontConfig(quality):
    pageSize = fontPageSize(quality)
    return ('text-pixels-per-unit %d\n'
            'text-page-size %d %d\n'
            'text-texture-margin %d\n'
            'text-minfilter linear_mipmap_linear') % (quality, pageSize, pageSize, fontTextureMargin(quality))


def loadedFonts(textNodes):
    from otp.otpbase import OTPGlobals
    from toontown.toonbase import ToontownClientGlobals

    fonts = [TextNode.getDefaultFont(), OTPGlobals.InterfaceFont, OTPGlobals.SignFont, OTPGlobals.FancyFont,
             ToontownClientGlobals.ToonFont, ToontownClientGlobals.BuildingNametagFont, ToontownClientGlobals.MinnieFont,
             ToontownClientGlobals.SuitFont, ToontownClientGlobals.FontAwesome]
    fonts.extend(OTPGlobals.NametagFonts.values())
    fonts.extend(nodePath.node().getFont() for nodePath in textNodes)
    return [font for font in fonts if isinstance(font, DynamicTextFont)]


def applyFontQuality(quality):
    loadPrcFileData('Settings: Font Quality', fontConfig(quality))

    roots = [render, render2d]
    if getattr(base, 'render2dp', None) is not None:
        roots.append(base.render2dp)
    textNodes = []
    for root in roots:
        textNodes.extend(root.findAllMatches('**/+TextNode;+s'))

    pageSize = fontPageSize(quality)
    for font in loadedFonts(textNodes):
        font.clear()
        font.setPixelsPerUnit(quality)
        font.setPageSize(pageSize, pageSize)
        font.setTextureMargin(fontTextureMargin(quality))

    # Anything not in the scene graph right now picks up the new letters the
    # next time it is built.
    for nodePath in textNodes:
        nodePath.node().forceUpdate()


def applyVSync(enabled):
    ConfigVariableBool('sync-video').setValue(enabled)


def applyAnimationSmoothing(enabled):
    ConfigVariableBool('interpolate-frames').setValue(enabled)
    for root in (render, render2d):
        for nodePath in root.findAllMatches('**/+Character;+s'):
            character = nodePath.node()
            for index in range(character.getNumBundles()):
                character.getBundle(index).setFrameBlendFlag(enabled)
