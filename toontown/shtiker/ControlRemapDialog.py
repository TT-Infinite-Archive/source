from direct.gui.DirectGui import DGG, DirectButton
from direct.showbase.DirectObject import DirectObject
from panda3d.core import TextNode

from toontown.toonbase import SettingsGlobals, TTLocalizer
from toontown.toonbase.ColorGlobals import CBlack, CDefault, CGray, CRed, CYellow
from toontown.toontowngui import TTButton, TTDialog, TTLabel

PanelWidth = 2.26757
PanelHeight = 1.63266

ColumnXs = (-0.87168, -0.29056, 0.29056, 0.87168)
CategoryX = -1.07973

# Every remappable control:
ControlRows = (
    ('MOVE_UP', 'MOVE_LEFT', 'MOVE_DOWN', 'MOVE_RIGHT'),
    ('JUMP', 'ACTION_BUTTON', 'INTERACT_KEY', 'CHAT_HOTKEY'),
    ('OPTIONS_PAGE_HOTKEY', 'SCREENSHOT_KEY', 'VIEW_GAGS_KEY', 'VIEW_TASKS_KEY')
)

ControlLabelIndex = {
    'MOVE_UP': 0,
    'MOVE_LEFT': 1,
    'MOVE_DOWN': 2,
    'MOVE_RIGHT': 3,
    'JUMP': 4,
    'ACTION_BUTTON': 5,
    'OPTIONS_PAGE_HOTKEY': 6,
    'CHAT_HOTKEY': 7,
    'SCREENSHOT_KEY': 8,
    'INTERACT_KEY': 9,
    'VIEW_GAGS_KEY': 10,
    'VIEW_TASKS_KEY': 11
}

TitleZ = 0.6894
PromptZ = 0.58981
RowZs = ((0.46649, 0.37347, 0.26704),
         (0.12885, 0.03583, -0.0706),
         (-0.2088, -0.30182, -0.40825))
StatusZ = -0.55
ButtonZ = -0.7
DefaultsX = -0.90056
OkX = 0.87168
CancelX = 0.99905
IconScale = 1.0

# Wrapping widths
TextMargin = 0.2
PromptWrap = int((PanelWidth - TextMargin) / TTLabel.TTLabel.Scales[TTLabel.TTLabel.MediumSize])
StatusWrap = int((PanelWidth - TextMargin) / TTLabel.TTLabel.Scales[TTLabel.TTLabel.NormalSize])

KeyCaptureEvent = 'controlRemap-buttonPress'


def formatKeyName(keyName):
    # Turns a Panda button name such as 'arrow_up' into 'Arrow Up'
    return keyName.replace('_', ' ').title()


class IconButton(DirectButton):
    def __init__(self, parent, iconName, pos, command):
        buttons = loader.loadModel('phase_3/models/gui/dialog_box_buttons_gui')
        optiondefs = (
            ('relief', None, None),
            ('pos', pos, None),
            ('command', command, None),
            ('image', (buttons.find('**/%s_UP' % iconName),
                       buttons.find('**/%s_DN' % iconName),
                       buttons.find('**/%s_Rllvr' % iconName)), None),
            ('image_scale', IconScale, None)
        )

        self.defineoptions({}, optiondefs)
        DirectButton.__init__(self, parent)
        self.initialiseoptions(IconButton)
        buttons.removeNode()

    def enable(self):
        self['state'] = DGG.NORMAL
        self['image_color'] = CDefault

    def disable(self):
        self['state'] = DGG.DISABLED
        self['image_color'] = CGray


