from direct.directnotify import DirectNotifyGlobal
from direct.showbase.DirectObject import DirectObject
from toontown.battle import SuitBattleGlobals
from toontown.suit import SuitDNA
import random
import time
from direct.task import Task

class SuitInvasionManagerAI(DirectObject):
    """
    Manages invasions of Suits
    """

    notify = DirectNotifyGlobal.directNotify.newCategory('SuitInvasionManagerAI')

    # Cogs spent between shard status updates-- the website's count moves
    REPORT_EVERY = 25

    def __init__(self, air):
        DirectObject.__init__(self)

        self.air = air
        self.invading = 0
        self.cogType = None
        self.cogName = ""
        self.isSkeleton = 0
        self.totalNumCogs = 0
        self.numCogsRemaining = 0
        # 0 when the invasion runs until the Cogs are gone
        self.endTime = 0
        # When this shard will next try an invasion of its own
        self.nextInvasion = 0

        # Set of cog types to choose from See
        # SuitBattleGlobals.SuitAttributes.keys() for all choices I did not
        # put the highest level Cogs from each track in here to keep them
        # special and only found in buildings. I threw in the Flunky just
        # for fun.
        self.invadingCogTypes = (
            # Corporate
            'f', # Flunky
            'hh', # Head Hunter
            'cr', # Corporate Raider
            # Sales
            'tf', # Two-faced
            'm', # Mingler
            # Money
            'mb', # Money Bags
            'ls', # Loan shark
            # Legal
            'sd', # Spin Doctor
            'le', # Legal Eagle
            )

        # Picked from randomly how many cogs will invade
        # This might need to be adjusted based on population(?)
        self.invadingNumList = (1000, 2000, 3000, 4000)

        # Minimum time between invasions on this shard (in seconds)
        # No more than 1 per 2 days
        self.invasionMinDelay = 2 * 24 * 60 * 60
        # Maximum time between invasions on this shard (in seconds)
        # At least once every 7 days
        self.invasionMaxDelay = 7 * 24 * 60 * 60

        # The website drives invasions through the UberDOG's gateway
        self.accept('startInvasion', self.handleStartInvasion)
        self.accept('stopInvasion', self.handleStopInvasion)
        self.accept('queryShardStatus', self.sendShardStatus)

        # Kick off the first invasion
        self.waitForNextInvasion()

    def getCogName(self, cogType):
        return SuitBattleGlobals.SuitAttributes.get(cogType)["name"]

    def delete(self):
        taskMgr.remove(self.taskName("cogInvasionMgr"))
        taskMgr.remove(self.taskName("cogInvasionDuration"))
        self.ignoreAll()

    def computeInvasionDelay(self):
        # Compute the delay until the next invasion
        return ((self.invasionMaxDelay - self.invasionMinDelay) * random.random()
                + self.invasionMinDelay)

    def tryInvasionAndWaitForNext(self, task):
        # Start the invasion if there is not one already
        if self.getInvading():
            self.notify.warning("invasionTask: tried to start random invasion, but one is in progress")
        else:
            self.notify.info("invasionTask: starting random invasion")
            cogType = random.choice(self.invadingCogTypes)
            totalNumCogs = random.choice(self.invadingNumList)
            self.startInvasion(cogType, totalNumCogs)
        # In either case, fire off the next invasion
        self.waitForNextInvasion()
        return Task.done

    def waitForNextInvasion(self):
        taskMgr.remove(self.taskName("cogInvasionMgr"))
        delay = self.computeInvasionDelay()
        self.nextInvasion = int(time.time() + delay)
        self.notify.info("invasionTask: waiting %s seconds until next invasion" % delay)
        taskMgr.doMethodLater(delay, self.tryInvasionAndWaitForNext,
                              self.taskName("cogInvasionMgr"))
        self.sendShardStatus()

    def getInvading(self):
        return self.invading

    def getCogType(self):
        return self.cogType, self.isSkeleton

    def getNumCogsRemaining(self):
        return self.numCogsRemaining

    def getTotalNumCogs(self):
        return self.totalNumCogs

    def startInvasion(self, cogType, totalNumCogs, skeleton=0, duration=0):
        if self.invading:
            self.notify.warning("startInvasion: already invading cogType: %s numCogsRemaining: %s" %
                                (cogType, self.numCogsRemaining))
            return 0
        if not SuitBattleGlobals.SuitAttributes.get(cogType):
            self.notify.warning("startInvasion: unknown cogType: %s" % cogType)
            return 0

        self.notify.info("startInvasion: cogType: %s totalNumCogs: %s skeleton: %s duration: %s" %
                          (cogType, totalNumCogs, skeleton, duration))
        self.invading = 1
        self.cogType = cogType
        self.isSkeleton = skeleton
        self.totalNumCogs = totalNumCogs
        self.numCogsRemaining = self.totalNumCogs
        self.cogName = self.getCogName(cogType)

        # Whichever runs out first ends the invasion: the Cogs or the timer
        if duration > 0:
            self.endTime = int(time.time()) + duration
            taskMgr.doMethodLater(duration, self.durationExpiredTask,
                                  self.taskName("cogInvasionDuration"))
        else:
            self.endTime = 0

        # Tell the news manager that an invasion is beginning
        self.air.newsManager.invasionBegin(self.cogType, self.totalNumCogs, self.isSkeleton)

        # And the Shticker book's district list, through the district's stats
        deptIndex, typeIndex = divmod(
            SuitDNA.suitHeadTypes.index(self.cogType), SuitDNA.suitsPerDept)
        self.air.districtStats.b_setInvasionStatus([deptIndex, typeIndex])

        # Get rid of all the current cogs on the streets
        # (except those already in battle, they can stay)
        for suitPlanner in self.air.suitPlanners.values():
            suitPlanner.flySuits()

        self.sendShardStatus()

        # Success!
        return 1

    def durationExpiredTask(self, task):
        self.notify.info("durationExpiredTask: the invasion is over")
        self.stopInvasion()
        return Task.done

    def spendInvadingCog(self):
        """
        Charges the invasion for one Cog. getCogType() is the look without one.
        """
        if not self.invading:
            return
        self.numCogsRemaining -= 1
        self.notify.debug("spendInvadingCog: spent cog: %s, num remaining: %s" %
                          (self.cogType, self.numCogsRemaining))
        if self.numCogsRemaining <= 0:
            self.stopInvasion()
        elif self.numCogsRemaining % self.REPORT_EVERY == 0:
            self.sendShardStatus()

    def getInvadingCog(self):
        self.spendInvadingCog()
        return self.getCogType()

    def stopInvasion(self):
        if not self.invading:
            return

        self.notify.info("stopInvasion: invasion is over now")
        taskMgr.remove(self.taskName("cogInvasionDuration"))
        # Tell the news manager that an invasion is ending
        self.air.newsManager.invasionEnd(self.cogType, 0, self.isSkeleton)
        self.air.districtStats.b_setInvasionStatus([])
        self.invading = 0
        self.cogType = None
        self.isSkeleton = 0
        self.totalNumCogs = 0
        self.numCogsRemaining = 0
        self.cogName = ""
        self.endTime = 0
        # Get rid of all the current invasion cogs on the streets
        # (except those already in battle, they can stay)
        for suitPlanner in self.air.suitPlanners.values():
            suitPlanner.flySuits()

        self.sendShardStatus()

    def getInvasionStatus(self):
        if not self.invading:
            return None

        return {
            'cogType': self.cogType,
            'cogName': self.cogName,
            'skeleton': bool(self.isSkeleton),
            'total': self.totalNumCogs,
            'remaining': self.numCogsRemaining,
            # 0 when the invasion has no timer on it
            'endTime': self.endTime
        }

    def sendShardStatus(self):
        """
        Let the UberDOG know what is invading, so the website/launcher can show it.
        """
        self.air.sendNetEvent(
            'shardStatus',
            [self.air.ourChannel,
             {'invasion': self.getInvasionStatus(),
              'nextInvasion': self.nextInvasion}])

    # --- WEBSITE COMMANDS ---

    def handleStartInvasion(self, requestId, shardId, cogType, totalNumCogs,
                            skeleton, duration):
        if shardId != self.air.ourChannel:
            return

        if self.getInvading():
            self.respond(requestId, False, 'This district is already invaded.')
        elif not SuitBattleGlobals.SuitAttributes.get(cogType):
            self.respond(requestId, False, 'No such Cog: %s' % cogType)
        elif self.startInvasion(cogType, totalNumCogs, skeleton, duration):
            self.respond(requestId, True, None)
        else:
            self.respond(requestId, False, 'The invasion could not be started.')

    def handleStopInvasion(self, requestId, shardId):
        if shardId != self.air.ourChannel:
            return

        if not self.getInvading():
            self.respond(requestId, False, 'This district is not invaded.')
            return

        self.stopInvasion()
        self.respond(requestId, True, None)

    def respond(self, requestId, ok, error):
        self.air.sendNetEvent('invasionResponse-%s' % requestId, [ok, error])

    # Need this here since this is not a distributed object
    def taskName(self, taskString):
        return (taskString + "-" + str(hash(self)))
