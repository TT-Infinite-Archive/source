from direct.gui.DirectGui import DirectButton, OnscreenImage


class TTRadioButton(DirectButton):
    def __init__(self, value, selected=False, parent=aspect2d, pos=(0.0, 0.0, 0.0), scale=1):
        self.group = None
        gui = loader.loadModel('phase_3/models/gui/nameshop_gui')
        circle = gui.find('**/namePanelCircle')
        self.value = value
        self.selected = selected
        DirectButton.__init__(self, parent=parent, relief=None, pos=pos, scale=scale)
        self.outerCircle = DirectButton(
            parent=self,
            relief=None,
            pos=(0, 0, 0),
            image=circle,
            image_scale=(0.5, 0.5, 0.5),
            image_color=(0.9, 0.9, 0.9, 1.0),
            command=self.setSelected,
            extraArgs=[True]
        )
        self.innerCircle = OnscreenImage(
            parent=self,
            pos=(0, 0, 0),
            image=circle,
            scale=(0.25, 0.25, 0.25),
            color=(0, 0, 0, 1)
        )
        if selected:
            self.innerCircle.show()
        else:
            self.innerCircle.hide()
        self.setSelected(selected)
        gui.removeNode()

    def destroy(self):
        self.group.buttonLeftGroup(self)
        self.group = None
        DirectButton.destroy(self)

    def setGroup(self, group):
        """
        If this is called while selected in a group the previous group may be left without a selected
        radio button.
        """
        if self.group:
            self.group.buttonLeftGroup()
        self.group = group

    def setSelected(self, flag):
        """
        If this method is called without a group assigned it will not perform the callback.
         This is useful when we are initializing radio buttons.
        """
        if self.selected == flag:
            return
        self.selected = flag
        if self.group and flag:
            self.group.buttonClicked(self)

        if self.selected:
            self.innerCircle.show()
        else:
            self.innerCircle.hide()
