from panda3d.core import ConfigVariableBool, ConfigVariableString, NodePath, Texture, Vec4, loadPrcFile, loadPrcFileData
#!/usr/bin/env python2
import gc

# Due to the newer Panda3D versions being less stable on the C++ side of
# things, we need to disable the garbage collector during startup or a thread
# related error will cause an AttributeError.
# ~ Chan
gc.disable()

import builtins
import os, sys

builtins.process = 'client'

from direct.directnotify.DirectNotifyGlobal import directNotify

builtins.directNotify = directNotify
notify = directNotify.newCategory('ClientStart')
notify.setInfo(True)

if __debug__:

    loadPrcFile('config/general.prc')
    loadPrcFile('config/distribution/dev.prc')

    try:
        import wx
    except ModuleNotFoundError as e:
        notify.warning('Failed to start injector -- %s' % e)
    else:
        from otp.otpbase.OTPInjectorDev import Injector

        notify.info('Starting injector...')
        builtins.injector = Injector()


builtins.version = ConfigVariableString('server-version', 'n/a').getValue()


from otp.settings.Settings import Settings
from toontown.toonbase import ToontownGlobals

# The launcher gives each signed-in account a preferences file of its own
preferencesPath = os.environ.get('TTI_PREFERENCES') or os.path.join(ToontownGlobals.CurrentDirectory, ConfigVariableString('preferences-path', 'preferences.json').getValue())
notify.info('Reading %s...' % preferencesPath)
builtins.settings = Settings(preferencesPath)
from toontown.toonbase import SettingsGlobals
SettingsGlobals.loadInitialSettings()

# Load server settings (used for the hosting screen)
from otp.settings.Settings import Settings
builtins.serverSettings = Settings("serversettings.json")
from toontown.toonbase import ServerSettingsGlobals
ServerSettingsGlobals.loadInitialSettings()

loadPrcFileData('Settings: res',
                'win-size %d %d' % tuple(settings.get(SettingsGlobals.Resolution, (800, 600))))
loadPrcFileData('Settings: fullscreen',
                'fullscreen #%s' % 't' if settings[SettingsGlobals.Fullscreen] else 'f')
loadPrcFileData('Settings: music', 'audio-music-active %s' % settings[SettingsGlobals.Music])
loadPrcFileData('Settings: sfx',
                'audio-sfx-active %s' % settings[SettingsGlobals.Sound])
loadPrcFileData('Settings: musicVol',
                'audio-master-music-volume %s' % settings[SettingsGlobals.MusicVolume])
loadPrcFileData('Settings: sfxVol',
                'audio-master-sfx-volume %s' % settings[SettingsGlobals.SoundVolume])
loadPrcFileData('Settings: showFps',
                'show-frame-rate-meter %s' % (1 if settings[SettingsGlobals.ShowFps] else 0))
loadPrcFileData('Settings: vsync',
                'sync-video %s' % (1 if settings[SettingsGlobals.VSync] else 0))
loadPrcFileData('Settings: animationSmoothing',
                'interpolate-frames %s' % (1 if settings[SettingsGlobals.AnimationSmoothing] else 0))
loadPrcFileData('Settings: Texture Quality',
                'max-texture-dimension %d' % SettingsGlobals.TextureOptionToDimension[settings.get(SettingsGlobals.TextureQuality)])
loadPrcFileData('Settings: Texture Compression',
                'compressed-textures #%s' % 't' if settings[SettingsGlobals.CompressTextures] else 'f')
if settings[SettingsGlobals.ThreadedRender]:
    loadPrcFileData('Settings: Experimental Threaded Rendering',
                    'threading-model Cull/Draw')
    notify.warning("Experimental Threaded Rendering is enabled! The game may crash randomly! You have been warned!")

if sys.platform != 'android':
    loadPrcFileData('Settings: loadDisplay',
                    'load-display %s' % settings[SettingsGlobals.LoadDisplay])
else:
    loadPrcFileData('Settings: loadDisplay',
                    'load-display pandagles')

from toontown.toonbase.ContentPacksManager import ContentPacksManager

contentPacksPath = os.path.join(ToontownGlobals.CurrentDirectory, ConfigVariableString('content-packs-path', 'contentpacks').getValue())
if not os.path.exists(contentPacksPath):
    os.makedirs(contentPacksPath)
builtins.contentPacksMgr = ContentPacksManager(contentPacksPath)
contentPacksMgr.applyAll()

if sys.platform != 'android':
    if not os.path.isdir('astron/data'):
        os.makedirs('astron/data')

from toontown.launcher.TTILauncher import TTILauncher

builtins.launcher = TTILauncher()

if not __debug__:
    if launcher.getServerMode() is None:
        notify.error("No server was chosen, please start the game from the launcher.  Aborting.")

notify.info('Starting the game...')

from direct.gui import DirectGuiGlobals

DirectGuiGlobals.setDefaultFontFunc(ToontownGlobals.getInterfaceFont)

launcher.setPandaErrorCode(7)

from toontown.toonbase import ToonBase

ToonBase.ToonBase()

if base.win is None:
    notify.error('Unable to open window; aborting.')

launcher.setPandaErrorCode(0)


base.setBackgroundColor(Vec4(0, 0, 0, 0))
base.graphicsEngine.renderFrame()

DirectGuiGlobals.setDefaultRolloverSound(
    loader.loadSfx('phase_3/audio/sfx/GUI_rollover.ogg'))
DirectGuiGlobals.setDefaultClickSound(
    loader.loadSfx('phase_3/audio/sfx/GUI_create_toon_fwd.ogg'))
