from direct.distributed.ClockDelta import *
from . import RaceGlobals

class Racer(object):
    def __init__(self,race,air,avId,zoneId):

        self.race=race
        self.air=air
        self.avId=avId
        self.zoneId=zoneId
        
        self.avatar=air.doId2do[avId]
        self.avatar.takeOutKart(zoneId)

        self.kart=self.avatar.kart

        #race necessities
        self.lapT=0
        self.times=[]
        self.totalTime = 0
        self.maxLap=0
        self.hasGag=False
        self.gagType=0
        self.startingPlace=None
        self.baseTime=0

        #racer State
        self.finished=False
        self.exited=False
        self.anvilTarget=False

        #in case of disconnect
        self.exitEvent=self.air.getAvatarExitEvent(avId)
        self.race.accept(self.exitEvent,race.unexpectedExit,extraArgs=[avId])

    def setLapT(self,numLaps,lapT,timestamp):
        # Laps come one at a time, timed by our clock with a second's grace
        # for the client's own timestamp
        if numLaps > self.maxLap + 1:
            return
        if(numLaps>self.maxLap):
            now = globalClock.getFrameTime() - self.baseTime
            lapTime = min(max(globalClockDelta.networkToLocalTime(timestamp) - self.baseTime, now - 1.0), now)
            if lapTime - self.totalTime < RaceGlobals.getMinimumLapTime(self.race.trackId):
                self.air.writeServerEvent('suspicious', self.avId, 'Racer.setLapT lap %s in %s' % (numLaps, lapTime - self.totalTime))
                return
            self.maxLap=numLaps
            self.times.append(lapTime - self.totalTime)
            self.totalTime = lapTime
        self.lapT=numLaps + lapT
