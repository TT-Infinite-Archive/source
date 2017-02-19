from direct.directnotify import DirectNotifyGlobal
from direct.fsm.FSM import FSM
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.MsgTypes import *
from otp.ai.MagicWordGlobal import *
from direct.distributed.DistributedObjectAI import DistributedObjectAI

import datetime
import time
import os


class BanFSM(FSM):
    def __init__(self, mgr, air, avId, comment, duration):
        FSM.__init__(self, 'banFSM-%s' % avId)
        self.air = air
        self.mgr = mgr
        self.avId = avId

        # Needed variables for the actual banning.
        self.comment = comment
        self.duration = duration
        self.DISLid = None
        self.accountId = None
        self.avName = None
        self.mac_address = None
        self.public_ip = None

    def ejectPlayer(self):
        av = self.air.doId2do.get(self.avId)
        if not av:
            return

        # Send the client a 'CLIENTAGENT_EJECT' with the players name.
        datagram = PyDatagram()
        datagram.addServerHeader(
                av.GetPuppetConnectionChannel(self.avId),
                self.air.ourChannel, CLIENTAGENT_EJECT)
        datagram.addUint16(152)
        datagram.addString(self.avName)
        self.air.send(datagram)

    def dbCallback(self, dclass, fields):
        if dclass != self.air.dclassesByName['AccountAI']:
            return

        self.accountId = fields.get('ACCOUNT_ID')

        if not self.accountId:
            return

        if self.duration != 0:
            now = datetime.datetime.now()
            self.duration = int(time.mktime((now + datetime.timedelta(days=self.duration)).timetuple()))

        self.request('Waiting')

    def getAvatarDetails(self):
        av = self.air.doId2do.get(self.avId)
        if not av:
            return

        self.DISLid = av.getDISLid()
        self.avName = av.getName()

    def cleanup(self):
        self.air = None
        self.avId = None

        self.DISLid = None
        self.avName = None
        self.accountId = None
        self.comment = None
        self.duration = None

    def enterStart(self):
        self.getAvatarDetails()
        self.air.dbInterface.queryObject(self.air.dbId, self.DISLid,
                                         self.dbCallback)

    def exitStart(self):
        pass

    def enterOff(self):
        self.cleanup()

    def exitOff(self):
        pass

    def enterWaiting(self):
        self.mgr.sendUpdateToAvatarId(self.avId, 'requestUserInfo', [])

    def exitWaiting(self):
        pass

    def enterBan(self):
        self.ejectPlayer()

    def exitBan(self):
        pass


class BanManagerAI(DistributedObjectAI):
    BAN_LIST_FILE = 'banned_players.txt'
    notify = DirectNotifyGlobal.directNotify.newCategory('BanManagerAI')

    def __init__(self, air):
        DistributedObjectAI.__init__(self, air)
        self.air = air
        self.banFSMs = {}
        self.banQueue = []
        self.banList = []

        if not os.path.exists(self.BAN_LIST_FILE):
            banList = open(self.BAN_LIST_FILE, 'w+')
            banList.close()
        else:
            self.readBans()

        self.accept('banCheck', self.banCheck)

    def readBans(self):
        banList = open(self.BAN_LIST_FILE, 'r+')
        bans = banList.readlines()
        for ban in bans:
            if ban not in self.banList:
                self.banList.append(ban)

        banList.close()

    def banCheck(self, sender, mac_addr, ip_addr):
        timestamp = 0
        isBanned = False
        for ban in self.banList:
            if mac_addr in ban:
                timestamp = int(ban.split(':')[1])
                isBanned = True
                break

            if ip_addr in ban:
                timestamp = int(ban.split(':')[1])
                isBanned = True
                break

        if timestamp and int(time.time()) > timestamp:
            isBanned = False

        if timestamp != 0:
            # This is by far the ugliest math I've ever written, save your brain cells..
            difference = int(timestamp) - time.time()
            days = max(0, int(difference / 86400))
            hours = max(0, int((difference / 3600)-(24 * days)))
            minutes = max(0, int((difference - ((86400 * days) + (3600 * hours)))/60))
            seconds = max(0, int(difference - ((86400 * days) + (3600 * hours) + (60 * minutes))))
            banLengthString = 'You have been banned from this server. Your ban will expire in:\n' \
                              '{0}d, {1}h, {2}m, {3}s'.format(days, hours, minutes, seconds)
        else:
            banLengthString = 'You have been permanently banned from this server. ' \
                              'You will not be able to play on this server anymore.'

        self.air.sendNetEvent('banCheckResponse-%s' % sender, [sender, isBanned, banLengthString])

    def ban(self, avId, duration, comment):
        self.banFSMs[avId] = BanFSM(self, self.air, avId, comment, duration)
        self.banFSMs[avId].request('Start')
        self.banQueue.append(avId)

        self.acceptOnce(self.air.getAvatarExitEvent(avId), self.banDone, [avId])

    def banDone(self, avId):
        self.banFSMs[avId].request('Off')
        self.banFSMs[avId] = None

    def addBannedPlayer(self, avId, mac_addr, ip_addr, banFSM, task=None):
        banTaskName = 'ban-%s' % avId
        if taskMgr.hasTaskNamed(banTaskName):
            taskMgr.remove(banTaskName)

        if self.banQueue[0] == avId:
            duration = banFSM.duration

            # We are at the top of the queue, we will process this first.
            banList = open(self.BAN_LIST_FILE, 'a')
            banList.write('%s:%s\n%s:%s' % (mac_addr, duration, ip_addr, duration))
            banList.close()

            if avId in self.banQueue:
                self.banQueue.remove(avId)

            banFSM.request('Ban')

            if task:
                return task.done
        else:
            taskMgr.doMethodLater(3, lambda: self.addBannedPlayer(avId, mac_addr, ip_addr, banFSM), banTaskName)

    def sendUserInfo(self, mac_address, public_ip):
        avId = self.air.getAvatarIdFromSender()
        if (not mac_address) and (not public_ip):
            return

        if avId in self.banFSMs:
            banFSM = self.banFSMs[avId]
            if banFSM:
                self.addBannedPlayer(avId, mac_address, public_ip, banFSM)


@magicWord(category=CATEGORY_MODERATOR, types=[str])
def kick(reason='No reason specified'):
    """
    Kick the target from the game server.
    """
    target = spellbook.getTarget()
    if target == spellbook.getInvoker():
        return "You can't kick yourself!"
    datagram = PyDatagram()
    datagram.addServerHeader(
        target.GetPuppetConnectionChannel(target.doId),
        simbase.air.ourChannel, CLIENTAGENT_EJECT)
    datagram.addUint16(155)
    datagram.addString('You were kicked by a moderator for the following reason: %s' % reason)
    simbase.air.send(datagram)
    return "Kicked %s from the game server!" % target.getName()

@magicWord(category=CATEGORY_MODERATOR, types=[int, str])
def ban(duration, reason):
    """
    Ban the target from the game server.
    """
    target = spellbook.getTarget()
    if target == spellbook.getInvoker():
        return "You can't ban yourself!"
    if reason not in ('hacking', 'language', 'other'):
        return "'%s' is not a valid reason." % reason
    simbase.air.banManager.ban(target.doId, duration, reason)
    return "Banned %s from the game server!" % target.getName()
