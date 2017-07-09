from toontown.battle import DistributedBattle
from direct.directnotify import DirectNotifyGlobal
from toontown.hood import Hood

class DistributedBattleTutorial(DistributedBattle.DistributedBattle):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedBattleTutorial')

    def startTimer(self, ts = 0):
        self.townBattle.timer.hide()

        # if self.battleNumber == 0:
            # self.townBattle.timer.hide()
        # else:
            # self.townBattle.timer.show()

    def playReward(self, ts):
        self.movie.playTutorialReward(ts, self.uniqueName('reward'), self.handleRewardDone)

        # if self.battleNumber > 0:
            # self.movie.playReward()

    # def exitReward(self):
        # base.cr.playGame.hood.loader.loadInfinite()

    # def enterFaceOff(self, ts):
        # pass
        # Unload Infinite and load dummy infinite for battle