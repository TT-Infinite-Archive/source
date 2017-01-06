from direct.directnotify import DirectNotifyGlobal
from toontown.toonbase import TTLocalizer, EventGlobals
from toontown.toontowngui import TTDialog
from direct.gui.DirectGui import DGG
from toontown.guilds import GuildGlobals

globalGuildInvitee = None

def showGuildInvitee(senderName, senderGuildName):
    global globalGuildInvitee
    if globalGuildInvitee is not None:
        globalGuildInvitee.unload()
        globalGuildInvitee = None
    globalGuildInvitee = GuildInvitee(senderName, senderGuildName)


def hideGuildInvitee():
    global globalGuildInvitee
    if globalGuildInvitee is not None:
        globalGuildInvitee.unload()
        globalGuildInvitee = None


def unloadGuildInvitee():
    global globalGuildInvitee
    if globalGuildInvitee is not None:
        globalGuildInvitee.unload()
        globalGuildInvitee = None


class GuildInvitee(TTDialog.TTDialog):
    notify = DirectNotifyGlobal.directNotify.newCategory('GuildInvitee')

    def __init__(self, senderName, senderGuildName, **kw):
        self.senderName = senderName
        self.senderGuildName = senderGuildName
        self.responded = False
        text = TTLocalizer.GuildInviteeInvitation % (senderName, senderGuildName)
        style = TTDialog.TwoChoice
        buttonTextList = [TTLocalizer.lYes, TTLocalizer.lNo]
        command = self.__handleButton
        optiondefs = (('image', DGG.getDefaultDialogGeom(), None),
                      ('relief', None, None),
                      ('dialogName', 'GuildInvitee', None),
                      ('text', text, None),
                      ('style', style, None),
                      ('buttonTextList', buttonTextList, None),
                      ('command', command, None),
                      ('image_color', (1.0, 0.89, 0.77, 1.0), None),
                      ('geom_scale', 0.2, None),
                      ('geom_pos', (-0.1, 0, -0.025), None),
                      ('pad', (0.075, 0.075), None),
                      ('topPad', 0, None),
                      ('midPad', 0, None),
                      ('pos', (0.45, 0, 0.75), None),
                      ('scale', 0.75, None))

        self.defineoptions(kw, optiondefs)
        TTDialog.TTDialog.__init__(self, style=self['style'])
        self.accept(EventGlobals.CancelGuildInvitation, self.__handleCancelFromAbove)
        self.initialiseoptions(GuildInvitee)
        self.show()

    def unload(self):
        self.ignore(EventGlobals.CancelGuildInvitation)
        self.destroy()

    def cleanup(self):
        # Something is wrong with this method
        pass

    def __handleButton(self, value):
        if value == DGG.DIALOG_OK:
            base.cr.guildManager.d_respondToInvite(GuildGlobals.GUILD_INVITE_RESPONSE_ACCEPTED)
            self.responded = True
        elif value == DGG.DIALOG_CANCEL or DGG.DIALOG_NO:
            base.cr.guildManager.d_respondToInvite(GuildGlobals.GUILD_INVITE_RESPONSE_REJECTED)
            self.responded = True
        unloadGuildInvitee()

    def __handleCancelFromAbove(self):
        unloadGuildInvitee()
