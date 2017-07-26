from pandac.PandaModules import *
from toontown.toontowngui import TTDialog
from toontown.toonbase import TTLocalizer
import random

class DownloadForceAcknowledge:

    def __init__(self, doneEvent):
        self.doneEvent = doneEvent
        self.dialog = None
        return

    def enter(self, zone):
        doneStatus = {}
        if base.cr.zoneManager.getZoneComplete(zone):
            doneStatus['mode'] = 'complete'
            messenger.send(self.doneEvent, [doneStatus])
        else:
            try:
                base.localAvatar.b_setAnimState('neutral', 1)
            except:
                pass

            if base.cr.zoneManager.currentRequestedZone != zone:
                base.cr.zoneManager.requestZoneData(zone)

            doneStatus['mode'] = 'incomplete'
            self.doneStatus = doneStatus
            # percentComplete = base.zoneManager.getPercentZoneComplete(zone)
            phaseName = ''  # TTLocalizer.LauncherPhaseNames[phase]
            verb = random.choice(TTLocalizer.DownloadForceAcknowledgeVerbList)
            msg = TTLocalizer.DownloadForceAcknowledgeMsg % {'verb': verb}
            self.dialog = TTDialog.TTDialog(text=msg, command=self.handleOk, style=TTDialog.Acknowledge)
            self.dialog.show()

    def exit(self):
        if self.dialog:
            self.dialog.hide()
            self.dialog.cleanup()
            self.dialog = None
        return

    def handleOk(self, value):
        messenger.send(self.doneEvent, [self.doneStatus])
