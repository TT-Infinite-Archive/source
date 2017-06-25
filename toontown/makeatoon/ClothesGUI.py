from pandac.PandaModules import *
from toontown.toon import ToonDNA
from direct.fsm import StateData
from direct.gui.DirectGui import *
from pandac.PandaModules import *
from MakeAToonGlobals import *
from toontown.toonbase import TTLocalizer
from direct.directnotify import DirectNotifyGlobal
from MakeAToonGUI import MATFrame, MATShuffleButton
import ShuffleButton
import random
CLOTHES_MAKETOON = 0
CLOTHES_TAILOR = 1
CLOTHES_CLOSET = 2

class ClothesGUI(StateData.StateData):
    notify = DirectNotifyGlobal.directNotify.newCategory('ClothesGUI')

    def __init__(self, type, doneEvent, swapEvent = None):
        StateData.StateData.__init__(self, doneEvent)
        self.type = type
        self.toon = None
        self.swapEvent = swapEvent
        self.gender = '?'
        self.girlInShorts = 0
        self.swappedTorso = 0
        self.shirtButtons = []
        self.bottomButtons = []
        return

    def load(self):
        self.parentFrame = DirectFrame(relief=DGG.RAISED, pos=(0.98, 0, 0.416), frameColor=(1, 0, 0, 0))
        self.parentFrame.setPos(-0.36, 0, -0.5)
        self.parentFrame.reparentTo(base.a2dTopRight)
        self.shuffleFetchMsg = 'ClothesShopShuffle'
        self.shuffleButton = ShuffleButton.ShuffleButton(self, self.shuffleFetchMsg)

        #Let's use the old GUI for closets.
        if self.type == CLOTHES_CLOSET or self.type == CLOTHES_TAILOR:
            self.shirtFrame = MATFrame(parent=self.parentFrame, relief=None, pos=(0, 0, -0.4), hpr=(0, 0, 3), scale=1.2,
                                       text=TTLocalizer.ClothesShopShirt, text_scale=0.0575, text_pos=(-0.001, -0.015),
                                       arrowcommand=self.swapTop)

            self.bottomFrame = MATFrame(parent=self.parentFrame, pos=(0, 0, -0.65), hpr=(0, 0, -2), scale=1.2,
                                        text=TTLocalizer.ColorShopToon, text_scale=0.0575, text_pos=(-0.001, -0.015),
                                        arrowcommand=self.swapBottom)
            self.parentFrame.hide()
            return


        #self.shirtStyleFrame = MATFrame(parent=self.parentFrame, pos=(0, 0, 0.2), hpr=(0, 0, 3), scale=1.2,
        #                                text=TTLocalizer.ClothesShopShirtsStyle, text_scale=0.0545, text_pos=(-0.001, -0.015),
        #                                arrowcommand=self.swapTopStyle)
        self.shirtFrame = MATFrame(parent=base.a2dTopLeft,  pos=(.6, 0, -.4), hpr=(0, 0, 3), scale=1.2,
                                   text= TTLocalizer.ClothesShopShirtsColor, text_scale=0.0545, text_pos=(-0.001, -0.015),
                                   arrowcommand=self.swapTopColor)

        #self.bottomStyleFrame = MATFrame(parent=self.parentFrame, pos=(0, 0, -0.4), hpr=(0, 0, -2), scale=1.2,
        #                                    text=TTLocalizer.ClothesShopShortsStyle, text_scale=0.0515, text_pos=(-0.001, -0.015),
        #                                    arrowcommand=self.swapBottomStyle)

        self.bottomFrame = MATFrame(parent=base.a2dTopRight, pos=(-.6, 0, -.4), hpr=(0, 0, -2), scale=1.2, text=TTLocalizer.ClothesShopShortsColor,
                                       text_scale=0.0515, text_pos=(-0.001, -0.015), arrowcommand=self.swapBottomColor)
        self.shirtFrame.hide()
        self.bottomFrame.hide()
        self.parentFrame.hide()
        self.shuffleFetchMsg = 'ClothesShopShuffle'
        self.shuffleButton = ShuffleButton.ShuffleButton(self, self.shuffleFetchMsg)
        return

    def unload(self):
        self.parentFrame.destroy()
        self.shirtFrame.destroy()
        self.bottomFrame.destroy()

        if self.type == CLOTHES_MAKETOON:
        #    self.shirtStyleFrame.destroy()
        #    self.bottomStyleFrame.destroy()
        #    del self.shirtStyleFrame
        #    del self.bottomStyleFrame
            for btn in self.shirtButtons:
                btn.destroy()
                del btn
            for btn in self.bottomButtons:
                btn.destroy()
                del btn
            
        del self.parentFrame
        del self.shirtFrame
        del self.bottomFrame
        self.shuffleButton.unload()
        self.ignore('MAT-newToonCreated')

    def showButtons(self):
        self.parentFrame.show()
        for button in self.shirtButtons:
            button.show()
        for button in self.bottomButtons:
            button.show()
        self.shirtFrame.show()
        self.bottomFrame.show()
            
    def hideButtons(self):
        self.parentFrame.hide()
        for button in self.shirtButtons:
            button.hide()
        for button in self.bottomButtons:
            button.hide()
        self.shirtFrame.hide()
        self.bottomFrame.hide()

    def enter(self, toon):
        self.notify.debug('enter')
        base.disableMouse()
        self.toon = toon
        self.setupScrollInterface()
        if not self.type == CLOTHES_TAILOR:
            currTop = (self.toon.style.topTex,
             self.toon.style.topTexColor,
             self.toon.style.sleeveTex,
             self.toon.style.sleeveTexColor)
            currTopStyle = (self.toon.style.topTex, self.toon.style.sleeveTex)
            currTopIndex = self.tops.index(currTop)
            self.swapTop(currTopIndex - self.topChoice)
            currBottom = (self.toon.style.botTex, self.toon.style.botTexColor)
            currBottomStyle = (self.toon.style.botTex)
            currBottomIndex = self.bottoms.index(currBottom)
            self.swapBottom(currBottomIndex - self.bottomChoice)
        choicePool = [self.tops, self.bottoms]
        self.shuffleButton.setChoicePool(choicePool)
        self.accept(self.shuffleFetchMsg, self.changeClothes)
        self.acceptOnce('MAT-newToonCreated', self.shuffleButton.cleanHistory)
        self.createShirtButtons()
        self.createBottomButtons()
        for button in self.shirtButtons:
            button['image_color'] = (ToonDNA.ClothesColors[self.toon.style.topTexColor]);
            button['image3_color'] = (ToonDNA.ClothesColors[self.toon.style.topTexColor] - Vec4(0, 0, 0, .4));

    def exit(self):
        try:
            del self.toon
        except:
            self.notify.warning('ClothesGUI: toon not found')

        self.hideButtons()
        self.ignore('enter')
        self.ignore('next')
        self.ignore('last')
        self.ignore(self.shuffleFetchMsg)

    def setupButtons(self):
        self.girlInShorts = 0
        if self.gender == 'f':
            if self.type != CLOTHES_MAKETOON:
                if self.bottomChoice == -1:
                    botTex = self.bottoms[0][0]
                else:
                    botTex = self.bottoms[self.bottomChoice][0]
                if ToonDNA.GirlBottoms[botTex][1] == ToonDNA.SHORTS:
                    self.girlInShorts = 1
            else:
                if self.bottomStyleChoice == -1:
                    botTex = self.bottoms[0][0]
                else:
                    botTex = self.bottoms[self.bottomChoice][0]
                if ToonDNA.GirlBottoms[botTex][1] == ToonDNA.SHORTS:
                    self.girlInShorts = 1            
        if self.toon.style.getGender() == 'm':
            if self.type != CLOTHES_MAKETOON:
                self.bottomFrame['text'] = TTLocalizer.ClothesShopShorts
            else:
                self.bottomFrame['text'] = TTLocalizer.ClothesShopShortsColor
        else:
            if self.type != CLOTHES_MAKETOON:
                self.bottomFrame['text'] = TTLocalizer.ClothesShopBottoms
            else:
                self.bottomFrame['text'] = TTLocalizer.ClothesShopBottomsColor
        self.acceptOnce('last', self.__handleBackward)
        self.acceptOnce('next', self.__handleForward)
        return None

    def swapTop(self, offset):
        length = len(self.tops)
        self.topChoice += offset
        if self.topChoice <= 0:
            self.topChoice = 0
        self.updateFrame(self.topChoice, length, self.shirtFrame)
        if self.topChoice < 0 or self.topChoice >= len(self.tops) or len(self.tops[self.topChoice]) != 4:
            self.notify.warning('topChoice index is out of range!')
            return None
        self.toon.style.topTex = self.tops[self.topChoice][0]
        self.toon.style.topTexColor = self.tops[self.topChoice][1]
        self.toon.style.sleeveTex = self.tops[self.topChoice][2]
        self.toon.style.sleeveTexColor = self.tops[self.topChoice][3]
        self.toon.generateToonClothes()
        if self.swapEvent != None:
            messenger.send(self.swapEvent)
        messenger.send('wakeup')

    def swapBottom(self, offset):
        length = len(self.bottoms)
        self.bottomChoice += offset
        if self.bottomChoice <= 0:
            self.bottomChoice = 0
        self.updateFrame(self.bottomChoice, length, self.bottomFrame)
        if self.bottomChoice < 0 or self.bottomChoice >= len(self.bottoms) or len(self.bottoms[self.bottomChoice]) != 2:
            self.notify.warning('bottomChoice index is out of range!')
            return None
        self.toon.style.botTex = self.bottoms[self.bottomChoice][0]
        self.toon.style.botTexColor = self.bottoms[self.bottomChoice][1]
        if self.toon.generateToonClothes() == 1:
            self.toon.loop('neutral', 0)
            self.swappedTorso = 1
        if self.swapEvent != None:
            messenger.send(self.swapEvent)
        messenger.send('wakeup')

    def setTopStyle(self, id):
        for btn in self.shirtButtons:
            btn['state'] = DGG.NORMAL;
            
        self.shirtButtons[id]['state'] = DGG.DISABLED;
    
        self.topStyleChoice = id
        self.toon.style.topTex = self.topStyles[self.topStyleChoice][0]
        self.toon.style.sleeveTex = self.topStyles[self.topStyleChoice][1]
        colors = self.getColors('top')
        colorLength = len(colors)
        if self.topColorChoice < 0 or self.topColorChoice >= colorLength:
            self.topColorChoice = colorLength - 1
        self.updateFrame(self.topColorChoice, colorLength, self.shirtFrame)
        self.toon.style.topTexColor = colors[self.topColorChoice][0]
        self.toon.style.sleeveTexColor = colors[self.topColorChoice][1]
        self.toon.generateToonClothes()
        if self.swapEvent != None:
            messenger.send(self.swapEvent)
        messenger.send('wakeup')      
        
    def setBottomStyle(self, id):
        for btn in self.bottomButtons:
            btn['state'] = DGG.NORMAL;
            
        self.bottomButtons[id]['state'] = DGG.DISABLED;
    
        self.bottomStyleChoice = id
        length = len(self.bottomStyles)
        if self.bottomStyleChoice < 0 or self.bottomStyleChoice >= length:
            self.notify.warning('bottomChoice index is out of range!')
            return None
        self.toon.style.botTex = self.bottomStyles[self.bottomStyleChoice]
        colors = self.getColors('bottom')
        colorLength = len(colors)
        if self.bottomColorChoice < 0 or self.bottomColorChoice >= colorLength:
            self.bottomColorChoice = colorLength - 1
        self.updateFrame(self.bottomColorChoice, colorLength, self.bottomFrame)
        self.toon.style.botTexColor = colors[self.bottomColorChoice]
        if self.toon.generateToonClothes() == 1:
            self.toon.loop('neutral', 0)
            self.swappedTorso = 1
        if self.swapEvent != None:
            messenger.send(self.swapEvent)
        messenger.send('wakeup')
        
    def swapTopStyle(self, offset):
        length = len(self.topStyles)
        self.topStyleChoice += offset
        if self.topStyleChoice <= 0:
            self.topStyleChoice = 0
        self.updateFrame(self.topStyleChoice, length, self.shirtStyleFrame)
        if self.topStyleChoice < 0 or self.topStyleChoice >= length:
            self.notify.warning('topChoice index is out of range!')
            return None
        self.toon.style.topTex = self.topStyles[self.topStyleChoice][0]
        self.toon.style.sleeveTex = self.topStyles[self.topStyleChoice][1]
        colors = self.getColors('top')
        colorLength = len(colors)
        if self.topColorChoice < 0 or self.topColorChoice >= colorLength:
            self.topColorChoice = colorLength - 1
        self.updateFrame(self.topColorChoice, colorLength, self.shirtFrame)
        self.toon.style.topTexColor = colors[self.topColorChoice][0]
        self.toon.style.sleeveTexColor = colors[self.topColorChoice][1]
        self.toon.generateToonClothes()
        if self.swapEvent != None:
            messenger.send(self.swapEvent)
        messenger.send('wakeup')        

    def swapTopColor(self, offset):
        self.topColorChoice += offset    
        colors = self.getColors('top')
        length = len(colors)
        if self.topColorChoice <= 0:
            self.topColorChoice = 0
        self.updateFrame(self.topColorChoice, length, self.shirtFrame)
        if self.topColorChoice < 0 or self.topColorChoice >= length:
            self.notify.warning('topChoice index is out of range!')
            self.topColorChoice = len(colors) - 1
            self.updateFrame(self.topColorChoice, length, self.shirtFrame)
        self.toon.style.topTexColor = colors[self.topColorChoice][0]
        self.toon.style.sleeveTexColor = colors[self.topColorChoice][1]
        self.toon.generateToonClothes()
        for btn in self.shirtButtons:
            btn['image_color'] = (ToonDNA.ClothesColors[self.toon.style.topTexColor]);
            btn['image3_color'] = (ToonDNA.ClothesColors[self.toon.style.topTexColor] - Vec4(0, 0, 0, .4));
        if self.swapEvent != None:
            messenger.send(self.swapEvent)
        messenger.send('wakeup')

    def swapBottomStyle(self, offset):
        length = len(self.bottomStyles)
        self.bottomStyleChoice += offset
        if self.bottomStyleChoice <= 0:
            self.bottomStyleChoice = 0
        self.updateFrame(self.bottomStyleChoice, length, self.bottomStyleFrame)
        if self.bottomStyleChoice < 0 or self.bottomStyleChoice >= length:
            self.notify.warning('bottomChoice index is out of range!')
            return None
        self.toon.style.botTex = self.bottomStyles[self.bottomStyleChoice]
        colors = self.getColors('bottom')
        colorLength = len(colors)
        if self.bottomColorChoice < 0 or self.bottomColorChoice >= colorLength:
            self.bottomColorChoice = colorLength - 1
        self.updateFrame(self.bottomColorChoice, colorLength, self.bottomFrame)
        self.toon.style.botTexColor = colors[self.bottomColorChoice]
        if self.toon.generateToonClothes() == 1:
            self.toon.loop('neutral', 0)
            self.swappedTorso = 1
        if self.swapEvent != None:
            messenger.send(self.swapEvent)
        messenger.send('wakeup')

    def swapBottomColor(self, offset):
        self.bottomColorChoice += offset    
        colors = self.getColors('bottom')
        length = len(colors)
        if self.bottomColorChoice <= 0:
            self.bottomColorChoice = 0
        self.updateFrame(self.bottomColorChoice, length, self.bottomFrame)
        if self.bottomColorChoice < 0 or self.bottomColorChoice >= length:
            self.notify.warning('bottomColor choice index is out of range!')
            self.bottomColorChoice = len(colors)
            self.updateFrame(self.bottomColorChoice, length, self.self.bottomFrame)
        self.toon.style.botTexColor = colors[self.bottomColorChoice]
        if self.toon.generateToonClothes() == 1:
            self.toon.loop('neutral', 0)
            self.swappedTorso = 1
        if self.swapEvent != None:
            messenger.send(self.swapEvent)
        messenger.send('wakeup')

    def updateFrame(self, choice, length, frame):
        if choice >= length - 1:
            frame.rightArrow['state'] = DGG.DISABLED
        else:
            frame.rightArrow['state'] = DGG.NORMAL
        if choice <= 0:
            frame.leftArrow['state'] = DGG.DISABLED
        else:
            frame.leftArrow['state'] = DGG.NORMAL

    def __handleForward(self):
        self.doneStatus = 'next'
        messenger.send(self.doneEvent)

    def __handleBackward(self):
        self.doneStatus = 'last'
        messenger.send(self.doneEvent)

    def resetClothes(self, style):
        if self.toon:
            self.toon.style.makeFromNetString(style.makeNetString())
            if self.swapEvent != None and self.swappedTorso == 1:
                self.toon.swapToonTorso(self.toon.style.torso, genClothes=0)
                self.toon.generateToonClothes()
                self.toon.loop('neutral', 0)
        return

    def changeClothes(self):
        self.notify.debug('Entering changeClothes')
        newChoice = self.shuffleButton.getCurrChoice()
        if newChoice[0] in self.tops:
            newTopIndex = self.tops.index(newChoice[0])
        else:
            newTopIndex = self.topChoice
        if newChoice[1] in self.bottoms:
            newBottomIndex = self.bottoms.index(newChoice[1])
        else:
            newBottomIndex = self.bottomChoice
        oldTopIndex = self.topChoice
        oldBottomIndex = self.bottomChoice
        self.swapTop(newTopIndex - oldTopIndex)
        self.swapBottom(newBottomIndex - oldBottomIndex)

    def getColors(self, type):
        if type == 'top':
            return ToonDNA.getTopColors(self.gender, self.topStyles[self.topStyleChoice], tailorId=ToonDNA.MAKE_A_TOON)

        return ToonDNA.getBottomColors(self.gender, self.bottomStyles[self.bottomStyleChoice], tailorId=ToonDNA.MAKE_A_TOON)

    def getCurrToonSetting(self):
        return [self.tops[self.topChoice], self.bottoms[self.bottomChoice]]
        
    def createShirtButtons(self):
        pos = ((.3, 0, .3),  (.5, 0, .3),  (.7, 0, .3),  (.9, 0, .3),
               (.3, 0, .1),  (.5, 0, .1),  (.7, 0, .1),  (.9, 0, .1),
               (.3, 0, -.1), (.5, 0, -.1), (.7, 0, -.1), (.9, 0, -.1),
               (.3, 0, -.3), (.5, 0, -.3), (.7, 0, -.3), (.9, 0, -.3));
        for x in range(len(self.topStyles)):
            id = self.topStyles[x][0]
            image = ToonDNA.Shirts[id]

            btn = MATShuffleButton(wantArrows=False, image = image,
                image_scale = .06 ,image1_scale = 0.07, image2_scale = 0.07,
                image_color = (1, 1, 1, 1),
                image3_color = (.5, .5, .5, 1), text = (''),
                scale = 0.95, command = self.setTopStyle, extraArgs = [x]);
            btn.reparentTo(base.a2dLeftCenter);
            btn.setPos(pos[x]);
            self.shirtButtons.append(btn);
            
    def createBottomButtons(self):
        pos = ((-.3, 0, .3),  (-.5, 0, .3),  (-.7, 0, .3),  (-.9, 0, .3),
               (-.3, 0, .1),  (-.5, 0, .1),  (-.7, 0, .1),  (-.9, 0, .1),
               (-.3, 0, -.1), (-.5, 0, -.1), (-.7, 0, -.1), (-.9, 0, -.1),
               (-.3, 0, -.3), (-.5, 0, -.3), (-.7, 0, -.3), (-.9, 0, -.3));
        for x in range(len(self.bottomStyles)):
            id = self.bottomStyles[x]
            if self.gender == 'f':
                image = ToonDNA.GirlBottoms[id][0]
            else:
                image = ToonDNA.BoyShorts[id]

            btn = MATShuffleButton(wantArrows=False, image = image,
                image_scale = .06 ,image1_scale = 0.07, image2_scale = 0.07,
                image_color = (1, 1, 1, 1),
                image3_color = (.5, .5, .5, 1), text = (''),
                scale = 0.95, command = self.setBottomStyle, extraArgs = [x]);
            btn.reparentTo(base.a2dRightCenter);
            btn.setPos(pos[x]);
            self.bottomButtons.append(btn);