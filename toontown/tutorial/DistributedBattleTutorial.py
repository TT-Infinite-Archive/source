from toontown.battle import DistributedBattle
from direct.directnotify import DirectNotifyGlobal
from toontown.hood import Hood

class DistributedBattleTutorial(DistributedBattle.DistributedBattle):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedBattleTutorial')

    def startTimer(self, ts = 0):
        self.townBattle.timer.hide()

    def playReward(self, ts):
        self.movie.playTutorialReward(ts, self.uniqueName('reward'), self.handleRewardDone)

    def exitReward(self):
        base.cr.playGame.hood.loader.loadInfinite()