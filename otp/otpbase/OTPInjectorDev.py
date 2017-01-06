from otp.settings.Settings import Settings
from direct.stdpy import threading
import OTPLocalizer
import wx

class CustomDialog(wx.Dialog):

    def __init__(self, parent, caption, title, inputMethod):
        wx.Dialog.__init__(self, parent, -1, title)

        self.text = wx.StaticText(self, -1, caption)
        self.input = inputMethod(self)
        self.buttons = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        self.sizer = wx.BoxSizer(wx.VERTICAL)

        self.sizer.Add(self.text, 0, wx.ALL, 5)
        self.sizer.Add(self.input, 1, wx.EXPAND | wx.ALL, 5)
        self.sizer.Add(self.buttons, 0, wx.EXPAND | wx.ALL, 5)
        self.SetSizerAndFit(self.sizer)
        self.input.SetFocus()
        self.Centre()

class ListDialog(CustomDialog):

    def __init__(self, parent, caption, title, choices):
        CustomDialog.__init__(self, parent, caption, title, lambda self: wx.ListBox(self, choices=sorted(choices)))

class InputDialog(CustomDialog):

    def __init__(self, parent, caption, title):
        CustomDialog.__init__(self, parent, caption, title, lambda self: wx.TextCtrl(self))

    def getInput(self):
        return self.input.GetValue()

class Injector:
    DEFAULT_TEXT = ''

    def __init__(self):
        self.snippets = Settings('snippets.json')
        self.app = wx.App(redirect=False)
        self.frame = wx.Frame(None, title=OTPLocalizer.InjectorTitle, size=(500, 300), style=wx.SYSTEM_MENU | wx.CAPTION | wx.MINIMIZE_BOX | wx.CLOSE_BOX | wx.RESIZE_BORDER)
        self.panel = wx.Panel(self.frame)
        self.buttonPanel = wx.Panel(self.panel)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.injectButton = wx.Button(parent=self.buttonPanel, size=(100, 50), label=OTPLocalizer.InjectorInject)
        self.saveButton = wx.Button(parent=self.buttonPanel, size=(100, 50), label=OTPLocalizer.InjectorSave)
        self.loadButton = wx.Button(parent=self.buttonPanel, size=(100, 50), label=OTPLocalizer.InjectorLoad)
        self.removeButton = wx.Button(parent=self.buttonPanel, size=(100, 50), label=OTPLocalizer.InjectorRemove)
        self.injectBox = wx.TextCtrl(parent=self.panel, style=wx.TE_MULTILINE | wx.TE_RICH2)

        self.injectBox.SetLabel(self.DEFAULT_TEXT)
        self.injectBox.Bind(wx.EVT_KEY_DOWN, self.__keyDown)
        self.injectButton.Bind(wx.EVT_BUTTON, self.__inject)
        self.saveButton.Bind(wx.EVT_BUTTON, self.__save)
        self.loadButton.Bind(wx.EVT_BUTTON, self.__load)
        self.removeButton.Bind(wx.EVT_BUTTON, self.__remove)

        for i, button in enumerate((self.injectButton, self.saveButton, self.loadButton, self.removeButton)):
            if i:
                self.buttonSizer.AddSpacer(30)

            self.buttonSizer.Add(button)

        self.sizer.Add(self.injectBox, 1, wx.EXPAND)
        self.sizer.Add(self.buttonPanel, 0, wx.ALIGN_CENTER)

        self.buttonPanel.SetSizer(self.buttonSizer)
        self.panel.SetSizer(self.sizer)
        self.frame.SetMinSize((500, 300))
        self.frame.Show()

        threading.Thread(target=self.app.MainLoop).start()

    def info(self, parent, message, caption, icon=wx.ICON_INFORMATION, buttons=wx.OK):
        return wx.MessageDialog(parent, message, caption, buttons | icon).ShowModal() == wx.ID_YES

    def chooseSnippet(self, caption):
        dialog = ListDialog(self.frame, caption, OTPLocalizer.InjectorTitle, self.snippets.keys())

        if dialog.ShowModal() == wx.ID_OK:
            return dialog.input.GetStringSelection()

    def reloadSnippets(self):
        self.snippets.read()

    def saveSnippet(self, name, content):
        self.snippets[name] = content

    def __keyDown(self, event):
        if event.GetKeyCode() == wx.WXK_TAB:
            self.injectBox.WriteText(' ' * 4)
        else:
            event.Skip()

    def __inject(self, event):
        exec(self.injectBox.GetValue(), globals())

    def __save(self, event):
        dialog = InputDialog(self.frame, OTPLocalizer.InjectorSaveQuestion, OTPLocalizer.InjectorTitle)

        if dialog.ShowModal() != wx.ID_OK:
            return

        input = dialog.getInput()
        snippet = self.injectBox.GetValue()

        if not input or not snippet:
            self.info(dialog, OTPLocalizer.InjectorNotSaved, OTPLocalizer.InjectorOops, wx.ICON_WARNING)
            return
        elif input in self.snippets and not self.info(dialog, OTPLocalizer.InjectorSnippetExists, OTPLocalizer.InjectorOops, wx.ICON_WARNING, wx.YES_NO):
            return

        self.snippets[input] = snippet
        self.info(dialog, OTPLocalizer.InjectorSaved % input, OTPLocalizer.InjectorOhYea)

    def __load(self, event):
        input = self.chooseSnippet(OTPLocalizer.InjectorLoadQuestion)

        if not input or (self.injectBox.GetValue() and not self.info(self.frame, OTPLocalizer.InjectorOverwriteWarning, OTPLocalizer.InjectorOops, wx.ICON_WARNING, wx.YES_NO)):
            return

        self.injectBox.SetValue(self.snippets[input])
        self.info(self.frame, OTPLocalizer.InjectorLoaded % input, OTPLocalizer.InjectorOhYea)

    def __remove(self, event):
        input = self.chooseSnippet(OTPLocalizer.InjectorRemoveQuestion)

        if not input or not self.info(self.frame, OTPLocalizer.InjectorRemoveWarning % input, OTPLocalizer.InjectorOops, wx.ICON_WARNING, wx.YES_NO):
            return

        del self.snippets[input]
        self.info(self.frame, OTPLocalizer.InjectorRemoved % input, OTPLocalizer.InjectorOhYea)
