from otp.chat.SequenceList import SequenceList

class TTSequenceList(SequenceList):
    MOUNT_POINT = '/'
    if __debug__:
        MOUNT_POINT = '../resources/'
    BLACKLIST_FILEPATH = MOUNT_POINT + 'phase_4/etc/blacklist.json'

    def __init__(self):
        SequenceList.__init__(self, self.BLACKLIST_FILEPATH)