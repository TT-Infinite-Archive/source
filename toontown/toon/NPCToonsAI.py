"""
Builds a district's NPCs.

This lives apart from NPCToons. An import of it from there would 
reach every DistributedNPC*AI module and drag the whole NPC server
tree into the client build.
"""
from panda3d.core import ConfigVariableBool

from toontown.hood import ZoneUtil
from toontown.toon import NPCToons
from toontown.toon import ToonDNA
from toontown.toonbase import ToontownGlobals

from toontown.toon import DistributedNPCToonAI
from toontown.toon import DistributedNPCClerkAI
from toontown.toon import DistributedNPCTailorAI
from toontown.toon import DistributedNPCBlockerAI
from toontown.toon import DistributedNPCFishermanAI
from toontown.toon import DistributedNPCPetclerkAI
from toontown.toon import DistributedNPCKartClerkAI
from toontown.toon import DistributedNPCPartyPersonAI
from toontown.toon import DistributedNPCSpecialQuestGiverAI
from toontown.toon import DistributedNPCFlippyInToonHallAI
from toontown.toon import DistributedNPCScientistAI
from toontown.toon import DistributedSmartNPCAI
from toontown.toon import DistributedNPCBankerAI
from toontown.toon import DistributedNPCYinAI
from toontown.toon import DistributedNPCYangAI
from toontown.toon import DistributedNPCLowdenClearAI


def createNPC(air, npcId, desc, zoneId, posIndex = 0, questCallback = None):
    canonicalZoneId, name, dnaType, gender, protected, type = desc
    if type == NPCToons.NPC_REGULAR:
        npc = DistributedNPCToonAI.DistributedNPCToonAI(air, npcId, questCallback=questCallback)
    elif type == NPCToons.NPC_HQ:
        npc = DistributedNPCToonAI.DistributedNPCToonAI(air, npcId, questCallback=questCallback, hq=1)
    elif type == NPCToons.NPC_CLERK:
        npc = DistributedNPCClerkAI.DistributedNPCClerkAI(air, npcId)
    elif type == NPCToons.NPC_TAILOR:
        npc = DistributedNPCTailorAI.DistributedNPCTailorAI(air, npcId)
    elif type == NPCToons.NPC_BLOCKER:
        npc = DistributedNPCBlockerAI.DistributedNPCBlockerAI(air, npcId)
    elif type == NPCToons.NPC_FISHERMAN:
        npc = DistributedNPCFishermanAI.DistributedNPCFishermanAI(air, npcId)
    elif type == NPCToons.NPC_PETCLERK:
        npc = DistributedNPCPetclerkAI.DistributedNPCPetclerkAI(air, npcId)
    elif type == NPCToons.NPC_KARTCLERK:
        npc = DistributedNPCKartClerkAI.DistributedNPCKartClerkAI(air, npcId)
    elif type == NPCToons.NPC_PARTYPERSON:
        npc = DistributedNPCPartyPersonAI.DistributedNPCPartyPersonAI(air, npcId)
    elif type == NPCToons.NPC_SPECIALQUESTGIVER:
        npc = DistributedNPCSpecialQuestGiverAI.DistributedNPCSpecialQuestGiverAI(air, npcId)
    elif type == NPCToons.NPC_FLIPPYTOONHALL:
        npc = DistributedNPCFlippyInToonHallAI.DistributedNPCFlippyInToonHallAI(air, npcId)
    elif type == NPCToons.NPC_SCIENTIST:
        npc = DistributedNPCScientistAI.DistributedNPCScientistAI(air, npcId)
    elif type == NPCToons.NPC_SMART:
        npc = DistributedSmartNPCAI.DistributedSmartNPCAI(air, npcId)
    elif type == NPCToons.NPC_BANKER:
        npc = DistributedNPCBankerAI.DistributedNPCBankerAI(air, npcId)
    elif type == NPCToons.NPC_YIN:
        if simbase.wantYinYang or simbase.holidayManager.isHolidayRunning(ToontownGlobals.HALLOWEEN):
            npc = DistributedNPCYinAI.DistributedNPCYinAI(air, npcId)
    elif type == NPCToons.NPC_YANG:
        if simbase.wantYinYang:
            npc = DistributedNPCYangAI.DistributedNPCYangAI(air, npcId)
    elif type == NPCToons.NPC_RESISTANCE:
        if air.wantGuilds:
            npc = DistributedNPCLowdenClearAI.DistributedNPCLowdenClearAI(air, npcId)
    else:
        print('createNPC() error!!!')

    npc.setName(name)
    dna = ToonDNA.ToonDNA()

    if dnaType == 'r':
        dnaNetString = NPCToons.getRandomDNA(npcId, gender)
        dna.makeFromNetString(dnaNetString)
    else:
        dna.newToonFromProperties(*dnaType)

    npc.setDNAString(dna.makeNetString())
    npc.setHp(15)
    npc.setMaxHp(15)
    npc.setPositionIndex(posIndex)
    npc.generateWithRequired(zoneId)

    if hasattr(npc, 'startAnimState'):
        npc.d_setAnimState(npc.startAnimState, 1.0)
    else:
        npc.d_setAnimState('neutral', 1.0)

    return npc


def createNpcsInZone(air, zoneId):
    npcs = []
    canonicalZoneId = ZoneUtil.getCanonicalZoneId(zoneId)
    npcIdList = NPCToons.zone2NpcDict.get(canonicalZoneId, [])
    for npcId in npcIdList:
        while npcIdList.count(npcId) > 1:
            npcIdList.remove(npcId)
    typeCounters = {}
    for npcId in npcIdList:
        npcDesc = NPCToons.NPCToonDict.get(npcId)
        if npcDesc[5] == NPCToons.NPC_FISHERMAN:
            if not air.wantFishing:
                continue
        if npcDesc[5] == NPCToons.NPC_PARTYPERSON:
            if not air.wantParties:
                continue
        if npcDesc[5] == NPCToons.NPC_SMART:
            if not ConfigVariableBool('want-talkative-tyler', False).getValue():
                continue
        posIndex = typeCounters.get(npcDesc[5], 0)
        typeCounters[npcDesc[5]] = posIndex + 1
        npcs.append(createNPC(air, npcId, npcDesc, zoneId, posIndex=posIndex))
    return npcs
