class VolumeInterval:
    ReadyState = 0
    RunningState = 1
    DoneState = 2

    def __init__(self, sound, volume, time, callback=None):
        self.sound = sound
        self.volume = volume
        self.time = time
        self.callback = callback
        self.stepVol = ((self.sound.getVolume() - float(volume)) / float(time)) / 10.0
        self.state = self.ReadyState
        self.step()

    def step(self):
        self.state = self.RunningState
        self.sound.setVolume(self.sound.getVolume() - self.stepVol)
        if self.stepVol > 0:
            # If we're going down in volume
            self.sound.setVolume(max(self.sound.getVolume(), self.volume))
        elif self.stepVol < 0:
            # If we're going up in volume
            self.sound.setVolume(min(self.sound.getVolume(), self.volume))
        else:
            # We aren't stepping, just set the volume
            self.sound.setVolume(self.volume)
        if self.sound.getVolume() == self.volume:
            self.finish()
        else:
            taskMgr.doMethodLater(0.1, self.step, self.getTaskName(), extraArgs=[])

    def cleanup(self):
        taskMgr.remove(self.getTaskName())

    def finish(self):
        if self.callback:
            self.callback()
        self.cleanup()
        self.state = self.DoneState

    def isRunning(self):
        return self.state == self.RunningState

    def getTaskName(self):
        return 'volumeIntervalTask-%s' % id(self)
