from pandac.PandaModules import *
from toontown.toonbase import ToontownGlobals
import AvatarChoice
from direct.fsm import ClassicFSM, State, StateData
from toontown.launcher import DownloadForceAcknowledge
from direct.gui.DirectGui import *
from toontown.toonbase import TTLocalizer
from direct.directnotify import DirectNotifyGlobal
from direct.interval.IntervalGlobal import *
import random
from toontown.toontowngui import TTDialog
from toontown.toontowngui.TTLabel import TTLabel
from toontown.toonbase import ColorGlobals

MAX_AVATARS = 6
POSITIONS = (Vec3(-0.860167, 0, 0.359333),
             Vec3(0, 0, 0.346533),
             Vec3(0.848, 0, 0.3293),
             Vec3(-0.863554, 0, -0.445659),
             Vec3(0.00799999, 0, -0.5481),
             Vec3(0.894907, 0, -0.445659))
COLORS = (Vec4(0.917, 0.164, 0.164, 1),
          Vec4(0.152, 0.75, 0.258, 1),
          Vec4(0.598, 0.402, 0.875, 1),
          Vec4(0.133, 0.59, 0.977, 1),
          Vec4(0.895, 0.348, 0.602, 1),
          Vec4(0.977, 0.816, 0.133, 1))
chooser_notify = DirectNotifyGlobal.directNotify.newCategory('AvatarChooser')

PreloadModels = (
    'phase_3/models/gui/pick_a_toon_gui.bam',
    'phase_3/models/gui/quit_button.bam',
    'phase_3/models/gui/tt_m_gui_pat_mainGui.bam'
)


def preload():
    print 'Preloading the Pick-A-Toon UI...'

    for modelPath in PreloadModels:
        preloader.loadModel(modelPath)


def unload():
    for modelPath in PreloadModels:
        preloader.unloadModel(modelPath)


