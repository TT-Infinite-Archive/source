from panda3d.core import ConfigVariableInt, ConfigVariableString

from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectAI import DistributedObjectAI
from otp.ai.MagicWordGlobal import *


class MagicWordManagerAI(DistributedObjectAI):
    notify = DirectNotifyGlobal.directNotify.newCategory("MagicWordManagerAI")

    def __init__(self, air):
        DistributedObjectAI.__init__(self, air)
        self.wantCheats = self.air.wantCheats
        self.minimumAccess = ConfigVariableInt(
            'magic-word-minimum-access', MINIMUM_MAGICWORD_ACCESS).getValue()

    def sendMagicWord(self, word, targetId):
        invokerId = self.air.getAvatarIdFromSender()
        invoker = self.air.doId2do.get(invokerId)
        target = self.air.doId2do.get(targetId)
        targets = spellbook.getTargets(word)

        if not invoker:
            self.notify.warning('Magic word %r from unknown avatar %s.' % (word, invokerId))
            return

        if invoker.getAdminAccess() < self.minimumAccess:
            self.air.writeServerEvent('suspicious', invokerId, 'Attempted to issue magic word: %s' % word)
            return

        if not word.split():
            return
        cheat = word.split()[0].lower()  # Remove arguments from word

        if not self.wantCheats and cheat not in [name.lower() for name in NON_CHEATS]:
            self.sendUpdateToAvatarId(invokerId, 'sendMagicWordResponse', ['Cheats are disabled on this server. Only magic words that allow for moderation are enabled.'])
            return

        if targets:
            if target is not None and target.__class__.__name__ not in targets:
                self.sendUpdateToAvatarId(invokerId, 'sendMagicWordResponse',
                                          ['Target is a %s object! Expected: %s' % (target.__class__.__name__, targets)])
                return

        if target is None:
            self.sendUpdateToAvatarId(invokerId, 'sendMagicWordResponse', ['Missing target!'])
            return

        response = spellbook.process(invoker, target, word)
        if response:
            self.sendUpdateToAvatarId(invokerId, 'sendMagicWordResponse', [response])

        if targetId == invokerId:
            # Also do client word in-case it's a client thing
            self.sendUpdateToAvatarId(invokerId, 'doClientWord', [targetId, word])

        self.air.writeServerEvent('magic-word',
                                  invokerId, invoker.getAdminAccess(),
                                  targetId, target.getAdminAccess(),
                                  word, response)


@magicWord(category=CATEGORY_USER, types=[str])
def help(wordName=None):
    if not wordName:
        return 'What were you interested getting help for?'
    word = spellbook.words.get(wordName.lower())
    if not word:
        accessLevel = spellbook.getInvoker().getAdminAccess()
        wname = wordName.lower()
        for key in spellbook.words:
            if spellbook.requiredAccess(spellbook.words[key]) <= accessLevel:
                if wname in key:
                    return 'Did you mean %s' % spellbook.words.get(key).name
        return 'I have no clue what %s is referring to' % wordName
    if spellbook.requiredAccess(word) > spellbook.getInvokerAccess():
        # Don't describe a word they can't run; it should read as nonexistent.
        return 'I have no clue what %s is referring to' % wordName
    return word.doc.strip()


@magicWord(category=CATEGORY_USER, types=[])
def words():
    accessLevel = spellbook.getInvoker().getAdminAccess()
    wordString = None
    for key in spellbook.words:
        word = spellbook.words.get(key)
        if spellbook.requiredAccess(word) <= accessLevel:
            if wordString is None:
                wordString = key
            else:
                wordString += ", "
                wordString += key
    if wordString is None:
        return "You are chopped liver"
    else:
        return wordString


@magicWord(category=CATEGORY_MODERATOR, types=[str])
def kick(reason='No reason specified'):
    """
    Kick the target from the game server.
    """
    target = spellbook.getTarget()
    if target == spellbook.getInvoker():
        return "You can't kick yourself!"
    simbase.air.kickAvatar(target.doId, 'You were kicked by a moderator for the following reason: %s' % reason)
    return "Kicked %s from the game server!" % target.getName()


@magicWord(category=CATEGORY_MODERATOR, types=[int, str])
def ban(days, reason):
    target = spellbook.getTarget()
    if target == spellbook.getInvoker():
        return "You can't ban yourself!"
    if ConfigVariableString('accountdb-type', 'developer').getValue() == 'production':
        return "Accounts are banned from the website's staff tools, which sign them out of the game too."
    if days < 0:
        return 'Ban for 0 days (for good) or more.'
    simbase.air.sendNetEvent('banAccount', [target.getDISLid(), reason, days])
    return "Banned %s's account!" % target.getName()
