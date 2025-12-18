import operator
from direct.interval.IntervalGlobal import Func, Track
from direct.task import Task
from panda3d.core import TextNode
from toontown.toonbase.TTLocalizerEnglish import BossLeaderboardLabel
from toontown.toonbase.ToontownGlobals import getSuitFont

TEXT_HEIGHT = -0.05
TEXT_GREEN = (0.0, 1.0, 0.0, 1.0)
TEXT_WHITE = (1.0, 1.0, 1.0, 1.0)


class BossBattleLeaderboard:
    def __init__(self):
        self.avId2Names = {}
        self.avId2Nodes = {}
        self.avId2Damage = {}
        self.avId2FlashTrack = {}
        self.index2Pos = {}
        self.currentIndex = 0
        self.leaderboardLabel = None
        self.leaderboardLabelNP = None
        self.isSorting = False

    def load(self):
        pass

    def hasAvatar(self, avId):
        return avId in list(self.avId2Names.keys())

    def addLeaderboardLabel(self):
        self.leaderboardLabel = TextNode('leaderboardLabel')
        self.leaderboardLabel.setAlign(TextNode.ACenter)
        self.leaderboardLabel.setFlattenFlags(TextNode.FFMedium)
        self.leaderboardLabel.setFont(getSuitFont())
        self.leaderboardLabel.setTextScale(0.075)
        self.leaderboardLabel.setTextColor(*TEXT_WHITE)
        self.leaderboardLabel.setText(BossLeaderboardLabel)
        self.leaderboardLabelNP = aspect2d.attachNewNode(self.leaderboardLabel)
        self.leaderboardLabelNP.reparentTo(base.a2dTopRight)
        self.leaderboardLabelNP.setPos(-0.35, 0.0, -0.1)

    def makeFlashTrack(self, tNode, damage):
        return Track(
            (0.25, Func(tNode.setTextColor, *TEXT_GREEN)),
            (0.50, Func(tNode.setTextColor, *TEXT_WHITE)),
            (0.50, Func(tNode.setText, damage)),
            (0.75, Func(tNode.setTextColor, *TEXT_GREEN)),
            (1.0, Func(tNode.setTextColor, *TEXT_WHITE)),
            (1.25, Func(tNode.setTextColor, *TEXT_GREEN)),
            (1.50, Func(tNode.setTextColor, *TEXT_WHITE)),
            (1.75, Func(tNode.setTextColor, *TEXT_GREEN)),
            (2.0, Func(tNode.setTextColor, *TEXT_WHITE)),
        )

    def addAvatar(self, avId, name, damage):
        if self.currentIndex == 0:
            self.addLeaderboardLabel()

        self.avId2Names[avId] = name
        self.avId2Damage[avId] = damage

        text = TextNode('leaderboard-%d' % avId)
        text.setAlign(TextNode.ACenter)
        text.setFlattenFlags(TextNode.FFMedium)
        text.setFont(getSuitFont())
        text.setTextScale(0.05)
        text.setTextColor(*TEXT_WHITE)
        text.setText(name + ': ' + str(damage))
        textNodePath = aspect2d.attachNewNode(text)
        textNodePath.reparentTo(base.a2dTopRight)
        
        self.index2Pos[self.currentIndex] = (-0.35, 0.0, (TEXT_HEIGHT * (self.currentIndex + 1)) - 0.1)
        textNodePath.setPos(*self.index2Pos[self.currentIndex])
        
        self.currentIndex += 1

        self.avId2Nodes[avId] = [textNodePath, text]
        self.sortLeaderboard()

    def updateAvatar(self, avId, damage):
        if avId in self.avId2Nodes and avId in self.avId2Names:
            self.avId2Damage[avId] = self.avId2Damage[avId] + damage

            if avId in self.avId2FlashTrack:
                if self.avId2FlashTrack[avId].isPlaying():
                    self.avId2FlashTrack[avId].finish()

            damageString = self.avId2Names[avId] + ': ' + str(self.avId2Damage[avId])
            flashTrack = self.makeFlashTrack(self.avId2Nodes[avId][1], damageString)
            flashTrack.start()
            self.avId2FlashTrack[avId] = flashTrack

            self.sortLeaderboard()

    def sortLeaderboard(self):
        if not self.isSorting:
            self.isSorting = True
            for avId in self.avId2Nodes:
                self.avId2Nodes[avId][0].hide()

            sortedTuples = sorted(list(self.avId2Damage.items()), key=operator.itemgetter(1), reverse=True)
            sortedAvIds = [data[0] for data in sortedTuples]

            for avId in self.avId2Nodes:
                self.avId2Nodes[avId][0].setPos(*self.index2Pos[sortedAvIds.index(avId)])

            for avId in self.avId2Nodes:
                self.avId2Nodes[avId][0].show()

            self.isSorting = False
        else:
            taskMgr.remove('checkSort')
            taskMgr.doMethodLater(0.1, self.checkSort, 'checkSort')

    def checkSort(self):
        if self.isSorting:
            return Task.again
        self.sortLeaderboard()
        return Task.done

    def destroy(self):
        taskMgr.remove('checkSort')

        for flashTrack in list(self.avId2FlashTrack.values()):
            flashTrack.finish()

        self.avId2FlashTrack = {}

        for avId in list(self.avId2Nodes.keys()):
            self.avId2Nodes[avId][1].setText('')
            self.avId2Nodes[avId][0].removeNode()

        self.avId2Nodes = {}
        self.avId2Names = {}
        self.currentIndex = 0

        if self.leaderboardLabel:
            self.leaderboardLabel.setText('')

        if self.leaderboardLabelNP:
            self.leaderboardLabelNP.removeNode()
