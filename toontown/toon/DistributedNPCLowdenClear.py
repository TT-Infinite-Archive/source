from direct.distributed.ClockDelta import *
from direct.gui.DirectGui import *

from .DistributedNPCToonBase import *
from toontown.chat.ChatGlobals import *
from toontown.toonbase import TTLocalizer, ToontownGlobals, EventGlobals
from toontown.guilds.IconSelector import IconSelectionDialog
from toontown.guilds import GuildGlobals
from toontown.toon import GuildMasterGlobals
from toontown.toontowngui import TTDialog
from toontown.toontowngui.ConfirmDialog import ConfirmDialog
import random


class DistributedNPCLowdenClear(DistributedNPCToonBase):
    notify = directNotify.newCategory('DistributedNPCLowdenClear')

    def __init__(self, cr):
        DistributedNPCToonBase.__init__(self, cr)
        self.timestamp = 0
        self.dialogIndex = 0
        self.textField = None
        self.textBox = None
        self.submitButton = None
        self.confirmationDialog = None
        self.moneyDisplay = None
        self.cancel = None
        self.costDisplay = None
        self.iconSelector = None

        self.nameButtonModels = loader.loadModel('phase_3/models/gui/tt_m_gui_mat_nameShop')
        self.squareUp = self.nameButtonModels.find('**/tt_t_gui_mat_namePanelSquareUp')
        self.squareDown = self.nameButtonModels.find('**/tt_t_gui_mat_namePanelSquareDown')
        self.squareHover = self.nameButtonModels.find('**/tt_t_gui_mat_namePanelSquareHover')

    def announceGenerate(self):
        DistributedNPCToonBase.announceGenerate(self)

        self.putOnSuit('mb', False)

    def disable(self):
        self.ignoreAll()
        taskMgr.remove(self.uniqueName('lerpCamera'))
        self.av = None
        base.localAvatar.posCamera(0, 0)

        DistributedNPCToonBase.disable(self)

    def resetClerk(self):
        self.ignoreAll()
        taskMgr.remove(self.uniqueName('lerpCamera'))
        self.startLookAround()
        self.detectAvatars()

    def handleCollisionSphereEnter(self, collEntry):
        if base.cr.guildManager.guild is not None and not base.cr.guildManager.guild.rejected:
            # We're in a guild, no need to request dialog
            base.cr.playGame.getPlace().setState('purchase')
            self.setMovie(GuildMasterGlobals.GUILD_MOVIE_CONVERSE, base.localAvatar.doId)
        else:
            self.sendAvatarEnter()
            self.nametag3d.setDepthTest(0)
            base.cr.playGame.getPlace().setState('purchase')
            self.nametag3d.setBin('fixed', 0)

    def freeAvatar(self):
        DistributedNPCToonBase.freeAvatar(self)

        self.showNametag2d()
        self.nametag3d.setDepthTest(1)

    def sendAvatarEnter(self):
        if base.cr.guildManager.guild is None:
            self.sendUpdate('avatarEnter', [0])
        else:
            rejected = base.cr.guildManager.guild.rejected
            self.sendUpdate('avatarEnter', [rejected])

    def setMovie(self, mode, avId, timestamp=0):
        self.notify.debug('Setting movie %d for avatar %d with timestamp %d' % (mode, avId, timestamp))
        isLocalToon = avId == base.localAvatar.doId

        if isLocalToon:
            self.cleanupGuildNameTextField()
            self.cleanupGuildIconSelector()
            self.cleanupDialogConfirmation()

        if mode == GuildMasterGlobals.GUILD_MOVIE_START:
            if isLocalToon:
                self.setupCamera(mode)
                self.openDialogConfirmation()
            self.clearChat()
            self.setChatAbsolute(GuildMasterGlobals.GUILD_MOVIE_TO_DIALOG[mode], CFSpeech | CFTimeout)
        elif mode == GuildMasterGlobals.GUILD_MOVIE_PROMPT_NAME:
            if isLocalToon:
                self.openGuildNameTextField()
            self.clearChat()
            self.setChatAbsolute(GuildMasterGlobals.GUILD_MOVIE_TO_DIALOG[mode] % {'cost': GuildMasterGlobals.GUILD_COST}, CFSpeech | CFTimeout)
        elif mode == GuildMasterGlobals.GUILD_MOVIE_PROMPT_ICON:
            if isLocalToon:
                self.openGuildIconSelector()
            self.clearChat()
            self.setChatAbsolute(GuildMasterGlobals.GUILD_MOVIE_TO_DIALOG[mode], CFSpeech | CFTimeout)
        elif mode == GuildMasterGlobals.GUILD_MOVIE_RENAME:
            if isLocalToon:
                self.openDialogConfirmation()
            self.clearChat()
            self.setChatAbsolute(GuildMasterGlobals.GUILD_MOVIE_TO_DIALOG[mode], CFSpeech | CFTimeout)
        elif mode == GuildMasterGlobals.GUILD_MOVIE_RENAME_NAME:
            if isLocalToon:
                self.openGuildNameTextField()
            self.clearChat()
            self.setChatAbsolute(GuildMasterGlobals.GUILD_MOVIE_TO_DIALOG[mode], CFSpeech | CFTimeout)
        elif mode == GuildMasterGlobals.GUILD_MOVIE_DONE:
            if isLocalToon:
                self.freeAvatar()
            self.clearChat()
            self.setChatAbsolute(GuildMasterGlobals.GUILD_MOVIE_TO_DIALOG[mode], CFSpeech | CFTimeout)
            self.resetClerk()
        elif mode == GuildMasterGlobals.GUILD_MOVIE_DENY:
            if isLocalToon:
                self.freeAvatar()
            self.clearChat()
            self.setChatAbsolute(GuildMasterGlobals.GUILD_MOVIE_TO_DIALOG[mode], CFSpeech | CFTimeout)
        elif mode == GuildMasterGlobals.GUILD_MOVIE_CLEAR:
            if not avId:
                self.setChatAbsolute('', CFSpeech | CFTimeout)
            if isLocalToon:
                self.freeAvatar()
            self.resetClerk()
        elif mode == GuildMasterGlobals.GUILD_MOVIE_TIMEOUT:
            if isLocalToon:
                self.freeAvatar()
            self.resetClerk()
            self.setChatAbsolute(TTLocalizer.STOREOWNER_TOOKTOOLONG, CFSpeech | CFTimeout)
        elif mode == GuildMasterGlobals.GUILD_MOVIE_REJECT:
            if isLocalToon:
                base.localAvatar.posCamera(0, 0)
                base.cr.playGame.getPlace().setState('walk')
        elif mode == GuildMasterGlobals.GUILD_MOVIE_CONVERSE:
            if isLocalToon:
                base.localAvatar.posCamera(0, 0)
                base.cr.playGame.getPlace().setState('walk')
                self.setChatAbsolute(random.choice(TTLocalizer.GUILDMASTER_CONVERSE), CFSpeech | CFTimeout)
        elif mode == GuildMasterGlobals.GUILD_MOVIE_REJECT_NO_BEANS:
            if isLocalToon:
                base.localAvatar.posCamera(0, 0)
                base.cr.playGame.getPlace().setState('walk')
                self.setChatAbsolute(GuildMasterGlobals.GUILD_MOVIE_TO_DIALOG[mode] % GuildMasterGlobals.GUILD_COST, CFSpeech | CFTimeout)

    def setupCamera(self, mode):
        base.camera.wrtReparentTo(render)
        if mode == GuildMasterGlobals.GUILD_MOVIE_START:
            base.camera.posQuatInterval(1, (5, 9, self.getHeight() - 0.5), (155, -2, 0), other=self, blendType='easeOut').start()
        else:
            base.camera.posQuatInterval(1, (-5, 9, self.getHeight() - 0.5), (-150, -2, 0), other=self, blendType='easeOut').start()

    # - Icon Selector

    def openGuildIconSelector(self):
        self.notify.debug('Prompting the user for an icon to represent their guild')
        self.cleanupDialogConfirmation()
        self.cleanupGuildNameTextField()
        possibleIcons = GuildGlobals.GUILD_POSSIBLE_ICONS
        self.iconSelector = IconSelectionDialog(aspect2d, TTLocalizer.GuildIconSelectorDialogTitle, possibleIcons, color=(0.6, 0.63, 1.0, 1.0), command=self.__handleSelectIcon)

    def cleanupGuildIconSelector(self):
        if self.iconSelector is not None:
            self.iconSelector.destroy()
            self.iconSelector = None

    def __handleSelectIcon(self, iconId):
        self.d_requestDialog(GuildMasterGlobals.GUILD_MOVIE_DONE)
        base.cr.guildManager.d_requestCreateGuild(self.guildName, iconId)

    # - Yes/No Selector

    def openDialogConfirmation(self):
        self.notify.debug('Asking the user if they want to make a guild')
        self.cleanupDialogConfirmation()
        self.confirmationDialog = ConfirmDialog(commands=(self.__handleYes, self.__handleNo))

    def cleanupDialogConfirmation(self):
        if self.confirmationDialog is not None:
            self.confirmationDialog.destroy()
            self.confirmationDialog = None

    def __handleYes(self, e=None):
        self.confirmationDialog = None
        if base.cr.guildManager.guild is None:
            self.d_requestDialog(GuildMasterGlobals.GUILD_MOVIE_PROMPT_NAME)
        elif base.cr.guildManager.guild.rejected:
            self.d_requestDialog(GuildMasterGlobals.GUILD_MOVIE_RENAME_NAME)

    def __handleNo(self, e=None):
        self.confirmationDialog = None
        self.d_rejectNextDialog()


    # - Name Entry

    def openGuildNameTextField(self):
        self.notify.debug('Prompting the user a name for their guild')
        self.cleanupGuildNameTextField()
        self.accept(base.localAvatar.uniqueName('moneyChange'), self.__moneyChange)
        localAvatar.chatMgr.fsm.request('otherDialog')
        gui = loader.loadModel('phase_3.5/models/gui/tt_m_gui_sbk_codeRedemptionGui')
        textBoxGui = gui.find('**/tt_t_gui_sbk_cdrCodeBox')
        submitButtonGui = loader.loadModel('phase_3/models/gui/quit_button')
        submitButtonImage = (submitButtonGui.find('**/QuitBtn_UP'), submitButtonGui.find('**/QuitBtn_DN'), submitButtonGui.find('**/QuitBtn_RLVR'), submitButtonGui.find('**/QuitBtn_UP'))
        jarGui = loader.loadModel('phase_3.5/models/gui/jar_gui')
        buttons = loader.loadModel('phase_3/models/gui/dialog_box_buttons_gui')
        closeButton = (buttons.find('**/CloseBtn_UP'), buttons.find('**/CloseBtn_DN'), buttons.find('**/CloseBtn_Rllvr'))

        self.textBox = DirectFrame(parent=aspect2d, relief=None, image=textBoxGui, pos=(0.0, 0.0, -0.5), scale=1.5)
        self.textField = DirectEntry(parent=self.textBox,
                                     relief=None,
                                     scale=0.05,
                                     borderWidth=(0.0,0.0),
                                     frameColor=((1, 1, 1, 1), (1, 1, 1, 1), (0.5, 0.5, 0.5, 0.5)),
                                     entryFont=ToontownGlobals.getToonFont(),
                                     width=10,
                                     numLines=1,
                                     focus=1,
                                     cursorKeys=1,
                                     text_align=TextNode.ACenter,
                                     autoCapitalize=0,
                                     command=self.__typedAName)
        self.textField.bind(DGG.TYPE, self.typeCallback)

        self.submitButton = DirectButton(parent=self.textBox,
                                         relief=None,
                                         image=submitButtonImage,
                                         scale=(1.5, 1.0, 2.0),
                                         image3_color=Vec4(0.5, 0.5, 0.5, 0.5),
                                         image_scale=0.5,
                                         state=DGG.NORMAL,
                                         text=TTLocalizer.NameShopSubmitButton,
                                         text_scale=0.03,
                                         text_font = ToontownGlobals.getToonFont(),
                                         text_align=TextNode.ACenter,
                                         text_pos=(0.0, -0.01),
                                         text3_fg=(0.5, 0.5, 0.5, 0.75),
                                         textMayChange=0,
                                         pos=(0.3, 0, -0.075),
                                         command=self.__typedAName)

        self.moneyDisplay = DirectLabel(parent=self.textBox,
                                        relief=None,
                                        pos=(-0.35, 0, -0.075),
                                        scale=0.5,
                                        text=str(base.localAvatar.getMoney()),
                                        text_scale=0.18,
                                        text_fg=(0.95, 0.95, 0, 1),
                                        text_shadow=(0, 0, 0, 1),
                                        text_pos=(0, -0.1, 0),
                                        image=jarGui.find('**/Jar'),
                                        text_font=ToontownGlobals.getSignFont())
        self.cancel = DirectButton(parent=self.textBox,
                                   relief=None,
                                   pos=(0.375, 0, 0.08),
                                   state=DGG.NORMAL,
                                   image=closeButton,
                                   image_scale=(0.8, 1, 0.8),
                                   command=self.d_rejectNextDialog)
        self.costDisplay = DirectLabel(parent=self.textBox,
                                       relief=None,
                                       pos=(0.3, 0, -0.175),
                                       text=str(GuildMasterGlobals.GUILD_COST) + ' ' + TTLocalizer.Jellybeans,
                                       text_scale=0.05,
                                       text_fg=(1, 0.1, 0.1, 1),
                                       text_shadow=(0, 0, 0, 1),
                                       text_font=ToontownGlobals.getToonFont())
        self.costDisplay.hide()

        if base.cr.guildManager.guild is not None and base.cr.guildManager.guild.rejected:
            # This guild was rejected, so it doesnt cost to rename
            self.costDisplay['text'] = TTLocalizer.GuildRenameCost

        self.submitButton.bind(DGG.WITHIN, self.showCost)
        self.submitButton.bind(DGG.WITHOUT, self.hideCost)

        # This allows the text box to handle mouse events
        self.textBox.guiItem.setActive(True)
        self.textBox.bind(DGG.WITHIN, self.focusField)

        buttons.removeNode()
        gui.removeNode()
        submitButtonGui.removeNode()
        jarGui.removeNode()

    def cleanupGuildNameTextField(self):
        self.ignore(base.localAvatar.uniqueName('moneyChange'))
        if self.costDisplay is not None:
            self.costDisplay.destroy()
            self.costDisplay = None
        if self.cancel is not None:
            self.cancel.destroy()
            self.cancel = None
        if self.moneyDisplay is not None:
            self.moneyDisplay.destroy()
            self.moneyDisplay = None
        if self.submitButton is not None:
            self.submitButton.destroy()
            self.submitButton = None
        if self.textField is not None:
            self.textField.destroy()
            self.textField = None
        if self.textBox is not None:
            self.textBox.destroy()
            self.textBox = None
        localAvatar.chatMgr.fsm.request('mainMenu')

    def typeCallback(self, e):
        messenger.send(EventGlobals.WakeUp)
        if self.textField is None:
            return
        name = self.textField.get()
        sentence = name.split(' ')
        newName = ''
        # Capitalize the first letter in each word by force
        for index, word in enumerate(sentence):
            if len(word) == 0:
                continue
            newName += word[0].capitalize()
            if len(word) > 1:
                newName += word[1:]
            if index != len(sentence) - 1:
                newName += ' '
        if name[-1] == ' ':
            newName += ' '
        self.textField.enterText(newName)

    def __typedAName(self, *args):
        invalidNames = ('', ' ')
        self.notify.debug('__typedAName')
        self.textField['focus'] = 0
        name = self.textField.get()
        name = TextEncoder().decodeText(name)
        name = name.strip()
        name = TextEncoder().encodeWtext(name)
        sentence = name.split(' ')
        name = ''
        if len(sentence) == 0:
            self.reject = TTDialog.TTGlobalDialog(doneEvent='guildNameRejectDone', message=TTLocalizer.GuildNameInvalid, style=TTDialog.Acknowledge)
            self.reject.show()
            self.accept('guildNameRejectDone', self.__handleRejectDone)
            return

        # Capitalize the first letter in each word by force
        for index, word in enumerate(sentence):
            if len(word) == 0:
                continue
            name += word[0].capitalize()
            if len(word) > 1:
                name += word[1:]
            if index != (len(sentence) - 1):
                name += ' '

        if name in invalidNames:
            self.reject = TTDialog.TTGlobalDialog(doneEvent='guildNameRejectDone', message=TTLocalizer.GuildNameInvalid, style=TTDialog.Acknowledge)
            self.reject.show()
            self.accept('guildNameRejectDone', self.__handleRejectDone)
            return
        self.guildName = name
        self.textField.enterText(name)
        self.handleCheckName(name)

    def handleCheckName(self, guildName):
        self.notify.debug('Asking uberdog if %s is ok...' % guildName)
        # Ask the server if our name is a-OK
        self.checkName = TTDialog.TTGlobalDialog(message=TTLocalizer.GuildCheckingName % guildName)
        self.checkName.show()
        self.accept(EventGlobals.GuildCheckNameResp, self.handleCheckNameResponse)
        base.cr.guildManager.d_requestCheckName(guildName)

    def handleCheckNameResponse(self, valid):
        self.notify.debug('Is that name valid? Uberdog says: %s' % valid)
        self.ignore(EventGlobals.GuildCheckNameResp)
        self.checkName.cleanup()
        del self.checkName
        if not valid:
            # This wasn't a valid name, do not proceed
            self.reject = TTDialog.TTGlobalDialog(doneEvent='guildNameRejectDone', message=TTLocalizer.GuildNameInvalid, style=TTDialog.Acknowledge)
            self.reject.show()
            self.accept('guildNameRejectDone', self.__handleRejectDone)
            return

        # Valid name, proceed
        if base.cr.guildManager.guild is None:
            # We don't have a guild, ask for an icon selector
            self.d_requestDialog(GuildMasterGlobals.GUILD_MOVIE_PROMPT_ICON)
        elif base.cr.guildManager.guild.rejected:
            # We have a guild and it was rejected, we don't need to re-select an icon
            self.d_requestDialog(GuildMasterGlobals.GUILD_MOVIE_DONE)
            base.cr.guildManager.guild.rejected = False
            base.cr.guildManager.d_requestRenameGuild(self.guildName)
        self.cleanupGuildNameTextField()

    def showCost(self, event=None):
        self.costDisplay.show()

    def hideCost(self, event=None):
        self.costDisplay.hide()

    def focusField(self, event=None):
        localAvatar.chatMgr.fsm.request('otherDialog')

    def __moneyChange(self, money):
        self.moneyDisplay['text'] = str(money)

    def __handleRejectDone(self):
        self.ignore('guildNameRejectDone')
        self.reject.cleanup()
        del self.reject

    # Client Requests

    def d_requestDialog(self, dialogIndex):
        self.sendUpdate('requestDialog', [dialogIndex])

    def d_rejectNextDialog(self):
        self.sendUpdate('rejectNextDialog', [])
