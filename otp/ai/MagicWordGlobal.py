import traceback

from direct.directnotify import DirectNotifyGlobal

from otp.ai.LiveMagicWordAccess import LIVE_ACCESS, LIVE_DEFAULT_ACCESS

_notify = DirectNotifyGlobal.directNotify.newCategory('MagicWordGlobal')

FAILURE_RESPONSE = 'The command did not execute. Please see game logs.'


class MagicError(Exception):
    pass


def ensureAccess(access, msg='Insufficient access'):
    if spellbook.getInvokerAccess() < access:
        raise MagicError(msg)


class Spellbook:
    """
    The Spellbook manages the list of all Magic Words that have been registered
    anywhere in the system. When the MagicWordManager(AI) wants to process a
    Magic Word, it is passed off to the Spellbook, which performs the operation.

    To add Magic Words to the Spellbook, use the @magicWord() decorator.
    """

    def __init__(self):
        self.words = {}

        self.currentInvoker = None
        self.currentTarget = None

        self.accessOverrides = {}
        self.accessDefault = None
        self._defaulted = set()

    def addWord(self, word):
        self.words[word.name.lower()] = word  # lets make this stuff case insensitive

    def useLiveAccess(self):
        self.accessOverrides = LIVE_ACCESS
        self.accessDefault = LIVE_DEFAULT_ACCESS

    def requiredAccess(self, word):
        if self.accessDefault is None:
            return word.access
        name = word.name.lower()
        override = self.accessOverrides.get(name)
        if override is None:
            override = self.accessDefault
            if name not in self._defaulted:
                self._defaulted.add(name)
                _notify.warning('Magic word %r is not in the live table; '
                                'holding it at %d.' % (word.name, override))
        return max(word.access, override)

    def process(self, invoker, target, incantation):
        self.currentInvoker = invoker
        self.currentTarget = target
        word, args = (incantation.split(' ', 1) + [''])[:2]

        try:
            return self.doWord(word, args)
        except MagicError as e:
            return ' '.join(e.args)
        except Exception:
            _notify.warning('Magic word %r raised for %s:\n%s'
                            % (incantation, invoker, traceback.format_exc()))
            return FAILURE_RESPONSE
        finally:
            self.currentInvoker = None
            self.currentTarget = None

    def doWord(self, wordName, args):
        wordName = wordName.lower()
        word = self.words.get(wordName)

        if not word:
            if process == 'ai':
                for key in self.words:
                    if self.requiredAccess(self.words[key]) <= self.getInvokerAccess():
                        if wordName in key:
                            return 'Did you mean %s' % self.words.get(key).name
            if not word:
                return

        ensureAccess(self.requiredAccess(word))
        if self.getTarget() and self.getTarget() != self.getInvoker():
            if self.getInvokerAccess() <= self.getTarget().getAdminAccess():
                raise MagicError('Target must have lower access')

        result = word.run(args)
        if result is not None:
            return str(result)

    def getInvoker(self):
        return self.currentInvoker

    def getTarget(self):
        return self.currentTarget

    def getInvokerAccess(self):
        if not self.currentInvoker:
            return 0
        return self.currentInvoker.getAdminAccess()

    def getTargets(self, word):
        if word == "":
            return
        word = self.words.get(word.split()[0].lower())
        if word is None:
            return []

        return word.targets


spellbook = Spellbook()


# CATEGORIES
class MagicWordCategory:
    def __init__(self, name, defaultAccess=200):
        self.name = name
        self.defaultAccess = defaultAccess


CATEGORY_UNKNOWN = MagicWordCategory('Unknown')
CATEGORY_USER = MagicWordCategory('User', defaultAccess=100)
CATEGORY_MODERATOR = MagicWordCategory('Moderator', defaultAccess=200)
CATEGORY_ADMINISTRATOR = MagicWordCategory('Administrator', defaultAccess=300)
CATEGORY_HOST = MagicWordCategory('Host', defaultAccess=400)

MINIMUM_MAGICWORD_ACCESS = CATEGORY_USER.defaultAccess
PRODUCTION_MAGICWORD_ACCESS = CATEGORY_MODERATOR.defaultAccess
ACCESS_ADMINISTRATOR = 600
ACCESS_SYSTEM_ADMINISTRATOR = 700
GM_ICON_LEVELS = (0, 200, 300, 400, 500, ACCESS_ADMINISTRATOR, ACCESS_SYSTEM_ADMINISTRATOR)

NON_CHEATS = ['ban', 'kick', 'warn', 'mute', 'system', 'gmIcon', 'target']

class MagicWord:
    def __init__(self, name, func, types, targets, access, doc):
        self.name = name
        self.func = func
        self.types = types
        self.targets = targets
        self.access = access
        self.doc = doc

    def parseArgs(self, string):
        maxArgs = self.func.__code__.co_argcount
        minArgs = maxArgs - (len(self.func.__defaults__) if self.func.__defaults__ else 0)

        args = string.split(None, maxArgs-1)[:maxArgs]
        if len(args) < minArgs:
            raise MagicError('Magic word %s requires at least %d arguments' % (self.name, minArgs))

        output = []
        for i, (type, arg) in enumerate(zip(self.types, args)):
            try:
                targ = type(arg)
            except (TypeError, ValueError):
                raise MagicError('Argument %d of magic word %s must be %s' % (i, self.name, type.__name__))

            output.append(targ)

        return output

    def run(self, rawArgs):
        args = self.parseArgs(rawArgs)
        return self.func(*args)


class MagicWordDecorator:
    """
    This class manages Magic Word decoration. It is aliased as magicWord, so that
    the @magicWord(...) construct instantiates this class and has the resulting
    object process the Magic Word's construction.
    """

    def __init__(self, name=None, types=[str], targets=['DistributedToonAI'], access=None, category=CATEGORY_UNKNOWN):
        self.name = name
        self.types = types
        self.category = category
        self.targets = targets

        if access is not None:
            self.access = access
        else:
            self.access = self.category.defaultAccess

    def __call__(self, mw):
        # This is the actual decoration routine. We add the function 'mw' as a
        # Magic Word to the Spellbook, using the attributes specified at construction
        # time.

        name = self.name
        if name is None:
            name = mw.__name__

        word = MagicWord(name, mw, self.types, self.targets, self.access, mw.__doc__)
        spellbook.addWord(word)

        return mw

magicWord = MagicWordDecorator
