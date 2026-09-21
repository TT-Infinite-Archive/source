from toontown.nametag import NametagGlobals
from toontown.toon import ToonDNA
from toontown.toon.NPCToons import NPCToonDict, getRandomDNA
from toontown.toonbase import SettingsGlobals


def createLocalNPC(npcId):
    from . import Toon

    if npcId not in NPCToonDict:
        return None

    desc = NPCToonDict[npcId]
    canonicalZoneId, name, dnaType, gender, protected, type = desc

    npc = Toon.Toon()
    npc.setName(name)
    npc.setPickable(0)
    npc.setPlayerType(NametagGlobals.CCNonPlayer)

    dna = ToonDNA.ToonDNA()

    if dnaType == 'r':
        dnaNetString = getRandomDNA(npcId, gender)
        dna.makeFromNetString(dnaNetString)
    else:
        dna.newToonFromProperties(*dnaType)

    npc.setDNAString(dna.makeNetString())
    npc.animFSM.request('neutral')
    if settings.get(SettingsGlobals.AnimationSmoothing):
        npc.setBlend(frameBlend=True)

    return npc
