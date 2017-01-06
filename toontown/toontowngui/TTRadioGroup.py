from direct.showbase.DirectObject import DirectObject


class TTRadioGroup(DirectObject):
    def __init__(self, buttons, command=None):
        """
        :param buttons: List of TTRadioButtons
        :param command: Command to call when a radio button is clicked with the value of the button as an argument
        """
        DirectObject.__init__(self)
        self.buttons = buttons
        self.command = command
        self.selectedButton = None
        for button in self.buttons:
            button.setGroup(self)
            if button.selected:
                self.selectedButton = button

    def destroy(self):
        for button in self.buttons:
            button.destroy()
        self.selectedButton = None
        self.command = None

    def hide(self):
        for button in self.buttons:
            button.hide()

    def show(self):
        for button in self.buttons:
            button.show()

    def buttonClicked(self, button):
        """
        Called by a TTRadioButton to tell the group that it was selected
        """
        if button == self.selectedButton:
            return
        if self.selectedButton:
            self.selectedButton.setSelected(False)
            self.selectedButton = None
        for button in self.buttons:
            if button.selected:
                self.selectedButton = button

        if self.command is not None:
            self.command(self.selectedButton.value)

    def buttonLeftGroup(self, button):
        """
        Occurs when a TTRadioButton is assigned a new group
        """
        if button == self.selectedButton:
            self.selectedButton.setSelected(False)
        self.selectedButton = None