DirectGuiGlobals.setDefaultDialogGeom(
    loader.loadModel('phase_3/models/gui/dialog_box_gui.bam'))

from toontown.toon import Toon

Toon.preload()

from toontown.suit import Suit

Suit.preload()

from toontown.login import AvatarChooser

AvatarChooser.preload()

from toontown.shtiker import ShtikerGUI

ShtikerGUI.preload()

from toontown.toontowngui.Introduction import Introduction

introduction = Introduction()

from toontown.toontowngui.ClickToStart import ClickToStart

clickToStart = ClickToStart(version=version)
clickToStart.setColorScale(0, 0, 0, 0)

from toontown.toonbase import TTLocalizer
from otp.otpbase import OTPLocalizer
from otp.otpgui import OTPDialog


def syncLoginFSM(task=None):
    stateName = base.cr.loginFSM.getCurrentState().getName()
    if preloader.requests:
        if (introduction.getCurrentOrNextState() != 'Label') and (
                introduction.label.getText() != TTLocalizer.LoaderLabel):
            introduction.request('Label', TTLocalizer.LoaderLabel)
        taskMgr.doMethodLater(1, syncLoginFSM, 'syncLoginFSM-task')
    elif base.cr.introPending:
        # The session is warming up behind the cinematic
        introduction.request('ClickToStart')
    elif stateName in ('connect', 'login', 'waitForGameList',
                       'waitForShardList'):
        introduction.request('Label', OTPLocalizer.CRConnecting)
    elif stateName == 'failedToConnect':
        url = base.cr.serverList[0]
        if base.cr.bootedIndex in (1400, 1403, 1405):
            message = OTPLocalizer.CRNoConnectProxyNoPort % (url.getServer(), url.getPort(), url.getPort())
            style = OTPDialog.CancelOnly
        else:
            message = OTPLocalizer.CRNoConnectTryAgain % (url.getServer(), url.getPort())
            style = OTPDialog.TwoChoice
        if style == OTPDialog.CancelOnly:
            introduction.request('ExitDialog', message,
                                 base.cr.loginFSM.request, ['shutdown'])
        else:
            introduction.request(
                'YesNoDialog', message, base.cr.loginFSM.request,
                ['connect', [base.cr.serverList]], base.cr.loginFSM.request,
                ['shutdown'])
    elif stateName == 'noConnection':
        if (base.cr.bootedIndex is not None) and (
                base.cr.bootedIndex in OTPLocalizer.CRBootedReasons):
            message = OTPLocalizer.CRBootedReasons[base.cr.bootedIndex]
        elif base.cr.bootedIndex == 155:
            message = base.cr.bootedText
        elif base.cr.bootedText is not None:
            message = OTPLocalizer.CRBootedReasonUnknownCode % base.cr.bootedIndex
        else:
            message = OTPLocalizer.CRLostConnection
        if base.cr.bootedIndex == 152:
            message %= {'name': base.cr.bootedText}
        introduction.request('ExitDialog', message, base.cr.loginFSM.request,
                             ['shutdown'])
    elif stateName == 'missingGameRootObject':
        introduction.request(
            'YesNoDialog', OTPLocalizer.CRMissingGameRootObject,
            base.cr.loginFSM.request, ['waitForGameList'],
            base.cr.loginFSM.request, ['shutdown'])
    elif stateName == 'noShards':
        introduction.request(
            'YesNoDialog', OTPLocalizer.CRNoDistrictsTryAgain,
            base.cr.loginFSM.request, ['noShardsWait'],
            base.cr.loginFSM.request, ['shutdown'])
    else:
        introduction.request('ClickToStart')
    if task is not None:
        return task.done


from direct.interval.IntervalGlobal import Sequence, Func, Wait

presentsTrack = Sequence(
    Func(introduction.request, 'Presents'),
    Wait(7),
    Func(syncLoginFSM)
)
disclaimerTrack = Sequence(
    Func(introduction.request, 'Disclaimer'),
    Wait(7),
    Func(presentsTrack.start)
)

from toontown.distributed import ToontownClientRepository

base.cr = ToontownClientRepository.ToontownClientRepository(version, launcher)
base.cr.introduction = introduction
base.cr.clickToStart = clickToStart
base.initNametagGlobals()

from otp.distributed.OtpDoGlobals import OTP_DO_ID_FRIEND_MANAGER

base.cr.generateGlobalObject(OTP_DO_ID_FRIEND_MANAGER, 'FriendManager')

if not launcher.isDummy():
    base.startShow(gameserver=launcher.getGameServer())
else:
    base.startShow()

# Started from the launcher? Play the beautiful intro (unless opted-out)!
wantIntro = ConfigVariableBool('want-intro',
                               launcher.getServerMode() is not None).getValue()

if wantIntro:
    notify.info('Playing the introduction.')
    clickToStart.startMusic()
    disclaimerTrack.start()

    # Connect while the cinematic plays, so the click at the end of it opens
    # Pick-A-Toon instead of the usual "Connecting..." screen:
    base.cr.startWarmupSession()

    def skip():
        if disclaimerTrack.isPlaying():
            disclaimerTrack.finish()
        elif presentsTrack.isPlaying():
            presentsTrack.finish()

    base.accept('mouse1', skip)
else:
    notify.info('Skipping the introduction.')
    clickToStart.stop()
    clickToStart.begin()



# Now that everything is loaded we can enable the garbage collector again.
gc.enable()
gc.collect()

try:
    if ConfigVariableBool('want-leak-graph-client', False).getValue():
        from toontown.debug import LeakGraph
        LeakGraph.outputLeaking()

    base.run()
except SystemExit:
    pass
except Exception:
    import traceback
    traceback.print_exc()
