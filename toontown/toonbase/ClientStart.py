#!/usr/bin/env python2
import gc

# Due to the newer Panda3D versions being less stable on the C++ side of
# things, we need to disable the garbage collector during startup or a thread
# related error will cause an AttributeError.
# ~ Chan
gc.disable()

import __builtin__

__builtin__.process = 'client'

import tempfile
import atexit
import shutil
import os

# Create a temporary directory
__builtin__.tempdir = tempfile.mkdtemp()
atexit.register(shutil.rmtree, tempdir)

if __nirai__:
    # Output the DC file data to it (for use with Astron)
    filepath = os.path.join(tempdir, 'game_data.dc')
    with open(filepath, 'w') as f:
        f.write(dcData)

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
    except:
        notify.warning('Failed to start injector - wx module missing!')
    else:
        from otp.otpbase.OTPInjectorDev import Injector

        notify.info('Starting injector...')
        __builtin__.injector = Injector()

from panda3d.core import ConfigVariableString, loadPrcFileData

from otp.settings.Settings import Settings

preferencesPath = ConfigVariableString('preferences-path', 'preferences.json')
notify.info('Reading %s...' % preferencesPath.getValue())
__builtin__.settings = Settings(preferencesPath.getValue())
if 'fullscreen' not in settings:
    settings['fullscreen'] = False
if 'music' not in settings:
    settings['music'] = True
if 'sfx' not in settings:
    settings['sfx'] = True
if 'music-volume' not in settings:
    settings['music-volume'] = 1.0
if 'sound-volume' not in settings:
    settings['sound-volume'] = 1.0
if 'loadDisplay' not in settings:
    settings['loadDisplay'] = 'pandagl'
if 'toonChatSounds' not in settings:
    settings['toonChatSounds'] = True
if 'want-custom-controls' not in settings:
    settings['want-custom-controls'] = False
if 'keymap' not in settings:
    settings['keymap'] = {
        "ACTION_BUTTON": "delete",
        "CHAT_HOTKEY": "t",
        "JUMP": "control",
        "MOVE_DOWN": "s",
        "MOVE_LEFT": "a",
        "MOVE_RIGHT": "d",
        "MOVE_UP": "w",
        "OPTIONS_PAGE_HOTKEY": "escape"
    }
loadPrcFileData('Settings: res',
                'win-size %d %d' % tuple(settings.get('res', (800, 600))))
loadPrcFileData('Settings: fullscreen',
                'fullscreen %s' % settings['fullscreen'])
loadPrcFileData('Settings: music', 'audio-music-active %s' % settings['music'])
loadPrcFileData('Settings: sfx',
                'audio-sfx-active %s' % settings['sfx'])
loadPrcFileData('Settings: musicVol',
                'audio-master-music-volume %s' % settings.get('music-volume', 1.0))
loadPrcFileData('Settings: sfxVol',
                'audio-master-sfx-volume %s' % settings['sound-volume'])
loadPrcFileData('Settings: loadDisplay',
                'load-display %s' % settings['loadDisplay'])
loadPrcFileData('Settings: toonChatSounds',
                'toon-chat-sounds %s' % settings['toonChatSounds'])

import os

from toontown.toonbase.ContentPacksManager import ContentPacksManager

contentPacksPath = ConfigVariableString('content-packs-path', 'contentpacks')
if not os.path.exists(contentPacksPath.getValue()):
    os.makedirs(contentPacksPath.getValue())
__builtin__.contentPacksMgr = ContentPacksManager(contentPacksPath.getValue())
contentPacksMgr.applyAll()

if not os.path.isdir('astron\singleplayerdb'):
    os.makedirs('astron\singleplayerdb')

if not os.path.isdir('astron\multiplayerdb'):
    os.makedirs('astron\multiplayerdb')

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
    base.loadSfx('phase_3/audio/sfx/GUI_rollover.ogg'))
DirectGuiGlobals.setDefaultClickSound(
    base.loadSfx('phase_3/audio/sfx/GUI_create_toon_fwd.ogg'))
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

version = ConfigVariableString('server-version', 'n/a')
clickToStart = ClickToStart(version=version.getValue())
clickToStart.setColorScale(0, 0, 0, 0)

music = None
if base.musicManagerIsValid:
    if ToontownGlobals.HALLOWEEN_PROPS in base.clientHolidayIdList:
        music = loader.loadMusic('phase_3/audio/bgm/tti_theme_halloween.ogg')
    if ToontownGlobals.WACKY_WINTER_DECORATIONS in base.clientHolidayIdList:
        music = loader.loadMusic('phase_3/audio/bgm/tti_theme_christmas.ogg')
    else:
        music = loader.loadMusic('phase_3/audio/bgm/tti_theme.ogg')

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

base.cr = ToontownClientRepository.ToontownClientRepository(
    version.getValue(), launcher)
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

disclaimerTrack.start()
if music is not None:
    base.playMusic(music, looping=1, volume=0.9)


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
