from direct.task import Task
from toontown.parties import PartyGlobals
from toontown.parties.DistributedPartyTeamActivityAI import DistributedPartyTeamActivityAI
from toontown.toonbase.TTLocalizer import PartyTeamActivityRewardMessage

GAME_TIED = 3
MOVEMENT_MULTIPLIER = 0.04


class DistributedPartyTugOfWarActivityAI(DistributedPartyTeamActivityAI):
    notify = directNotify.newCategory("DistributedPartyTugOfWarActivityAI")
    DURATION = 40
    COUNTDOWN_TIME = 8

    def __init__(self, air, party, activityInfo):
        DistributedPartyTeamActivityAI.__init__(self, air, party, activityInfo)
        self.forceDict = [{}, {}]
        self.keyRateDict = {}
        self.rewardDict = {}
        self.offset = 0
        self.fallIn = False
        self.losingTeam = None

    def toonReady(self):
        avId = self.air.getAvatarIdFromSender()
        if avId not in self.toonsPlaying:
            self.notify.debug('Unknown avatar %s tried to become ready!' % avId)
            return

        self.toonsPlaying[avId] = True

        if avId in self.teamDict[PartyGlobals.TeamActivityTeams.LeftTeam]:
            self.forceDict[PartyGlobals.TeamActivityTeams.LeftTeam][avId] = 0
        else:
            self.forceDict[PartyGlobals.TeamActivityTeams.RightTeam][avId] = 0

        if self.allToonsReady():
            self.balancePlayers()
            self.setState('Active')
            taskMgr.doMethodLater(self.DURATION, self.enterConclusion, self.uniqueName('duration'))

    def setToonsPlaying(self, leftTeamToonIds, rightTeamToonIds):
        self.sendUpdate('setToonsPlaying', [leftTeamToonIds, rightTeamToonIds])

    def updateToonKeyRate(self, toonId, keyRate):
        self.sendUpdate('updateToonKeyRate', [toonId, keyRate])

    def updateToonPositions(self, offset):
        self.sendUpdate('updateToonPositions', [offset])

    def reportKeyRateForce(self, keyRate, force):
        avId = self.air.getAvatarIdFromSender()
        self.keyRateDict[avId] = keyRate
        if avId in self.teamDict[PartyGlobals.TeamActivityTeams.LeftTeam]:
            self.forceDict[PartyGlobals.TeamActivityTeams.LeftTeam][avId] = force
        elif avId in self.teamDict[PartyGlobals.TeamActivityTeams.RightTeam]:
            self.forceDict[PartyGlobals.TeamActivityTeams.RightTeam][avId] = force
        self.updateToonKeyRate(avId, keyRate)
        self.calculateOffset()
        self.updateToonPositions(self.offset)

    def calculateOffset(self):
        f = [0, 0]
        for i in [0, 1]:
            for x in self.forceDict[i].values():
                f[i] += x
        deltaF = f[1] - f[0]
        deltaX = deltaF * MOVEMENT_MULTIPLIER
        self.offset += deltaX
        if self.offset > 32.765:
            self.offset = 32.765
        elif self.offset < -32.765:
            self.offset = -32.765

    def reportFallIn(self, losingTeam):
        if not self.state == 'Active':
            return

        taskMgr.remove(self.uniqueName('duration'))
        self.fallIn = True
        self.losingTeam = losingTeam
        self.enterConclusion()

    def enterConclusion(self, task=None):
        if not self.state == 'Active':
            if task:
                return Task.done
            return

        self.offset = round(self.offset, 2)
        if self.losingTeam:
            self.setState('Conclusion', [self.losingTeam])
        elif self.offset in (-0.01, 0, 0.01):
            self.setState('Conclusion', [GAME_TIED])
        elif self.offset > 0:
            self.setState('Conclusion', [PartyGlobals.TeamActivityTeams.LeftTeam])
        else:
            self.setState('Conclusion', [PartyGlobals.TeamActivityTeams.RightTeam])

        taskMgr.doMethodLater(3, self.processResults, self.uniqueName('awardBeans'))
        if task:
            return Task.done

    def processResults(self, task=None):
        self.getBeansToAward()
        self.awardBeans()
        self.cleanup()
        self.clearGame()
        if task:
            return Task.done

    def getBeansToAward(self):
        if self.fallIn:
            for avId in self.toonsPlaying:
                if avId in self.teamDict[self.losingTeam]:
                    self.rewardDict[int(avId)] = PartyGlobals.TugOfWarFallInLossReward
                else:
                    self.rewardDict[int(avId)] = PartyGlobals.TugOfWarFallInWinReward
        else:
            self.offset = round(self.offset, 2)
            for avId in self.toonsPlaying:
                if self.offset in (-0.01, 0, 0.01):
                    self.rewardDict[int(avId)] = PartyGlobals.TugOfWarTieReward
                elif avId in self.teamDict[0]:
                    if self.offset > 0:
                        self.rewardDict[int(avId)] = PartyGlobals.TugOfWarWinReward
                    else:
                        self.rewardDict[int(avId)] = PartyGlobals.TugOfWarLossReward
                elif avId in self.teamDict[1]:
                    if self.offset < 0:
                        self.rewardDict[int(avId)] = PartyGlobals.TugOfWarWinReward
                    else:
                        self.rewardDict[int(avId)] = PartyGlobals.TugOfWarLossReward
        self.awardBeans()

    def awardBeans(self):
        for avId in self.toonsPlaying:
            av = simbase.air.doId2do.get(avId)
            if not av:
                return
            reward = self.rewardDict[avId]
            if self.isDoubleJelleybeans():
                reward *= 2
            message = PartyTeamActivityRewardMessage % reward
            self.sendUpdateToAvatarId(avId, 'showJellybeanReward', [reward, av.getMoney(), message])
            av.addMoney(reward)

    def cleanup(self):
        self.forceDict = [{}, {}]
        self.keyRateDict = {}
        self.rewardDict = {}
        self.fallIn = False
        self.losingTeam = None
        self.offset = 0
        taskMgr.remove(self.uniqueName('duration'))
        taskMgr.remove(self.uniqueName('awardBeans'))
