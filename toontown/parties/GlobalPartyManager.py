from direct.distributed.DistributedObjectGlobal import DistributedObjectGlobal


class GlobalPartyManager(DistributedObjectGlobal):
    notify = directNotify.newCategory('GlobalPartyManager')