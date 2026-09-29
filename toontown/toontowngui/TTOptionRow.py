from panda3d.core import TextNode

from direct.gui.DirectGui import DirectFrame

from toontown.toonbase import ColorGlobals
from toontown.toontowngui import TTButton, TTCheckBox, TTLabel, TTSlider
from toontown.toontowngui.TTArrow import TTArrow
from toontown.toontowngui.TTLabel import fitText


class TTOptionRow(DirectFrame):
    Height = 0.105
    LabelX = -0.78
    LabelWidth = 0.85
    ControlX = 0.38

    def __init__(self, parent, text = '', requiresRestart = False):
        DirectFrame.__init__(self, parent = parent, relief = None)

        self.requiresRestart = requiresRestart
        self.label = TTLabel.TTLabel(
            parent = self,
            text = text,
            text_align = TextNode.ALeft,
            text_wordwrap = 50,
            pos = (self.LabelX, 0, -0.014)
        )
        self.marker = TTLabel.TTLabel(
            parent = self,
            text = '*',
            text_fg = ColorGlobals.CRed,
            text_align = TextNode.ALeft,
            pos = (self.LabelX + fitText(self.label, self.LabelWidth) + 0.015, 0, -0.014)
        )
        self.marker.hide()

    def markChanged(self):
        if self.requiresRestart:
            self.marker.show()


class TTOptionHeading(TTOptionRow):
    Height = 0.11

    def __init__(self, parent, text = ''):
        TTOptionRow.__init__(self, parent, text)
        self.label['text_scale'] = TTLabel.TTLabel.Scales[TTLabel.TTLabel.MediumSize]
        fitText(self.label, self.LabelWidth)


class TTToggleRow(TTOptionRow):
    def __init__(self, parent, text = '', checked = False, requiresRestart = False, disable = False, command = None):
        TTOptionRow.__init__(self, parent, text, requiresRestart)

        self.command = command
        self.checkBox = TTCheckBox.TTCheckBox(
            parent = self,
            pos = (self.ControlX, 0, 0),
            checked = checked,
            disable = disable,
            command = self.__changed
        )

    def __changed(self):
        self.markChanged()
        if self.command:
            self.command(self.checkBox.checked)

    def getValue(self):
        return self.checkBox.checked

    def setValue(self, checked):
        self.checkBox.setChecked(checked)

    def enable(self):
        self.checkBox.enable()

    def disable(self):
        self.checkBox.disable()


class TTChoiceRow(TTOptionRow):
    ValueX = 0.38
    ValueWidth = 0.30
    LeftArrowX = 0.16
    RightArrowX = 0.60

    def __init__(self, parent, text = '', values = (), valueLabels = (), value = None,
                 requiresRestart = False, command = None):
        TTOptionRow.__init__(self, parent, text, requiresRestart)

        self.command = command
        self.values = []
        self.valueLabels = []
        self.index = 0

        self.leftArrow = TTArrow(
            parent = self,
            orientation = TTArrow.OrientationLeft,
            pos = (self.LeftArrowX, 0, 0.012),
            command = self.__step,
            extraArgs = [-1]
        )
        self.rightArrow = TTArrow(
            parent = self,
            orientation = TTArrow.OrientationRight,
            pos = (self.RightArrowX, 0, 0.012),
            command = self.__step,
            extraArgs = [1]
        )
        self.valueLabel = TTLabel.TTLabel(
            parent = self,
            text_wordwrap = 50,
            pos = (self.ValueX, 0, -0.014)
        )
        self.setValues(values, valueLabels, value)

    def __step(self, delta):
        index = self.index + delta
        if index < 0 or index >= len(self.values):
            return

        self.index = index
        self.__refresh()
        self.markChanged()
        if self.command:
            self.command(self.values[index])

    def __refresh(self):
        self.valueLabel['text'] = self.valueLabels[self.index] if self.valueLabels else ''
        self.valueLabel['text_scale'] = TTLabel.TTLabel.Scales[TTLabel.TTLabel.NormalSize]
        fitText(self.valueLabel, self.ValueWidth)
        if self.index > 0:
            self.leftArrow.enable()
        else:
            self.leftArrow.disable()
        if self.index + 1 < len(self.values):
            self.rightArrow.enable()
        else:
            self.rightArrow.disable()

    def setValues(self, values, valueLabels, value = None):
        self.values = list(values)
        self.valueLabels = list(valueLabels)
        self.index = self.values.index(value) if value in self.values else 0
        self.__refresh()

    def getValue(self):
        return self.values[self.index] if self.values else None

    def setValue(self, value):
        if value in self.values:
            self.index = self.values.index(value)
            self.__refresh()


class TTSliderRow(TTOptionRow):
    SliderX = 0.34
    PercentX = 0.55

    def __init__(self, parent, text = '', value = 0, enabled = True, command = None):
        TTOptionRow.__init__(self, parent, text)

        self.command = command
        self.slider = TTSlider.TTSlider(
            parent = self,
            value = value,
            scale = 0.8,
            length = 0.42,
            pos = (self.SliderX, 0, 0.0),
            enabled = enabled,
            command = self.__changed
        )
        self.slider.percent.hide()
        self.percent = TTLabel.TTLabel(
            parent = self,
            text_size = TTLabel.TTLabel.SmallSize,
            text_align = TextNode.ALeft,
            pos = (self.PercentX, 0, -0.01)
        )
        self.__showPercent()

    def __showPercent(self):
        self.percent['text'] = '%d%%' % self.slider.getValue()

    def __changed(self):
        self.__showPercent()
        if self.command:
            self.command(self.slider.getValue())

    def getValue(self):
        return self.slider.getValue()

    def setValue(self, value):
        self.slider.setValue(value)
        self.__showPercent()

    def enable(self):
        self.slider.enable()

    def disable(self):
        self.slider.disable()


class TTButtonRow(TTOptionRow):
    ButtonX = 0.38

    def __init__(self, parent, text = '', buttonText = '', disable = False, command = None):
        TTOptionRow.__init__(self, parent, text)

        self.button = TTButton.TTButton(
            parent = self,
            text = buttonText,
            pos = (self.ButtonX, 0, 0.0),
            disable = disable,
            command = command
        )

    def enable(self):
        self.button.enable()

    def disable(self):
        self.button.disable()
