from direct.directnotify import DirectNotifyGlobal
from direct.task import Task
from toontown.parties.DistributedPartyTeamActivityAI import DistributedPartyTeamActivityAI
from toontown.parties import PartyGlobals
from toontown.toonbase import TTLocalizer

NORMAL_HIT = 1
CRITICAL_HIT = 3
MID_DISTANCE = 25
MAX_DISTANCE = (NORMAL_HIT << 7)
DIST_MULITPLIER = MID_DISTANCE / float(MAX_DISTANCE - NORMAL_HIT)
PERFECT_WIN = MAX_DISTANCE * 3
GAME_TIED = 2


class DistributedPartyCogActivityAI(DistributedPartyTeamActivityAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedPartyCogActivityAI')

    def __init__(self, air, party, activityInfo):
        DistributedPartyTeamActivityAI.__init__(self, air, party, activityInfo)
        self.scores = {}
        self.highScore = 0
        self.cogDistances = [0, 0, 0]  # Using integers for accuracy

    # For some reason we need these here.
    def pieThrow(self, todo0, todo1, todo2, todo3, todo4, todo5, todo6):
        pass

    def pieHitsToon(self, todo0, todo1, todo2, todo3, todo4):
        pass

    def pieHitsCog(self, toonId, timestamp, hitCogNum, x, y, z, direction, hitHead):
        if self.state != 'Active':
            return

        if toonId not in self.toonsPlaying:
            return

        av = simbase.air.doId2do.get(toonId)
        if not av:
            return

        pointGiven = NORMAL_HIT

        if hitHead:
            self.notify.debug('BOOM HEADSHOT')
            pointGiven = CRITICAL_HIT

        if toonId not in self.scores:
            if -MAX_DISTANCE < self.cogDistances[hitCogNum] < MAX_DISTANCE:
                self.scores[toonId] = pointGiven
        elif -MAX_DISTANCE < self.cogDistances[hitCogNum] < MAX_DISTANCE:
            self.scores[toonId] += pointGiven

        if direction == 1.0:
            self.cogDistances[hitCogNum] += pointGiven
        else:
            self.cogDistances[hitCogNum] -= pointGiven

        if not -MAX_DISTANCE < self.cogDistances[hitCogNum] < MAX_DISTANCE:
            self.cogDistances[hitCogNum] = MAX_DISTANCE if self.cogDistances[hitCogNum] > 0 else -MAX_DISTANCE

        self.sendCogDistances(self.cogDistances)

    def sendCogDistances(self, distances):
        # Have to send the distances as floats down the wire.
        self.sendUpdate('setCogDistances', [[d / 100.0 for d in distances]])

    def getTotalDistances(self):
        return sum(self.cogDistances)

    def setHighScore(self, toonName, score):
        self.highScore = score
        self.sendUpdate('setHighScore', [toonName, score])

    def getHighScore(self):
        avId = max(self.scores)
        return avId, self.scores[avId]

    def toonReady(self):
        avId = self.air.getAvatarIdFromSender()
        if avId not in self.toonsPlaying:
            self.notify.warning('Unknown avatar %s tried to become ready!' % avId)
            return

        self.toonsPlaying[avId] = True

        if self.allToonsReady():
            self.cancelCountdown()
            self.balancePlayers()
            self.setState('Active')
            taskMgr.doMethodLater(self.DURATION, self.enterConclusion, self.uniqueName('duration'))
            
    def enterConclusion(self, task):
        self.setState('Conclusion', [self.getTeamDistance(PartyGlobals.TeamActivityTeam.LEFT),
            self.getTeamDistance(PartyGlobals.TeamActivityTeam.RIGHT)])
        if self.scores:
            avId, topScore = self.getHighScore()
            av = simbase.air.doId2do.get(avId)
            if av:
                if topScore > self.highScore:
                    self.setHighScore(av.getName(), topScore)
        taskMgr.doMethodLater(10, self.awardBeans, self.uniqueName('awardBeans'))
        return Task.done

    def getTeamScore(self, team):
        score = 0
        if team == PartyGlobals.TeamActivityTeam.LEFT:
            for d in self.cogDistances:
                if d > 0:
                    score += self.convertScoreToFeet(d)
        elif team == PartyGlobals.TeamActivityTeam.RIGHT:
            for d in self.cogDistances:
                if d < 0:
                    score += self.convertScoreToFeet(d)
        return int(score)

    def getTeamDistance(self, team):
        dist = 0
        if team == PartyGlobals.TeamActivityTeam.LEFT:
            for d in self.cogDistances:
                if d == 0:
                    dist += MID_DISTANCE
                elif d > 0:
                    dist += self.convertScoreToFeet(d)
                else:
                    dist += (MID_DISTANCE * 2) - self.convertScoreToFeet(d)

        elif team == PartyGlobals.TeamActivityTeam.RIGHT:
            for d in self.cogDistances:
                if d == 0:
                    dist += MID_DISTANCE
                elif d < 0:
                    dist += self.convertScoreToFeet(d)
                else:
                    dist += (MID_DISTANCE * 2) - self.convertScoreToFeet(d)
        return int(dist)

    def convertScoreToFeet(self, score):
        return round(abs(score) * DIST_MULITPLIER + MID_DISTANCE)

    def getWinningTeam(self):
        leftTeam = self.getTeamDistance(PartyGlobals.TeamActivityTeam.LEFT)
        rightTeam = self.getTeamDistance(PartyGlobals.TeamActivityTeam.RIGHT)
        if leftTeam > rightTeam:
            return PartyGlobals.TeamActivityTeam.LEFT
        elif rightTeam > leftTeam:
            return PartyGlobals.TeamActivityTeam.RIGHT
        return GAME_TIED

    def getBeansToAward(self, avId):
        beansToAward = 0
        if self.getWinningTeam() == 2:
            beansToAward = PartyGlobals.CogActivityTieBeans
        elif avId in self.leftTeam:
            if self.getTotalDistances() == -PERFECT_WIN:
                self.notify.debug('Left side got a perfect win')
                beansToAward = PartyGlobals.CogActivityPerfectWinBeans
            elif self.getTotalDistances() == PERFECT_WIN:
                self.notify.debug('Left side got rekt.')
                beansToAward = PartyGlobals.CogActivityPerfectLossBeans
            elif self.getWinningTeam() == PartyGlobals.TeamActivityTeam.LEFT:
                self.notify.debug('Left side won!')
                beansToAward = PartyGlobals.CogActivityWinBeans
            else:
                self.notify.debug('Left side lost! :(')
                beansToAward = PartyGlobals.CogActivityLossBeans
        elif avId in self.rightTeam:
            if self.getTotalDistances() == PERFECT_WIN:
                self.notify.debug('Right side got a perfect win!')
                beansToAward = PartyGlobals.CogActivityPerfectWinBeans
            elif self.getTotalDistances() == -PERFECT_WIN:
                self.notify.debug('Right side got rekt.')
                beansToAward = PartyGlobals.CogActivityPerfectLossBeans
            elif self.getWinningTeam() == PartyGlobals.TeamActivityTeam.RIGHT:
                self.notify.debug('Right side won!')
                beansToAward = PartyGlobals.CogActivityWinBeans
            else:
                self.notify.debug('Right side lost! :(')
                beansToAward = PartyGlobals.CogActivityLossBeans

        if self.isDoubleJelleybeans():
            beansToAward *= 2
        return beansToAward

    def awardBeans(self, task):
        for avId in self.leftTeam:
            av = simbase.air.doId2do.get(avId)
            reward = self.getBeansToAward(avId)
            self.notify.debug('Avatar is in leftTeam')
            message = TTLocalizer.PartyCogRewardMessage % self.getTeamScore(PartyGlobals.TeamActivityTeam.LEFT)
            if self.getWinningTeam() == PartyGlobals.TeamActivityTeam.LEFT:
                bonus = PartyGlobals.CogActivityWinBeans
                message += TTLocalizer.PartyCogRewardBonus % (bonus, (TTLocalizer.PartyCogJellybeanPlural if bonus > 1 else ''))
            self.sendUpdateToAvatarId(avId, 'showJellybeanReward', [reward, av.getMoney(), message])
            av.addMoney(reward)                
        for avId in self.rightTeam:
            av = simbase.air.doId2do.get(avId)
            reward = self.getBeansToAward(avId)
            self.notify.debug('Avatar is in rightTeam')
            message = TTLocalizer.PartyCogRewardMessage % self.getTeamScore(PartyGlobals.TeamActivityTeam.RIGHT)
            if self.getWinningTeam() == PartyGlobals.TeamActivityTeam.RIGHT:
                bonus = PartyGlobals.CogActivityWinBeans
                message += TTLocalizer.PartyCogRewardBonus % (bonus, (TTLocalizer.PartyCogJellybeanPlural if bonus > 1 else ''))            
            self.sendUpdateToAvatarId(avId, 'showJellybeanReward', [reward, av.getMoney(), message])
            av.addMoney(reward)

        self.cleanup()
        self.clearGame()

        return Task.done

    def cleanup(self):
        self.scores = {}
        self.highScore = 0
        self.cogDistances = [0, 0, 0]
        self.sendCogDistances(self.cogDistances)
