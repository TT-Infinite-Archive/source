from direct.directnotify import DirectNotifyGlobal
from toontown.toonbase import ToontownGlobals
from . import Walk

class PublicWalk(Walk.Walk):
    notify = DirectNotifyGlobal.directNotify.newCategory('PublicWalk')

    def __init__(self, parentFSM, doneEvent):
        Walk.Walk.__init__(self, doneEvent)
        self.parentFSM = parentFSM
        self.hotkeys = ()

    def load(self):
        Walk.Walk.load(self)

    def unload(self):
        Walk.Walk.unload(self)
        del self.parentFSM

    def enter(self, slowWalk = 0):
        Walk.Walk.enter(self, slowWalk)
        base.localAvatar.book.showButton()
        self.hotkeys = (ToontownGlobals.StickerBookHotkey, ToontownGlobals.OptionsPageHotkey)
        self.accept(self.hotkeys[0], self.__handleStickerBookEntry)
        self.accept('enterStickerBook', self.__handleStickerBookEntry)
        self.accept(self.hotkeys[1], self.__handleOptionsEntry)
        base.localAvatar.laffMeter.start()
        base.localAvatar.beginAllowPies()

    def exit(self):
        Walk.Walk.exit(self)
        base.localAvatar.book.hideButton()
        for hotkey in self.hotkeys:
            self.ignore(hotkey)
        self.hotkeys = ()
        self.ignore('enterStickerBook')
        base.localAvatar.laffMeter.stop()
        base.localAvatar.endAllowPies()

    def __handleStickerBookEntry(self):
        currentState = base.localAvatar.animFSM.getCurrentState().getName()
        if currentState == 'jumpAirborne':
            return
        if base.localAvatar.book.isObscured():
            return
        else:
            doneStatus = {}
            doneStatus['mode'] = 'StickerBook'
            messenger.send(self.doneEvent, [doneStatus])
            return

    def __handleOptionsEntry(self):
        currentState = base.localAvatar.animFSM.getCurrentState().getName()
        if currentState == 'jumpAirborne':
            return
        if base.localAvatar.book.isObscured():
            return
        if base.localAvatar.chatMgr.fsm.getCurrentState().getName() in ('normalChat', 'whisperChat', 'whisperChatPlayer'):
            return
        else:
            doneStatus = {}
            doneStatus['mode'] = 'Options'
            messenger.send(self.doneEvent, [doneStatus])
            return
