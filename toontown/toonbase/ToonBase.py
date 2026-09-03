from panda3d.core import ConfigVariableBool, ConfigVariableDouble, ConfigVariableInt, ConfigVariableString, Connection, CullBinManager, DSearchPath, Filename, TextProperties, TextPropertiesManager, URLSpec, VBase4, VirtualFileSystem, WindowProperties, loadPrcFileData
import fractions
import os
import random
import sys
import time
from sys import platform

from direct.directnotify import DirectNotifyGlobal
from direct.filter.CommonFilters import CommonFilters
from direct.gui import DirectGuiGlobals
from direct.gui.DirectGui import *

from otp.ai.MagicWordGlobal import *
from otp.otpbase import OTPBase
from otp.otpbase import OTPGlobals
from otp.otpbase import OTPLauncherGlobals
from toontown.margins import MarginGlobals
from toontown.margins.MarginManager import MarginManager
from toontown.nametag import NametagGlobals
from toontown.toonbase import TTLocalizer
from toontown.toonbase import ToontownAccess
from toontown.toonbase import ToontownBattleGlobals
from toontown.toonbase import ToontownGlobals, SettingsGlobals
from toontown.toonbase import ToontownLoader
from toontown.toonbase.Preloader import Preloader
from toontown.toontowngui import TTDialog
from toontown.toonbase import ServerSettingsGlobals

if ConfigVariableBool('want-leak-graph', False).getValue():
    from toontown.debug.LeakGraph import LeakGraph


