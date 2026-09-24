from direct.directnotify.DirectNotifyGlobal import *
from otp.avatar import AvatarDNA
notify = directNotify.newCategory('CharDNA')
charTypes = ['mk',
 'vmk',
 'mn',
 'wmn',
 'g',
 'sg',
 'd',
 'fd',
 'dw',
 'p',
 'wp',
 'cl',
 'dd',
 'shdd',
 'ch',
 'da',
 'pch',
 'jda']

class CharDNA(AvatarDNA.AvatarDNA):

    def __init__(self, type = None, dna = None, r = None, b = None, g = None):
        if type != None:
            if type == 'c':
                self.newChar(dna)
        else:
            self.type = 'u'
        return

    def __str__(self):
        if self.type == 'c':
            return 'type = char, name = %s' % self.name
        else:
            return 'type undefined'

    def __defaultChar(self):
        self.type = 'c'
        self.name = charTypes[0]

    def newChar(self, name = None):
        if name == None:
            self.__defaultChar()
        else:
            self.type = 'c'
            if name in charTypes:
                self.name = name
            else:
                notify.error('unknown avatar type: %s' % name)
        return

    def getType(self):
        if self.type == 'c':
            type = self.getCharName()
        else:
            notify.error('Invalid DNA type: %s' % self.type)
        return type

    def getCharName(self):
        if self.name == 'mk':
            return 'mickey'
        elif self.name == 'vmk':
            return 'vampire_mickey'
        elif self.name == 'mn':
            return 'minnie'
        elif self.name == 'wmn':
            return 'witch_minnie'
        elif self.name == 'g':
            return 'goofy'
        elif self.name == 'sg':
            return 'super_goofy'
        elif self.name == 'd':
            return 'donald'
        elif self.name == 'dw':
            return 'donald-wheel'
        elif self.name == 'fd':
            return 'franken_donald'
        elif self.name == 'dd':
            return 'daisy'
        elif self.name == 'shdd':
            return 'sockHop_daisy'
        elif self.name == 'p':
            return 'pluto'
        elif self.name == 'wp':
            return 'western_pluto'
        elif self.name == 'cl':
            return 'clarabelle'
        elif self.name == 'ch':
            return 'chip'
        elif self.name == 'da':
            return 'dale'
        elif self.name == 'pch':
            return 'police_chip'
        elif self.name == 'jda':
            return 'jailbird_dale'
        else:
            notify.error('unknown char type: %s' % self.name)
