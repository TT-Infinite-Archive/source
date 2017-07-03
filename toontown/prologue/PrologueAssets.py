from toontown.prologue import PrologueGlobals
from panda3d.core import NodePath
from toontown.toon import NPCToons


class PrologueAssets:
    def __init__(self, parent):
        self.propPool = {}
        self.actorPool = {}
        self.musicPool = {}
        self.sfxPool = {}
        self.parent = parent
        self.loaded = False

    def load(self):
        for name, data in PrologueGlobals.ACTORS.items():
            if 'npcId' in data:
                # This is an NPC
                self.createNPC(name, data)

        for name, path in PrologueGlobals.MUSIC.items():
            self.musicPool[name] = base.loadMusic(path)

        for name, path in PrologueGlobals.SFX.items():
            self.sfxPool[name] = base.loadSfx(path)
        self.loaded = True

    def cleanup(self):
        for model in self.propPool.values():
            model.removeNode()

        for actor in self.actorPool.values():
            actor.delete()

        self.actorPool.clear()
        self.musicPool.clear()
        self.sfxPool.clear()

        self.loaded = False
    
    def applyTransform(self, object, data):
        if 'pos' in data:
            object.setPos(data['pos'])
        if 'rotation' in data:
            object.setHpr(data['rotation'])
        if 'scale' in data:
            object.setScale(data['scale'])

    def createNPC(self, name, data):
        npc = NPCToons.createLocalNPC(data['npcId'])
        npc.metadata = data
        npc.initializeBodyCollisions('toon')
        npc.reparentTo(hidden)
        self.applyTransform(npc, data)
        if 'initial' in data:
            npc.animFSM.request(data['initial'])
        self.actorPool[name] = npc

    def __modelDone(self, nodePath, name):
        self.propPool[name] = nodePath

    def getCopyModel(self, name):
        np = self.parent.attachNewNode(name)
        self.propPool.get(name).copyTo(np)
        return np

    def getNPC(self, name):
        return self.actorPool.get(name)
