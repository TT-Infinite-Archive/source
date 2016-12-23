from direct.showbase.DirectObject import DirectObject
from direct.directnotify.DirectNotifyGlobal import directNotify
from panda3d.core import *


class TTPicker(DirectObject):
    notify = directNotify.newCategory('TTPicker')
    ModeOutmostParent = 0
    ModeParent = 1
    ModePrecise = 2

    def __init__(self, mode=0, callback=None):
        DirectObject.__init__(self)
        self.pickedObj = None
        self.callback = callback
        self.mode = mode

        # Collision stuff
        self.picker = CollisionTraverser()
        self.queue = CollisionHandlerQueue()
        self.pickerNode = CollisionNode('mouseRay')
        self.pickerNP = base.camera.attachNewNode(self.pickerNode)
        self.pickerNode.setFromCollideMask(GeomNode.getDefaultCollideMask())
        self.pickerRay = CollisionRay()
        self.pickerNode.addSolid(self.pickerRay)
        self.picker.addCollider(self.pickerNP, self.queue)

        # Accept hot keys and mouse clicks
        self.accept('mouse1', self.__handleMouseClicked, extraArgs=[])
        self.accept('control-f1', self.setPickedObj, extraArgs=[base.localAvatar])
        self.accept('control-f2', self.setPickedObj, extraArgs=[base.camera])

    def destroy(self):
        self.pickedObj = None
        self.callback = None
        self.ignoreAll()

    def findObject(self, mpos):
        obj = None
        self.pickerRay.setFromLens(base.camNode, mpos.getX(), mpos.getY())
        self.picker.traverse(render)
        if self.queue.getNumEntries():
            self.queue.sortEntries()
            obj = self.queue.getEntry(0).getIntoNodePath()
            parent = obj.getParent()
            if self.mode == self.ModeOutmostParent:
                while parent != render and not parent.isEmpty():
                    # Get the highest order object which is not render
                    obj = parent
                    if obj.hasParent():
                        parent = obj.getParent()
            elif self.mode == self.ModeParent:
                if parent != render and not parent.isEmpty():
                    obj = parent

            if obj == render or obj.isEmpty():
                obj = None
        return obj

    def setPickedObj(self, obj):
        self.pickedObj = obj
        if self.callback:
            self.callback(obj)

    def getPickedObj(self):
        return self.pickedObj

    def __handleMouseClicked(self):
        object = self.findObject(base.mouseWatcherNode.getMouse())
        self.setPickedObj(object)
