from direct.directnotify import DirectNotifyGlobal
from otp.launcher.DownloadWatcher import DownloadWatcher
from toontown.toonbase import TTLocalizer


class ToontownDownloadWatcher(DownloadWatcher):
    notify = DirectNotifyGlobal.directNotify.newCategory('ToontownDownloadWatcher')

    def __init__(self):
        DownloadWatcher.__init__(self)
        self.accept('downloadWatcherUpdate', self.update)

    def update(self, name, percent):
        DownloadWatcher.update(self, name, percent)
        self.text['text'] = TTLocalizer.LoadingDownloadWatcherUpdate % name
