#!/usr/bin/env python2
import gc

# Due to the newer Panda3D versions being less stable on the C++ side of
# things, we need to disable the garbage collector during startup or a thread
# related error will cause an AttributeError.
# ~ Chan
gc.disable()

import __builtin__

__builtin__.process = 'client'

from panda3d.core import ConfigVariableString

__builtin__.version = ConfigVariableString('server-version', 'n/a').getValue()

from direct.directnotify.DirectNotifyGlobal import directNotify

__builtin__.directNotify = directNotify
notify = directNotify.newCategory('ClientStart')
notify.setInfo(True)

if __debug__:
    from panda3d.core import loadPrcFile

    loadPrcFile('config/general.prc')
    loadPrcFile('config/distribution/dev.prc')

    try:
        import wx
    except ImportError as e:
        notify.warning('Failed to start injector -- %s' % e.message)
    else:
        from otp.otpbase.OTPInjectorDev import Injector

        notify.info('Starting injector...')
        __builtin__.injector = Injector()

from panda3d.core import *

for dtool in ('children', 'parent', 'name'):
    del NodePath.DtoolClassDict[dtool]

from panda3d.core import loadPrcFileData

from otp.settings.Settings import Settings

preferencesPath = ConfigVariableString('preferences-path', 'preferences.json')
notify.info('Reading %s...' % preferencesPath.getValue())
__builtin__.settings = Settings(preferencesPath.getValue())
from toontown.toonbase import SettingsGlobals
SettingsGlobals.loadInitialSettings()

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
loadPrcFileData('Settings: loadDisplay',
                'load-display %s' % settings[SettingsGlobals.LoadDisplay])
loadPrcFileData('Settings: showFps',
                'show-frame-rate-meter %s' % (1 if settings[SettingsGlobals.ShowFps] else 0))
loadPrcFileData('Settings: vsync',
                'sync-video %s' % (1 if settings[SettingsGlobals.VSync] else 0))
loadPrcFileData('Settings: animationSmoothing',
                'interpolate-frames %s' % (1 if settings[SettingsGlobals.AnimationSmoothing] else 0))

import os

from toontown.toonbase.ContentPacksManager import ContentPacksManager

contentPacksPath = ConfigVariableString('content-packs-path', 'contentpacks')
if not os.path.exists(contentPacksPath.getValue()):
    os.makedirs(contentPacksPath.getValue())
__builtin__.contentPacksMgr = ContentPacksManager(contentPacksPath.getValue())
contentPacksMgr.applyAll()

if not os.path.isdir('astron/data/singleplayer'):
    os.makedirs('astron/data/singleplayer')

if not os.path.isdir('astron/data/multiplayer'):
    os.makedirs('astron/data/multiplayer')

from toontown.launcher.TTILauncher import TTILauncher

__builtin__.launcher = TTILauncher()

notify.info('Starting the game...')

from direct.gui import DirectGuiGlobals
from toontown.toonbase import ToontownGlobals

DirectGuiGlobals.setDefaultFontFunc(ToontownGlobals.getInterfaceFont)

launcher.setPandaErrorCode(7)

from toontown.toonbase import ToonBase

ToonBase.ToonBase()

if base.win is None:
    notify.error('Unable to open window; aborting.')

launcher.setPandaErrorCode(0)
launcher.setPandaWindowOpen()

from panda3d.core import Vec4

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

music = None
if base.musicManagerIsValid:
    music = loader.loadMusic('phase_3/audio/bgm/tti_classic_theme.ogg')

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
base.cr.music = music
base.cr.introduction = introduction
base.cr.clickToStart = clickToStart
base.initNametagGlobals()

from otp.distributed.OtpDoGlobals import OTP_DO_ID_FRIEND_MANAGER

base.cr.generateGlobalObject(OTP_DO_ID_FRIEND_MANAGER, 'FriendManager')

if not launcher.isDummy():
    base.startShow(gameserver=launcher.getGameServer())
else:
    base.startShow()

__builtin__.loader = base.loader
if music is not None:
    base.playMusic(music, looping=1, volume=0.9)

if __debug__:
    # Skip the introduction if we are in dev mode
    clickToStart.stop()
    clickToStart.begin()
else:
    disclaimerTrack.start()

    def skip():
        if disclaimerTrack.isPlaying():
            disclaimerTrack.finish()
        elif presentsTrack.isPlaying():
            presentsTrack.finish()

    base.accept('mouse1', skip)



# Now that everything is loaded we can enable the garbage collector again.
gc.enable()
gc.collect()

try:
    if config.GetBool('want-leak-graph-client', False):
        from toontown.debug import LeakGraph
        LeakGraph.outputLeaking()

    base.run()
except SystemExit:
    pass
except Exception:
    import traceback
    traceback.print_exc()