class AvatarChooser(StateData.StateData):
    def __init__(self, avatarList, parentFSM, doneEvent):
        StateData.StateData.__init__(self, doneEvent)
        self.choice = None
        base.isLoggingOut = None
        self.avatarList = avatarList
        self.fsm = ClassicFSM.ClassicFSM('AvatarChooser',
                                         [State.State('Choose', self.enterChoose, self.exitChoose, ['CheckDownload']),
                                          State.State('CheckDownload', self.enterCheckDownload, self.exitCheckDownload,
                                                      ['Choose'])], 'Choose', 'Choose')
        self.fsm.enterInitialState()
        self.parentFSM = parentFSM
        self.parentFSM.getCurrentState().addChild(self.fsm)

    def enter(self):
        if not self.isLoaded:
            self.load()
        base.disableMouse()
        self.title.reparentTo(aspect2d)
        self.userNameLabel.reparentTo(hidden)
        # if base.cr.loginInterface.supportsRelogin():
        # self.logoutButton.show()
        self.pickAToonBG.setBin('background', 1)
        self.pickAToonBG.reparentTo(aspect2d)
        base.setBackgroundColor(Vec4(0.145, 0.368, 0.78, 1))
        choice = base.config.GetInt('auto-avatar-choice', -1)
        for panel in self.panelList:
            panel.show()
            self.accept(panel.doneEvent, self.__handlePanelDone)
            if panel.position == choice and panel.mode == AvatarChoice.AvatarChoice.MODE_CHOOSE:
                self.__handlePanelDone('chose', panelChoice=choice)

    def exit(self):
        if self.isLoaded == 0:
            return None
        for panel in self.panelList:
            panel.hide()

        self.ignoreAll()
        self.title.reparentTo(hidden)
        self.logoutButton.hide()
        self.pickAToonBG.reparentTo(hidden)
        base.setBackgroundColor(ToontownGlobals.DefaultBackgroundColor)
        base.ignore('confirmBack')

    def load(self):
        if self.isLoaded:
            return None

        gui = preloader.getModel('phase_3/models/gui/pick_a_toon_gui.bam')
        if gui is not None:
            gui2 = preloader.getModel('phase_3/models/gui/quit_button.bam')
            newGui = preloader.getModel(
                'phase_3/models/gui/tt_m_gui_pat_mainGui.bam')
        else:
            gui = loader.loadModel('phase_3/models/gui/pick_a_toon_gui.bam')
            gui2 = loader.loadModel('phase_3/models/gui/quit_button.bam')
            newGui = loader.loadModel(
                'phase_3/models/gui/tt_m_gui_pat_mainGui.bam')

        self.pickAToonBG = newGui.find('**/tt_t_gui_pat_background').copyTo(hidden)
        self.pickAToonBG.setPos(0.0, 2.73, 0.0)
        self.pickAToonBG.setScale(1.5, 1, 2)

        self.title = OnscreenText(
            TTLocalizer.AvatarChooserPickAToon, scale=TTLocalizer.ACtitle,
            parent=hidden, font=ToontownGlobals.getSignFont(),
            fg=(1, 0.9, 0.1, 1), pos=(0.0, 0.82))

        self.userNameLabel = TTLabel(
            parent=hidden,
            pos=(1.45, 0, 0.9),
            text=TTLocalizer.HomeScreenLoggedIn,
            text_fg=ColorGlobals.CDefault,
            text_font=ToontownGlobals.getToonFont(),
            text_size=TTLabel.MediumSize,
            text_wordwrap=25
        )

        quitHover = gui.find('**/QuitBtn_RLVR')
        self.logoutButton = DirectButton(
            image=(quitHover, quitHover, quitHover), relief=None,
            text='Log Out',
            text_font=ToontownGlobals.getSignFont(),
            text_fg=(0.977, 0.816, 0.133, 1),
            text_pos=TTLocalizer.AClogOutTextPos,
            text_scale=TTLocalizer.AClogOutButtonScale, image_scale=1,
            image1_scale=1.05, image2_scale=1.05, scale=1.05,
            pos=(0.25, 0, 0.075), command=self.__back)
        self.logoutButton.reparentTo(base.a2dBottomLeft)

        """
        self.logoutButton = DirectButton(
            relief=None, image=(quitHover, quitHover, quitHover),
            text=TTLocalizer.OptionsPageLogout,
            text_font=ToontownGlobals.getSignFont(),
            text_fg=(0.977, 0.816, 0.133, 1),
            text_scale=TTLocalizer.AClogoutButton, text_pos=(0, -0.035),
            pos=(0.40, 0, 0.05), image_scale=1.15, image1_scale=1.15,
            image2_scale=1.18, scale=0.5,
            command=self.__handleLogoutWithoutConfirm)
        self.logoutButton.reparentTo(base.a2dBottomLeft)
        self.logoutButton.hide()
        """

        self.panelList = []
        used_position_indexs = []
        for av in self.avatarList:
            panel = AvatarChoice.AvatarChoice(av, position=av.position)
            panel.setPos(POSITIONS[av.position])
            used_position_indexs.append(av.position)
            self.panelList.append(panel)

        for panelNum in xrange(0, MAX_AVATARS):
            if panelNum not in used_position_indexs:
                panel = AvatarChoice.AvatarChoice(position=panelNum)
                panel.setPos(POSITIONS[panelNum])
                self.panelList.append(panel)

        if len(self.avatarList) > 0:
            self.initLookAtInfo()

        self.isLoaded = 1

    def getLookAtPosition(self, toonHead, toonidx):
        lookAtChoice = random.random()
        if len(self.used_panel_indexs) == 1:
            lookFwdPercent = 0.33
            lookAtOthersPercent = 0
        else:
            lookFwdPercent = 0.2
            if len(self.used_panel_indexs) == 2:
                lookAtOthersPercent = 0.4
            else:
                lookAtOthersPercent = 0.65
        lookRandomPercent = 1.0 - lookFwdPercent - lookAtOthersPercent
        if lookAtChoice < lookFwdPercent:
            self.IsLookingAt[toonidx] = 'f'
            return Vec3(0, 1.5, 0)
        elif lookAtChoice < lookRandomPercent + lookFwdPercent or len(self.used_panel_indexs) == 1:
            self.IsLookingAt[toonidx] = 'r'
            return toonHead.getRandomForwardLookAtPoint()
        else:
            other_toon_idxs = []
            for i in xrange(len(self.IsLookingAt)):
                if self.IsLookingAt[i] == toonidx:
                    other_toon_idxs.append(i)

            if len(other_toon_idxs) == 1:
                IgnoreStarersPercent = 0.4
            else:
                IgnoreStarersPercent = 0.2
            NoticeStarersPercent = 0.5
            bStareTargetTurnsToMe = 0
            if len(other_toon_idxs) == 0 or random.random() < IgnoreStarersPercent:
                other_toon_idxs = []
                for i in self.used_panel_indexs:
                    if i != toonidx:
                        other_toon_idxs.append(i)

                if random.random() < NoticeStarersPercent:
                    bStareTargetTurnsToMe = 1
            if len(other_toon_idxs) == 0:
                return toonHead.getRandomForwardLookAtPoint()
            else:
                lookingAtIdx = random.choice(other_toon_idxs)
            if bStareTargetTurnsToMe:
                self.IsLookingAt[lookingAtIdx] = toonidx
                otherToonHead = None
                for panel in self.panelList:
                    if panel.position == lookingAtIdx:
                        otherToonHead = panel.headModel

                otherToonHead.doLookAroundToStareAt(otherToonHead, self.getLookAtToPosVec(lookingAtIdx, toonidx))
            self.IsLookingAt[toonidx] = lookingAtIdx
            return self.getLookAtToPosVec(toonidx, lookingAtIdx)
        return

    def getLookAtToPosVec(self, fromIdx, toIdx):
        x = -(POSITIONS[toIdx][0] - POSITIONS[fromIdx][0])
        y = POSITIONS[toIdx][1] - POSITIONS[fromIdx][1]
        z = POSITIONS[toIdx][2] - POSITIONS[fromIdx][2]
        return Vec3(x, y, z)

    def initLookAtInfo(self):
        self.used_panel_indexs = []
        for panel in self.panelList:
            if panel.dna != None:
                self.used_panel_indexs.append(panel.position)

        if len(self.used_panel_indexs) == 0:
            return
        self.IsLookingAt = []
        for i in xrange(MAX_AVATARS):
            self.IsLookingAt.append('f')

        for panel in self.panelList:
            if panel.dna != None:
                panel.headModel.setLookAtPositionCallbackArgs((self, panel.headModel, panel.position))

        return

    def unload(self):
        if self.isLoaded == 0:
            return None
        cleanupDialog('globalDialog')
        for panel in self.panelList:
            panel.destroy()

        del self.panelList
        self.title.removeNode()
        del self.title
        self.logoutButton.destroy()
        del self.logoutButton
        self.userNameLabel.destroy()
        del self.userNameLabel
        # self.logoutButton.destroy()
        # del self.logoutButton
        self.pickAToonBG.removeNode()
        del self.pickAToonBG
        unload()
        del self.avatarList
        self.parentFSM.getCurrentState().removeChild(self.fsm)
        del self.parentFSM
        del self.fsm
        self.ignoreAll()
        self.isLoaded = 0
        ModelPool.garbageCollect()
        TexturePool.garbageCollect()
        base.setBackgroundColor(ToontownGlobals.DefaultBackgroundColor)

    def __handlePanelDone(self, panelDoneStatus, panelChoice=0):
        self.doneStatus = {}
        self.doneStatus['mode'] = panelDoneStatus
        self.choice = panelChoice
        if panelDoneStatus == 'chose':
            self.__handleChoice()
        elif panelDoneStatus == 'nameIt':
            self.__handleCreate()
        elif panelDoneStatus == 'delete':
            self.__handleDelete()
        elif panelDoneStatus == 'create':
            self.__handleCreate()

    def getChoice(self):
        return self.choice

    def __handleChoice(self):
        self.fsm.request('CheckDownload')

    def __handleCreate(self):
        self.fsm.request('CheckDownload')

    def __handleDelete(self):
        messenger.send(self.doneEvent, [self.doneStatus])

    def __handleQuit(self):
        cleanupDialog('globalDialog')
        self.doneStatus = {'mode': 'exit'}
        messenger.send(self.doneEvent, [self.doneStatus])

    def enterChoose(self):
        pass

    def exitChoose(self):
        pass

    def enterCheckDownload(self):
        self.accept('downloadAck-response', self.__handleDownloadAck)
        self.downloadAck = DownloadForceAcknowledge.DownloadForceAcknowledge('downloadAck-response')
        self.downloadAck.enter(2000)

    def exitCheckDownload(self):
        self.downloadAck.exit()
        self.downloadAck = None
        self.ignore('downloadAck-response')
        return

    def __handleDownloadAck(self, doneStatus):
        if doneStatus['mode'] == 'complete':
            base.transitions.fadeOut(finishIval=EventInterval(self.doneEvent, [self.doneStatus]))
        else:
            self.fsm.request('Choose')

    def __handleLogoutWithoutConfirm(self):
        base.cr.loginFSM.request('login')

    def __back(self):
        if base.isHosting:
            self.confirm = TTDialog.TTGlobalDialog(
                doneEvent='confirmBack',
                message=TTLocalizer.LogOutHost,
                style=TTDialog.TwoChoice)
            self.confirm.show()
            base.accept('confirmBack', self.__backConfirm)
            return
        elif not base.isHosting:
            self.confirm = TTDialog.TTGlobalDialog(
                doneEvent='confirmBack',
                message=TTLocalizer.LogOut,
                style=TTDialog.TwoChoice)
            self.confirm.show()
            base.accept('confirmBack', self.__backConfirm)
            return

    def __backConfirm(self):
        status = self.confirm.doneStatus
        self.ignore('confirmDone')
        self.confirm.cleanup()
        del self.confirm
        if status == 'ok':
            base.isLoggingOut = True
            base.cr.loginFSM.request('serverMenu')

    '''
    def __back(self):
        if base.wantSinglePlayer:
            self.confirm = TTDialog.TTGlobalDialog(
                doneEvent='confirmBack',
                message=TTLocalizer.LeaveServerHostSP,
                style=TTDialog.TwoChoice)
            self.confirm.show()
            base.accept('confirmBack', self.__backConfirm)
            return
        elif base.isHosting and not base.wantSinglePlayer:
            self.confirm = TTDialog.TTGlobalDialog(
                doneEvent='confirmBack',
                message=TTLocalizer.LeaveServerHost,
                style=TTDialog.TwoChoice)
            self.confirm.show()
            base.accept('confirmBack', self.__backConfirm)
            return
        elif not base.isHosting or base.wantSinglePlayer:
            self.confirm = TTDialog.TTGlobalDialog(
                doneEvent='confirmBack',
                message=TTLocalizer.LeaveServer,
                style=TTDialog.TwoChoice)
            self.confirm.show()
            base.accept('confirmBack', self.__backConfirm)
            return
        '''