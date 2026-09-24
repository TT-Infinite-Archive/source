from . import PlayingCardGlobals

class PlayingCardBase:

    def __init__(self, value):
        self.faceUp = 1
        self.setValue(value)

    def getRank(self):
        return self.rank

    def getSuit(self):
        return self.suit

    def getValue(self):
        return self.value

    def setImage(self):
        pass

    def setValue(self, value):
        self.value = value
        if self.value == PlayingCardGlobals.Unknown:
            self.suit = None
            self.rank = None
            self.turnDown()
        else:
            self.suit = value // PlayingCardGlobals.MaxRank
            self.rank = value % PlayingCardGlobals.MaxRank
        self.setImage()
        return

    def isFaceUp(self):
        return self.faceUp

    def isFaceDown(self):
        return not self.faceUp

    def turnUp(self):
        self.faceUp = 1
        self.setImage()

    def turnDown(self):
        self.faceUp = 0
        self.setImage()
