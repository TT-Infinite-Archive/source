import time
import os


class CrashLogManager:
    def __init__(self, air):
        self.air = air

    def log(self, avId, exception):
        self.air.writeServerEvent('client-exception', avId, exception)


class RemoteCrashLogManager(CrashLogManager):
    def log(self, avId, exception):
        CrashLogManager.log(self, avId, exception)

        self.air.mongodb.crashes.insert_one(
            {'timestamp': int(time.time()), 'avId': avId, 'exception': exception})


class CrashLogManagerAI:
    def __init__(self, air):
        self.manager = RemoteCrashLogManager(air)

    def log(self, avId, exception):
        self.manager.log(avId, exception)
