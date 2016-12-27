from toontown.battle import DistributedBattle
from direct.directnotify import DirectNotifyGlobal

class DistributedBattleTutorial(DistributedBattle.DistributedBattle):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedBattleTutorial')

    def generate(self):
        DistributedBattle.DistributedBattle.generate(self)
        self.reparentTo(base.cr.playGame.hood.loader.islands[0])

    def startTimer(self, ts = 0):
        self.townBattle.timer.hide()

    def playReward(self, ts):
        self.movie.playTutorialReward(ts, self.uniqueName('reward'), self.handleRewardDone)
