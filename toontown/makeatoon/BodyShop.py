from direct.gui.DirectGui import DirectFrame, DGG
from direct.fsm import StateData

from toontown.toonbase import TTLocalizer
from toontown.toon import ToonDNA

from MakeAToonGlobals import *
from MakeAToonGUI import MATFrame
import ShuffleButton


SPECIES = {
    'b': TTLocalizer.AnimalToSpecies['bear'],
    'c': TTLocalizer.AnimalToSpecies['cat'],
    'd': TTLocalizer.AnimalToSpecies['dog'],
    'f': TTLocalizer.AnimalToSpecies['duck'],
    'h': TTLocalizer.AnimalToSpecies['horse'],
    'm': TTLocalizer.AnimalToSpecies['mouse'],
    'p': TTLocalizer.AnimalToSpecies['monkey'],
    'r': TTLocalizer.AnimalToSpecies['rabbit'],
    's': TTLocalizer.AnimalToSpecies['pig']
}


class BodyShop(StateData.StateData):
    notify = directNotify.newCategory('BodyShop')

    def __init__(self, doneEvent):
        StateData.StateData.__init__(self, doneEvent)
        self.toon = None
        self.torsoChoice = 0
        self.legChoice = 0
        self.headChoice = 0
        self.speciesChoice = 0
        return

    def enter(self, toon, shopsVisited = []):
        base.disableMouse()
        self.toon = toon
        self.dna = self.toon.getStyle()
        gender = self.toon.style.getGender()
        self.speciesStart = self.getSpeciesStart()
        self.speciesChoice = self.speciesStart
        self.headChoice = ToonDNA.toonHeadTypes.index(self.dna.head) - ToonDNA.getHeadStartIndex(self.species)
        self.torsoChoice = ToonDNA.toonTorsoTypes.index(self.dna.torso) % 3
        self.legChoice = ToonDNA.toonLegTypes.index(self.dna.legs)
        if CLOTHESSHOP in shopsVisited:
            self.clothesPicked = 1
        else:
            self.clothesPicked = 0
        self.clothesPicked = 1
        if gender == 'm' or ToonDNA.GirlBottoms[self.dna.botTex][1] == ToonDNA.SHORTS:
            torsoPool = ToonDNA.toonTorsoTypes[:3]
        else:
            torsoPool = ToonDNA.toonTorsoTypes[3:6]
        self.__swapSpecies(0)
        self.__swapHead(0)
        self.__swapTorso(0)
        self.__swapLegs(0)
        choicePool = [ToonDNA.toonHeadTypes, torsoPool, ToonDNA.toonLegTypes]
        self.shuffleButton.setChoicePool(choicePool)
        self.accept(self.shuffleFetchMsg, self.changeBody)
        self.acceptOnce('last', self.__handleBackward)
        self.accept('next', self.__handleForward)
        self.acceptOnce('MAT-newToonCreated', self.shuffleButton.cleanHistory)

    def getSpeciesStart(self):
        for species in ToonDNA.toonSpeciesTypes:
            if species == self.dna.head[0]:
                self.species = species
                return ToonDNA.toonSpeciesTypes.index(species)

    def showButtons(self):
        self.parentFrame.show()

    def hideButtons(self):
        self.parentFrame.hide()

    def exit(self):
        try:
            del self.toon
        except:
            self.notify.warning('BodyShop: toon not found')

        self.hideButtons()
        self.ignore('last')
        self.ignore('next')
        self.ignore('enter')
        self.ignore(self.shuffleFetchMsg)

    def load(self):
        self.parentFrame = DirectFrame(relief=DGG.RAISED, pos=(0.98, 0, 0.416), frameColor=(1, 0, 0, 0))
        self.parentFrame.setPos(-0.36, 0, -0.5)
        self.parentFrame.reparentTo(base.a2dTopRight)

        self.speciesFrame = MATFrame(parent=self.parentFrame, pos=(0, 0, -0.073), hpr=(0, 0, 0), scale=1.3,
                                     text='Species', text_scale=0.0625, text_pos=(-0.001, -0.015),
                                     arrowcommand=self.__swapSpecies)

        self.headFrame = MATFrame(parent=self.parentFrame, pos=(0, 0, -0.3), hpr=(0, 0, 2), scale=0.9,
                                  text=TTLocalizer.BodyShopHead, text_scale=0.0625, text_pos=(-0.001, -0.015),
                                  arrowcommand=self.__swapHead)

        self.bodyFrame = MATFrame(parent=self.parentFrame, pos=(0, 0, -0.5), hpr=(0, 0, -2), scale=0.9,
                                  text=TTLocalizer.BodyShopBody, text_scale=0.0625, text_pos=(-0.001, -0.015),
                                  arrowcommand=self.__swapTorso)

        self.legsFrame = MATFrame(parent=self.parentFrame, pos=(0, 0, -0.7), hpr=(0, 0, 3), scale=0.9,
                                  text=TTLocalizer.BodyShopLegs, text_scale=0.0625, text_pos=(-0.001, -0.015),
                                  arrowcommand=self.__swapLegs)

        self.parentFrame.hide()
        self.shuffleFetchMsg = 'BodyShopShuffle'
        self.shuffleButton = ShuffleButton.ShuffleButton(self, self.shuffleFetchMsg)
        return

    def unload(self):
        self.parentFrame.destroy()
        self.speciesFrame.destroy()
        self.headFrame.destroy()
        self.bodyFrame.destroy()
        self.legsFrame.destroy()
        del self.parentFrame
        del self.speciesFrame
        del self.headFrame
        del self.bodyFrame
        del self.legsFrame
        self.shuffleButton.unload()
        self.ignore('MAT-newToonCreated')

    def __swapTorso(self, offset):
        gender = self.toon.style.getGender()
        if not self.clothesPicked:
            length = len(ToonDNA.toonTorsoTypes[6:])
            torsoOffset = 6
        elif gender == 'm':
            length = len(ToonDNA.toonTorsoTypes[:3])
            torsoOffset = 0
            if self.toon.style.topTex not in ToonDNA.MakeAToonBoyShirts:
                randomShirt = ToonDNA.getRandomTop(gender, ToonDNA.MAKE_A_TOON)
                shirtTex, shirtColor, sleeveTex, sleeveColor = randomShirt
                self.toon.style.topTex = shirtTex
                self.toon.style.topTexColor = shirtColor
                self.toon.style.sleeveTex = sleeveTex
                self.toon.style.sleeveTexColor = sleeveColor
            if self.toon.style.botTex not in ToonDNA.MakeAToonBoyBottoms:
                botTex, botTexColor = ToonDNA.getRandomBottom(gender, ToonDNA.MAKE_A_TOON)
                self.toon.style.botTex = botTex
                self.toon.style.botTexColor = botTexColor
        else:
            length = len(ToonDNA.toonTorsoTypes[3:6])
            if self.toon.style.torso[1] == 'd':
                torsoOffset = 3
            else:
                torsoOffset = 0
            if self.toon.style.topTex not in ToonDNA.MakeAToonGirlShirts:
                randomShirt = ToonDNA.getRandomTop(gender, ToonDNA.MAKE_A_TOON)
                shirtTex, shirtColor, sleeveTex, sleeveColor = randomShirt
                self.toon.style.topTex = shirtTex
                self.toon.style.topTexColor = shirtColor
                self.toon.style.sleeveTex = sleeveTex
                self.toon.style.sleeveTexColor = sleeveColor
            if self.toon.style.botTex not in ToonDNA.MakeAToonGirlBottoms:
                if self.toon.style.torso[1] == 'd':
                    botTex, botTexColor = ToonDNA.getRandomBottom(gender, ToonDNA.MAKE_A_TOON, girlBottomType=ToonDNA.SKIRT)
                    self.toon.style.botTex = botTex
                    self.toon.style.botTexColor = botTexColor
                    torsoOffset = 3
                else:
                    botTex, botTexColor = ToonDNA.getRandomBottom(gender, ToonDNA.MAKE_A_TOON, girlBottomType=ToonDNA.SHORTS)
                    self.toon.style.botTex = botTex
                    self.toon.style.botTexColor = botTexColor
                    torsoOffset = 0
        self.torsoChoice = (self.torsoChoice + offset) % length
        self.__updateFrame(self.torsoChoice, length, self.bodyFrame)
        torso = ToonDNA.toonTorsoTypes[torsoOffset + self.torsoChoice]
        self.dna.torso = torso
        self.toon.swapToonTorso(torso)
        self.toon.loop('neutral', 0)

    def __swapLegs(self, offset):
        length = len(ToonDNA.toonLegTypes)
        self.legChoice = (self.legChoice + offset) % length
        self.notify.debug('self.legChoice=%d, length=%d, self.legStart=%d' % (self.legChoice, length, 0))
        self.__updateFrame(self.legChoice, length, self.legsFrame)
        newLeg = ToonDNA.toonLegTypes[self.legChoice]
        self.dna.legs = newLeg
        self.toon.swapToonLegs(newLeg)
        self.toon.loop('neutral', 0)

    def __swapHead(self, offset):
        self.headList = ToonDNA.getHeadList(self.species)
        length = len(self.headList)
        self.headChoice = (self.headChoice + offset) % length
        self.__updateHead()

    def __swapSpecies(self, offset):
        length = len(ToonDNA.toonSpeciesTypes)
        self.speciesChoice = (self.speciesChoice + offset) % length
        self.__updateFrame(self.speciesChoice, length, self.speciesFrame, self.speciesStart)
        self.species = ToonDNA.toonSpeciesTypes[self.speciesChoice]
        self.headList = ToonDNA.getHeadList(self.species)
        self.__changeSpeciesName(self.species)
        maxHeadChoice = len(self.headList) - 1
        if self.headChoice > maxHeadChoice:
            self.headChoice = maxHeadChoice
        self.__updateHead()

    def __updateHead(self):
        self.__updateFrame(self.headChoice, len(self.headList), self.headFrame)
        headIndex = ToonDNA.getHeadStartIndex(self.species) + self.headChoice
        newHead = ToonDNA.toonHeadTypes[headIndex]
        self.dna.head = newHead
        self.toon.swapToonHead(newHead)
        self.toon.loop('neutral', 0)

    def __updateFrame(self, choice, length, frame, start=0):
        if choice == (start - 1) % length:
            frame.rightArrow['state'] = DGG.DISABLED
        elif choice != (start - 1) % length:
            frame.rightArrow['state'] = DGG.NORMAL
        if choice == start % length:
            frame.leftArrow['state'] = DGG.DISABLED
        elif choice != start % length:
            frame.leftArrow['state'] = DGG.NORMAL
        if frame.leftArrow['state'] == DGG.DISABLED and frame.rightArrow['state'] == DGG.DISABLED:
            if choice == start % length:
                frame.leftArrow['state'] = DGG.DISABLED
                frame.rightArrow['state'] = DGG.NORMAL
            elif choice == (start - 1) % length:
                frame.leftArrow['state'] = DGG.NORMAL
                frame.rightArrow['state'] = DGG.DISABLED
            else:
                frame.leftArrow['state'] = DGG.NORMAL
                frame.rightArrow['state'] = DGG.NORMAL

    def __handleForward(self):
        self.doneStatus = 'next'
        messenger.send(self.doneEvent)

    def __handleBackward(self):
        self.doneStatus = 'last'
        messenger.send(self.doneEvent)

    def changeBody(self):
        newChoice = self.shuffleButton.getCurrChoice()
        newHead = newChoice[0]
        newSpeciesIndex = ToonDNA.toonSpeciesTypes.index(ToonDNA.getSpecies(newHead))
        newHeadIndex = ToonDNA.toonHeadTypes.index(newHead) - ToonDNA.getHeadStartIndex(ToonDNA.getSpecies(newHead))
        newTorsoIndex = ToonDNA.toonTorsoTypes.index(newChoice[1])
        newLegsIndex = ToonDNA.toonLegTypes.index(newChoice[2])
        oldHead = self.toon.style.head
        oldSpeciesIndex = ToonDNA.toonSpeciesTypes.index(ToonDNA.getSpecies(oldHead))
        oldHeadIndex = ToonDNA.toonHeadTypes.index(oldHead) - ToonDNA.getHeadStartIndex(ToonDNA.getSpecies(oldHead))
        oldTorsoIndex = ToonDNA.toonTorsoTypes.index(self.toon.style.torso)
        oldLegsIndex = ToonDNA.toonLegTypes.index(self.toon.style.legs)
        self.__swapSpecies(newSpeciesIndex - oldSpeciesIndex)
        self.__swapHead(newHeadIndex - oldHeadIndex)
        self.__swapTorso(newTorsoIndex - oldTorsoIndex)
        self.__swapLegs(newLegsIndex - oldLegsIndex)

    def getCurrToonSetting(self):
        return [self.toon.style.head, self.toon.style.torso, self.toon.style.legs]

    def __changeSpeciesName(self, species):
        self.speciesFrame['text'] = SPECIES.get(species, '')
