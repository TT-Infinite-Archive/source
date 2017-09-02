from direct.gui.DirectGui import DirectFrame
from panda3d.core import Point3
from pandac.PandaModules import TextNode
from toontown.toontowngui.TTLabel import TTLabel
from direct.interval.IntervalGlobal import Func, Sequence
from direct.interval.MetaInterval import Parallel
from toontown.makeatoon.MakeAToonGUI import MATShuffleButton, MATArrow
from toontown.mainmenu import MainMenuGlobals
from toontown.toonbase import ServerSettingsGlobals
from direct.gui.DirectGui import DirectLabel
from toontown.toonbase import TTLocalizer, ToontownGlobals
from toontown.toontowngui.TTCheckBox import TTCheckBox
from direct.interval.FunctionInterval import Func, Wait
from direct.interval.IntervalGlobal import LerpScaleInterval
from direct.gui.DirectGui import DirectButton
from pandac.PandaModules import Vec4
from direct.fsm.FSM import FSM
from toontown.mainmenu.PlayScreen import PlayScreen


class HostScreen(DirectFrame, FSM):
    def __init__(self, mainMenu):
        DirectFrame.__init__(self, mainMenu)
        FSM.__init__(self, 'HostScreen')

        self.mainMenu = mainMenu
        base.isSinglePlayer = None
        halfButtonScale = (0.6, 0.6, 0.6)
        halfButtonHoverScale = (0.7, 0.7, 0.7)

        self.playScreen = PlayScreen(self)
        self.playScreen.hide()

        self.hostScreenElements = []
        self.projectorSfx = loader.loadSfx('phase_5/audio/sfx/TL_presentation.ogg')

        self.hostWantRacingLabel = TTLabel(
            parent=self,
            pos=(-0.9, 0, 0.36),
            text="Racing",
            text_align=TextNode.ALeft,
        )
        self.hostScreenElements.append(self.hostWantRacingLabel)

        self.hostWantGolfLabel = TTLabel(
            parent=self,
            pos=(-0.9, 0, 0.26),
            text="Golf",
            text_align=TextNode.ALeft,
        )
        self.hostScreenElements.append(self.hostWantGolfLabel)

        self.hostWantSinglePlayer = TTLabel(
            parent=self,
            pos=(-0.9, 0, 0.16),
            text="Single Player",
            text_align=TextNode.ALeft,
        )
        self.hostScreenElements.append(self.hostWantSinglePlayer)

        self.hostWantRacingBox = TTCheckBox(
            parent=self,
            pos=(-0.95, 0, 0.37),
            checked=serverSettings[ServerSettingsGlobals.WantRacing],
            command=self.toggleServerSetting, extraArgs=[ServerSettingsGlobals.WantRacing]
        )
        self.hostScreenElements.append(self.hostWantRacingBox)

        self.hostWantGolfBox = TTCheckBox(
            parent=self,
            pos=(-0.95, 0, 0.27),
            checked=serverSettings[ServerSettingsGlobals.WantGolf],
            command=self.toggleServerSetting, extraArgs=[ServerSettingsGlobals.WantGolf]
        )
        self.hostScreenElements.append(self.hostWantGolfBox)

        self.hostSinglePlayerBox = TTCheckBox(
            parent=self,
            pos=(-0.95, 0, 0.17),
            checked=serverSettings[ServerSettingsGlobals.WantSinglePlayer],
            command=self.toggleServerSetting, extraArgs=[ServerSettingsGlobals.WantSinglePlayer]
        )
        self.hostScreenElements.append(self.hostSinglePlayerBox)

        self.hostExpMultDec = MATArrow(
            parent=self,
            pos=(-0.8, 0, -0.02), command=self.setServerExpMult)
        self.hostScreenElements.append(self.hostExpMultDec)

        self.hostExpMultInc = MATArrow(
            parent=self,
            pos=(-0.29, 0, -0.02), inverted=True, command=self.setServerExpMult)
        self.hostScreenElements.append(self.hostExpMultInc)

        self.hostExpMultLabel = TTLabel(
            parent=self,
            pos=(-0.55, 0, -0.04),
            text="EXP Multiplier: %sx" % str(serverSettings[ServerSettingsGlobals.ExpMultiplier]),
            text_align=TextNode.ACenter,
        )
        self.hostScreenElements.append(self.hostExpMultLabel)

        self.label = DirectLabel(parent=self, relief=None, text=TTLocalizer.ServerSettings, text_fg=(0, 0, 0, 1),
                                   text_font=ToontownGlobals.getToonFont(), text_scale=0.09, text_wordwrap=25,
                                   pos=(-0.55, 0, 0.5))
        self.hostScreenElements.append(self.label)

        gui = loader.loadModel('phase_3/models/gui/tt_m_gui_mat_mainGui')

        guiAcceptUp = gui.find('**/tt_t_gui_mat_okUp')
        guiAcceptUp.flattenStrong()
        guiAcceptDown = gui.find('**/tt_t_gui_mat_okDown')
        guiAcceptDown.flattenStrong()
        guiNextUp = gui.find('**/tt_t_gui_mat_nextUp')
        guiNextUp.flattenStrong()
        guiNextDown = gui.find('**/tt_t_gui_mat_nextDown')
        guiNextDown.flattenStrong()

        self.startServerButton = DirectButton(
            parent=self,
            relief=None,
            image=(guiAcceptUp, guiAcceptDown, guiAcceptUp, guiAcceptDown),
            image_scale=halfButtonScale,
            image1_scale=halfButtonHoverScale,
            image2_scale=halfButtonHoverScale,
            pos=(1.75, 0, -0.90),
            command=lambda: self.mainMenu.request('StartHost'),
            text=('', TTLocalizer.HostDone, TTLocalizer.HostDone, ''),
            text_font=ToontownGlobals.getInterfaceFont(),
            text_scale=0.08,
            text_align=TextNode.ARight,
            text_pos=(0.075, 0.13),
            text_fg=(1, 1, 1, 1),
            text_shadow=(0, 0, 0, 1))
        self.hostScreenElements.append(self.startServerButton)

        self.backButton = DirectButton(
            parent=self,
            relief=None,
            image=(guiNextUp, guiNextDown, guiNextUp, guiNextDown),
            image3_color=Vec4(0.5, 0.5, 0.5, 0.75),
            image_scale=(-0.3, 0.3, 0.3),
            image1_scale=(-0.35, 0.35, 0.35),
            image2_scale=(-0.35, 0.35, 0.35),
            pos=(-1.75, 0, -0.90),
            command=lambda: self.request('Back'),
            text=('', TTLocalizer.MakeAToonLast, TTLocalizer.MakeAToonLast, ''),
            text_font=ToontownGlobals.getInterfaceFont(),
            text_scale=0.08,
            text_pos=(0, 0.115),
            text_fg=(1, 1, 1, 1),
            text_shadow=(0, 0, 0, 1))
        self.hostScreenElements.append(self.backButton)

        self.avScreen = loader.loadModel('phase_5/models/props/av_screen_server_settings.bam')
        self.avScreen.setPosHpr(-329, -196, 0.025, 95, 0, 0)
        self.avScreen.reparentTo(hidden)
        self.avScreen.setScale(0.1)

        self.propTrackGrow = Sequence()
        self.propTrackGrow.append(Func(self.avScreen.setScale, Point3(0.1, 0.1, 0.1)))
        self.propTrackGrow.append(LerpScaleInterval(self.avScreen, 1.2, Point3(1.3, 1.3, 1.3)))
        self.propTrackGrowDuration = self.propTrackGrow.getDuration()

        self.propTrackShrink = Sequence()
        self.propTrackShrink.append(Func(self.avScreen.setScale, Point3(1.3, 1.3, 1.3)))
        self.propTrackShrink.append(LerpScaleInterval(self.avScreen, 1.2, Point3(0.1, 0.1, 0.1)))
        self.propTrackShrink.append(Func(self.avScreen.reparentTo, hidden))
        self.propTrackShrinkDuration = self.propTrackShrink.getDuration()

        CAMSTARTPOS = (-454.5, -96, 2.7)
        CAMENDPOS = (-423.5, -159, 12)
        CAMENDPOS2 = (-359.5, -204, 3.7)

        CAMSTARTHPR = (215, 0, 0)
        CAMENDHPR = (250, -5, 0)
        CAMENDHPR2 = (280, 0, 0)

        self.cameraPosInterval = camera.posInterval(2, Point3(CAMENDPOS), startPos=Point3(CAMSTARTPOS), blendType = 'easeIn')
        self.cameraPosInterval2 = camera.posInterval(2, Point3(CAMENDPOS2), startPos=Point3(CAMENDPOS), blendType = 'easeOut')

        self.cameraHprInterval = camera.hprInterval(2, (CAMENDHPR), startHpr=(CAMSTARTHPR), blendType = 'easeIn')
        self.cameraHprInterval2 = camera.hprInterval(2, (CAMENDHPR2), startHpr=(CAMENDHPR), blendType = 'easeOut')

        self.cameraPosInterval3 = camera.posInterval(2, Point3(CAMENDPOS), startPos=Point3(CAMENDPOS2), blendType = 'easeIn') 
        self.cameraPosInterval4 = camera.posInterval(2, Point3(CAMSTARTPOS), startPos=Point3(CAMENDPOS), blendType = 'easeOut')

        self.cameraHprInterval3 = camera.hprInterval(2, (CAMENDHPR), startHpr=(CAMENDHPR2), blendType = 'easeIn') 
        self.cameraHprInterval4 = camera.hprInterval(2, (CAMSTARTHPR), startHpr=(CAMENDHPR), blendType = 'easeOut')

        for elements in self.hostScreenElements:
            elements.hide()

    def toggleServerSetting(self, setting):
        if serverSettings.get(setting) == True:
            serverSettings[setting] = False
        else:
            serverSettings[setting] = True

    def setServerExpMult(self, offset):
        value = max(min((serverSettings[ServerSettingsGlobals.ExpMultiplier] + offset), 20), 1)
        serverSettings[ServerSettingsGlobals.ExpMultiplier] = value
        self.hostExpMultLabel['text'] = "EXP Multiplier: %sx" % str(value)

    def showHostScreenElements(self):
        for elements in self.hostScreenElements:
            elements.show()

    def enter(self):
        Sequence(
            Parallel(self.cameraPosInterval, self.cameraHprInterval),
            Parallel(self.cameraPosInterval2, self.cameraHprInterval2),
            Parallel(Func(self.avScreen.reparentTo, render), Func(self.propTrackGrow.start),
            Func(self.projectorSfx.play)), Wait(self.propTrackGrowDuration), Func(self.projectorSfx.stop),
            Parallel(Func(self.label.show), Func(self.showHostScreenElements))).start()

    def enterAfterFail(self):
        Sequence(Wait(1), Func(self.showHostScreenElements)).start()

    def exit(self):
        for elements in self.hostScreenElements:
            elements.hide()

    def enterBack(self):
        for elements in self.hostScreenElements:
            elements.hide()

        self.buttonSequence = Sequence(
            Func(self.mainMenu.randomSuit2.show),
            Func(self.mainMenu.randomSuit3.show),
            Wait(4),
            Func(self.playScreen.buttonPosInterval.start),
            Func(self.playScreen.buttonPosInterval2.start),
            Func(self.playScreen.buttonPosInterval3.start)
        )

        Sequence(
            Func(self.buttonSequence.start),
            Parallel(Func(self.propTrackShrink.start),
                     self.cameraPosInterval3,
                     self.cameraHprInterval3),
            Parallel(self.cameraPosInterval4,
                     self.cameraHprInterval4),
            Func(self.mainMenu.request, 'PlayScreen')).start()

    def destroyAvScreen(self):
        self.avScreen.removeNode()