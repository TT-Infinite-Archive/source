from pandac.PandaModules import *
from toontown.toontowngui import TTDialog
from toontown.toonbase import TTLocalizer
import random
from toontown.hood import ZoneUtil
from toontown.toonbase import ToontownGlobals
from direct.showbase.DirectObject import DirectObject


class DownloadForceAcknowledge(DirectObject):

    def __init__(self, doneEvent):
        self.doneEvent = doneEvent
        self.dialog = None
        return

    def enter(self, zone):
        doneStatus = {}
        if zone not in ToontownGlobals.HoodHierarchy.keys():
            zone = ZoneUtil.getBranchZone(zone)

        if base.cr.zoneManager.getZoneComplete(zone):
            doneStatus['mode'] = 'complete'
            messenger.send(self.doneEvent, [doneStatus])
        else:
            try:
                base.localAvatar.b_setAnimState('neutral', 1)
            except:
                pass

            doneStatus['mode'] = 'incomplete'
            self.doneStatus = doneStatus

            if base.cr.zoneManager.currentRequestedZone != zone:
                base.transitions.fadeScreen(0.5)
                self.dialog = TTDialog.TTDialog(text='Communicating with zone server...', style=TTDialog.NoButtons)
                self.acceptOnce('zoneResponse', self.zoneResponse)
                taskMgr.doMethodLater(1.25, self.sendRequest, 'sendZoneRequest', extraArgs=[zone])
            else:
                self.zoneResponse(False)

    def zoneResponse(self, response):
        base.transitions.noFade()
        self.cleanupDialog()
        if response:
            self.__areaReady()
        else:
            self.__areaNotReady()

    def __areaNotReady(self):
        verb = random.choice(TTLocalizer.DownloadForceAcknowledgeVerbList)
        msg = TTLocalizer.DownloadForceAcknowledgeMsg % {
            'verb': verb
        }
        self.dialog = TTDialog.TTDialog(text=msg, command=self.handleOk, style=TTDialog.Acknowledge)
        self.dialog.show()

    def __areaReady(self):
        self.doneStatus['mode'] = 'complete'
        messenger.send(self.doneEvent, [self.doneStatus])

    def sendRequest(self, zone):
        base.cr.zoneManager.requestZoneData(zone)

    def cleanupDialog(self):
        if self.dialog:
            self.dialog.hide()
            self.dialog.cleanup()
            self.dialog = None
        return

    def exit(self):
        taskMgr.remove('sendZoneRequest')
        self.ignoreAll()
        self.cleanupDialog()

    def handleOk(self, value):
        messenger.send(self.doneEvent, [self.doneStatus])
