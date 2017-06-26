from direct.distributed.DistributedObjectGlobal import DistributedObjectGlobal


class ChatAgent(DistributedObjectGlobal):
    def __init__(self, cr):
        DistributedObjectGlobal.__init__(self, cr)

    def delete(self):
        self.ignoreAll()
        self.cr.chatManager = None
        DistributedObjectGlobal.delete(self)
        return

    def adminChat(self, aboutId, message):
        self.notify.warning('Admin Chat(%s): %s' % (aboutId, message))
        messenger.send('adminChat', [aboutId, message])

    def sendChatMessage(self, message, channel):
        self.sendUpdate('chatMessage', [message, base.localAvatar.getName(), channel])
