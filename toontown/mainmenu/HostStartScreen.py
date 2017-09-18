from direct.gui.DirectGui import DirectFrame, DirectLabel
from toontown.toonbase import ToontownGlobals, TTLocalizer, EventGlobals
from toontown.makeatoon.MakeAToonGUI import MATShuffleButton
from toontown.toonbase import ServerSettingsGlobals
from panda3d.core import Point3
from direct.interval.FunctionInterval import Func, Wait
from direct.interval.MetaInterval import Sequence, Parallel
from toontown.mainmenu import MainMenuGlobals


class HostStartScreen(DirectFrame):

    def __init__(self, mainMenu):
        DirectFrame.__init__(self, mainMenu)

        self.mainMenu = mainMenu

        CAMSTARTPOS = (-359.5, -204, 3.7)
        CAMENDPOS = (-336.35, -197.5, 4.8)

        self.label = DirectLabel(
            parent=self,
            relief=None,
            text='',
            text_fg=(0, 0, 0, 1),
            text_font=ToontownGlobals.getToonFont(),
            text_scale=0.1,
            text_wordwrap=25,
        )
        self.label.hide()

        self.backButton = MATShuffleButton(
            parent=self,
            pos=(0, 0, -0.45),
            text=TTLocalizer.OptionsGoBack,
            command=lambda: self.mainMenu.request('HostScreenAfterFail'),
            **MainMenuGlobals.BUTTON_PROPERTIES_2
        )
        self.backButton.hide()

        self.zoomIntoScreen = camera.posInterval(1, Point3(CAMENDPOS),
                           startPos=Point3(CAMSTARTPOS), blendType='easeIn')

        self.zoomOutOfScreen = camera.posInterval(1, Point3(CAMSTARTPOS),
                           startPos=Point3(CAMENDPOS), blendType='easeOut')

        self.accept(EventGlobals.LocalServerStarterProcess, self.__handleServerStarterStart)
        self.accept(EventGlobals.LocalServerStarterProcess, self.__handleServerStarterProcess)
        self.accept(EventGlobals.LocalServerStarterFailed, self.__handleServerStarterFailed)
        self.accept(EventGlobals.LocalServerStarterFailedRunning, self.__handleServerStarterFailedRunning)
        self.accept(EventGlobals.LocalServerStarterDone, self.__handleServerStarterDone)

    def enter(self):
        if serverSettings[ServerSettingsGlobals.WantSinglePlayer]:
            base.isSinglePlayer = True
        else:
            base.isSinglePlayer = False
        base.isHosting = True

        Sequence(self.zoomIntoScreen, Func(self.label.show), Func(base.cr.localServerStarter.request, 'Start')).start()

    def exitBackToHostScreen(self):
        base.isHosting = False
        self.backButton.hide()
        self.label.hide()
        Sequence(self.zoomOutOfScreen).start()

    def __handleServerStarterStart(self):
        self.label['text'] = TTLocalizer.LocalServerStarting

    def __handleServerStarterProcess(self, processName):
        if __debug__:
            self.label['text'] = TTLocalizer.StartingServerDev % processName
        else:
            self.label['text'] = TTLocalizer.StartingServerLive

    def __handleServerStarterFailed(self, processName):
        self.label['text'] = TTLocalizer.StartingFailed % processName
        self.backButton.show()
        self.label.show()

    def __handleServerStarterFailedRunning(self):
        self.label['text'] = TTLocalizer.LocalServerRunningAlready
        self.backButton.show()
        self.label.show()

    def __handleServerStarterDone(self):
        self.label['text'] = TTLocalizer.LocalServerDone
        base.cr.loginFSM.request('serverMenu')