from direct.gui.DirectGui import DGG
from direct.fsm import StateData

from toontown.toon import ToonDNA
from toontown.toon.ColorDNA import convertToRgb, ToonColorDNA, PartColorDNA
from toontown.toonbase.ToontownGlobals import getInterfaceFont
from toontown.toonbase import TTLocalizer

import ShuffleButton
import random

from MakeAToonGUI import *


class ColorShop(StateData.StateData):
    notify = directNotify.newCategory('ColorShop')

    def __init__(self, doneEvent):
        StateData.StateData.__init__(self, doneEvent)
        self.toon = None
        self.colorAll = 1
        self.colorValues = {
            'head': (PartColorDNA(), TTLocalizer.ColorShopHead),
            'body': (PartColorDNA(), TTLocalizer.ColorShopBody),
            'legs': (PartColorDNA(), TTLocalizer.ColorShopLegs),
            'all': (PartColorDNA(), TTLocalizer.ColorShopToon)
        }
        self.currentToonSettings = []
        self.startColor = 0
        self.selectedPart = None
        self.wantFullColorMode = True
        self.wantAdvancedColor = False

    def getGenderColorList(self, dna):
        if self.dna.getGender() == 'm':
            colorList = ToonDNA.defaultBoyColorList
        else:
            colorList = ToonDNA.defaultGirlColorList

        return colorList

    def enter(self, toon, shopsVisited=[]):
        base.disableMouse()
        self.toon = toon
        self.dna = toon.getStyle()
        if self.dna.colorDNA is None:
            self.dna.colorDNA = ToonColorDNA()
        self.selectedPart = 'all'

        if not self.wantAdvancedColor:
            colorList = self.getGenderColorList(self.dna)
            if len(self.currentToonSettings) > 0:
                self.headChoice = colorList.index(self.currentToonSettings[0])
                self.armChoice = colorList.index(self.currentToonSettings[0])
                self.legChoice = colorList.index(self.currentToonSettings[0])
            else:
                self.headChoice = random.choice(colorList)
                self.armChoice = self.headChoice
                self.legChoice = self.headChoice

                self.currentToonSettings = [
                    self.headChoice,
                    self.armChoice,
                    self.legChoice
                ]

                self.__swapHeadColor(0)
                self.__swapArmColor(0)
                self.__swapLegColor(0)

        elif self.wantFullColorMode and self.wantAdvancedColor:
            self.updatePicker()

        self.acceptOnce('last', self.__handleBackward)
        self.acceptOnce('next', self.__handleForward)

        choicePool = [
            self.getGenderColorList(self.dna),
            self.getGenderColorList(self.dna),
            self.getGenderColorList(self.dna)
        ]
        self.shuffleButton.setChoicePool(choicePool)
        self.accept(self.shuffleFetchMsg, self.changeColor)
        
        self.acceptOnce('MAT-newToonCreated', self.shuffleButton.cleanHistory)
        self.accept('MAT-advancedColorChanged', self.updateToonColor)

    def showButtons(self):
        self.parentFrame.show()

        if not self.wantAdvancedColor:
            self.colorPicker.hide()
            self.colorFrame.hide()
        else:
            self.toonFrame.hide()
            self.headFrame.hide()
            self.bodyFrame.hide()
            self.legsFrame.hide()
            self.shuffleButton.hideButtons()

            self.colorPicker.show()
            self.colorFrame.show()
            self.selectedPart = 'all'

            self.colorFrame['text'] = self.selectedPart.capitalize()
            self.wantFullColorMode = True

    def hideButtons(self):
        self.colorPicker.hide()
        self.parentFrame.hide()

    def chooseColorDNA(self):
        if not self.wantFullColorMode:
            self.toon.style.setColorDNA(
                ToonColorDNA(
                    headColor=self.colorValues['head'][0],
                    armColor=self.colorValues['body'][0],
                    legColor=self.colorValues['legs'][0]
                )
            )

        else:
            # We want to paint the whole toon the color from 'all'
            self.toon.style.setColorDNA(
                 ToonColorDNA(
                     headColor=self.colorValues['all'][0],
                     armColor=self.colorValues['all'][0],
                     legColor=self.colorValues['all'][0]
                 )
            )

    def exit(self):
        self.ignore('last')
        self.ignore('next')
        self.ignore('enter')
        self.ignore(self.shuffleFetchMsg)
        try:
            del self.toon
        except:
            print 'ColorShop: toon not found'

        self.hideButtons()

    def load(self):
        self.parentFrame = DirectFrame(
            relief=DGG.RAISED,
            pos=(0.98, 0, 0.416),
            frameColor=(1, 0, 0, 0)
        )
        self.parentFrame.setPos(-0.36, 0, -0.5)
        self.parentFrame.reparentTo(base.a2dTopRight)

        self.toonFrame = MATFrame(
            parent=self.parentFrame,
            text=TTLocalizer.ColorShopToon,
            text_scale=TTLocalizer.CStoonFrame,
            text_pos=(0.0, -0.01, 0.0),
            pos=(0, 0, -0.073),
            scale=1.3,
            arrowcommand=self.__swapAllColor
        )

        self.headFrame = MATFrame(
            parent=self.parentFrame,
            pos=(0, 0, -0.3),
            hpr=(0, 0, 2),
            scale=0.9,
            text=TTLocalizer.ColorShopHead,
            text_scale=0.0625,
            arrowcommand=self.__swapHeadColor
        )

        self.bodyFrame = MATFrame(
            parent=self.parentFrame,
            pos=(0, 0, -0.5),
            hpr=(0, 0, -2),
            scale=0.9,
            text=TTLocalizer.ColorShopBody,
            text_scale=0.0625,
            arrowcommand=self.__swapArmColor
        )

        self.legsFrame = MATFrame(
            parent=self.parentFrame,
            pos=(0, 0, -0.7),
            hpr=(0, 0, 3),
            scale=0.9,
            text=TTLocalizer.ColorShopLegs,
            text_scale=0.0625,
            arrowcommand=self.__swapLegColor
        )

        self.shuffleFetchMsg = 'ColorShopShuffle'
        self.shuffleButton = ShuffleButton.ShuffleButton(self, self.shuffleFetchMsg)
        self.shuffleButton.parentFrame.setPos(0, 0, -0.98)

        self.colorPicker = MATAdvancedColorPicker(
            parent=self.parentFrame
        )
        self.colorPicker.load()
        self.colorPicker.setPos(-0.18, 0, -0.3)
        self.colorPicker.setAnnounceEvent('MAT-advancedColorChanged')

        self.colorFrame = MATFrame(
            parent=self.parentFrame,
            pos=(0, 0, -0.9),
            scale=1.3,
            text=TTLocalizer.ColorShopHead,
            text_scale=0.0625,
            text_pos=(0, -0.015, 0.0),
            arrowcommand=self.swapSelectedPart
        )

        self.colorSelectionButton = MATShuffleButton(
            parent=self.parentFrame,
            pos=(0, 0, -1.15),
            text=TTLocalizer.ColorShopAdvanced,
            text_font=getInterfaceFont(),
            command=self.toggleColorSelection,
            wantArrows=False
        )
        self.colorSelectionButton.setProp('image_scale', (-0.75, 1, 0.75))
        self.colorPicker.hide()
        self.parentFrame.hide()

    def unload(self):
        self.parentFrame.destroy()
        self.toonFrame.destroy()
        self.headFrame.destroy()
        self.bodyFrame.destroy()
        self.legsFrame.destroy()
        self.colorPicker.destroy()
        self.colorFrame.destroy()
        del self.parentFrame
        del self.toonFrame
        del self.headFrame
        del self.bodyFrame
        del self.legsFrame
        del self.colorPicker
        del self.colorFrame
        self.shuffleButton.unload()
        self.ignore('MAT-newToonCreated')
        self.ignore('MAT-advancedColorChanged')

    def updateToonColor(self):
        self.colorValues[self.selectedPart][0].reset(*self.colorPicker.getHsv())

        if self.selectedPart == 'all':
            self.toon.setToonColor(self.colorPicker.getRgb(), self.dna, True, True, True)
            return

        self.toon.setToonColor(
            self.colorPicker.getRgb(),
            self.dna,
            headColorBool=(self.selectedPart == 'head'),
            armColorBool=(self.selectedPart == 'body'),
            legColorBool=(self.selectedPart == 'legs')
        )

    def swapSelectedPart(self, index):
        self.wantFullColorMode = False
        
        if self.selectedPart == 'all':
            if index == 1:
                self.selectedPart = 'head'
            else:
                self.selectedPart = 'legs'
        elif self.selectedPart == 'head':
            if index == 1:
                self.selectedPart = 'body'
            else:
                self.selectedPart = 'all'
        elif self.selectedPart == 'body':
            if index == 1:
                self.selectedPart = 'legs'
            else:
                self.selectedPart = 'head'
        elif self.selectedPart == 'legs':
            if index == 1:
                self.selectedPart = 'all'
            else:
                self.selectedPart = 'body'
                
        if self.selectedPart == 'all':
            self.wantFullColorMode = True
        else:
            for part in ('head', 'body', 'legs'):
                currColor = self.colorValues[part][0].get()

                # Color legitimacy checks
                hue = min(currColor[0], 1.0)
        
                # Add limits
                saturation = min(max(currColor[1], .2), .88)
                value = min(max(currColor[2], .55), .90)

                self.colorValues[part][0].reset(hue, saturation, value)

            self.toon.setToonColor(
                self.colorValues['head'][0].getRgb(),
                self.dna,
                True,
                False,
                False
            )
            self.toon.setToonColor(
                self.colorValues['body'][0].getRgb(),
                self.dna,
                False,
                True,
                False
            )
            self.toon.setToonColor(
                self.colorValues['legs'][0].getRgb(),
                self.dna,
                False,
                False,
                True
            )

        self.updatePicker()
        self.updateToonColor()

        self.colorFrame['text'] = self.selectedPart.capitalize()

    def toggleColorSelection(self):
        if not self.wantAdvancedColor:
            self.wantAdvancedColor = True
            self.colorSelectionButton['text'] = TTLocalizer.ColorShopSimple
            self.colorSelectionButton.setProp("image_scale", (-0.6, 1, 0.6))

            if (self.currentToonSettings[0] == self.currentToonSettings[1]) and (self.currentToonSettings[0] == self.currentToonSettings[2]):
                self.selectedPart = 'all'
            else:
                self.selectedPart = 'head'

            self.toonFrame.hide()
            self.headFrame.hide()
            self.bodyFrame.hide()
            self.legsFrame.hide()
            self.shuffleButton.hideButtons()
            
            self.colorPicker.show()
            self.colorFrame.show()

            self.colorFrame['text'] = self.selectedPart.capitalize()
            self.updatePicker()
        else:
            self.__swapAllColor(0)
            self.wantAdvancedColor = False
            self.colorSelectionButton['text'] = TTLocalizer.ColorShopAdvanced
            self.colorSelectionButton.setProp("image_scale", (-0.75, 1, 0.75))

            self.toonFrame.show()
            self.headFrame.show()
            self.bodyFrame.show()
            self.legsFrame.show()
            self.shuffleButton.showButtons()

            self.colorPicker.hide()
            self.colorFrame.hide()

    def updatePicker(self):
        self.colorPicker.setRgb(*self.colorValues[self.selectedPart][0].getRgb())

    def __swapAllColor(self, offset):
        colorList = self.getGenderColorList(self.dna)
        length = len(colorList)
        choice = (self.headChoice + offset) % length
        self.__updateScrollButtons(choice, length, self.toonFrame.leftArrow, self.toonFrame.rightArrow)
        self.__swapHeadColor(offset)
        oldArmColorIndex = colorList.index(self.currentToonSettings[1])
        oldLegColorIndex = colorList.index(self.currentToonSettings[2])
        self.__swapArmColor(choice - oldArmColorIndex)
        self.__swapLegColor(choice - oldLegColorIndex)
        newColor = colorList[self.headChoice]
        self.colorValues['all'][0].resetRgb(*ToonDNA.allColorsList[newColor])

    def __swapHeadColor(self, offset):
        colorList = self.getGenderColorList(self.dna)
        length = len(colorList)
        self.headChoice = (self.headChoice + offset) % length
        self.__updateScrollButtons(self.headChoice, length, self.headFrame.leftArrow, self.headFrame.rightArrow)
        newColor = colorList[self.headChoice]
        self.currentToonSettings[0] = newColor
        self.dna.colorDNA.headColor.resetRgb(*ToonDNA.allColorsList[newColor])
        self.colorValues['head'][0].resetRgb(*ToonDNA.allColorsList[newColor])
        self.toon.swapToonColor(self.dna)

    def __swapArmColor(self, offset):
        colorList = self.getGenderColorList(self.dna)
        length = len(colorList)
        self.armChoice = (self.armChoice + offset) % length
        self.__updateScrollButtons(self.armChoice, length, self.bodyFrame.leftArrow, self.bodyFrame.rightArrow)
        newColor = colorList[self.armChoice]
        self.currentToonSettings[1] = newColor
        self.dna.colorDNA.armColor.resetRgb(*ToonDNA.allColorsList[newColor])
        self.colorValues['body'][0].resetRgb(*ToonDNA.allColorsList[newColor])
        self.toon.swapToonColor(self.dna)

    def __swapLegColor(self, offset):
        colorList = self.getGenderColorList(self.dna)
        length = len(colorList)
        self.legChoice = (self.legChoice + offset) % length
        self.__updateScrollButtons(self.legChoice, length, self.legsFrame.leftArrow, self.legsFrame.rightArrow)
        newColor = colorList[self.legChoice]
        self.currentToonSettings[2] = newColor
        self.dna.colorDNA.legColor.resetRgb(*ToonDNA.allColorsList[newColor])
        self.colorValues['legs'][0].resetRgb(*ToonDNA.allColorsList[newColor])
        self.toon.swapToonColor(self.dna)

    def __updateScrollButtons(self, choice, length, lButton, rButton):
        if choice == (self.startColor - 1) % length:
            rButton['state'] = DGG.DISABLED
        else:
            rButton['state'] = DGG.NORMAL
        if choice == self.startColor % length:
            lButton['state'] = DGG.DISABLED
        else:
            lButton['state'] = DGG.NORMAL

    def __handleForward(self):
        self.doneStatus = 'next'
        messenger.send(self.doneEvent)

    def __handleBackward(self):
        self.doneStatus = 'last'
        messenger.send(self.doneEvent)

    def changeColor(self):
        self.notify.debug('Entering changeColor')
        colorList = self.getGenderColorList(self.dna)
        newChoice = self.shuffleButton.getCurrChoice()

        newHeadColorIndex = colorList.index(newChoice[0])
        newArmColorIndex = colorList.index(newChoice[1])
        newLegColorIndex = colorList.index(newChoice[2])

        oldHeadColorIndex = colorList.index(self.currentToonSettings[0])
        oldArmColorIndex = colorList.index(self.currentToonSettings[1])
        oldLegColorIndex = colorList.index(self.currentToonSettings[2])

        self.currentToonSettings = [
            newHeadColorIndex,
            newArmColorIndex,
            newLegColorIndex
        ]

        self.__swapHeadColor(newHeadColorIndex - oldHeadColorIndex)
        if self.colorAll:
            self.__swapArmColor(newHeadColorIndex - oldArmColorIndex)
            self.__swapLegColor(newHeadColorIndex - oldLegColorIndex)
        else:
            self.__swapArmColor(newArmColorIndex - oldArmColorIndex)
            self.__swapLegColor(newLegColorIndex - oldLegColorIndex)

    def getCurrToonSetting(self):
        return self.currentToonSettings
