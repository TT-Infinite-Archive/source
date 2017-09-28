from toontown.toontowngui.TTLabel import TTLabel
from direct.gui.DirectGui import DirectFrame, DirectEntry
from direct.directnotify.DirectNotifyGlobal import directNotify
from toontown.toonbase import TTLocalizer, ColorGlobals, EventGlobals
from toontown.mainmenu import MainMenuGlobals
from toontown.makeatoon.MakeAToonGUI import MATShuffleButton
from toontown.util import PlacerTool3D
from toontown.toontowngui.TTDialog import TTDialog
from otp.otpgui import OTPDialog
import hashlib


class LoginScreen(DirectFrame):
    notify = directNotify.newCategory('LoginScreen')

    def __init__(self, parent=base.aspect2d):
        DirectFrame.__init__(self, parent)
        self.errorLabel = TTLabel(
            parent=self,
            text='',
            pos=(0, 0, -0.05),
            text_fg=ColorGlobals.CRed,
            text_size=TTLabel.GiantSize,
            text_wordwrap=25
        )

        self.usernameLabel = TTLabel(
            parent=self,
            text=TTLocalizer.Username,
            pos=(0, 0, -0.18),
            **MainMenuGlobals.LABEL_PROPERTIES
        )

        self.passwordLabel = TTLabel(
            parent=self,
            text=TTLocalizer.Password,
            pos=(0, 0, -0.48),
            **MainMenuGlobals.LABEL_PROPERTIES
        )

        self.usernameInput = DirectEntry(
            parent=self,
            pos=(0, 0, -0.30),
            width=10.5,
            **MainMenuGlobals.ENTRY_PROPERTIES
        )

        self.passwordInput = DirectEntry(
            parent=self,
            pos=(0, 0, -0.60),
            width=10.5,
            obscured=True,
            **MainMenuGlobals.ENTRY_PROPERTIES
        )

        self.logInButton = MATShuffleButton(
            parent=self,
            pos=(0, 0, -0.8),
            text=TTLocalizer.LoginScreenLogin,
            command=self.doLogin,
            **MainMenuGlobals.BUTTON_PROPERTIES
        )

        self.loginDialog = None

    def destroy(self):
        if self.loginDialog:
            self.loginDialog.cleanup()
            self.loginDialog = None
        taskMgr.remove('clearLoginErrorTask')
        DirectFrame.destroy(self)

    def setErrorMessage(self, text):
        self.errorLabel['text'] = text

    def doLogin(self):
        # Do login magic here
        base.cr.sendSetAvatarIdMsg(0)
        self.acceptOnce(EventGlobals.LoginError, self.__handleLoginError)
        self.acceptOnce(EventGlobals.LoginDone, self.__handleLoginSuccess)
        password = hashlib.sha512(self.passwordInput.get()).hexdigest()
        base.cr.csm.performLogin(EventGlobals.LoginDone, self.usernameInput.get(), password)
        base.cr.waitForDatabaseTimeout(requestName='WaitOnCSMLoginResponse')
        self.showLoginDialog()

    def showLoginDialog(self):
        if self.loginDialog is not None:
            self.loginDialog.cleanup()
            self.loginDialog = None
        self.loginDialog = TTDialog(
            text=TTLocalizer.LoggingIn,
            dialogName='loggingIn',
            buttonTextList=[TTLocalizer.lCancel],
            style=OTPDialog.CancelOnly,
            command=self.__handleLoginCancel
        )

    def hideLoginDialog(self):
        if self.loginDialog:
            self.loginDialog.cleanup()
            self.loginDialog = None

    def __handleLoginCancel(self, e=None):
        self.hideLoginDialog()
        base.cr.cleanupWaitingForDatabase()
        self.ignore(EventGlobals.LoginDone)
        self.ignore(EventGlobals.LoginError)

    def __handleLoginError(self, errorCode):
        self.hideLoginDialog()
        self.ignore(EventGlobals.LoginDone)
        base.cr.cleanupWaitingForDatabase()
        self.setErrorMessage(TTLocalizer.LoginError[errorCode])
        taskMgr.remove('clearLoginErrorTask')
        taskMgr.doMethodLater(5, self.setErrorMessage, 'clearLoginErrorTask', extraArgs=[''])

    def __handleLoginSuccess(self, doneStatus):
        self.ignore(EventGlobals.LoginError)
        base.cr.cleanupWaitingForDatabase()
        base.cr.handleLoginDone(doneStatus)
