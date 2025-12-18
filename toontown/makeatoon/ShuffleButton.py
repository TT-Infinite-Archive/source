from pandac.PandaModules import *
from direct.gui.DirectGui import *
from toontown.toonbase import TTLocalizer
from toontown.toonbase import ToontownGlobals
from .MakeAToonGlobals import *
from direct.directnotify import DirectNotifyGlobal
from direct.interval.IntervalGlobal import *
import random

from .MakeAToonGUI import MATShuffleButton


class ShuffleButton:
    notify = DirectNotifyGlobal.directNotify.newCategory('ShuffleButton')

    def __init__(self, parent, fetchEvent):
        self._parent = parent
        self.fetchEvent = fetchEvent
        self.history = [0]
        self.historyPtr = 0
        self.maxHistory = 10
        self.load()

    def load(self):
        self.parentFrame = DirectFrame(parent=self._parent.parentFrame, relief=DGG.RAISED, pos=(0, 0, -1),
                                       frameColor=(1, 0, 0, 0))

        self.button = MATShuffleButton(parent=self.parentFrame, text_font=ToontownGlobals.getInterfaceFont(),
                                       text=(TTLocalizer.ShuffleButton, TTLocalizer.ShuffleButton, TTLocalizer.ShuffleButton, ''),
                                       command=self.chooseRandom, arrowcommand=self.handleArrow)
        self.button.hideArrows()
        self.button.frame.hide()
        self.lerpDuration = 0.5
        self.showLerp = None
        self.frameShowLerp = LerpColorInterval(self.button.frame, self.lerpDuration, Vec4(1, 1, 1, 1), Vec4(1, 1, 1, 0))
        self.incBtnShowLerp = LerpColorInterval(self.button.rightArrow, self.lerpDuration, Vec4(1, 1, 1, 1), Vec4(1, 1, 1, 0))
        self.decBtnShowLerp = LerpColorInterval(self.button.leftArrow, self.lerpDuration, Vec4(1, 1, 1, 1), Vec4(1, 1, 1, 0))
        self.__updateArrows()
        return

    def unload(self):
        if self.showLerp:
            self.showLerp.finish()
            del self.showLerp
        self._parent = None
        self.parentFrame.destroy()
        self.button.destroy()
        del self.parentFrame
        del self.button
        return

    def showButtons(self):
        self.button.show()
        self.button.frame.hide()

    def hideButtons(self):
        self.button.hide()

    def setChoicePool(self, pool):
        self.pool = pool

    def chooseRandom(self):
        self.saveCurrChoice()
        self.currChoice = []
        for prop in self.pool:
            self.currChoice.append(random.choice(prop))

        self.notify.debug('current choice : %s' % self.currChoice)
        if len(self.history) == self.maxHistory:
            self.history.remove(self.history[0])
        self.history.append(0)
        self.historyPtr = len(self.history) - 1
        if len(self.history) == 2:
            self.startShowLerp()
        self.__updateArrows()
        messenger.send(self.fetchEvent)

    def getCurrChoice(self):
        return self.currChoice

    def saveCurrChoice(self):
        self.currChoice = self._parent.getCurrToonSetting()
        self.history[self.historyPtr] = self.currChoice

    def handleArrow(self, direction):
        self.saveCurrChoice()
        self.historyPtr += direction
        self.currChoice = self.history[self.historyPtr]
        self.__updateArrows()
        messenger.send(self.fetchEvent)

    def __updateArrows(self):
        if self.historyPtr == 0:
            self.button.leftArrow['state'] = DGG.DISABLED
        else:
            self.button.leftArrow['state'] = DGG.NORMAL
        if self.historyPtr >= len(self.history) - 1:
            self.button.rightArrow['state'] = DGG.DISABLED
        else:
            self.button.rightArrow['state'] = DGG.NORMAL

    def startShowLerp(self):
        self.showLerp = Sequence(
            Func(self.button.showArrows),
            Parallel(self.frameShowLerp, self.incBtnShowLerp, self.decBtnShowLerp)
        )
        self.showLerp.start()

    def cleanHistory(self):
        self.history = [0]
        self.historyPtr = 0
        self.button.hideArrows()
