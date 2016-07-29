from BossCog import AnimList, GenericModel, ModelDict
from toontown.battle.BattleProps import globalPropPool
from toontown.suit import Suit
from toontown.toonbase.ToontownGlobals import getBuildingNametagFont
from direct.gui.DirectGui import DirectWaitBar, DirectFrame, DGG
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import Sequence, Parallel, ActorInterval, Func, Wait
from direct.task.Task import Task
from panda3d.core import TextNode, VBase4


class BossBattleHealthBar(DirectFrame):
    def __init__(self, dept, maxHp, **kw):
        DirectFrame.__init__(self, parent=render2d, relief=None, **kw)
        self.dept = dept
        self.filePrefix = ModelDict[dept]
        self.maxHp = float(maxHp)
        self.hp = self.maxHp

        self.head = None
        self.headActor = None
        self.animDict = {}

        self.healthBar = None
        self.redBar = None
        self.healthCondition = None
        self.hitInterval = None
        self.damageTrack = None
        self.blinkTask = None

        self.dizzy = False
        self.helmet = False

        self.healthColors = Suit.Suit.healthColors

        self.finished = False

    def load(self):
        self.head = loader.loadModel(self.filePrefix + '-head-zero')

        for anim in AnimList:
            self.animDict[anim] = '%s-%s-%s' % (GenericModel, 'head', anim)

        self.headActor = Actor(self.head, self.animDict)
        self.headActor.hide()
        self.headActor.setBin("fixed", 40)
        self.headActor.setDepthTest(True)
        self.headActor.setDepthWrite(True)

        self.headActor.reparentTo(self)
        self.headActor.setHpr(-90, 0, 270)
        self.headActor.setScale(0.025)
        self.headActor.setPos(-0.25, 0.0, 0.65)
        self.headActor.setPlayRate(2.0, 'turn2Fb')
        self.headActor.loop('Ff_neutral')

        self.eyes = loader.loadModel('phase_10/models/cogHQ/CashBotBossEyes.bam')
        self.eyes.setPosHprScale(4.5, 0, -2.5, 90, 90, 0, 0.4, 0.4, 0.4)
        self.eyes.reparentTo(self.headActor)
        self.eyes.hide()

        self.stars = globalPropPool.getProp('stun')
        self.stars.setPosHprScale(7, 0, 0, 0, 0, -90, 3, 3, 3)
        self.stars.loop('stun')

        self.safe = loader.loadModel('phase_10/models/cogHQ/CBSafe.bam')
        self.safe.reparentTo(self.headActor)
        self.safe.setPosHpr(-1, 0, 0.2, 0, -90, 90)
        self.safe.setBin("fixed", 40)
        self.safe.setDepthTest(True)
        self.safe.setDepthWrite(True)
        self.safe.hide()

        self.headActor.show()

        self.healthBar = DirectWaitBar(parent=self, pos=(0.05, 0, 0.75), relief=DGG.SUNKEN,
                                       frameSize=(-1.75, 1.75, -0.3, 0.3),
                                       borderWidth=(0.02, 0.02), scale=0.12, range=1, sortOrder=50,
                                       frameColor=(0.5, 0.5, 0.5, 0.5), barColor=(0.75, 0.75, 1.0, 0.8), text='',
                                       text_scale=0.4, text_fg=(1, 1, 1, 1), text_align=TextNode.ACenter,
                                       text_shadow=(0, 0, 0, 1), text_pos=(0, -0.05), text_font=getBuildingNametagFont())

        self.healthBar.setBin('fixed', 50)

        self.redBar = DirectWaitBar(parent=self, pos=(0.05, 0, 0.75), relief=DGG.FLAT,
                                    frameSize=(-1.75, 1.75, -0.3, 0.3),
                                    borderWidth=(0.02, 0.02), scale=0.12, range=1,
                                    frameColor=(0.5, 0.5, 0.5, 0.01), barColor=(1.0, 0.0, 0.0, 0.65), text='')

        self.redBar.setBin('fixed', 40)

        self.updateHealthBar(self.maxHp)

    def getHealthCondition(self, hp):
        hp /= self.maxHp
        if hp > 0.95:
            condition = 0
        elif hp > 0.9:
            condition = 1
        elif hp > 0.8:
            condition = 2
        elif hp > 0.7:
            condition = 3
        elif hp > 0.6:
            condition = 4
        elif hp > 0.5:
            condition = 5
        elif hp > 0.3:
            condition = 6
        elif hp > 0.15:
            condition = 7
        elif hp > 0.05:
            condition = 8
        elif hp > 0.0:
            condition = 9
        else:
            condition = 9

        return condition

    def updateHealthBar(self, hp):

        def update(health):
            if self.redBar:
                self.redBar.setProp('value', health / self.maxHp)

        lastHp = self.hp
        if lastHp == self.maxHp == hp:
            self.setHealthBar(self.maxHp)
            self.hp = float(hp)
            self.cleanupHit()
            return

        self.cleanupHit()
        self.cleanupDamage()

        self.damageTrack = Sequence(Func(self.doHit))
        delay = 1.0 / float(lastHp - hp)
        if delay < 0.05:
            delay = 0.05

        redBarTrack = Sequence()
        healthBarTrack = Sequence()
        for i in xrange(int(lastHp - hp)):
            lastHp -= 1

            redBarTrack.append(Func(update, lastHp))
            redBarTrack.append(Wait(delay))

            healthBarTrack.append(Func(self.setHealthBar, lastHp))
            healthBarTrack.append(Wait(delay / 3.0))

        self.damageTrack.append(Parallel(redBarTrack, healthBarTrack))

        self.damageTrack.start()
        self.hp = float(hp)

    def setHealthBar(self, hp):
        self.healthCondition = self.getHealthCondition(hp)

        if self.healthCondition == 9 and hp > 0:
            if self.blinkTask is None:
                self.startBlinkTask()
        elif self.blinkTask:
            self.stopBlinkTask()

        if self.healthBar:
            self.healthBar.setProp('text', str(int(hp)))
            self.healthBar.setProp('barColor', self.healthColors[self.healthCondition])
            self.healthBar.setProp('value', hp / self.maxHp)

    def cleanupHit(self, finish=1):
        if self.hitInterval:
            if finish:
                self.hitInterval.finish()
            else:
                self.hitInterval.pause()
            self.hitInterval = None
        return

    def cleanupDamage(self):
        if self.damageTrack:
            self.damageTrack.finish()
            self.damageTrack = None

    def doHit(self):
        self.cleanupHit()
        if not self.headActor or self.headActor.isEmpty() or self.finished:
            if self.hitInterval:
                if self.hitInterval.isPlaying():
                    self.hitInterval.pause()
                self.hitInterval = None
            return

        self.hitInterval = Sequence(
            Parallel(
                Sequence(
                    Func(self.headActor.setColorScale, 1, 1, 1, 1),
                    self.headActor.colorScaleInterval(0.1, colorScale=VBase4(1, 0, 0, 1)),
                    self.headActor.colorScaleInterval(0.3, colorScale=VBase4(1, 1, 1, 1))
                ),
                ActorInterval(self.headActor, 'turn2Fb')
            ),
            Func(self.headActor.loop, 'Ff_neutral')
        )

        if self.headActor and not self.headActor.isEmpty() and not self.finished:
            self.hitInterval.start()

    def startBlinkTask(self):
        self.blinkTask = Task.loop(Task(self.__blinkRed), Task.pause(0.75), Task(self.__blinkGray), Task.pause(0.1))
        taskMgr.add(self.blinkTask, 'bosshealthbar-blink-task')

    def __blinkRed(self, task):
        if not self.healthBar:
            return
        self.healthBar.setProp('barColor', self.healthColors[8])
        return Task.done

    def __blinkGray(self, task):
        if not self.healthBar:
            return
        self.healthBar.setProp('barColor', self.healthColors[9])
        return Task.done

    def stopBlinkTask(self):
        taskMgr.remove('bosshealthbar-blink-task')
        self.blinkTask = None

    def setDizzy(self, dizzy):
        self.dizzy = dizzy

        if dizzy:
            self.stars.reparentTo(self.headActor)
        else:
            self.stars.detachNode()

    def setHelmet(self, helmet):
        self.helmet = helmet

        if helmet:
            self.safe.show()
            self.eyes.show()

        else:
            self.safe.hide()
            self.eyes.hide()

    def destroy(self):
        self.finished = True
        self.cleanupHit(finish=0)
        self.cleanupDamage()
        self.stars.cleanup()
        self.stopBlinkTask()

        if self.redBar:
            self.redBar.destroy()
            self.redBar = None

        if self.healthBar:
            self.healthBar.destroy()
            self.healthBar = None

        if self.headActor:
            self.headActor.delete()
            self.headActor = None

        self.head.removeNode()
        self.safe.removeNode()
        self.eyes.removeNode()