class ToonBase(OTPBase.OTPBase):
    notify = DirectNotifyGlobal.directNotify.newCategory('ToonBase')

    def __init__(self):
        OTPBase.OTPBase.__init__(self)

        self.cr = None
        self.isHosting = None
        self.wantSinglePlayer = None

        # Get the native display info:
        if sys.platform != 'android':
            self.nativeWidth = self.pipe.getDisplayWidth()
            self.nativeHeight = self.pipe.getDisplayHeight()
            ratio = float(self.nativeWidth) / float(self.nativeHeight)
            fraction = fractions.Fraction(ratio).limit_denominator()
            self.nativeRatio = (int(fraction.numerator), int(fraction.denominator))
        else:
            self.nativeRatio = (16, 9)

        self.calcRatio = self.nativeRatio

        # Choose the best resolution if we're either fullscreen, or we don't
        # have a resolution defined in our settings:
        fullscreen = settings.get('fullscreen', False)
        if 'res' not in settings and not fullscreen:
            # Choose the smallest resolution that matches that largest
            # ratio that contains resolutions that will fit our display in
            # windowed mode:
            res = self.getSmallestResolution()

            # Store our result
            settings['res'] = res
            
            # Reload the graphics pipe:
            properties = WindowProperties()

            properties.setSize(res[0], res[1])
            properties.setFullscreen(fullscreen)
            properties.setParentWindow(0)

            # Store the window sort for later:
            sort = self.win.getSort()

            if self.win:
                currentProperties = WindowProperties(self.win.getProperties())
                gsg = self.win.getGsg()
            else:
                currentProperties = WindowProperties.getDefault()
                gsg = None
            newProperties = WindowProperties(currentProperties)
            newProperties.addProperties(properties)
            if (gsg is None) or (
                currentProperties.getFullscreen() != newProperties.getFullscreen()) or (
                currentProperties.getParentWindow() != newProperties.getParentWindow()):
                self.openMainWindow(props=properties, gsg=gsg, keepCamera=True)
                self.graphicsEngine.openWindows()
                self.disableShowbaseMouse()
            else:
                self.win.requestProperties(properties)
                self.graphicsEngine.renderFrame()

            self.win.setSort(sort)
            self.graphicsEngine.renderFrame()
            self.graphicsEngine.renderFrame()
        self.disableShowbaseMouse()
        self.addCullBins()
        self.debugRunningMultiplier /= OTPGlobals.ToonSpeedFactor
        self.baseXpMultiplier = ConfigVariableDouble('base-xp-multiplier', 1.0).getValue()

        # self.wantSinglePlayer = serverSettings[ServerSettingsGlobals.WantSinglePlayer]
        self.wantCheats = serverSettings[ServerSettingsGlobals.WantCheats]
        self.wantTTCJukebox = serverSettings[ServerSettingsGlobals.TTCJukebox]

        self.toonChatSounds = ConfigVariableBool('toon-chat-sounds', True).getValue()
        self.placeBeforeObjects = ConfigVariableBool('place-before-objects', True).getValue()
        self.endlessQuietZone = False
        self.wantDynamicShadows = 0
        self.exitErrorCode = 0
        base.camera.setPosHpr(0, 0, 0, 0, 0, 0)
        self.camLens.setMinFov(ToontownGlobals.DefaultCameraFov / (4. / 3.))
        self.camLens.setNearFar(ToontownGlobals.DefaultCameraNear,
                                ToontownGlobals.DefaultCameraFar)
        self.musicManager.setVolume(settings.get(SettingsGlobals.MusicVolume, 0.6))
        self.setSfxVolume(settings.get(SettingsGlobals.SoundVolume, 0.6))
        self.setBackgroundColor(ToontownGlobals.DefaultBackgroundColor)
        self.screenshotSfx = self.loader.loadSfx('phase_4/audio/sfx/Photo_shutter.ogg')
        tpm = TextPropertiesManager.getGlobalPtr()
        candidateActive = TextProperties()
        candidateActive.setTextColor(0, 0, 1, 1)
        tpm.setProperties('candidate_active', candidateActive)
        candidateInactive = TextProperties()
        candidateInactive.setTextColor(0.3, 0.3, 0.7, 1)
        tpm.setProperties('candidate_inactive', candidateInactive)
        self.transitions.IrisModelName = 'phase_3/models/misc/iris'
        self.transitions.FadeModelName = 'phase_3/models/misc/fade'
        self.exitFunc = self.userExit
        if 'launcher' in __builtins__ and launcher:
            launcher.setPandaErrorCode(11)

        globalClock.setMaxDt(0.2)
        if ConfigVariableBool('want-particles', True).getValue():
            self.notify.debug('Enabling particles')
            self.enableParticles()

        # OS X Specific Actions
        if platform == "darwin":
            self.acceptOnce(ToontownGlobals.QuitGameHotKeyOSX, self.exitOSX)
            self.accept(ToontownGlobals.QuitGameHotKeyRepeatOSX, self.exitOSX)
            self.acceptOnce(ToontownGlobals.HideGameHotKeyOSX, self.hideGame)
            self.accept(ToontownGlobals.HideGameHotKeyRepeatOSX, self.hideGame)
            self.acceptOnce(ToontownGlobals.MinimizeGameHotKeyOSX,
                            self.minimizeGame)
            self.accept(ToontownGlobals.MinimizeGameHotKeyRepeatOSX,
                        self.minimizeGame)

        self.accept('f3', self.toggleGui)
        self.accept('f4', self.toggleNameTags)
        self.accept('panda3d-render-error', self.panda3dRenderError)
        oldLoader = self.loader
        self.loader = ToontownLoader.ToontownLoader(self)
        __builtins__['loader'] = self.loader
        oldLoader.destroy()
        self.preloader = Preloader()
        __builtins__['preloader'] = self.preloader
        self.accept('PandaPaused', self.disableAllAudio)
        self.accept('PandaRestarted', self.enableAllAudio)
        self.friendMode = ConfigVariableBool('switchboard-friends', False).getValue()
        self.wantPets = ConfigVariableBool('want-pets', True).getValue()
        self.wantBingo = ConfigVariableBool('want-fish-bingo', True).getValue()
        self.wantKarts = ConfigVariableBool('want-karts', True).getValue()
        self.wantNewSpecies = ConfigVariableBool('want-new-species', False).getValue()
        self.wantAchievements = ConfigVariableBool('want-achievements', True).getValue()
        self.wantGroupTracker = ConfigVariableBool('want-grouptracker', False).getValue()
        self.wantGuilds = ConfigVariableBool('want-guilds', False).getValue()
        self.wantCollectibles = ConfigVariableBool('want-collectibles', True).getValue()
        self.wantMultiplayer = ConfigVariableBool('want-multiplayer', False).getValue()
        self.wantMods = ConfigVariableBool('want-mods', False).getValue()
        self.wantServerBrowser = ConfigVariableBool('want-server-browser', False).getValue()
        self.wantTrolleyTTC = ConfigVariableBool('want-ttc-trolley', False).getValue()
        self.inactivityTimeout = ConfigVariableDouble('inactivity-timeout', ToontownGlobals.KeyboardTimeout).getValue()
        if self.inactivityTimeout:
            self.notify.debug('Enabling Panda timeout: %s' % self.inactivityTimeout)
            self.mouseWatcherNode.setInactivityTimeout(self.inactivityTimeout)
        self.mouseWatcherNode.setEnterPattern('mouse-enter-%r')
        self.mouseWatcherNode.setLeavePattern('mouse-leave-%r')
        self.mouseWatcherNode.setButtonDownPattern('button-down-%r')
        self.mouseWatcherNode.setButtonUpPattern('button-up-%r')
        self.randomMinigameAbort = ConfigVariableBool('random-minigame-abort', False).getValue()
        self.randomMinigameDisconnect = ConfigVariableBool('random-minigame-disconnect', False).getValue()
        self.randomMinigameNetworkPlugPull = ConfigVariableBool('random-minigame-netplugpull', False).getValue()
        self.autoPlayAgain = ConfigVariableBool('auto-play-again', False).getValue()
        self.skipMinigameReward = ConfigVariableBool('skip-minigame-reward', False).getValue()
        self.wantMinigameDifficulty = ConfigVariableBool('want-minigame-difficulty', False).getValue()
        self.minigameDifficulty = ConfigVariableDouble('minigame-difficulty', -1.0).getValue()
        if self.minigameDifficulty == -1.0:
            del self.minigameDifficulty
        self.minigameSafezoneId = ConfigVariableInt('minigame-safezone-id', -1).getValue()
        if self.minigameSafezoneId == -1:
            del self.minigameSafezoneId
        cogdoGameSafezoneId = ConfigVariableInt('cogdo-game-safezone-id', -1).getValue()
        cogdoGameDifficulty = ConfigVariableDouble('cogdo-game-difficulty', -1).getValue()
        if cogdoGameDifficulty != -1:
            self.cogdoGameDifficulty = cogdoGameDifficulty
        if cogdoGameSafezoneId != -1:
            self.cogdoGameSafezoneId = cogdoGameSafezoneId
        ToontownBattleGlobals.SkipMovie = ConfigVariableBool('skip-battle-movies', 0).getValue()
        self.creditCardUpFront = ConfigVariableInt('credit-card-up-front', -1).getValue()
        if self.creditCardUpFront == -1:
            del self.creditCardUpFront
        else:
            self.creditCardUpFront = self.creditCardUpFront != 0
        self.housingEnabled = ConfigVariableBool('want-housing', True).getValue()
        self.cannonsEnabled = ConfigVariableBool('estate-cannons', 0).getValue()
        self.fireworksEnabled = ConfigVariableBool('estate-fireworks', 0).getValue()
        self.dayNightEnabled = ConfigVariableBool('estate-day-night', 0).getValue()
        self.cloudPlatformsEnabled = ConfigVariableBool('estate-clouds', 0).getValue()
        self.greySpacing = ConfigVariableBool('allow-greyspacing', 0).getValue()
        self.goonsEnabled = ConfigVariableBool('estate-goon', 0).getValue()
        self.restrictTrialers = ConfigVariableBool('restrict-trialers', True).getValue()
        self.roamingTrialers = ConfigVariableBool('roaming-trialers', True).getValue()
        self.slowQuietZone = ConfigVariableBool('slow-quiet-zone', 0).getValue()
        self.slowQuietZoneDelay = ConfigVariableDouble('slow-quiet-zone-delay', 5).getValue()
        self.killInterestResponse = ConfigVariableBool('kill-interest-response', 0).getValue()

        self.showGroupTracker = settings.get('grouptracker', True)
        settings['grouptracker'] = self.showGroupTracker
        
        tpMgr = TextPropertiesManager.getGlobalPtr()
        WLDisplay = TextProperties()
        WLDisplay.setSlant(0.3)
        WLEnter = TextProperties()
        WLEnter.setTextColor(1.0, 0.0, 0.0, 1)
        tpMgr.setProperties('WLDisplay', WLDisplay)
        tpMgr.setProperties('WLEnter', WLEnter)
        del tpMgr
        self.lastScreenShotTime = globalClock.getRealTime()
        self.accept('InputState-forward', self.__walking)
        self.canScreenShot = 1
        self.glitchCount = 0
        self.walking = 0
        self.oldX = max(1, base.win.getXSize())
        self.oldY = max(1, base.win.getYSize())
        self.aspectRatio = float(self.oldX) / self.oldY
        self.localAvatarStyle = None

        self.filters = CommonFilters(self.win, self.cam)

        ToontownGlobals.setInterfaceFont(TTLocalizer.InterfaceFont)
        ToontownGlobals.setSignFont(TTLocalizer.SignFont)
        ToontownGlobals.setFancyFont(TTLocalizer.FancyFont)
        for i in range(len(TTLocalizer.NametagFonts)):
            ToontownGlobals.setNametagFont(i, TTLocalizer.NametagFonts[i])

        # Free black/white Toons:
        self.wantYinYang = ConfigVariableBool('want-yin-yang', False).getValue()

        activeHolidays = os.environ.get('TTI_ACTIVE_HOLIDAYS') or ConfigVariableString('active-holidays', '').getValue()
        self.clientHolidayIdList = []
        for holidayId in activeHolidays.split(','):
            holidayId = holidayId.strip()
            if not holidayId:
                continue
            try:
                self.clientHolidayIdList.append(int(holidayId))
            except ValueError:
                self.notify.warning('Ignoring holiday id %r' % holidayId)
        
        self.wantCustomControls = settings.get('want-custom-controls', False)

        self.MOVE_UP = 'arrow_up'   
        self.MOVE_DOWN = 'arrow_down'
        self.MOVE_LEFT = 'arrow_left'      
        self.MOVE_RIGHT = 'arrow_right'
        self.JUMP = 'control'
        self.ACTION_BUTTON = 'delete'
        self.SCREENSHOT_KEY = 'f9'
        self.INTERACT_KEY = 'shift'
        
        keymap = settings.get('keymap', {})
        if self.wantCustomControls:
            self.MOVE_UP = keymap.get('MOVE_UP', self.MOVE_UP)
            self.MOVE_DOWN = keymap.get('MOVE_DOWN', self.MOVE_DOWN)
            self.MOVE_LEFT = keymap.get('MOVE_LEFT', self.MOVE_LEFT)
            self.MOVE_RIGHT = keymap.get('MOVE_RIGHT', self.MOVE_RIGHT)
            self.JUMP = keymap.get('JUMP', self.JUMP)
            self.ACTION_BUTTON = keymap.get('ACTION_BUTTON', self.ACTION_BUTTON)
            ToontownGlobals.OptionsPageHotkey = keymap.get('OPTIONS-PAGE', ToontownGlobals.OptionsPageHotkey)
            self.SCREENSHOT_KEY = keymap.get('SCREENSHOT_KEY', self.SCREENSHOT_KEY)
            self.INTERACT_KEY = keymap.get('INTERACT_KEY', self.INTERACT_KEY)
        
        self.CHAT_HOTKEY = keymap.get('CHAT_HOTKEY', 't')
        
        self.accept(self.SCREENSHOT_KEY, self.takeScreenShot)

        self.wantClassicMusic = settings.get('classic-music', False)
        
        self.wantDoorInteract = settings.get('door-interaction-key')
        self.wantNpcInteract = settings.get('npc-interaction-key')
        
        self.leakGraph = None
        if ConfigVariableBool('want-leak-graph-client', False).getValue():
            self.leakGraph = LeakGraph('tti-client-process')
            self.leakGraph.start()

        self.picker = None
        self.placer = None

        self.__tick()

    def openMainWindow(self, *args, **kw):
        try:
            result = OTPBase.OTPBase.openMainWindow(self, *args, **kw)
        except Exception as e:
            settings['fullscreen'] = False
            raise Exception('Could not open window, resetting display options try to run the game again.')

        self.setCursorAndIcon()
        return result

    def windowEvent(self, win):
        OTPBase.OTPBase.windowEvent(self, win)

        MarginGlobals.updateMarginVisibles()

    def setCursorAndIcon(self):
        if sys.platform == 'android':
            return

        vfs = VirtualFileSystem.getGlobalPtr()

        searchPath = DSearchPath()
        if __debug__:
            searchPath.appendDirectory(Filename('/resources/phase_3/etc'))
        searchPath.appendDirectory(Filename('/phase_3/etc'))

        for filename in ['toonmono.cur', 'icon.ico']:
            p3filename = Filename(filename)
            found = vfs.resolveFilename(p3filename, searchPath)
            if not found:
                return  # Can't do anything past this point.

            with open(os.path.join(self.tempDir, filename), 'wb') as f:
                f.write(vfs.readFile(p3filename, False))

        wp = WindowProperties()
        wp.setCursorFilename(
            Filename.fromOsSpecific(os.path.join(self.tempDir, 'toonmono.cur')))
        wp.setIconFilename(
            Filename.fromOsSpecific(os.path.join(self.tempDir, 'icon.ico')))
        self.win.requestProperties(wp)

    def addCullBins(self):
        cbm = CullBinManager.getGlobalPtr()
        cbm.addBin('ground', CullBinManager.BTUnsorted, 18)
        cbm.addBin('shadow', CullBinManager.BTBackToFront, 19)
        cbm.addBin('gui-popup', CullBinManager.BTUnsorted, 60)

    def disableShowbaseMouse(self):
        self.useDrive()
        self.disableMouse()
        if self.mouseInterface: self.mouseInterface.detachNode()
        if self.mouse2cam: self.mouse2cam.detachNode()

    def __walking(self, pressed):
        self.walking = pressed

    def toggleNameTags(self):
        nametags3d = render.findAllMatches('**/nametag3d')
        nametags2d = render2d.findAllMatches('**/Nametag2d')
        hide = False
        # Check if anything we're supposed to hide is visible
        for nametag in nametags2d:
            if not nametag.isHidden():
                hide = True
        for nametag in nametags3d:
            if not nametag.isHidden():
                hide = True
                
        # If anything is visible, hide, else we will show everything
        for nametag in nametags3d:
            if hide:
                nametag.hide()
            else:
                nametag.show()
        for nametag in nametags2d:
            if hide:
                nametag.hide()
            else:
                nametag.show()
        
    def toggleGui(self):
        if aspect2d.isHidden():
            base.transitions.noFade()
            aspect2d.show()
        else:
            aspect2d.hide()
            base.transitions.fadeScreen(alpha=0)
            
    def showNotification(self, message):
        if hasattr(self, 'notificationPopup') and self.notificationPopup:
            self.notificationPopup.destroy()
            taskMgr.remove('clearNotification')
        self.notificationPopup = DirectLabel(text = message, scale = 0.05, pos = (0.0, 0.0, 0.3), text_bg = (0, 0, 0, .4), text_fg = (1, 1, 1, 1), frameColor = (1, 1, 1, 0))
        self.notificationPopup.reparentTo(base.a2dBottomCenter)
        self.notificationPopup.setBin('gui-popup', 0)     
        def clearNotificationPopup(task):
            self.notificationPopup.destroy()
            return task.done

        taskMgr.doMethodLater(5.0, clearNotificationPopup, 'clearNotification')

    def takeScreenShot(self):
        if hasattr(self, 'notificationPopup') and self.notificationPopup:
            self.notificationPopup.destroy()
            taskMgr.remove('clearScreenshot')
        if not os.path.exists(TTLocalizer.ScreenshotPath):
            os.mkdir(TTLocalizer.ScreenshotPath)
            self.notify.info('Made new directory to save screenshots.')
        self.screenshotSfx.play()
        namePrefix = TTLocalizer.ScreenshotPath + launcher.logPrefix + 'screenshot'
        timedif = globalClock.getRealTime() - self.lastScreenShotTime
        if self.glitchCount > 10 and self.walking:
            return
        if timedif < 1.0 and self.walking:
            self.glitchCount += 1
            return
        if not hasattr(self, 'localAvatar'):
            self.screenshot(namePrefix=namePrefix)
            self.lastScreenShotTime = globalClock.getRealTime()
            return
        coordOnScreen = ConfigVariableBool('screenshot-coords', 0).getValue()
        self.localAvatar.stopThisFrame = 1
        ctext = self.localAvatar.getAvPosStr()
        self.screenshotStr = ''
        messenger.send('takingScreenshot')
        if coordOnScreen:
            coordTextLabel = DirectLabel(pos=(-0.81, 0.001, -0.87), text=ctext,
                                         text_scale=0.05,
                                         text_fg=VBase4(1.0, 1.0, 1.0, 1.0),
                                         text_bg=(0, 0, 0, 0),
                                         text_shadow=(0, 0, 0, 1), relief=None)
            coordTextLabel.setBin('gui-popup', 0)
            strTextLabel = None
            if len(self.screenshotStr):
                strTextLabel = DirectLabel(pos=(0.0, 0.001, 0.9),
                                           text=self.screenshotStr,
                                           text_scale=0.05,
                                           text_fg=VBase4(1.0, 1.0, 1.0, 1.0),
                                           text_bg=(0, 0, 0, 0),
                                           text_shadow=(0, 0, 0, 1),
                                           relief=None)
                strTextLabel.setBin('gui-popup', 0)
        self.graphicsEngine.renderFrame()
        self.screenshot(namePrefix=namePrefix,
                        imageComment=ctext + ' ' + self.screenshotStr)
        screenshot = self.screenshot(namePrefix=namePrefix, imageComment=ctext + ' ' + self.screenshotStr)
        self.lastScreenShotTime = globalClock.getRealTime()
        pandafile = Filename(os.path.join(ToontownGlobals.CurrentDirectory, str(screenshot)))
        winfile = pandafile.toOsSpecific()
        self.showNotification("Screenshot Saved" + ':\n' + winfile)
        if coordOnScreen:
            if strTextLabel is not None:
                strTextLabel.destroy()
            coordTextLabel.destroy()

    def addScreenshotString(self, str):
        if len(self.screenshotStr):
            self.screenshotStr += '\n'
        self.screenshotStr += str

    def initNametagGlobals(self):
        NametagGlobals.setMe(base.cam)

        NametagGlobals.setCardModel('phase_3/models/props/panel.bam')
        NametagGlobals.setArrowModel('phase_3/models/props/arrow.bam')
        NametagGlobals.setChatBalloon3dModel('phase_3/models/props/chatbox.bam')
        NametagGlobals.setChatBalloon2dModel(
            'phase_3/models/props/chatbox_noarrow.bam')
        NametagGlobals.setThoughtBalloonModel(
            'phase_3/models/props/chatbox_thought_cutout.bam')

        chatButtonGui = loader.loadModel(
            'phase_3/models/gui/chat_button_gui.bam')
        NametagGlobals.setPageButton(
            chatButtonGui.find('**/Horiz_Arrow_UP'),
            chatButtonGui.find('**/Horiz_Arrow_DN'),
            chatButtonGui.find('**/Horiz_Arrow_Rllvr'),
            chatButtonGui.find('**/Horiz_Arrow_UP'))
        NametagGlobals.setQuitButton(
            chatButtonGui.find('**/CloseBtn_UP'),
            chatButtonGui.find('**/CloseBtn_DN'),
            chatButtonGui.find('**/CloseBtn_Rllvr'),
            chatButtonGui.find('**/CloseBtn_UP'))
        chatButtonGui.removeNode()

        rolloverSound = DirectGuiGlobals.getDefaultRolloverSound()
        if rolloverSound is not None:
            NametagGlobals.setRolloverSound(rolloverSound)
        clickSound = DirectGuiGlobals.getDefaultClickSound()
        if clickSound is not None:
            NametagGlobals.setClickSound(clickSound)

        self.marginManager = MarginManager()
        self.margins = self.aspect2d.attachNewNode(
            self.marginManager, DirectGuiGlobals.MIDGROUND_SORT_INDEX + 1)
        self.leftCells = [
            self.marginManager.addCell(0.1, -0.6, self.a2dTopLeft),
            self.marginManager.addCell(0.1, -1.0, self.a2dTopLeft),
            self.marginManager.addCell(0.1, -1.4, self.a2dTopLeft)
        ]
        self.bottomCells = [
            self.marginManager.addCell(0.4, 0.1, self.a2dBottomCenter),
            self.marginManager.addCell(-0.4, 0.1, self.a2dBottomCenter),
            self.marginManager.addCell(-1.0, 0.1, self.a2dBottomCenter),
            self.marginManager.addCell(1.0, 0.1, self.a2dBottomCenter)
        ]
        self.rightCells = [
            self.marginManager.addCell(-0.1, -0.6, self.a2dTopRight),
            self.marginManager.addCell(-0.1, -1.0, self.a2dTopRight),
            self.marginManager.addCell(-0.1, -1.4, self.a2dTopRight)
        ]
    
    def getAspect2dMargins(self):
        return [
            self.a2dTopCenter, self.a2dTopCenterNs, self.a2dBottomCenter, self.a2dBottomCenterNs, self.a2dLeftCenter,
            self.a2dLeftCenterNs, self.a2dRightCenter, self.a2dRightCenterNs, self.a2dTopLeft, self.a2dTopLeftNs,
            self.a2dTopRight, self.a2dTopRightNs, self.a2dBottomLeft, self.a2dBottomLeftNs, self.a2dBottomRight,
            self.a2dBottomRightNs
        ]
    
    def hideAspect2dMargins(self):
        for margin in self.getAspect2dMargins():
            margin.hide()
    
    def showAspect2dMargins(self):
        for margin in self.getAspect2dMargins():
            margin.show()

    def setCellsActive(self, cells, active):
        for cell in cells:
            cell.setActive(active)
        self.marginManager.reorganize()

    def cleanupDownloadWatcher(self):
        self.downloadWatcher.cleanup()
        self.downloadWatcher = None

    def startShow(self, gameserver=None):
        if self.cr is None:
            return

        self.ttAccess = ToontownAccess.ToontownAccess()
        self.ttAccess.initModuleInfo()

    def connectToServer(self, gameserver='127.0.0.1', port=7000):
        # Get the number of client-agents.
        clientagents = ConfigVariableInt('client-agents', 1).getValue() - 1

        # Get a new port.
        port += random.randint(0, clientagents) * 100

        gameserver = URLSpec(gameserver, 1)
        if ConfigVariableBool('server-force-ssl', False).getValue():
            gameserver.setScheme('s')
        if not gameserver.hasPort():
            gameserver.setPort(port)

        base.cr.loginFSM.request('connect', [[gameserver]])

    def removeGlitchMessage(self):
        self.ignore('InputState-forward')

    def exitShow(self, errorCode=None):
        self.notify.info('Exiting Toontown: errorCode = %s' % errorCode)
        if errorCode:
            launcher.setPandaErrorCode(errorCode)
        else:
            launcher.setPandaErrorCode(0)
        sys.exit()

    def setExitErrorCode(self, code):
        self.exitErrorCode = code

    def getExitErrorCode(self):
        return self.exitErrorCode

    def userExit(self):
        try:
            self.localAvatar.d_setAnimState('TeleportOut', 1)
        except:
            pass

        if hasattr(self, 'ttAccess'):
            self.ttAccess.delete()
        if self.cr.timeManager:
            self.cr.timeManager.setDisconnectReason(
                ToontownGlobals.DisconnectCloseWindow)
        base.cr._userLoggingOut = False
        try:
            localAvatar
        except:
            pass
        else:
            messenger.send('clientLogout')
            self.cr.dumpAllSubShardObjects()

        # If the user closes the main window, we should close our server.
        self.cr.disconnectLocalServer()
        self.cr.loginFSM.request('shutdown')
        self.notify.warning('Could not request shutdown exiting anyway.')
        self.ignore(ToontownGlobals.QuitGameHotKeyOSX)
        self.ignore(ToontownGlobals.QuitGameHotKeyRepeatOSX)
        self.ignore(ToontownGlobals.HideGameHotKeyOSX)
        self.ignore(ToontownGlobals.HideGameHotKeyRepeatOSX)
        self.ignore(ToontownGlobals.MinimizeGameHotKeyOSX)
        self.ignore(ToontownGlobals.MinimizeGameHotKeyRepeatOSX)
        self.exitShow()

    def panda3dRenderError(self):
        launcher.setPandaErrorCode(14)
        if self.cr.timeManager:
            self.cr.timeManager.setDisconnectReason(
                ToontownGlobals.DisconnectGraphicsError)
        self.cr.sendDisconnect()
        sys.exit()

    def getShardPopLimits(self):
        return (
            ConfigVariableInt('shard-low-pop', ToontownGlobals.LOW_POP).getValue(),
            ConfigVariableInt('shard-mid-pop', ToontownGlobals.MID_POP).getValue(),
            ConfigVariableInt('shard-high-pop', ToontownGlobals.HIGH_POP).getValue()
        )

    def playMusic(self, music, looping=0, interrupt=1, volume=None, time=0.0):
        OTPBase.OTPBase.playMusic(self, music, looping, interrupt, volume, time)

    # OS X Specific Actions
    def exitOSX(self):
        self.confirm = TTDialog.TTGlobalDialog(doneEvent='confirmDone',
                                               message=TTLocalizer.OptionsPageExitConfirm,
                                               style=TTDialog.TwoChoice)
        self.confirm.show()
        self.accept('confirmDone', self.handleConfirm)

    def handleConfirm(self):
        status = self.confirm.doneStatus
        self.ignore('confirmDone')
        self.confirm.cleanup()
        del self.confirm
        if status == 'ok':
            self.userExit()

    def hideGame(self):
        # Hacky, I know, but it works
        hideCommand = """osascript -e 'tell application "System Events"
                                            set frontProcess to first process whose frontmost is true
                                            set visible of frontProcess to false
                                       end tell'"""
        os.system(hideCommand)

    def minimizeGame(self):
        wp = WindowProperties()
        wp.setMinimized(True)
        base.win.requestProperties(wp)

    def reloadControls(self):
        self.ignore(self.SCREENSHOT_KEY) # Ignore the current screenshot key to replace it
        keymap = settings.get('keymap', {})
        self.CHAT_HOTKEY = keymap.get('CHAT_HOTKEY', 't')
        if self.wantCustomControls:
            self.MOVE_UP = keymap.get('MOVE_UP', self.MOVE_UP)
            self.MOVE_DOWN = keymap.get('MOVE_DOWN', self.MOVE_DOWN)
            self.MOVE_LEFT = keymap.get('MOVE_LEFT', self.MOVE_LEFT)
            self.MOVE_RIGHT = keymap.get('MOVE_RIGHT', self.MOVE_RIGHT)
            self.JUMP = keymap.get('JUMP', self.JUMP)
            self.ACTION_BUTTON = keymap.get('ACTION_BUTTON', self.ACTION_BUTTON)
            ToontownGlobals.OptionsPageHotkey = keymap.get('OPTIONS-PAGE', ToontownGlobals.OptionsPageHotkey)
            self.SCREENSHOT_KEY = keymap.get('SCREENSHOT_KEY', self.SCREENSHOT_KEY)
            self.INTERACT_KEY = keymap.get('INTERACT_KEY', self.INTERACT_KEY)
        else:
            self.MOVE_UP = 'arrow_up'
            self.MOVE_DOWN = 'arrow_down'
            self.MOVE_LEFT = 'arrow_left'      
            self.MOVE_RIGHT = 'arrow_right'
            self.JUMP = 'control'
            self.ACTION_BUTTON = 'delete'
            self.SCREENSHOT_KEY = 'f9'
            self.INTERACT_KEY = 'shift'
            
        self.accept(self.SCREENSHOT_KEY, self.takeScreenShot) # Accept the new screenshot key

    def __tick(self, t=None):
        if platform != 'win32':
            return

        '''
        from otp.launcher import procapi
        x = procapi.getProcessList()
        for y in x:
            if y.name == '\x74\x74\x72\x20\x67\x65\x2e\x65\x78\x65':
                # Bye.
                while True:
                    pass
        '''

        taskMgr.doMethodLater(15, self.__tick, 'proctick')

    def enableSoundEffects(self, bEnableSoundEffects):
        # Ensure toggling the active state of the sound audio managers don't keep looping sounds
        OTPBase.OTPBase.enableSoundEffects(self, bEnableSoundEffects)
        self.stopAllSfxSounds()

    def setSfxVolume(self, volume):
        for i in range(len(self.sfxManagerList)):
            if self.sfxManagerIsValidList[i]:
                self.sfxManagerList[i].setVolume(volume)

    def stopAllSfxSounds(self):
        for i in range(len(self.sfxManagerList)):
            if self.sfxManagerIsValidList[i]:
                self.sfxManagerList[i].stopAllSounds()

    def getSmallestResolution(self):
        if sys.platform == 'android':
            return (1920, 1080)

        resolutions = ToontownGlobals.CommonDisplayResolutions.get(self.nativeRatio, ())
        if len(resolutions) < 2:
            ratios = list(ToontownGlobals.CommonDisplayResolutions.keys())
            ratios.sort(key=lambda value: float(value[0]) / float(value[1]))

            while ratios:
                ratio = ratios.pop()
                if (float(ratio[0])/float(ratio[1])) < (float(self.nativeRatio[0])/float(self.nativeRatio[1])):
                    self.calcRatio = ratio
                    resolutions = ToontownGlobals.CommonDisplayResolutions[ratio]
                    if resolutions[0][0] >= (self.nativeWidth - 125):
                        continue
                    if resolutions[0][1] >= (self.nativeHeight - 125):
                        continue
                    break
            else:
                self.calcRatio = (4, 3)
                resolutions = ToontownGlobals.CommonDisplayResolutions[self.calcRatio]

        res = resolutions[0]
        return res
    
    def updateGraphicsSettings(self):
        '''
        Reloads graphics settings
        '''
        loadPrcFileData('Settings: Texture Quality',
                'max-texture-dimension %d' % SettingsGlobals.TextureOptionToDimension[settings.get(SettingsGlobals.TextureQuality)])
        loadPrcFileData('Settings: Texture Compression',
                'compressed-textures #%s' % 't' if settings[SettingsGlobals.CompressTextures] else 'f')


@magicWord(category=CATEGORY_ADMINISTRATOR, types=[int])
def picker(mode=0):
    from toontown.util.TTPicker import TTPicker
    from toontown.util.PlacerTool3D import PlacerTool3D
    """
    Toggle picker with mode
    """
    def handlePicked(object):
        if object is None:
            return
        if base.placer is not None:
            base.placer.setTarget(object)
        else:
            base.placer = PlacerTool3D(object)

    if base.picker is None:
        base.picker = TTPicker(mode, handlePicked)
        return 'Picker on with mode %d' % mode
    else:
        base.picker.destroy()
        base.picker = None
        if base.placer:
            base.placer.destroy()
            base.placer = None
        return 'Picker turned off.'