class ControlRemap(DirectObject):

    def __init__(self):
        DirectObject.__init__(self)

        self.keymap = base.getKeymap()
        self.listeningFor = None
        self.controlButtons = {}
        self.controlLabels = {}

        self.dialog = TTDialog.TTDialog(
            style=TTDialog.NoButtons, suppressKeys=True, suppressMouse=True)
        self.dialog['image_scale'] = (PanelWidth, 1, PanelHeight)
        self.dialog['image_pos'] = (0, 0, 0)
        self.dialog['frameSize'] = (-PanelWidth / 2.0, PanelWidth / 2.0,
                                    -PanelHeight / 2.0, PanelHeight / 2.0)

        self.title = TTLabel.TTLabel(
            parent=self.dialog, text=TTLocalizer.RemapTitle,
            text_size=TTLabel.TTLabel.LargeSize, pos=(0, 0, TitleZ))
        self.prompt = TTLabel.TTLabel(
            parent=self.dialog, text=TTLocalizer.RemapPrompt,
            text_size=TTLabel.TTLabel.MediumSize, text_wordwrap=PromptWrap,
            pos=(0, 0, PromptZ))

        for row, controls in enumerate(ControlRows):
            categoryZ, labelZ, buttonZ = RowZs[row]
            TTLabel.TTLabel(
                parent=self.dialog, text=TTLocalizer.RemapCategories[row],
                text_align=TextNode.ALeft, text_wordwrap=20,
                pos=(CategoryX, 0, categoryZ))

            for column, control in enumerate(controls):
                x = ColumnXs[column]
                self.controlLabels[control] = TTLabel.TTLabel(
                    parent=self.dialog, text_wordwrap=12,
                    text=TTLocalizer.Controls[ControlLabelIndex[control]],
                    pos=(x, 0, labelZ))
                self.controlButtons[control] = TTButton.TTButton(
                    parent=self.dialog, pos=(x, 0, buttonZ),
                    buttonScale=(1.3, 1, 1), textScale=0.045,
                    text=formatKeyName(self.keymap[control]),
                    command=self.listenForKey, extraArgs=[control])

        # Reused as the "press a key" prompt and the duplicate binding warning:
        self.status = TTLabel.TTLabel(
            parent=self.dialog, text='', text_size=TTLabel.TTLabel.NormalSize,
            text_wordwrap=StatusWrap, text_fg=CRed, pos=(0, 0, StatusZ))

        self.defaultsButton = TTButton.TTButton(
            parent=self.dialog, text=TTLocalizer.RemapDefaults,
            pos=(DefaultsX, 0, ButtonZ), command=self.restoreDefaults)
        self.okButton = IconButton(
            self.dialog, 'ChtBx_OKBtn', (OkX, 0, ButtonZ), self.save)
        self.cancelButton = IconButton(
            self.dialog, 'CloseBtn', (CancelX, 0, ButtonZ), self.cancel)

        self.dialog.show()
        self.refresh()

        messenger.send('disable-hotkeys')
        if hasattr(base, 'localAvatar'):
            base.localAvatar.chatMgr.disableBackgroundFocus()

    def getConflicts(self):
        seen = {}
        conflicts = set()
        for control, keyName in list(self.keymap.items()):
            if keyName in seen:
                conflicts.add(control)
                conflicts.add(seen[keyName])
            else:
                seen[keyName] = control

        return conflicts

    def refresh(self):
        conflicts = self.getConflicts()
        for control, button in list(self.controlButtons.items()):
            color = CRed if control in conflicts else CBlack
            if control != self.listeningFor:
                # placeholder:
                button.button['text'] = formatKeyName(self.keymap[control])
            button.button['text_fg'] = color
            self.controlLabels[control]['text_fg'] = color

        if self.listeningFor is not None:
            control = self.listeningFor
            self.status['text'] = TTLocalizer.RemapPopup % (
                TTLocalizer.Controls[ControlLabelIndex[control]].rstrip(':'))
            self.status['text_fg'] = CBlack
        elif conflicts:
            self.status['text'] = TTLocalizer.RemapConflict
            self.status['text_fg'] = CRed
        else:
            self.status['text'] = ''

        if conflicts or self.listeningFor is not None:
            self.okButton.disable()
        else:
            self.okButton.enable()

    def listenForKey(self, control):
        if self.listeningFor is not None:
            return

        self.listeningFor = control
        for name, button in list(self.controlButtons.items()):
            if name == control:
                button.button['text'] = TTLocalizer.RemapListening
                button.button['image_color'] = CYellow
            else:
                button.disable()

        self.defaultsButton.disable()
        self.cancelButton.disable()
        self.refresh()

        base.buttonThrowers[0].node().setButtonDownEvent(KeyCaptureEvent)
        self.accept(KeyCaptureEvent, self.registerKey)

    def stopListening(self):
        self.ignore(KeyCaptureEvent)
        base.buttonThrowers[0].node().setButtonDownEvent('')

        listeningFor = self.listeningFor
        self.listeningFor = None
        if listeningFor is not None:
            self.controlButtons[listeningFor].button['image_color'] = CDefault

        for button in list(self.controlButtons.values()):
            button.enable()

        self.defaultsButton.enable()
        self.cancelButton.enable()
        self.refresh()

    def registerKey(self, keyName):
        # escape is reserved so there is always a way out of a capture:
        if keyName.startswith('mouse'):
            return

        if keyName != 'escape':
            self.keymap[self.listeningFor] = keyName

        self.stopListening()

    def restoreDefaults(self):
        self.keymap = dict(SettingsGlobals.DefaultKeymap)
        self.refresh()

    def save(self):
        if self.getConflicts():
            return

        keymap = settings.get(SettingsGlobals.Keymap, {})
        keymap.update(self.keymap)
        settings[SettingsGlobals.Keymap] = keymap
        settings.write()

        base.reloadControls()
        if hasattr(base, 'localAvatar'):
            base.localAvatar.controlManager.reload()
            base.localAvatar.chatMgr.reloadWASD()
        self.unload()
        if hasattr(base, 'localAvatar'):
            base.localAvatar.controlManager.disable()
        messenger.send('controlsRemapped')

    def cancel(self):
        self.unload()

    def unload(self):
        if self.listeningFor is not None:
            self.stopListening()
        self.ignoreAll()
        self.dialog.cleanup()
        del self.dialog
        del self.controlButtons
        del self.controlLabels
        if hasattr(base, 'localAvatar'):
            base.localAvatar.chatMgr.reloadWASD()
        messenger.send('enable-hotkeys')
