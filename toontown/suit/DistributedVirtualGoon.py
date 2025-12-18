from panda3d.core import CollideMask, CollisionBox, CollisionNode, CollisionSphere, ColorBlendAttrib, Point3, Texture, VBase3, Vec3, Vec4
from direct.interval.IntervalGlobal import *

from toontown.battle import SuitBattleGlobals
from toontown.battle import BattleProps
from toontown.battle import BattleParticles
from toontown.battle.MovieSuitAttacks import getPartTrack
from toontown.battle.MovieUtil import copyProp
from toontown.chat.ChatGlobals import CFTimeout, CFSpeech
from toontown.suit.DistributedCashbotBossGoon import DistributedCashbotBossGoon
from toontown.suit import Suit
from toontown.suit import SuitDNA
from toontown.toonbase.ToontownGlobals import WallBitmask

import random


ID_TO_PROP = {
    0: 'redtape',
    1: 'newspaper',
    2: 'power-tie',
    3: 'pink-slip',
    4: 'teeth',
    5: 'baseball',
    6: 'golf-ball',
    7: 'synergy',
    8: 'write-off',
    9: 'crunch',
}


class DistributedVirtualGoon(DistributedCashbotBossGoon):
    notify = directNotify.newCategory('DistributedVirtualGoon')

    def __init__(self, cr):
        DistributedCashbotBossGoon.__init__(self, cr)
        self.virtualSuit = None
        self.virtualSuitName = 'ls'
        self.attackInfo = []
        self.attackProp = ''
        self.toon = None
        self.propAttackTrack = None
        self.finished = False

    def setSuitName(self, name):
        self.virtualSuitName = name

    def getSuitName(self):
        return self.virtualSuitName

    def setAttackInfo(self, propId, damage):
        self.attackInfo = [propId, damage]

    def getAttackInfo(self):
        return self.attackInfo

    def scaleRadar(self):
        DistributedCashbotBossGoon.scaleRadar(self)
        self.radar.setColorScale(0.7, 0.0, 0.0, 0.8)
        self.radar.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.MAdd))

    def loadVirtualSuit(self):
        dna = SuitDNA.SuitDNA()
        dna.newSuit(self.getSuitName())
        self.virtualSuit = Suit.Suit()
        self.virtualSuit.reparentTo(self)
        self.virtualSuit.setDNA(dna)
        self.virtualSuit.setPos(self, 0.0, 2.5, 0.0)
        self.virtualSuit.makeSkeleton(wantNameInfo=False)
        self.virtualSuit.makeVirtual()
        self.virtualSuit.hideName()
        anims = self.generateSuitAnimDict()
        self.virtualSuit.loadAnims(anims)
        self.virtualSuit.loop('walk', 0)

        synergyBox = CollisionBox(0, 3.5, 10, 1)
        synergyBox.setTangible(0)
        synergyNode = CollisionNode(self.uniqueName('SynergyAttack'))
        synergyNode.setTag('damage', '10')
        synergyNode.addSolid(synergyBox)
        synergyNode.setIntoCollideMask(WallBitmask)
        self.synergyColl = self.virtualSuit.attachNewNode(synergyNode)
        self.synergyColl.setPos(0.0, 9.0, 0.0)
        self.synergyColl.stash()

        self.synergySfx = loader.loadSfx('phase_5/audio/sfx/SA_synergy.ogg')
        self.teeOffSfx = loader.loadSfx('phase_5/audio/sfx/SA_tee_off.ogg')
        self.writeOffSfx = loader.loadSfx('phase_5/audio/sfx/SA_writeoff_pen_only.ogg')
        self.dingSfx = loader.loadSfx('phase_5/audio/sfx/SA_writeoff_ding_only.ogg')

    def announceGenerate(self):
        DistributedCashbotBossGoon.announceGenerate(self)
        if not self.virtualSuit:
            self.loadVirtualSuit()

    def enterWalk(self, avId=None, ts=0):
        DistributedCashbotBossGoon.enterWalk(self, avId, ts)
        self.virtualSuit.loop('walk', 0)

    def exitWalk(self):
        DistributedCashbotBossGoon.exitWalk(self)
        if self.propAttackTrack:
            self.propAttackTrack.finish()
            self.propAttackTrack = None

    def enterStunned(self, ts=0):
        self.ignore(self.uniqueName('entertoonSphere'))
        self.isStunned = 1
        self.notify.debug('enterStunned')

        self.animTrack = Parallel(
            Sequence(
                ActorInterval(self, 'collapse'),
                Func(self.pose, 'collapse', 48),
                Func(self.radar.hide),
                Func(self.virtualSuit.hide),
            ),
            SoundInterval(self.collapseSound, node=self),
            LerpScaleInterval(self.virtualSuit, scale=0.01, duration=0.5),
            LerpScaleInterval(self.radar, scale=0.01, duration=0.5),
        )
        self.animTrack.start(ts)

    def getRecoveryTrack(self):
        return Parallel(
            Sequence(
                ActorInterval(self, 'recovery'),
                Func(self.pose, 'recovery', 96)
            ),
            Func(base.playSfx, self.recoverSound, node=self),
            Sequence(
                Func(self.virtualSuit.show),
                LerpScaleInterval(self.virtualSuit, scale=1.0, duration=0.5)
            ),
            LerpScaleInterval(self.radar, scale=1.0, duration=0.5),
        )

    def makePropAttackTrack(self):
        if self.finished:
            return
        prop = BattleProps.globalPropPool.getProp(self.attackProp)
        propIsActor = True
        animName = 'throw-paper'
        x, y, z, h, p, r = (0.1, 0.2, -0.35, 0, 336, 0)
        if self.attackProp == 'redtape':
            animName = 'throw-object'
            x, y, z, h, p, r = (0.24, 0.09, -0.38, -1.152, 86.581, -76.784)
            propIsActor = False
        elif self.attackProp == 'newspaper':
            animName = 'throw-object'
            propIsActor = False
            x, y, z, h, p, r = (-0.07, 0.17, -0.13, 161.867, -33.149, -48.086)
            prop.setScale(4)
        elif self.attackProp == 'pink-slip':
            animName = 'throw-paper'
            propIsActor = False
            x, y, z, h, p, r = (0.07, -0.06, -0.18, -172.075, -26.715, -89.131)
            prop.setScale(5)
        elif self.attackProp == 'power-tie':
            animName = 'throw-paper'
            propIsActor = False
            x, y, z, h, p, r = (1.16, 0.24, 0.63, 171.561, 1.745, -163.443)
            prop.setScale(4)
        elif self.attackProp == 'baseball':
            animName = 'throw-object'
            propIsActor = False
            x, y, z, h, p, r = (0.04, 0.03, -0.31, 0, 336, 0)
            prop.setScale(4)
        elif self.attackProp == 'teeth':
            animName = 'throw-object'
            propIsActor = True
            x, y, z, h, p, r = -0.05, 0.41, -0.54, 4.465, -3.563, 51.479
            prop.setScale(3)
        elif self.attackProp == 'golf-ball':
            propIsActor = False
            x, y, z = self.getGolfStartPoint()
            h, p, r = 0, 0, 0
            prop.setScale(1.5)

        # Make prop virtual:
        prop.setColorScale(1.0, 0.0, 0.0, 0.8)
        prop.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.MAdd))

        # Prop collisions:
        colNode = CollisionNode(self.uniqueName('SuitAttack'))
        colNode.setTag('damage', str(self.attackInfo[1]))

        bounds = prop.getBounds()
        center = bounds.getCenter()
        radius = bounds.getRadius()
        sphere = CollisionSphere(center.getX(), center.getY(), center.getZ(), radius)
        sphere.setTangible(0)
        colNode.addSolid(sphere)
        colNode.setIntoCollideMask(WallBitmask)
        prop.attachNewNode(colNode)

        toonId = self.toon

        toon = base.cr.doId2do.get(toonId)
        if not toon:
            return

        self.virtualSuit.lookAt(toon)

        if self.virtualSuit.style.body in ['a', 'b']:
            throwDelay = 3
        elif self.virtualSuit.style.body == 'c':
            throwDelay = 2.3
        else:
            throwDelay = 2

        def throwProp():
            if not self.virtualSuit:
                return

            toon = self.cr.doId2do.get(toonId)
            if not toon:
                self.cleanupProp(prop, propIsActor)
                self.finishPropAttack()
                return

            self.virtualSuit.lookAt(toon)

            prop.wrtReparentTo(render)

            hitPos = toon.getPos() + Vec3(0, 0, 2.5)
            distance = (prop.getPos() - hitPos).length()
            speed = 50.0
            if self.attackProp == 'golf-ball':
                speed *= 2

            if self.attackProp == 'teeth':
                throwSequence = Sequence(
                    Parallel(
                        prop.posInterval(distance / speed, hitPos),
                        ActorInterval(prop, 'teeth', duration=distance / speed),
                    ),
                    Func(self.cleanupProp, prop, propIsActor),
                )
            else:
                throwSequence = Sequence(
                    prop.posInterval(distance / speed, hitPos),
                    Func(self.cleanupProp, prop, propIsActor)
                )

            if self.finished:
                return

            throwSequence.start()

        if self.attackProp == 'golf-ball':
            club = BattleProps.globalPropPool.getProp('golf-club')
            club.setScale(1.1)
            track = Sequence(
                Parallel(
                    Track(
                        (0.4, Func(club.reparentTo, self.virtualSuit.getRightHand())),
                        (0.0, Func(club.setPosHpr, 0.0, 0.0, 0.0, 63.097, 43.988, -18.435)),
                        (0.0, Func(prop.reparentTo, self.virtualSuit)),
                        (0.0, Func(prop.setPosHpr, x, y, z, h, p, r)),
                        (0.0, Func(self.sayFaceoffTaunt)),
                        (0.1, Sequence(
                            ActorInterval(self.virtualSuit, 'golf-club-swing'),
                            Func(self.virtualSuit.loop, 'neutral', 0))
                         ),
                        (4.1, SoundInterval(self.teeOffSfx, node=self.virtualSuit)),
                        (throwDelay + 1.5, Func(throwProp)),
                        (throwDelay + 2, Func(club.removeNode)),
                        (throwDelay + 3, Func(self.finishPropAttack))
                    ),
                ),
                Func(self.virtualSuit.setHpr, 0, 0, 0),
                Func(self.virtualSuit.loop, 'walk', 0),
            )
        else:
            track = Sequence(
                Parallel(
                    Sequence(
                        ActorInterval(self.virtualSuit, animName),
                        Func(self.virtualSuit.loop, 'neutral', 0)
                    ),
                    Track(
                        (0.4, Func(prop.reparentTo, self.virtualSuit.getRightHand())),
                        (0.0, Func(prop.setPosHpr, x, y, z, h, p, r)),
                        (0.0, Func(self.sayFaceoffTaunt)),
                        (throwDelay, Func(throwProp)),
                        (throwDelay + 2, Func(self.finishPropAttack))
                    ),
                ),
                Func(self.virtualSuit.setHpr, 0, 0, 0),
                Func(self.virtualSuit.loop, 'walk', 0),
            )
        track.prop = prop
        track.propIsActor = propIsActor

        return track

    def makeSynergyTrack(self):
        particleEffect = BattleParticles.createParticleEffect('Synergy')
        waterfallEffect = BattleParticles.createParticleEffect(file='synergyWaterfall')
        soundTrack = Sequence(
            Wait(0.9),
            SoundInterval(self.synergySfx, node=self.virtualSuit)
        )
        track = Sequence(
            Parallel(
                ActorInterval(self.virtualSuit, 'magic3'),
                Track(
                    (0.0, Func(self.sayFaceoffTaunt)),
                    (0.1, ParticleInterval(waterfallEffect, self.virtualSuit, worldRelative=0, duration=1.9, cleanup=True)),
                    (0.2, ParticleInterval(particleEffect, self.virtualSuit, worldRelative=0, duration=1.9, cleanup=True)),
                    (0.5, Func(self.synergyColl.unstash)),
                ),
                soundTrack
            ),
            Func(self.synergyColl.stash),
            Func(self.virtualSuit.setHpr, 0, 0, 0),
            Func(self.virtualSuit.loop, 'walk', 0),
        )

        return track

    def makeWriteOffTrack(self):
        pad = BattleProps.globalPropPool.getProp('pad')
        pad.setScale(1.89)
        pencil = BattleProps.globalPropPool.getProp('pencil')
        BattleParticles.loadParticles()
        checkmark = copyProp(BattleParticles.getParticle('checkmark'))
        checkmark.setBillboardPointEye()

        # Make prop virtual:
        pad.setColorScale(1.0, 0.0, 0.0, 0.8)
        pad.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.MAdd))
        pencil.setColorScale(1.0, 0.0, 0.0, 0.8)
        pencil.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.MAdd))
        checkmark.setColorScale(1.0, 0.0, 0.0, 0.8)
        checkmark.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.MAdd))

        # Prop collisions:
        colNode = CollisionNode(self.uniqueName('SuitAttack'))
        colNode.setTag('damage', str(self.attackInfo[1]))

        bounds = checkmark.getBounds()
        center = bounds.getCenter()
        radius = bounds.getRadius()
        sphere = CollisionSphere(center.getX(), center.getY(), center.getZ(), radius)
        sphere.setTangible(0)
        colNode.addSolid(sphere)
        colNode.setIntoCollideMask(WallBitmask)
        checkmark.attachNewNode(colNode)

        toonId = self.toon

        toon = base.cr.doId2do.get(toonId)
        if not toon:
            return

        self.virtualSuit.lookAt(toon)

        if self.virtualSuit.style.body in ['a', 'b']:
            throwDelay = 3
        elif self.virtualSuit.style.body == 'c':
            throwDelay = 2.3
        else:
            throwDelay = 2

        def throwProp():
            if not self.virtualSuit:
                return

            toon = self.cr.doId2do.get(toonId)
            if not toon:
                self.cleanupProp(checkmark, False)
                self.finishPropAttack()
                return

            self.virtualSuit.lookAt(toon)

            checkmark.wrtReparentTo(render)

            hitPos = toon.getPos() + Vec3(0, 0, 2.5)
            distance = (checkmark.getPos() - hitPos).length()
            speed = 50.0

            throwSequence = Sequence(
                checkmark.posInterval(distance / speed, hitPos),
                Func(self.cleanupProp, checkmark, False)
            )

            throwSequence.start()

        pencilTrack = Sequence(
            Wait(0.5),
            Func(pencil.setPosHpr, -0.47, 1.08, 0.28, 21.045, 12.702, -176.374),
            Func(pencil.reparentTo, self.virtualSuit.getRightHand()),
            LerpScaleInterval(pencil, 0.5, Point3(1.5, 1.5, 1.5),
                              startScale=Point3(0.01)),
            Wait(throwDelay),
            Func(checkmark.reparentTo, render),
            Func(checkmark.setScale, 1.6),
            Func(checkmark.setPosHpr, pencil, 0, 0, 0, 0, 0, 0),
            Func(checkmark.setP, 0),
            Func(checkmark.setR, 0),
            Func(throwProp),
            Wait(0.3),
            LerpScaleInterval(pencil, 0.5, Point3(0.01, 0.01, 0.01)),
            Func(pencil.removeNode),
        )

        suitTrack = Sequence(
            ActorInterval(self.virtualSuit, 'hold-pencil'),
            Func(self.virtualSuit.loop, 'neutral', 0),
        )

        soundTrack = Sequence(
            Wait(2.3),
            SoundInterval(self.writeOffSfx, duration=0.9, node=self.virtualSuit),
            SoundInterval(self.dingSfx, node=self.virtualSuit)
        )

        padTrack = Track(
            (0.0, Func(pad.setPosHpr, -0.25, 1.38, -0.08, -19.078, -6.603, -171.594)),
            (0.4, Func(pad.reparentTo, self.virtualSuit.getLeftHand())),
            (3.0, Func(pad.removeNode)),
        )

        track = Sequence(
            Parallel(
                suitTrack, soundTrack, padTrack, pencilTrack, Func(self.sayFaceoffTaunt)
            ),
            Func(self.virtualSuit.loop, 'walk', 0)
        )
        return track

    def makeCrunchTrack(self):
        toonId = self.toon

        toon = base.cr.doId2do.get(toonId)
        if not toon:
            return

        self.virtualSuit.lookAt(toon)

        if self.virtualSuit.style.body in ['a', 'b']:
            throwDelay = 3
        elif self.virtualSuit.style.body == 'c':
            throwDelay = 2.3
        else:
            throwDelay = 2

        numberNames = ['one',
         'two',
         'three',
         'four',
         'five',
         'six']
        BattleParticles.loadParticles()
        numberSpill1 = BattleParticles.createParticleEffect(file='numberSpill')
        numberSpill2 = BattleParticles.createParticleEffect(file='numberSpill')
        spillTexture1 = random.choice(numberNames)
        spillTexture2 = random.choice(numberNames)
        BattleParticles.setEffectTexture(numberSpill1, 'audit-' + spillTexture1)
        BattleParticles.setEffectTexture(numberSpill2, 'audit-' + spillTexture2)
        numberSpillTrack1 = getPartTrack(numberSpill1, 1.1, 2.2, [numberSpill1, self.virtualSuit, 0])
        numberSpillTrack2 = getPartTrack(numberSpill2, 1.5, 1.0, [numberSpill2, self.virtualSuit, 0])
        numberSprayTracks = Parallel()
        numOfNumbers = random.randint(5, 9)
        for i in range(0, numOfNumbers - 1):
            nextSpray = BattleParticles.createParticleEffect(file='numberSpray')
            nextTexture = random.choice(numberNames)
            BattleParticles.setEffectTexture(nextSpray, 'audit-' + nextTexture)
            nextStartTime = random.random() * 0.6 + 3.03
            nextDuration = random.random() * 0.4 + 1.4
            nextSprayTrack = getPartTrack(nextSpray, nextStartTime, nextDuration, [nextSpray, self.virtualSuit, 0])
            numberSprayTracks.append(nextSprayTrack)

        def throwProp(prop):
            if not self.virtualSuit:
                return

            toon = self.cr.doId2do.get(toonId)
            if not toon:
                self.cleanupProp(prop, False)
                self.finishPropAttack()
                return

            self.virtualSuit.lookAt(toon)

            prop.wrtReparentTo(render)

            hitPos = toon.getPos() + Vec3(0, 0, 2.5)
            distance = (prop.getPos() - hitPos).length()
            speed = 50.0

            throwSequence = Sequence(
                prop.posInterval(distance / speed, hitPos),
                Func(self.cleanupProp, prop, False)
            )

            throwSequence.start()

        numberTracks = Parallel()
        for i in range(0, numOfNumbers):
            texture = random.choice(numberNames)
            next = copyProp(BattleParticles.getParticle('audit-' + texture))
            next.reparentTo(self.virtualSuit.getRightHand())
            next.setScale(0.01, 0.01, 0.01)
            next.setColor(Vec4(0.0, 0.0, 0.0, 1.0))
            next.setPos(random.random() * 0.6 - 0.3, random.random() * 0.6 - 0.3, random.random() * 0.6 - 0.3)
            next.setHpr(VBase3(-1.15, 86.58, -76.78))

            # Make prop virtual:
            next.setColorScale(1.0, 0.0, 0.0, 0.8)
            next.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.MAdd))

            # Prop collisions:
            colNode = CollisionNode(self.uniqueName('SuitAttack'))
            colNode.setTag('damage', str(self.attackInfo[1]))

            bounds = next.getBounds()
            center = bounds.getCenter()
            radius = bounds.getRadius()
            sphere = CollisionSphere(center.getX(), center.getY(), center.getZ(), radius)
            sphere.setTangible(0)
            colNode.addSolid(sphere)
            colNode.setIntoCollideMask(WallBitmask)
            next.attachNewNode(colNode)

            numberTrack = Sequence(
                Wait(throwDelay),
                Parallel(
                    LerpScaleInterval(next, 0.6, Point3(1.0, 1.0, 1.0)),
                    Func(throwProp, next),
                ),
            )
            numberTracks.append(numberTrack)

            suitTrack = Parallel(
                    Func(self.sayFaceoffTaunt),
                    Sequence(
                        ActorInterval(self.virtualSuit, 'throw-object'),
                        ActorInterval(self.virtualSuit, 'neutral')
                    ),
            )

            return Sequence(
                Parallel(
                    suitTrack,
                    numberSpillTrack1,
                    numberSpillTrack2,
                    numberTracks,
                    numberSprayTracks
                ),
                Func(self.virtualSuit.loop, 'walk', 0),
                Func(self.virtualSuit.setHpr, 0, 0, 0),
            )

    def sayFaceoffTaunt(self, custom=False, phrase="", dialogue=None):
        if custom:
            self.virtualSuit.setChatAbsolute(phrase, CFSpeech | CFTimeout, dialogue)
        else:
            if self.attackProp == 'teeth':
                taunt = SuitBattleGlobals.getAttackTaunt(random.choice(['Bite', 'Chomp']))
            elif self.attackProp == 'synergy':
                taunt = SuitBattleGlobals.getAttackTaunt('Synergy')
            elif self.attackProp == 'golf-ball':
                taunt = SuitBattleGlobals.getAttackTaunt('TeeOff')
            elif self.attackProp == 'baseball':
                taunt = SuitBattleGlobals.getAttackTaunt('PlayHardball')
            elif self.attackProp == 'write-off':
                taunt = SuitBattleGlobals.getAttackTaunt('WriteOff')
            elif self.attackProp == 'crunch':
                taunt = SuitBattleGlobals.getAttackTaunt('Crunch')
            else:
                taunt = SuitBattleGlobals.getFaceoffTaunt(self.virtualSuit.style.name, self.doId)
            self.virtualSuit.setChatAbsolute(taunt, CFSpeech | CFTimeout)

    def __localToonHit(self, entry):
        self.ignore('enter' + self.uniqueName('SuitAttack'))
        self.ignore('enter' + self.uniqueName('SynergyAttack'))
        taskMgr.doMethodLater(3, self.cooldown, self.uniqueName('attackCooldown'))

        damage = int(entry.getIntoNode().getTag('damage'))
        self.sendUpdate('hitToon', [damage])

        messenger.send('interrupt-pie')
        place = self.cr.playGame.getPlace()
        currentState = None
        if place:
            currentState = place.fsm.getCurrentState().getName()
        if currentState != 'walk' and currentState != 'finalBattle' and currentState != 'crane':
            return

        self.boss.doZapToon(base.localAvatar, fling=1, shake=0)

    def cooldown(self, task=None):
        self.accept('enter' + self.uniqueName('SuitAttack'), self.__localToonHit)
        self.accept('enter' + self.uniqueName('SynergyAttack'), self.__localToonHit)

    def attackToon(self):
        if not self.getAttackInfo():
            self.notify.warning('No attack info is set!')
            return

        if self.finished:
            return

        self.attackProp = ID_TO_PROP.get(self.attackInfo[0], 'redtape')
        if self.propAttackTrack:
            self.propAttackTrack.finish()
            self.propAttackTrack = None

        self.accept('enter' + self.uniqueName('SuitAttack'), self.__localToonHit)
        self.accept('enter' + self.uniqueName('SynergyAttack'), self.__localToonHit)

        if self.attackProp == 'synergy':
            self.propAttackTrack = self.makeSynergyTrack()
        elif self.attackProp == 'write-off':
            self.propAttackTrack = self.makeWriteOffTrack()
        elif self.attackProp == 'crunch':
            self.propAttackTrack = self.makeCrunchTrack()
        else:
            self.propAttackTrack = self.makePropAttackTrack()

        self.propAttackTrack.start()

    def setToon(self, toonId):
        self.toon = toonId

    def cleanupProp(self, prop, propIsActor):
        if propIsActor:
            if hasattr(prop, 'cleanup'):
                prop.cleanup()
            prop.removeNode()
        else:
            prop.removeNode()

    def finishPropAttack(self):
        if self.virtualSuit:
            self.virtualSuit.setHpr(0, 0, 0)
            self.virtualSuit.loop('walk', 0)

    def getGolfStartPoint(self):
        if self.virtualSuitName == 'ym':
            return 2.1, 0, 0.1
        elif self.virtualSuitName == 'tbc':
            return 4.1, 0, 0.1
        elif self.virtualSuitName == 'm':
            return 3.2, 0, 0.1
        elif self.virtualSuitName == 'rb':
            return 4.2, 0, 0.1
        else:
            return 2.1, 0, 0.1

    def generateSuitAnimDict(self):
        animDict = dict()
        if self.virtualSuit.style.body == 'c':
            animDict['throw-paper'] = 'phase_3.5/models/char/suitC-throw-paper'
            animDict['throw-object'] = 'phase_3.5/models/char/suitC-throw-paper'
        else:
            animDict['throw-paper'] = 'phase_5/models/char/suit%s-throw-paper' % (self.virtualSuit.style.body.upper())
            animDict['throw-object'] = 'phase_5/models/char/suit%s-throw-object' % (self.virtualSuit.style.body.upper())

        if self.virtualSuit.style.body == 'c':
            animDict['magic3'] = 'phase_5/models/char/suitC-magic2.bam'
        else:
            animDict['magic3'] = 'phase_5/models/char/suit%s-magic3.bam' % (self.virtualSuit.style.body.upper())

        if self.virtualSuit.style.body == 'a':
            animDict['golf-club-swing'] = 'phase_5/models/char/suitA-golf-club-swing'

        return animDict

    def enterOff(self):
        if self.virtualSuit:
            self.virtualSuit.hide()

        DistributedCashbotBossGoon.enterOff(self)

    def exitOff(self):
        if self.virtualSuit:
            self.virtualSuit.show()

        DistributedCashbotBossGoon.exitOff(self)

    def delete(self):
        if self.propAttackTrack:
            self.propAttackTrack.pause()
            self.propAttackTrack = None
            self.finished = True
        self.virtualSuit.cleanup()
        self.virtualSuit.removeNode()
        self.virtualSuit = None
        self.ignore('enter' + self.uniqueName('SuitAttack'))
        self.ignore('enter' + self.uniqueName('SynergyAttack'))
        DistributedCashbotBossGoon.delete(self)
