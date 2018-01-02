from pandac.PandaModules import *
from toontown.toonbase import TTLocalizer
import ZoneUtil
from toontown.toonbase import ToontownGlobals


class TrialerForceAcknowledge:
    def __init__(self, doneEvent):
        self.doneEvent = doneEvent
        self.dialog = None
        return

    def enter(self, destHood):
        doneStatus = {
            'mode': 'pass'
        }
        messenger.send(self.doneEvent, [doneStatus])

    def exit(self):
        if self.dialog:
            self.dialog.cleanup()
            self.dialog.unload()
            self.dialog = None
        return

    def handleOk(self):
        messenger.send(self.doneEvent, [self.doneStatus])
